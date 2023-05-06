from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# КНОПКИ МЕНЮ
btn_subscription = KeyboardButton("Оплата 1000руб")


# КНОПКА ПОКУПКИ ПОДПИСКИ
BUTTON_TYPES = {
    "BTN_HOME": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_subscription),
}
