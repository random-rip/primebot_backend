### SETUP

Requirements:

- Python 3.8+
- MariaDB/MySQL (Windowsprogramm: XAMPP)
- virtualenv (pip package):  `pip install virtualenv`


1. Git Repository klonen HTTPS `git clone https://github.com/random-rip/primebot_backend.git`
2. `cd primebot_backend`
3. Erstelle virtuelle environment `virtualenv venv` oder über die IDE
4. Venv aktivieren (Linux): `source venv/Scripts/activate` oder in Windows Powershell (PS): `venv\Scripts\Activate.bat`
5. Installiere requirements `pip install -r requirements.txt`
6. Erstelle `.env` File aus der `.env.example` und setze Variablen
    1. Es muss ein Bot-Token und die Application ID aus dem
       Discord [Developerportal](https://discord.com/developers/applications) geholt werden
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
- ``bots`` enthält alle relevanten Discord- und Telegram-Skripte, LanguageFiles, und den MessageDispatcher.
- ``core`` enthält die PrimeLeague-Kommunikation, Parsing, Comparing und Updating
    - Module ``comparers``: Die hier vorhandenen Klassen übernehmen den Vergleich zwischen
      Datenbank, `TeamDataProcessor` und `TemporaryMatchData`
    - Module ``parsing``: Die hier vorhandenen Klassen parsen die Logs, die von der API übergeben werden (legacy)
    - Module ``processors``: Die hier vorhandenen Klassen bilden die Schnittstelle zwischen der Datenverarbeitung in
      python und den `Provider`-Klassen
    - Module `providers`: Die Klassen übernehmen die Kommunikation mit dem Filesystem, der Prime League API (und die
      Differenzierung ob Filesystem oder API) und das JSON-Parsing
    - Module `updater`: Die Klassen übernehmen Aktualisierung von Matches, den Teams und der Parallelisierung im
      Produktivsystem
    - Module `api.py`: Die Klasse stellt eine low level prime league api zur Verfügung
    - Module `temporary_match_data.py`: Die Klasse stellt Methoden zur Konvertierung der API-Daten in ``Comparer``
      -freundliche Daten bereit und kümmert sich um die Datenanreicherung von gegnerischen Teams zu einem Match
- ``storage`` hält die API-Daten als JSON-Dateien fürs Development. Es ist üblich, erst einen Request über die Api
  zu machen und anschließend das lokale Filesystem zu benutzen. (.env: ``FILES_FROM_STORAGE=True``)

### Manage.py Commands

- `python manage.py discord_bot` - Discordbot starten
- `python manage.py telegram_bot` - Telegrambot starten
- `python manage.py update_teams` - Teamupdates-Skript starten
- `python manage.py update_matches` - Teamupdates-Skript starten
- `python manage.py weekly_notifications` - Teamupdates-Skript starten
- `python manage.py runscript feedback` - Feedback-Skript starten
- `python manage.py runscript season_messages` - Season Messages-Skript starten
- `python manage.py runscript debug` - Debug-Skript starten

### Shell Commands

- `./restart_bots.sh`
- `./run_bots.sh`
- `./update_matches.sh`
- `./update_teams.sh`
- `./weekly_notifications.sh`
- `./feedback.sh`

Alle Shell-Skripte sind unter `shell_scripts` zu finden.