"""
Managment gateway into the scraper mechansim.
Usage: python manage.py scrape [--meta | --term <termid>]
"""
from django.core.management.base import BaseCommand, CommandError
import celery

from api import tasks
from api.models import Term
from pprint import PrettyPrinter

pp = PrettyPrinter()


class Command(BaseCommand):
    help = 'Scrapes the registrar for course data and evaluations.'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true',
                            help='scrape for all possible information')
        parser.add_argument('--meta', action='store_true',
                            help='scrape the term and subject meta')
        parser.add_argument('--terms', nargs='+', metavar='term',
                            help='scrape all the provided term codes')
        parser.add_argument('--extra', action='store_true',
                            help='attempt to scrape additional information')
        # TODO: incremental

    def handle(self, *args, **options):
        task_q = []

        def all_terms():
            return [t.code for t in Term.objects.all()]

        if options['meta'] or options['all']:
            task_q.append(celery.group([
                tasks.import_terms.s(),
                tasks.import_subjects.s(),
            ]))

        if options['terms'] or options['all']:
            terms = options['terms'] if not options['all'] else all_terms()
            task_q.append(celery.group([tasks.import_courses_in_term.s(t)
                                        for t in terms]))

        if options['extra'] or options['all']:
            task_q.append(tasks.import_all_extra_evals.s())

        celery.chain(task_q)()

        self.stdout.write(self.style.SUCCESS('sucessfully queued task chain:'))
        for task in task_q:
            self.stdout.write('- %s' % pp.pformat(task))
