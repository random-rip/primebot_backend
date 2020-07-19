from app_prime_league.models import Game
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    match = Game.objects.filter(game_id=596473).first()

    print(match.get_op_link_of_enemies(only_lineup=False))

    TelegramMessagesWrapper.send_new_lineup_of_enemies(match)
    # pattern = "Hallo {team_tag},\n" \
    #       "hier ein kurzes Update der letzten größeren Änderungen am Bot.\n\n" \
    #       "*Neuer Command:* \n" \
    #       "- /setlogo - setzt euer Telegram Gruppenbild auf das bei der PrimeLeague hinterlegte Foto. " \
    #       "(Der Bot benötigt dafür Adminrechte)\n\n" \
    #       "*Überarbeiteter Command:* \n" \
    #       "- /start - startet die Registirieung eines Teams. Hierbei wurden die Abfrage nach der TeamID angepasst und " \
    #       "der Bot fragt anschließend nach der Übernahme des Gruppenbildes. \n" \
    #       "- /settings - lässt euch weiterhin die Settings für euren Bot einstellen, jedoch wurde die Menüführung " \
    #       "verändert. Schaut es euch gern an. Die Einstellungen lassen sich nun bequem über ein übersichtliches Menü " \
    #       "einstellen. Weitere Optionen sind in Planung. Ihr könnt uns gerne /feedback geben.\n\n" \
    #       "*Bugfixes:* \n" \
    #       "1️⃣ Ein Fehler wurde behoben, durch den Teams, die sich registriert haben, keine Bestätigungsmeldung " \
    #       "bekommen haben!\n" \
    #       "2️⃣ Ein Fehler wurde behoben, durch den Spiele, die aufgrund von lineup\_notready beendet wurden, nicht als " \
    #       "gespielt markiert wurden.\n" \
    #       "3️⃣ Kleinere Fehler wurden behoben.\n" \
    #       "Sollte ihr einen Fehler bemerken, nutzt bitte /issue.\n\n" \
    #       "*Coming Soon:*\n" \
    #       "1️⃣ Vollständige Integration für Teams, die sich noch in der Swiss Starter Kalibrierungsphase befinden.\n" \
    #       "2️⃣ Anpinnen der Nachricht mit dem nächsten Spieltag.\n" \
    #       "3️⃣ Play-Off Integration. Möglicherweise noch nicht vollständig für diese Play-Offs.\n\n" \
    #       "Schreibt uns gerne, sollte euch noch etwas einfallen (/feedback).\n\n" \
    #       "Liebe Grüße\n" \
    #       "_Grayknife und Orbis_"


def run():
    main()
