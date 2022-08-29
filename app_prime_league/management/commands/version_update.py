from django.core.management import BaseCommand

from app_api.modules.status.views import GitHub
from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage

message = """
Hallo {team.name},

🔥 Version {version} ist draußen 🔥

1️⃣ Migrierung von Textcommands zu Slash Commands. Da Discord am 31.8.2022 alte API Versionen einstampft und den Messagecontent als privileged Intent einstuft (https://support-dev.discord.com/hc/en-us/articles/4404772028055), mussten wir die `discord.py` Version erhöhen.
Wir haben die Materie von Slash commands noch nicht zu 100% durchschaut, weswegen es noch zu Fehlern kommen kann. Bitte teilt diese uns mit. ♥

Dadurch ergeben sich folgende Änderungen für Discorduser:
- Ab sofort sind alle Interaktionen mit dem Bot über Slash Commands geregelt, also nicht mehr `!bop` sondern `/bop`. Am besten probiert ihr es aus. Wenn es nicht funktioniert, sind eventuell Slash Commands auf eurem Server deaktiviert oder ihr habt keine Berechtigungen Slash Commands auszuführen. Wendet euch dann an eure zuständigen Serveradmins (Hier ein Artikel dazu https://support.discord.com/hc/de/articles/4644915651095-Command-Permissions)

2️⃣ Alle weiteren Änderungen findet ihr auf unserer Website: https://www.primebot.me/changelogs

Sternige Grüße
– PrimeBot devs
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        teams = Team.objects.get_registered_teams().filter()
        for team in teams:
            try:
                print(team)
                dispatcher = MessageDispatcher(team)
                dispatcher.dispatch_raw_message(
                    msg=NotificationToTeamMessage(
                        team=team,
                        custom_message=message,
                        version=GitHub.latest_version()["version"],
                    )
                )
            except Exception as e:
                print(e)
