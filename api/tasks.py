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
from .models import User

logger = get_task_logger(__name__)


@shared_task
def scrape_terms():
    """
    Scrapes all terms and inserts them into the database.
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


@shared_task
def scrape_subjects():
    """
    Scrapes all subjects from web feeds and inserts them into the database.
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


@shared_task
def scrape_courses(term_suffix, subj_code):
    """
    Scrapes all courses from web feeds and inserts them into the database.
    Fails loudly if a subject is not already in the database, so make sure that
    scrape_subjects is run first.
    """
    subject = Subject.objects.get(code=subj_code)
    term = Term.objects.get(suffix=term_suffix)
    courses = registrar.courses.scrape(term.code, subj_code)

    # Insert courses that are not already in the database
    for course_data in courses:
        # Create the course, put in main course numbering
        course, created = Course.objects.get_or_create(
            id=course_data['course_id'],
        )
        if created:
            logger.info('imported course %s' % course)

        # Create primary course number
        course_num, created = subject.course_numbers.get_or_create(
            number=course_data['catalog_number'],
        )

        # Create the current offering
        offering, created = course.offerings.get_or_create(
            guid=course_data['guid'],
            defaults={
                'course': course,
                'title': course_data['title'],
                'term': term,
                'primary_number': course_num,
            }
        )

        # this line comes first so that the below two lines'
        # effects are not overwritten
        offering.cross_listings.clear()
        course_num.course = offering
        course_num.save()

        # Add crosslistings
        if 'cross_listings' in course_data:
            for xlist_data in course_data['crosslistings']:
                subject = Subject.objects.get(code=xlist_data['subject'])
                course_num, created = subject.course_numbers.get_or_create(
                    number=xlist_data['catalog_number'],
                )
                course_num.course = offering
                course_num.save()
                offering.cross_listings.add(course_num)

        # TODO: scrape dist reqs, etc. from course_details.py

        # Add instructors
        offering.instructors.clear()
        for instr_data in course_data['instructors']:
            instructor, created = Instructor.objects.get_or_create(
                id=instr_data['emplid'],
                defaults={
                    'first_name': instr_data['first_name'],
                    'last_name': instr_data['last_name'],
                },
            )
            offering.instructors.add(instructor)
            if created:
                    logger.info('imported instructor %s', instructor)

        # TODO: scrape professor from registrar

        # Add sections
        offering.sections.all().delete()
        for section_data in course_data['classes']:
            section = offering.sections.create(
                id=section_data['class_number'],
                name=section_data['section'],
                type=section_data['type_name'],
                status=section_data['status'],
                enrollment=int(section_data['enrollment']),
                capacity=int(section_data['capacity']),
            )

            # and the meetings
            section.meetings.all().delete()
            for meeting_data in section_data['schedule']['meetings']:
                location = ''
                if 'room' in meeting_data:
                    location = '%s %s' % (meeting_data['building']['name'],
                                          meeting_data['room'])

                meeting = section.meetings.create(
                    start_time=meeting_data['start_time'],
                    end_time=meeting_data['end_time'],
                    location=location,
                )


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
