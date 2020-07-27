from app_prime_league.models import Team
from telegram_interface import send_message


def main():
    pattern = "Hallo {team_tag},\n" \
              "hier ein kurze Zusammenfassung der letzten größeren Änderungen am PrimeBot.\n\n" \
              "*Updates:*\n" \
              "1️⃣Gruppen, die in eine Supergruppe migriert wurden, werden jetzt vollständig unterstützt.\n" \
              "2️⃣Spiele von Swiss Starter-Teams wurden integriert und werden täglich abgerufen.\n" \
              "3️⃣Die wöchentlichen Nachrichten mit dem OP.gg-Link werden jetzt an die Gruppe angepinnt. " \
              "Dazu benötigt der Bot Adminrechte. Das Anheften kann in den /settings deaktiviert bzw. " \
              "aktiviert werden.\n" \
              "4️⃣Die Benachrichtigungen zu Botpatches können in den /settings deaktiviert bzw. aktiviert werden.\n" \
              "5️⃣Der aktuelle Status einer Einstellung wird nun direkt in der Nachricht angezeigt.\n\n" \
              "*Bugfixes:*\n" \
              "Ein Fehler wurde behoben, durch den der OP.gg-Link des Gegnerteams auf IOS Geräten nicht " \
              "richtig dargestellt wurde.\n\n" \
              "*Coming Soon:*\n" \
              "1️⃣Pushnachrichten für neue Kommentare in ungespielten Matches\n" \
              "2️⃣Zeitnahe Integration der OP.gg-Links für Playoff-Spiele\n\n" \
              "Liebe Grüße\n" \
              "@Grayknife _und_ @OrbisK\n"

    teams = Team.objects.exclude(telegram_id__isnull=True)
    for team in teams:
        print(team.id)
        # if team.id in [111914, 93008, 105959, 105878, ]:
        #     continue
        msg = pattern.format(team_tag=team.team_tag, )
        print(send_message(msg=msg, chat_id=team.telegram_id))


def run():
    main()
