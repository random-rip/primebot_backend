from utils.changelogs import CHANGELOGS
from app_prime_league.models import Changelog

def main():
    changes = [
        Changelog(version_number=CHANGELOGS.get(1).get('version'), description=CHANGELOGS.get(1).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(2).get('version'), description=CHANGELOGS.get(2).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(3).get('version'), description=CHANGELOGS.get(3).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(4).get('version'), description=CHANGELOGS.get(4).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(5).get('version'), description=CHANGELOGS.get(5).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(6).get('version'), description=CHANGELOGS.get(6).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(7).get('version'), description=CHANGELOGS.get(7).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(8).get('version'), description=CHANGELOGS.get(8).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(9).get('version'), description=CHANGELOGS.get(9).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(10).get('version'), description=CHANGELOGS.get(10).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(11).get('version'), description=CHANGELOGS.get(11).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(12).get('version'), description=CHANGELOGS.get(12).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(13).get('version'), description=CHANGELOGS.get(13).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(14).get('version'), description=CHANGELOGS.get(14).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(15).get('version'), description=CHANGELOGS.get(15).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(16).get('version'), description=CHANGELOGS.get(16).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(17).get('version'), description=CHANGELOGS.get(17).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(18).get('version'), description=CHANGELOGS.get(18).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(19).get('version'), description=CHANGELOGS.get(19).get('text'),
                  created_at=None, updated_at=None),
        Changelog(version_number=CHANGELOGS.get(20).get('version'), description=CHANGELOGS.get(20).get('text'),
                  created_at=None, updated_at=None),
    ]

    Changelog.objects.bulk_create(changes)

def run():
    main()
