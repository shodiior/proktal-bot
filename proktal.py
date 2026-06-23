import os
import threading
import telebot
from telebot import types # ИСПРАВЛЕНО: добавили импорт типов
from flask import Flask

TOKEN = "8237088507:AAEk_fe02kOXCg8G5u0UAdcYinqS6zhVb58"
bot = telebot.TeleBot(TOKEN)

# ИСПРАВЛЕНО: создали хранилище для данных
user_data_chat_id = {}

def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("➡️ Назад"))
    return markup

def send_main_menu(chat_id, text_message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('ℹ️ О нас'), types.KeyboardButton('💊 Информация о лекарстве'))
    markup.add(types.KeyboardButton('📄 Оставить контакты'))
    bot.send_message(chat_id, text_message, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    send_main_menu(message.chat.id, "Привет! Выберите действие в меню ниже:")

@bot.message_handler(content_types=['text', 'contact'])
def handle_text(message):
    if message.text == '📄 Оставить контакты':
        ask_name(message)
    elif message.text == '💊 Информация о лекарстве':
        bot.send_message(message.chat.id, "Тут будет информация о лекарствах.")
    elif message.text == 'ℹ️ О нас':
        bot.send_message(message.chat.id, "Мы — компания Проктал.")

def ask_name(message):
    msg = bot.send_message(message.chat.id, "Введите ваше Имя:", reply_markup=get_back_keyboard())
    bot.register_next_step_handler(msg, save_name)

def save_name(message):
    if message.text == "➡️ Назад":
        send_main_menu(message.chat.id, "Отменено.")
        return
    user_data_chat_id[message.chat.id] = {'Имя': message.text}
    msg = bot.send_message(message.chat.id, "Введите Фамилию:", reply_markup=get_back_keyboard())
    bot.register_next_step_handler(msg, save_surname)

def save_surname(message):
    if message.text == "➡️ Назад":
        ask_name(message)
        return
    user_data_chat_id[message.chat.id]['Фамилия'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('📱 Отправить номер', request_contact=True))
    markup.add(types.KeyboardButton("➡️ Назад"))
    msg = bot.send_message(message.chat.id, "Отправьте номер телефона:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone_step)

def process_phone_step(message):
    chat_id = message.chat.id
    if message.text == "➡️ Назад":
        msg = bot.send_message(chat_id, "Введите Фамилию:", reply_markup=get_back_keyboard())
        bot.register_next_step_handler(msg, save_surname)
        return
    phone = message.contact.phone_number if message.contact else message.text
    user_data_chat_id[chat_id]['Телефон'] = phone
    print(f"Новая заявка: {user_data_chat_id[chat_id]}")
    send_main_menu(chat_id, "✅ Спасибо! Данные сохранены.")

# ИСПРАВЛЕНО: name и main
app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True)

if name == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
