### SETUP

1. Installiere Python 3.8+
2. Installiere MySQL
3. Installiere virtualenv (mit pip) `pip install virtualenv`
4. Git Repository klonen SSH `git@gitlab.com:Grayknife/prime_league_bot.git` oder HTTPS `https://gitlab.com/Grayknife/prime_league_bot.git`
5. `cd prime_league_bot`
6. Erstelle virtuelle environment `virtualenv venv`
7. Venv aktivieren `source venv/Scripts/activate` oder in CMD: `venv\Scripts\Activate.bat`
8. Installiere requirements `pip install -r requirements.txt`
9. Erstelle `.env` File aus der `.env.example` und setze Variablen
10. Erstelle ggfs. die angegebene Datenbank
11. Fülle Datenbank mit Initialdaten aus (bereitgestellt durch `.env`) `python prime_league/new_season.py`

### Structure

- `new_season.py` initialisiert die Datenbank mit der `TEAM_ID` und `CHAT_ID`
- `main.py` erkennt Änderungen von Spielen und mithilfe eines `cronjobs` sorgt sie für die 30 minütigen Aktualisierungen
- `weekly_new_update.py` erstellt die wöchentlichen neuen Push-Notifications für den kommenden Spieltag
