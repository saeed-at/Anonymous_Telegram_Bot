from http import client
from json.tool import main

import emoji

import requests
from loguru import logger
from markupsafe import Markup

from src.bot import bot
from src.constants import keyboards, keys, states
from src.filters import IsAdmin
from src.utils.io import write_json
from src.db import db
from datetime import datetime


class Bot:
        """
        Template Bot to connect two strangers randomly.
        """
        
        def __init__(self, telebot, mongodb):
                """
                Initial bot, database, states, filters and handlers
                """                

                self.bot = telebot

                self.db = mongodb

                #register handlers
                self.handlers()

                #ass custom filter
                self.bot.add_custom_filter(IsAdmin())

                #send activated message to users and time
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")     

                logger.info("Sending <bot activated> message to all users")
                users = self.db.users.find({})
                for user in users:
                        self.bot.send_message(user['chat']['id'], f"Bot activated at {current_time}")

                #start bot
                logger.info("Bot is running")
                self.bot.infinity_polling()


        def handlers(self):

                @self.bot.message_handler(commands=['start'])
                def start(message):
                        """
                        start command handler.
                        """                        
                        self.send_message('1871265971', f"""*New message* \n{message.from_user.first_name} sent " {message.text} "\n to the bot.""")
                        self.send_message(message.chat.id, f"Hey <strong>{message.chat.first_name}</strong>, whas up? :wink:", reply_markup=keyboards.main)
                        
                        self.db.users.update_one(
                                {'chat.id':message.chat.id},
                                {'$set':message.json},
                                upsert=True,
                        )
                        self.update_state(message.chat.id, states.main)
                
                @self.bot.message_handler(regexp=emoji.emojize(keys.random_connect))
                def random_connect(message):
                        """
                        Randomly connect to another user.
                        """                        
                        self.send_message(message.chat.id, 
                        "  در حال اتصال شما به یک کاربر ناشناس (در حال حاضر فقط می توانید متن یا ایموجی ارسال کنید)...:link: ",
                         reply_markup=keyboards.discard
                        )
                        self.update_state(message.chat.id, states.random_connect)
                        other_user = self.db.users.find_one(
                                {
                                'state' : states.random_connect,
                                'chat.id': {'$ne':message.chat.id}
                                }
                        )
                        if not other_user:
                                return
                        #Update other user state
                        self.update_state(other_user["chat"]["id"], states.connected)
                        self.send_message(
                                other_user['chat']['id'],
                                f" شما به {message.chat.id} متصل شده اید ..."
                        )


                        #Update current user state
                        #if user founded
                        self.update_state(message.chat.id, states.connected)
                        self.send_message(
                                message.chat.id,
                                f" شما به {other_user['chat']['id']} متصل شده اید ..."
                        )

                        #store connected user 
                        self.db.users.update_one(
                                
                                        {'chat.id':message.chat.id},
                                        {'$set':{'connected_to':other_user["chat"]["id"]}},      
                        )
                        self.db.users.update_one(
                                
                                        {'chat.id':other_user["chat"]["id"]},
                                        {'$set':{'connected_to':message.chat.id}},  
                        )

                @self.bot.message_handler(regexp=emoji.emojize(keys.exit))
                def exit(message):
                        """
                        Exit from chat or connecting state.
                        """                        
                        self.send_message(message.chat.id,'در حال خروج ...:hourglass:',
                         reply_markup=keyboards.main
                        )
                        self.update_state(message.chat.id, states.main)

                        #get connected user
                        connected_to = self.db.users.find_one({'chat.id': message.chat.id})

                        if not connected_to :
                                return

                        #update connected user state and send message and disconnet  other user
                        other_chat_id = connected_to['connected_to']
                        self.update_state(other_chat_id, states.main)
                        self.send_message(
                                other_chat_id,
                                keys.exit,
                                reply_markup=keyboards.main
                        )

                        #remove connected users
                        self.db.users.update_one(
                                {'chat.id':other_chat_id},
                                {'$set':{'connected_to':None}}
                        )

                        self.db.users.update_one(
                                {'chat.id':message.chat.id},
                                {'$set':{'connected_to':None}}
                        )

                @self.bot.message_handler(func=lambda _: True)
                def echo (message):
                        """
                        Echo message to connected user.
                        """                                        
                        #we can monitor user whom contact to bot by sending logs to out chat(1871265971 is my temporary chat)
                        # self.send_message('1871265971', f"""*New message* \n{message.from_user.first_name} sent " {message.text} "\n to the bot.""")

                        user = self.db.users.find_one(
                                {'chat.id':message.chat.id}
                        )
                        if ((not user) or (user['state'] != states.connected) or (user['connected_to'] is None)) :
                                return
                        self.send_message(
                                user['connected_to'],
                                message.text
                        )
                        


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

        def update_state(self, chat_id, state):
                self.db.users.update_one(
                        {'chat.id':chat_id},
                        {'$set':{'state':state}},
                )

if __name__ == "__main__":
        logger.info("Bot has been started!")
        nashenas_bot = Bot(telebot=bot, mongodb=db)
