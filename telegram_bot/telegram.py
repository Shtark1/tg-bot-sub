from datetime import datetime, timedelta
import logging

from aiogram import Bot
from aiogram.types import Message
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from content_text.messages import MESSAGES
from telegram_bot.KeyboardButton import BUTTON_TYPES
from config.cfg import TOKEN, CHAT_ID, PRICE, ID_YOOKASSA, TOKEN_YOOKASSA

import json
from yookassa import Configuration, Payment
import asyncio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())


# ===================================================
# =============== Стандартные команды ===============
# ===================================================
@dp.message_handler(text=['Оплата 1000руб'])
async def start_command(message: Message):
    Configuration.account_id = ID_YOOKASSA
    Configuration.secret_key = TOKEN_YOOKASSA

    def payment(value, description):
        payment = Payment.create({
            "amount": {
                "value": value,
                "currency": "RUB"
            },

            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/SellercityEkb_Bot"
            },
            "capture": True,
            "description": description
        })
        a = json.loads(payment.json())["confirmation"]["confirmation_url"]
        id = json.loads(payment.json())["id"]

        return a, id
    ad = payment(PRICE, 'Единоразовый платёж')

    btn_buy_ukassa = InlineKeyboardButton(text="Оплатить", callback_data="", url=f"{ad[0]}")

    await bot.send_message(message.from_user.id, "Единоразовый платёж", reply_markup=InlineKeyboardMarkup().add(btn_buy_ukassa))
    await check_payment(ad[1], message)


async def check_payment(payment_id, message):
    payment = json.loads((Payment.find_one(payment_id)).json())
    while payment['status'] == 'pending':
        payment = json.loads((Payment.find_one(payment_id)).json())
        await asyncio.sleep(3)

    if payment['status'] == 'succeeded':
        expire_date = datetime.now() + timedelta(days=1)
        link = await bot.create_chat_invite_link(CHAT_ID, expire_date, 1)
        await bot.send_message(message.from_user.id, MESSAGES['BUY'] + link.invite_link)
        return True
    else:
        return False


@dp.message_handler()
async def start_command(message: Message):
    await bot.send_message(message.from_user.id, f"{message.from_user.first_name}, " + MESSAGES["START"], reply_markup=BUTTON_TYPES["BTN_HOME"])


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def start():
    executor.start_polling(dp, on_shutdown=shutdown)
