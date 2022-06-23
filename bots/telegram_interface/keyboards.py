from django.utils.translation import gettext as _
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def boolean_keyboard(callback_data_prefix: int):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            _("Yes"),
            callback_data=f"{callback_data_prefix}yes"
        )],
        [InlineKeyboardButton(
            _("No"),
            callback_data=f"{callback_data_prefix}no"
        )],
    ])
    return reply_markup
