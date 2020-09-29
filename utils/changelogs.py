from utils.constants import EMOJI_ONE, EMOJI_TWO, EMOJI_ARROW_RIGHT

CHANGELOGS = {
    1: {
        "version": "1.12.0-beta",
        "text":
"""
Hallo {team.name}, 
hier ein kurze Zusammenfassung der letzten Änderungen am PrimeBot.

*Updates ({version}):*"""
f"""
{EMOJI_ONE} /reassign : Dieses Kommando ist jetzt in /start integriert. Falls ihr also ein *anderes* Team für diesen Chat registieren möchtet, führt /start aus. 
{EMOJI_TWO} Team-Sperre: Um ein Team in einem anderen Chat neu zu registrieren muss unter /settings {EMOJI_ARROW_RIGHT} Team-Sperre dein Team vorher freigegeben werden.

*Bugfixes:*
Ein Fehler wurde behoben, bei dem nicht angezeigt wurde, wenn eine Nachricht nicht angeheftet werden konnte.

*Coming Soon:*
{EMOJI_ONE} Pushnachrichten für neue Kommentare in ungespielten Matches
{EMOJI_TWO} Discord-Bot

Wenn ihr keine Patchnotes erhalten wollt, deaktiviert die Einstellung in /settings {EMOJI_ARROW_RIGHT} Bot Patches.

Sternige Grüße
@Grayknife und @OrbisK
"""
    },
}
