import os
import threading
import telebot
from flask import Flask

TOKEN = "8237088507:AAG-VHB9UC6BmQOsxSbCwAMmSKj0nrWia3I"
bot = telebot.TeleBot(TOKEN)

def get_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("➡️ Назад"))
    return markup

def send_main_menu(chat_id, text_message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('ℹ️ О нас'), types.KeyboardButton('💊 Информация о лекарстве'))
    markup.add(types.KeyboardButton('📄 Оставить контакты'))
    bot.send_message(chat_id, text_message, reply_markup=markup)

# Обработчик главного меню
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_cmd(message):
    # Очищаем старые шаги, если они были, и высылаем меню
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    send_main_menu(message.chat.id, "Привет! Выберите действие в меню ниже:")
@bot.message_handler(content_types=['text'])
@bot.message_handler(content_types=['text'])
def handle_text(message):
    print(f"Пользователь написал: {message.text}")
    
    # 1. Проверяем кнопку "Оставить контакты"
    if message.text == '📄 Оставить контакты':
        ask_name(message)
        
    # 2. Проверяем кнопку "Информация о лекарстве"
    elif message.text == '💊 Информация о лекарстве':
        # Здесь пишем текст, который бот должен ответить
        bot.send_message(message.chat.id, "Тут будет информация о лекарствах. Описание, дозировки и т.д.")
        
    # 3. Проверяем кнопку "О нас" (проверь точный текст с эмодзи, как у тебя на кнопке!)
    elif message.text == 'ℹ️ О нас':
        bot.send_message(message.chat.id, "Мы — компания Проктал. Помогаем заботиться о вашем здоровье!")

# --- ШАГ 1: ИМЯ ---
def ask_name(message):
    msg = bot.send_message(message.chat.id, "Введите ваше Имя:", reply_markup=get_back_keyboard())
    bot.register_next_step_handler(msg, save_name)

def save_name(message):
    text = message.text
    if text == "➡️ Назад" or text == "/start":
        send_main_menu(message.chat.id, "Заполнение отменено.")
        return
    if text.startswith('/'):
        msg = bot.send_message(message.chat.id, "❌ Нельзя вводить команды! Введите Имя:")
        bot.register_next_step_handler(msg, save_name)
        return

    user_data_chat_id[message.chat.id] = {'Имя': text}
    msg = bot.send_message(message.chat.id, "Введите вашу Фамилию:", reply_markup=get_back_keyboard())
    bot.register_next_step_handler(msg, save_surname)

# --- ШАГ 2: ФАМИЛИЯ ---
def save_surname(message):
    text = message.text
    if text == "➡️ Назад":
        ask_name(message)
        return
    if text == "/start":
        send_main_menu(message.chat.id, "Заполнение отменено.")
        return
    if text.startswith('/'):
        msg = bot.send_message(message.chat.id, "❌ Нельзя вводить команды! Введите Фамилию:")
        bot.register_next_step_handler(msg, save_surname)
        return

    user_data_chat_id[message.chat.id]['Фамилия'] = text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('📱 Отправить мой номер', request_contact=True))
    markup.add(types.KeyboardButton("➡️ Назад"))
    
    msg = bot.send_message(message.chat.id, "И последнее - отправьте ваш номер телефона:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone_step)

# --- ШАГ 3: ТЕЛЕФОН ---
def process_phone_step(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == "➡️ Назад":
        msg = bot.send_message(chat_id, "Введите вашу Фамилию:", reply_markup=get_back_keyboard())
        bot.register_next_step_handler(msg, save_surname)
        return

    if message.contact:
        user_data_chat_id[chat_id]['Телефон'] = message.contact.phone_number
    else:
        user_data_chat_id[chat_id]['Телефон'] = text

    print(f"Новая заявка! Имя: {user_data_chat_id[chat_id]['Имя']}, Фамилия: {user_data_chat_id[chat_id]['Фамилия']}, Телефон: {user_data_chat_id[chat_id]['Телефон']}")
    send_main_menu(chat_id, "✅ Спасибо! Ваши данные успешно сохранены.")

app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
