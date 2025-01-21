from telebot.types import ReplyKeyboardMarkup
from database import save_client_to_db

USER_STATE = {}  # Diccionario para manejar los estados de los usuarios

def handle_start(bot, message):
    """
    Maneja el comando /start y muestra los botones iniciales.
    """
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("Entrenador", "Cliente", "Trabajador")
    bot.send_message(message.chat.id, "¿Eres entrenador, cliente o trabajador?", reply_markup=markup)
    USER_STATE[message.chat.id] = {"step": "role_selection"}

def handle_role_selection(bot, message, USER_STATE):
    """
    Maneja la selección de rol.
    """
    if message.text == "Cliente":
        USER_STATE[message.chat.id]["role"] = "Cliente"
        USER_STATE[message.chat.id]["step"] = "get_name"
        bot.send_message(message.chat.id, "Por favor, ingresa tu nombre:")
    else:
        bot.send_message(message.chat.id, "Por ahora, solo estamos registrando clientes. 😊")

def handle_client_registration(bot, message, USER_STATE):
    """
    Recoge los datos del cliente paso a paso.
    """
    step = USER_STATE[message.chat.id]["step"]

    if step == "get_name":
        USER_STATE[message.chat.id]["name"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_lastname"
        bot.send_message(message.chat.id, "Por favor, ingresa tu primer apellido:")

    elif step == "get_lastname":
        USER_STATE[message.chat.id]["lastname"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_gender"
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Masculino", "Femenino", "Otro")
        bot.send_message(message.chat.id, "Selecciona tu género:", reply_markup=markup)

    elif step == "get_gender":
        USER_STATE[message.chat.id]["gender"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_id_card"
        bot.send_message(message.chat.id, "Por favor, ingresa tu carnet de identidad:")

    elif step == "get_id_card":
        USER_STATE[message.chat.id]["id_card"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_phone"
        bot.send_message(message.chat.id, "Por favor, ingresa tu número de teléfono móvil:")

    elif step == "get_phone":
        USER_STATE[message.chat.id]["phone"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_membership"
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("CrossFit", "Musculación", "Ambos")
        bot.send_message(message.chat.id, "Selecciona tu membresía:", reply_markup=markup)

    elif step == "get_membership":
        USER_STATE[message.chat.id]["membership"] = message.text
        save_client_to_db(USER_STATE[message.chat.id])
        bot.send_message(message.chat.id, "¡Registro completado con éxito! 🎉")
        del USER_STATE[message.chat.id]
