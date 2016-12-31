"""
Tasks to scrape the registrar for the API.
"""
from __future__ import absolute_import, unicode_literals
from celery import shared_task
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
    """Import and overwrite the given instructors data into the offering."""
    offering.instructors.clear()
    for instructor_data in instructors_data:
        instructor, created = Instructor.objects.get_or_create(
            id=instructor_data['emplid'],
            defaults={
                'first_name': instructor_data['first_name'],
                'last_name': instructor_data['last_name'],
            },
        )
        offering.instructors.add(instructor)

    # TODO: scrape the actual professor from registrar


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
def scrape_courses(term_code, subj_code):
    """
    Scrapes all courses from web feeds and inserts them into the database.
    Returns a list of the course ids found.
    Fails loudly if a subject is not already in the database, so make sure that
    scrape_subjects is run first.
    """
    pu.db
    subject = Subject.objects.get(code=subj_code)
    term = Term.objects.get(code=term_code)
    courses = registrar.courses.scrape(term_code, subj_code)
    course_ids = []

    for course_data in courses:
        course, created = Course.objects.get_or_create(
            id=course_data['course_id'],
        )
        if created:
            logger.info('new course %s' % course)
        course_ids.append(course.id)

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
        # TODO: scrape dist reqs, PDF/Audit, addl info from course_details.py
        import_instructors(course_data['instructors'], offering)
        import_sections(course_data['classes'], offering)

    return course_ids


@shared_task
def scrape_evals(term_code, course_id):
    """
    Delete and scrape all evaluations for a given course offering.
    """
    offering = Offering.objects.get(course__id=course_id,
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
