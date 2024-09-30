from django.core.management import BaseCommand

from request_queue.cluster import run


class Command(BaseCommand):
    help = "Start the request queue"
    requires_system_checks = []
    requires_migrations_checks = False

    def handle(self, *args, **options):
        run()
