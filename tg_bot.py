import telebot
import config

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Вітаю!\n За допомогою цього телеграм-боту ви можете залишити відгук про якість роботи нашої системи')
    bot.send_message(message.chat.id,
                     'Відправте ваш відгук у наступному повідомленні')
    @bot.message_handler()
    def get_message(message):
        print(message.text)
        bot.send_message(message.chat.id,
                         'Дякуємо за ваш відгук!')




@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Введіть /start для того, щоб залишити коментар')


bot.polling()