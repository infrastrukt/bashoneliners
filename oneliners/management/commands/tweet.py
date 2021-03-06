from optparse import make_option

from django.core.management.base import BaseCommand
from django.test.client import RequestFactory
from oneliners.models import OneLiner
from oneliners.tweet import tweet
from oneliners.views import format_tweet, format_canonical_url

default_limit = 5


class Command(BaseCommand):
    help = 'List and tweet one-liners'

    option_list = BaseCommand.option_list + (
        make_option('--pk', '--id', type=int, action='append',
                    help='Select one-liner by pk/id'),
        make_option('--limit', '-l', type=int, default=default_limit,
                    help='Maximum one-liners to select'),
        make_option('--tweet', action='store_true',
                    help='Tweet selected one-liners'),
    )

    def handle(self, *args, **options):
        pklist = options['pk']
        limit = options['limit']
        test = not options['tweet']

        if pklist:
            oneliners = OneLiner.objects.filter(pk__in=pklist)
        else:
            oneliners = OneLiner.recent()[:limit]

        for oneliner in oneliners:
            self.handle_oneliner(oneliner, test)

    def handle_oneliner(self, oneliner, test=True):
        request = RequestFactory().get('/')
        request.META = {
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '8000',
        }
        baseurl = format_canonical_url(request)
        message = format_tweet(oneliner, baseurl)
        self.stdout.write('%s: %s' % (oneliner.pk, message))
        result = tweet(message, test)
        if not test:
            self.stdout.write('# result: ' + str(result))
        self.stdout.write('')


# eof
