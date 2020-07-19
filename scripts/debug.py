from datetime import datetime

import requests
import re

from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from comparing.member_comparer import MemberComparer
from data_crawling.api import crawler, Crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime, \
    TeamHTMLParser
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper, send_message


def main():
    crawler = Crawler(local=False)
    website = crawler.get_team_website(105878)
    parser = TeamHTMLParser(website)
    team = Team(id=105878)
    members = parser.get_members()
    print(members[0][0])
    comparer = MemberComparer(105878, members)
    comparer.compare_members()


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
