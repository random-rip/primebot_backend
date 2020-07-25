from app_prime_league.models import Game, Team
from telegram_interface.tg_singleton import TelegramMessagesWrapper, send_message


def main():
    pattern = "Hallo Beschwörer,\n" \
              "ich war leider down #rip, aber jetzt gehts wieder (hoffentlich).\n" \
              "Aufgrund von Serverfehlern war ich am 24.07.2020 nicht vollständig erreichbar." \
              "Bitte versucht noch einmal, euer Team zu initialisieren (/start)." \
              "Die Registrierung ist in der Regel nach maximal 30 Sekunden abgeschlossen. " \
              "Sollte das bei euch nicht der Fall sein, schreibt bitte direkt meine Entwickler an (@Grayknife).\n" \
              "Liebe Grüße\n" \
              "_Grayknife und Orbis_"

    print(send_message(msg=pattern, chat_id=-490819576))
    print(send_message(msg=pattern, chat_id=-373994529))


def run():
    main()
