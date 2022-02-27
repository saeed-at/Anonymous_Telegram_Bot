import os
import telebot

bot = telebot.TeleBot(
    os.environ["anonymous_telebot_token"],
    parse_mode='HTML',
    )
