from datetime import datetime

import requests
import re

from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from data_crawling.api import crawler, Crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime, \
    TeamHTMLParser
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper, send_message


def main():
    pattern = "Hallo {team_tag},\n" \
          "hier ein kurzes Update der letzten größeren Änderungen am Bot.\n\n" \
          "*Neuer Command:* \n" \
          "- /setlogo - setzt euer Telegram Gruppenbild auf das bei der PrimeLeague hinterlegte Foto. " \
          "(Der Bot benötigt dafür Adminrechte)\n\n" \
          "*Überarbeiteter Command:* \n" \
          "- /start - startet die Registirieung eines Teams. Hierbei wurden die Abfrage nach der TeamID angepasst und " \
          "der Bot fragt anschließend nach der Übernahme des Gruppenbildes. \n" \
          "- /settings - lässt euch weiterhin die Settings für euren Bot einstellen, jedoch wurde die Menüführung " \
          "verändert. Schaut es euch gern an. Die Einstellungen lassen sich nun bequem über ein übersichtliches Menü " \
          "einstellen. Weitere Optionen sind in Planung. Ihr könnt uns gerne /feedback geben.\n\n" \
          "*Bugfixes:* \n" \
          "1️⃣ Ein Fehler wurde behoben, durch den Teams, die sich registriert haben, keine Bestätigungsmeldung " \
          "bekommen haben!\n" \
          "2️⃣ Ein Fehler wurde behoben, durch den Spiele, die aufgrund von lineup\_notready beendet wurden, nicht als " \
          "gespielt markiert wurden.\n" \
          "3️⃣ Kleinere Fehler wurden behoben.\n" \
          "Sollte ihr einen Fehler bemerken, nutzt bitte /issue.\n\n" \
          "*Coming Soon:*\n" \
          "1️⃣ Vollständige Integration für Teams, die sich noch in der Swiss Starter Kalibrierungsphase befinden.\n" \
          "2️⃣ Anpinnen der Nachricht mit dem nächsten Spieltag.\n" \
          "3️⃣ Play-Off Integration. Möglicherweise noch nicht vollständig für diese Play-Offs.\n\n" \
          "Schreibt uns gerne, sollte euch noch etwas einfallen (/feedback).\n\n" \
          "Liebe Grüße\n" \
          "_Grayknife und Orbis_"

    teams = Team.objects.exclude(telegram_channel_id__isnull=True)
    for team in teams:
        print(team.id)
        if team.id in  [111914, 93008, 105959, 105878, ]:
            continue
        msg = pattern.format(team_tag=team.team_tag, )
        send_message(msg=msg, chat_id=team.telegram_channel_id)


# Command to run this file:
# python manage.py runscript debug
def run():
    main()
