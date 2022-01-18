from app_prime_league.models import Changelog
from utils.changelogs import CHANGELOGS


def main():
    changes = []
    for number, change in CHANGELOGS.items():
        changes.append(Changelog(version_number=change.get('version'), description=change.get('text')))
    Changelog.objects.bulk_create(changes)


def run():
    main()