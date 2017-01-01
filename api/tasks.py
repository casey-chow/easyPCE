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
from .models import Offering
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
            logger.info('imported term meta %s' % term)

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
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults={
                'name': subject_data['name'],
            },
        )

        if created:
            logger.info('imported subject meta %s' % subject)

    return subjects


def import_crosslistings(xlists_data, offering):
    """
    Import the given crosslistings data into the offering, setting up the
    proper many to one relationship as well.
    """
    for xlist_data in xlists_data:
        subject = Subject.objects.get(code=xlist_data['subject'])
        course_num, created = subject.course_numbers.get_or_create(
            number=xlist_data['catalog_number'],
        )
        # course_num.course = offering
        # course_num.save()
        offering.cross_listings.add(course_num)


def import_instructors(instructors_data, offering):
    """
    Import the given instructors data into the database.
    Does not associate them to the course.
    """
    for instructor_data in instructors_data:
        instructor, created = Instructor.objects.get_or_create(
            emplid=instructor_data['emplid'],
            defaults={
                'first_name': instructor_data['first_name'],
                'last_name': instructor_data['last_name'],
            },
        )


def import_meetings(meetings_data, section):
    """Import and overwrite the given meetings data into the offering."""
    section.meetings.all().delete()
    for meeting_data in meetings_data:
        location = ''
        if 'room' in meeting_data:
            location = '%s %s' % (meeting_data['building']['name'],
                                  meeting_data['room'])

        meeting = section.meetings.create(
            start_time=meeting_data['start_time'],
            end_time=meeting_data['end_time'],
            location=location,
        )


def import_sections(sections_data, offering):
    """Import and overwrite the given sections data into the offering."""
    offering.sections.all().delete()
    for section_data in sections_data:
        section = offering.sections.create(
            id=section_data['class_number'],
            name=section_data['section'],
            type=section_data['type_name'],
            status=section_data['status'],
            enrollment=int(section_data['enrollment']),
            capacity=int(section_data['capacity']),
        )

        import_meetings(section_data['schedule']['meetings'], section)


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

    for course_data in courses:
        course, created = Course.objects.get_or_create(
            course_id=course_data['course_id'],
        )
        if created:
            logger.info('new course %s' % course)

        # Scrape details and evals for the course as well
        scrape_details.delay(term_code, course.course_id)
        scrape_evals.delay(term_code, course.course_id)

        # Primary course number
        course_num, created = subject.course_numbers.get_or_create(
            number=course_data['catalog_number'],
        )

        # Current offering
        offering, created = course.offerings.get_or_create(
            guid=course_data['guid'],
            defaults={
                'course': course,
                'title': course_data['title'],
                'term': term,
                'primary_number': course_num,
            },
        )

        # this comes first so that the main course num id isn't overwritten
        offering.cross_listings.clear()
        course_num.offering = offering
        course_num.save()

        if 'cross_listings' in course_data:
            import_crosslistings(course_data['cross_listings'], offering)
        import_instructors(course_data['instructors'], offering)
        import_sections(course_data['classes'], offering)

    return course_ids


@shared_task
def scrape_details(term_code, course_id):
    """
    Supplements existing course information with details, if possible.
    Assumes that instructors are already in the DB.
    """
    offering = Offering.objects.get(term__code=term_code,
                                    course__course_id=course_id)
    details = registrar.course_details.scrape(term_code, course_id)

    offering.additional_info = details['additional_info']
    offering.pdf = details['enroll_params']['pdf']
    offering.pdf_only = details['enroll_params']['pdf_only'] or False
    offering.audit = details['enroll_params']['audit']
    offering.dist_req = details['dist_req'] or ''

    instructors = Instructor.objects.filter(emplid__in=details['instructors'])
    offering.instructors.set(instructors)

    offering.save()


@shared_task
def scrape_evals(term_code, course_id):
    """
    Delete and scrape all evaluations for a given course offering.
    """
    offering = Offering.objects.get(course__course_id=course_id,
                                    term__code=int(term_code))
    stats, comments = registrar.evals.scrape(term_code, course_id)

    # Insert evaluations
    offering.evaluations.all().delete()
    for question, response in stats.iteritems():
        offering.evaluations.create(
            question_text=question,
            response_avg=response,
        )

    # Insert advice
    offering.advice.all().delete()
    for comment in comments:
        offering.advice.create(text=comment)


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
