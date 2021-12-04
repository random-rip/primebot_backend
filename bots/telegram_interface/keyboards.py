from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bots.languages.de_DE import YES, NO


def boolean_keyboard(callback_data_prefix: int):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            YES,
            callback_data=f"{callback_data_prefix}yes"
        )],
        [InlineKeyboardButton(
            NO,
            callback_data=f"{callback_data_prefix}no"
        )],
    ])
    return reply_markup


def scouting_keyboard():
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "OP.GG",
            callback_data=f"OP.GG"
        )],
        [InlineKeyboardButton(
            "U.GG",
            callback_data=f"U.GG"
        )],
        [InlineKeyboardButton(
            "XDX.GG",
            callback_data="XDX.GG"
        )],
        [InlineKeyboardButton(
            "Schließen",
            callback_data="schließen"
        )],
    ])

    return reply_markup