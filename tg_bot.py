import time

import telebot
import config
import pandas as pd
import uuid
import db_connection
import index_prediction

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Вітаю!\n За допомогою цього телеграм-боту ви можете залишити відгук про якість роботи нашої системи')
    bot.send_message(message.chat.id,
                     'Відправте ваш відгук у наступному повідомленні')
    @bot.message_handler()
    def get_message(message):
        content = message.text
        df_feedback = pd.DataFrame.from_dict({'id_review': [str(uuid.uuid1()).replace("-", "")], 'content': [content]})
        db_connection.connect(df_feedback, "feedbackstorage", operation_name="insert")
        bot.send_message(message.chat.id,
                         'Дякуємо за ваш відгук! Введіть /start для запису іншого відгуку.')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Введіть /start для того, щоб залишити коментар')


def query_handler():
    fetched_data = db_connection.connect(operation_name="select")
    if fetched_data:
        # Sort the resultative dictionary by priority
        fetched_data = sorted(fetched_data.items(), key=lambda x:x[1], reverse=True)
        # data format [('https://t.me/dvachannel', 0)]
        for item in fetched_data:
            index_prediction.get_indexes(item[0])
            db_connection.connect(channel_link=item[0], operation_name="delete")
    else:
        time.sleep(60)
        query_handler()


query_handler()
bot.polling()