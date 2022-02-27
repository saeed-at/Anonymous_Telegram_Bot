import emoji
import requests
from loguru import logger

from src.utils.io import write_json
from src.constants import keyboards

from src.filters import IsAdmin
from src.bot import bot

class Bot:
        """
        Template For Telegram bot 
        """
        
        def __init__(self, telebot):

                self.bot = telebot

                #register handlers
                self.handlers()

                #ass custom filter
                self.bot.add_custom_filter(IsAdmin())

                #start bot
                logger.info("Bot is running")
                self.bot.infinity_polling()


        def handlers(self):

                @self.bot.message_handler(is_admin=True)
                def admin_of_group(message):
                        self.send_message(message.chat.id, '<strong> You are admin of this group </strong>')

                @self.bot.message_handler(func=lambda _: True)
                def echo (message):
                        self.send_message(
                                message.chat.id,
                                message.text,
                                reply_markup = keyboards.main)
                        #we can monitor user whom contact to bot by sending logs to out chat(1871265971 is my temporary chat)
                        self.send_message('1871265971', f"""*New message* \n{message.from_user.first_name} sent " {message.text} "\n to the bot.""")


                # TODO  :Add faal feature to the bot
                ### faal hafez api
                # @bot.message_handler(commands=['fal'])
                # def send_fal(message):
                #         logger.info(f"api request from user : {message.from_user.username}")
                #         BASE_URL = 'https://one-api.ir/hafez/?token=946518:6216a532d23ae8.08076926'
                #         response = requests.get(f"{BASE_URL}")
                #         bot.reply_to(message,f"‍‍‍‍‍‍─┅━━━━┅─فال─┅━━━━┅─\n {response.json()['result']['RHYME']}\n ─┅━━━━┅─تعبیر─┅━━━━┅─\n {response.json()['result']['MEANING']}\n ")

        def send_message(self, chat_id, text, reply_markup=None, emojize=True):
                if emojize :
                        text = emoji.emojize(text, use_aliases=True)

                self.bot.send_message(chat_id, text, reply_markup=reply_markup)


if __name__ == "__main__":
        logger.info("Bot has been started!")
        nashenas_bot = Bot(telebot=bot)
