"""
Tasks to scrape the registrar for the API.
"""
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.utils.log import get_task_logger
from princeton_scrapers import courses

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
def scrape_all_terms_meta():
    """
    Scrapes all terms and inserts it into the database.
    """
    terms = courses.terms.scrape('all')

    # Insert terms that are not already in the database
    for term_data in terms:
        term, created = Term.objects.get_or_create(
            code=term_data['code'],
            defaults={
                'suffix': term_data['suffix'],
                'code': term_data['code'],
                'name': term_data['cal_name'],
                'start_date': term_data['start_date'],
                'end_date': term_data['end_date'],
            },
        )

        if created:
            logger.info('imported term meta %s' % term.name)
