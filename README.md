### SETUP
Requirements:
- Python 3.8+
- MariaDB/MySQL (Windowsprogramm: XAMPP)
- virtualenv (pip package):  `pip install virtualenv`


1. Git Repository klonen HTTPS `git clone https://gitlab.com/primebot1/prime_league_bot.git`
2. `cd prime_league_bot`
3. Erstelle virtuelle environment `virtualenv venv` oder über die IDE
4. Venv aktivieren (Linux): `source venv/Scripts/activate` oder in Windows Powershell (PS): `venv\Scripts\Activate.bat`
5. Installiere requirements `pip install -r requirements.txt`
6. Erstelle `.env` File aus der `.env.example` und setze Variablen
   1. Es muss ein Bot-Token und die Application ID aus dem Discord [Developerportal](https://discord.com/developers/applications) geholt werden
   2. Es muss ein Telegrambot bei Telegram erstellt werden (Chat mit Botfather)
7. Datenbank erstellen
8. Migrations auf Datenbank anwenden `python manage.py migrate`

### Projektstruktur

- ``app_prime_league`` enthält Models und Commands.
  - Model ``Match``: Relevante Informationen zu einem Match
  - Model ``Player``: Relevante Informationen zu einem Spieler (bspw. Summonername)
  - Model ``Team``: Relevante Informationen zu einem Team (bspw. Name, Tag, Bild, Discord Channel ID, )
  - Model ``ScoutingWebsite``: Hält alle möglichen Scoutingwebsites (aktuell: op.gg, u.gg, xdx.gg)
  - Model ``Suggestion``: Suggestions von Matches
  - Model ``Setting``: Einstellungen von Teams zu Benachrichtigungen etc.
  - Model ``Comment``: Kommentare zu Matches
  - ``MatchMetaData``: Vergleichsobjekt zu einem `Match` für den Comparer
- ``bots`` enthält alle relevanten Discord- und Telegram-Skripte, LanguageFiles, und den MessageDispatcher.
- ``core`` enthält alle die gesamte PrimeLeague-Kommunikation, Parsing und Comparing. Folgende modules sollten außerhalb benutzt werden:
  - Package `processors`: Die Klassen übernehmen die Kommunikation mit dem Filesystem/der API, das JSON-Parsing und Funktionsbereitstellung von `Teams` und `Matches`
  - Package `comparing`: Die hier vorhandenen Funktionen übernehmen den Vergleich zwischen Datenbank und `MatchMetaData`-Objekten und die Parallelisierung im Produktivumgebungen
- ``storage`` hält die heruntergeladenen json-Dateien fürs Development. Es ist üblich, erst einen Request über die Api zu machen und anschließend das lokale Filesystem zu benutzen. (.env)


### Manage.py Commands

- `python manage.py discord_bot` - Discordbot starten
- `python manage.py telegram_bot` - Telegrambot starten
- `python manage.py update_teams` - Teamupdates-Skript starten
- `python manage.py update_matches` - Teamupdates-Skript starten
- `python manage.py weekly_notifications` - Teamupdates-Skript starten
- `python manage.py runscript changelog` - Changelog-Skript starten
- `python manage.py runscript feedback` - Feedback-Skript starten
- `python manage.py runscript season_messages` - Season Messages-Skript starten
- `python manage.py runscript calibration` - Calibration-Skript starten
- `python manage.py runscript debug` - Debug-Skript starten

### Shell Commands


- `./restart_bots.sh`
- `./run_bots.sh`
- `./update_matches.sh`
- `./update_teams.sh`
- `./weekly_notifications.sh`


Alle Shell-Skripte sind unter `shell_scripts` zu finden.