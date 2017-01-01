"""
Managment gateway into the scraper mechansim.
Usage: python manage.py scrape [--meta | --term <termid>]
"""
from django.core.management.base import BaseCommand, CommandError
import celery

from api import tasks
from pprint import PrettyPrinter


class Command(BaseCommand):
    help = 'Scrapes the registrar for course data and evaluations.'

    def add_arguments(self, parser):
        parser.add_argument('--meta', action='store_true',
                            help='scrape the term and subject meta')
        parser.add_argument('--terms', nargs='+', metavar='term',
                            help='scrape all the provided term codes')
        # TODO: incremental

    def handle(self, *args, **options):
        pp = PrettyPrinter()
        pp.pprint(args)
        pp.pprint(options)
        task_q = []

        if options['meta']:
            task_q.append(celery.group([
                tasks.scrape_terms.s(),
                tasks.scrape_subjects.s(),
            ]))

        if 'terms' in options:
            terms = options['terms']
            task_q.append(celery.group([tasks.scrape_courses_in_term.s(t)
                                        for t in terms]))

        celery.chain(task_q)()

        self.stdout.write(self.style.SUCCESS('sucessfully queued task chain:'))
        for task in task_q:
            self.stdout.write('- %s' % pp.pformat(task))
