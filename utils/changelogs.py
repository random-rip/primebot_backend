CHANGELOGS = {
    1: {
        "version": "1.12.0-beta",
        "text":
            """
Das Kommando `/reassign` ist jetzt in /start integriert. 
Um ein Team in einem anderen Chat neu zu registrieren muss unter /settings->Team-Sperre das Team vorher freigegeben werden.
Ein Fehler wurde behoben, bei dem nicht angezeigt wurde, wenn eine Nachricht nicht angeheftet werden konnte.
"""
    },
    2: {
        "version": "1.12.1-beta",
        "text": f"Supergroup Hotfix."
    },
    3: {
        "version": "1.12.2-beta",
        "text": f"My SQL Has Gone Away Hotfix."
    },
    4: {
        "version": "1.12.3-beta",
        "text": f"Ein Fehler wurde behoben, in dem nicht alle Teams die wöchentliche Benachrichtigung bekommen haben, "
                f"obwohl sie es aktiviert hatten."
    },
    5: {
        "version": "1.13.0-beta",
        "text": "Bugfix"
    },
    6: {
        "version": "1.13.1-beta",
        "text": "Ein Fehler wurde behoben, bei dem Teams eine falsche Spieltag-Benachrichtigung bekommen haben."
    },
    7: {
        "version": "1.13.2-beta",
        "text": "Spiele, in denen die Zeit von einem Administrator manuell eingestellt wurde, werden nun korrekt "
                "im System gespeichert und es werden nicht mehr mehrere Benachrichtigungen dazu gesendet."
    },
    8: {
        "version": "1.14.0-beta",
        "text":
            """
Der PrimeBot steht jetzt auch bei *Discord* zu Verfügung!
Ein Fehler wurde behoben, bei dem Teams eine falsche Spieltag-Benachrichtigung bekommen haben.
Spiele, in denen die Zeit von einem Administrator manuell eingestellt wurde, werden nun korrekt im System gespeichert und es werden nicht mehr mehrere Benachrichtigungen dazu gesendet.
"""
    },
    9: {
        "version": "1.14.1-beta",
        "text": "Spiele, in denen denen eigene Lobbys erstellt wurden, werden nun beim Crawling berücksichtigt."
    },
    10: {
        "version": "1.14.2-beta",
        "text": "Bugfix"
    },
    11: {
        "version": "1.15-beta",
        "text": "Bugfix"
    },
    12: {
        "version": "1.15.1-beta",
        "text":
            """
Hotfix für Discord.
Bei Discord kann nun eine Rolle angeben werden, die bei Benachrichtigungen erwähnt wird.
"""
    },
    13: {
        "version": "1.15.2-beta",
        "text": "Der Changelog wurde überarbeitet."
    },
    14: {
        "version": "1.15.3-beta",
        "text": "Hotfix Logging Error."
    },
    15: {
        "version": "1.16",
        "text":
            """
Der Befehl `overview` wurde hinzugefügt.
Die Website zum PrimeBot wurde online gestellt.
Der PrimeBot wurde visuell aktualisiert.
""",
    },
    16: {
        "version": "1.16.1",
        "text": "Ein Fehler wurde behoben, bei dem nicht alle Teams eine wöchentliche Benachrichtigung bekommen haben.",
    },
    17: {
        "version": "1.17.2",
        "text": """
Der Logtype `lineup_fail`  wurde hinzugefügt.
Softdeletion für Teams wurde hinzugefügt, wenn die Gruppe oder der Channel nicht mehr existiert.
"""
    },
    18: {
        "version": "1.17.3",
        "text": "Bei Discord können jetzt Rollen mit Leerzeichen als Parameter übergeben werden.",
    },
    19: {
        "version": "1.18",
        "text":
            """
Mit dem Befehl `scouting` kann eine andere Scouting Website ausgewählt werden. Standardmäßig ist weiterhin op.gg ausgewählt.
Ein Fehler wurde behoben, bei dem nicht alle Teams eine wöchentliche Benachrichtigung bekommen haben. 
Der Spiel-Log `lineup_fail` wird jetzt berücksichtigt. 
Referenzen auf Channels und Gruppen die gelöscht wurden, werden entfernt sobald eine Benachrichtigung gesendet werden würde.
"""
    },
    20: {
        "version": "1.18.1",
        "text": "Beim Befehl ``overview`` wurden mehr Informationen zu Spielen hinzugefügt. BugFix in Bezug auf den "
                "TimeChangeLog. Der Befehl `delete` wurde hinzugefügt, sodass channel-/gruppenbezogene Daten "
                "(und ggfs. Teambezogene Daten) gelöscht werden."
    },
    21: {
        "version": "2.0",
        "text": """
Die Crawler-Logik wurde entfernt und die API, die von der PrimeLeague zur Verfügung gestellt wird, wurde integriert.
Es wurden interne Codeumstrukturierungen vorgenommen.
Das Admininterface wurde aktiviert, um zukünftig darüber alle Daten zu administrieren.
Es wurden Endpunkte und Logik für temporäre Einstellungslinks implementiert.
"""
    }
}
