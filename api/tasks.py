"""
Tasks to scrape the registrar for the API.
"""
from __future__ import absolute_import, unicode_literals
from celery import shared_task, group
from celery.utils.log import get_task_logger
from princeton_scrapers import registrar

from .models import Term
from .models import Subject
from .models import Course
from .models import CourseNumber
from .models import Instructor
from .models import Section
from .models import Evaluation
from .models import Advice

logger = get_task_logger(__name__)


# TODO: make a function that allows for incremental scraping so that
# this worker isn't running forever
@shared_task
def scrape_terms():
    """
    Scrapes all terms and inserts them into the database. Returns the
    terms found.
    """
    terms = registrar.terms.scrape()

    # Insert terms not already in the database
    for term_data in terms:
        logger.info('attempting import of term %s' % term_data['code'])
        term, created = Term.objects.get_or_create(
            code=term_data['code'],
            defaults={
                'suffix': term_data['suffix'],
                'name': term_data['cal_name'],
                'start_date': term_data['start_date'],
                'end_date': term_data['end_date'],
            },
        )
        if created:
            logger.info('created term meta %s' % term)

    return terms


@shared_task
def scrape_subjects():
    """
    Scrapes all subjects from web feeds and inserts them into the database.
    Returns the subjects found.
    """
    subjects = registrar.subjects.scrape()

    # Insert subjects not already in the database
    for subject_data in subjects:
        logger.info('attempting import of subject %s' % subject_data['code'])
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults={
                'name': subject_data['name'],
            },
        )
        if created:
            logger.info('created subject meta %s' % subject)

    return subjects


@shared_task
def scrape_courses_in_subject(term_code, subj_code):
    """
    Scrapes all courses from web feeds and inserts them into the database.
    Returns a list of the course ids found.
    Fails loudly if a subject is not already in the database, so make sure that
    scrape_subjects is run first.
    """
    subject = Subject.objects.get(code=subj_code)
    term = Term.objects.get(code=term_code)
    courses = registrar.courses.scrape(term_code, subj_code)
    course_ids = []

    def import_crosslistings(xlists_data, course):
        """
        Import the given crosslistings data into the course, setting up the
        proper many to one relationship as well.
        """
        for xlist_data in xlists_data:
            subject = Subject.objects.get(code=xlist_data['subject'])
            course_num, created = subject.course_numbers.get_or_create(
                number=xlist_data['catalog_number'],
            )
            course_num.course = course
            course_num.save()

    def import_instructors(instructors_data, course):
        """
        Import the given instructors data into the database.
        Does not associate them to the course.
        """
        for instructor_data in instructors_data:
            logger.info('attempting import of instructor %s'
                        % instructor_data['emplid'])
            instructor, created = Instructor.objects.get_or_create(
                emplid=instructor_data['emplid'],
                defaults={
                    'first_name': instructor_data['first_name'],
                    'last_name': instructor_data['last_name'],
                },
            )
            instructor.courses.add(course)
            if created:
                logger.info('created instructor %s' % instructor)

    def import_meetings(meetings_data, section):
        """Import and overwrite the given meetings data into the course."""
        section.meetings.all().delete()
        for meeting_data in meetings_data:
            location = ''
            if 'room' in meeting_data:
                location = '%s %s' % (meeting_data['building']['name'],
                                      meeting_data['room'])

            logger.info('attempting import of meeting at %s' % location)
            meeting = section.meetings.create(
                start_time=meeting_data['start_time'],
                end_time=meeting_data['end_time'],
                location=location,
            )
            logger.info('created meeting %s' % meeting)

    def import_sections(sections_data, course):
        """Import and overwrite the given sections data into the course."""
        course.sections.all().delete()
        for section_data in sections_data:
            logger.info('attempting import of section %s'
                        % section_data['class_number'])
            section = course.sections.create(
                class_id=section_data['class_number'],
                name=section_data['section'],
                type=section_data['type_name'],
                status=section_data['status'],
                enrollment=int(section_data['enrollment']),
                capacity=int(section_data['capacity']),
            )
            logger.info('imported section %s' % section)

            import_meetings(section_data['schedule']['meetings'], section)

    for course_data in courses:
        logger.info('attempting import of course %s' % course_data['guid'])

        course_num, _ = subject.course_numbers.get_or_create(
            number=course_data['catalog_number'],
        )

        course, created = Course.objects.get_or_create(
            course_id=course_data['course_id'],
            term=term,
            defaults={
                'title': course_data['title'],
                'term': term,
                'primary_number': course_num,
                'description': course_data['detail']['description'],
            },
        )
        # course.cross_listings.clear()
        course.primary_number = course_num
        course.save()

        course_num.course = course
        course_num.save()

        if created:
            logger.info('imported course %s' % course)

        if 'cross_listings' in course_data:
            import_crosslistings(course_data['cross_listings'], course)
        import_instructors(course_data['instructors'], course)
        import_sections(course_data['classes'], course)

        scrape_details.delay(term_code, course.course_id)
        scrape_evals.delay(term_code, course.course_id)


@shared_task(time_limit=30)
def scrape_details(term_code, course_id):
    """
    Supplements existing course information with details, if possible.
    Assumes that instructors are already in the DB.
    """
    logger.info('attempting import of details for %s in term %s'
                % (course_id, term_code))
    course = Course.objects.get(term__code=int(term_code),
                                course_id=course_id)
    details = registrar.course_details.scrape(term_code, course_id)

    course.additional_info = details['additional_info']
    course.pdf = details['enroll_params']['pdf']
    course.pdf_only = details['enroll_params']['pdf_only'] or False
    course.audit = details['enroll_params']['audit']
    course.dist_req = details['dist_req'] or ''

    instructors = Instructor.objects.filter(emplid__in=details['instructors'])
    course.instructors.set(instructors)

    course.details_scraped = True
    course.save()
    logger.info('imported details for %s in term %s' % (course_id, term_code))


@shared_task(time_limit=30)
def scrape_evals(term_code, course_id):
    """
    Delete and scrape all evaluations for a given course.
    """
    logger.info('attempting import of evals for %s in term %s'
                % (course_id, term_code))
    course = Course.objects.get(course_id=course_id,
                                term__code=int(term_code))
    stats, comments = registrar.evals.scrape(term_code, course_id)

    course.evaluations.all().delete()
    for question, response in stats.iteritems():
        course.evaluations.create(
            question_text=question,
            response_avg=response,
        )

    course.advice.all().delete()
    for comment in comments:
        course.advice.create(text=comment)

    course.evals_scraped = True
    course.save()
    logger.info('imported evals for %s in term %s' % (course_id, term_code))


@shared_task
def scrape_courses_in_term(term_code):
    """
    Scrapes all courses in the given term.
    TODO: Make this incremental.
    """
    subjects = [subject.code for subject in Subject.objects.all()]
    tasks = [scrape_courses_in_subject.s(term_code, subject)
             for subject in subjects]
    group(tasks)()
