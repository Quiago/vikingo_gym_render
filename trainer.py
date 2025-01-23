import re
from database import save_trainer_to_db, save_user
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def show_trainer_commands(bot, chat_id):
    """
    Muestra el menú para los entrenadores.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Ver Clientes"), KeyboardButton("Agregar Rutinas"))
    markup.add(KeyboardButton("Consultar Horarios"))
    bot.send_message(chat_id, "Bienvenido al menú de entrenador. ¿Qué deseas hacer?", reply_markup=markup)

def handle_trainer_registration(bot, message, USER_STATE):
    """
    Recoge los datos del cliente paso a paso con validaciones.
    """
    step = USER_STATE[message.chat.id]["step"]

    if step == "get_name":
        # Validar que el nombre solo contenga letras y espacios
        if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", message.text):
            bot.send_message(message.chat.id, "El nombre solo puede contener letras. Por favor, inténtalo de nuevo:")
            return
        USER_STATE[message.chat.id]["name"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_lastname"
        bot.send_message(message.chat.id, "Por favor, ingresa tu primer apellido:")

    elif step == "get_lastname":
        # Validar que el apellido solo contenga letras y espacios
        if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", message.text):
            bot.send_message(message.chat.id, "El apellido solo puede contener letras. Por favor, inténtalo de nuevo:")
            return
        USER_STATE[message.chat.id]["lastname"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_id_card"
        bot.send_message(message.chat.id, "Por favor, ingresa tu carnet de identidad (solo números):")

    elif step == "get_id_card":
        # Validar que el carnet de identidad solo contenga números
        if not message.text.isdigit() or len(message.text) != 11:
            bot.send_message(message.chat.id, "El carnet de identidad debe contener exactamente 11 dígitos. Por favor, inténtalo de nuevo:")
            return
        USER_STATE[message.chat.id]["id_card"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_phone"
        bot.send_message(message.chat.id, "Por favor, ingresa tu número de teléfono móvil (solo números):")

    elif step == "get_phone":
        # Validar que el número de teléfono solo contenga números
        if not message.text.isdigit() or len(message.text) != 8:
            bot.send_message(message.chat.id, "El número de teléfono debe contener 8 dígitos. Por favor, inténtalo de nuevo:")
            return
        USER_STATE[message.chat.id]["phone"] = message.text
        save_trainer_to_db(USER_STATE[message.chat.id])
        save_user(USER_STATE[message.chat.id])
        bot.send_message(message.chat.id, "¡Registro completado con éxito! 🎉")
        del USER_STATE[message.chat.id]
        show_trainer_commands(bot, message.chat.id)