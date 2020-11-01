from communication_interfaces import send_message
from utils.constants import EMOJI_CLOVER, EMOJI_PEACE


def main():
    print(
        send_message(
            msg=f"Hi Chat,\nich war leider down, #rip.\nAber jetzt geht es wieder (hoffentlich). {EMOJI_CLOVER} \n"
                f"Ihr könnt mich jetzt wieder in vollem Umfang benutzen! {EMOJI_PEACE}",
            chat_id=913800738,
        )
    )


def run():
    main()
