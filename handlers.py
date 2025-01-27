from telebot.types import ReplyKeyboardMarkup
from database import save_client_to_db

#USER_STATE = {}  # Diccionario para manejar los estados de los usuarios

def handle_start(bot, message, USER_STATE):
    """
    Maneja el comando /start y muestra los botones iniciales.
    """
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Entrenador", "Cliente", "Trabajador")
    bot.send_message(message.chat.id, "¿Eres entrenador, cliente o trabajador?", reply_markup=markup)
    USER_STATE[message.chat.id] = {"step": "role_selection"}
    USER_STATE[message.chat.id]['chat_id'] = message.chat.id

def handle_role_selection(bot, message, USER_STATE):
    """
    Maneja la selección de rol.
    """
    if message.text == "Cliente":
        USER_STATE[message.chat.id]["role"] = "cliente"
        USER_STATE[message.chat.id]["step"] = "get_name"
        bot.send_message(message.chat.id, "Por favor, ingresa tu primer nombre: 👤")
    if message.text == "Trabajador":
        USER_STATE[message.chat.id]["role"] = "trabajador"
        USER_STATE[message.chat.id]["step"] = "get_name"
        bot.send_message(message.chat.id, "Por favor, ingresa tu primer nombre: 👤")
    if message.text == "Entrenador":
        USER_STATE[message.chat.id]["role"] = "entrenador"
        USER_STATE[message.chat.id]["step"] = "get_name"
        bot.send_message(message.chat.id, "Por favor, ingresa tu primer nombre: 👤")



