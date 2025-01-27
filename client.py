import re
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import save_client_to_db, save_user, get_payment_date
from datetime import datetime

def show_client_commands(bot, chat_id):
    """
    Muestra el menú de comandos para clientes.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("Mi Fecha de pago"), KeyboardButton("Mi Marcas y Progreso"))
    markup.add(KeyboardButton("Pedir en la Cafeteria"))
    bot.send_message(chat_id, "Aquí están tus comandos disponibles como cliente:", reply_markup=markup)

def handle_fecha_pago(bot, message):
    """
    Muestra la fecha de pago del cliente.
    """
    # Obtener la fecha de pago del cliente
    date = get_payment_date(message.chat.id)
    if not date:
        bot.send_message(message.chat.id, "No se encontró una fecha de pago para tu usuario.")
    else:
        # Extract day from the payment date
        payment_day = int(date.split("/")[0])
        # Get current date
        current_date = datetime.now()
        # Create next payment date using current month and year
        next_payment = datetime(current_date.year, current_date.month, payment_day)

        # If payment day already passed this month, move to next month
        if current_date.day > payment_day:
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year if current_date.month < 12 else current_date.year + 1
            next_payment = datetime(next_year, next_month, payment_day)
        else:
            # Si el día actual es menor o igual al día de pago, es este mes
            next_payment = datetime(current_date.year, current_date.month, payment_day)
    
        # Calcular días restantes, excluyendo el día actual y contando el día de pago
        days_remaining = (next_payment - current_date).days
        payment_msg = f"Tu fecha de pago es el día {next_payment.day} de cada mes.\nPróximo pago: {next_payment.strftime('%d/%m/%Y')}\nDías restantes: {days_remaining}"
        bot.send_message(message.chat.id, payment_msg)
        return
def handle_client_registration(bot, message, USER_STATE):
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
        USER_STATE[message.chat.id]["step"] = "get_gender"
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Masculino", "Femenino")
        bot.send_message(message.chat.id, "Selecciona tu género:", reply_markup=markup)

    elif step == "get_gender":
        # Validar género
        if message.text not in ["Masculino", "Femenino"]:
            bot.send_message(message.chat.id, "Por favor, selecciona un género válido: Masculino o Femenino.")
            return
        USER_STATE[message.chat.id]["gender"] = message.text
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
        USER_STATE[message.chat.id]["step"] = "get_init_date"
        bot.send_message(message.chat.id, "Por favor, ingresa tu fecha de inscripción (DD/MM/YYYY):")

    elif step == "get_init_date":
        # Validar que la fecha tenga el formato DD/MM/YYYY y sea válida
        try:
            datetime.strptime(message.text, '%d/%m/%Y')
        except ValueError:
            bot.send_message(message.chat.id, "La fecha debe estar en el formato DD/MM/YYYY y ser válida. Por favor, inténtalo de nuevo:")
            return
        USER_STATE[message.chat.id]["init_date"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_membership"
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("CrossFit", "Musculación", "Ambos")
        bot.send_message(message.chat.id, "Selecciona tu membresía:", reply_markup=markup)

    elif step == "get_membership":
        # Validar que la membresía sea válida
        if message.text not in ["CrossFit", "Musculación", "Ambos"]:
            bot.send_message(message.chat.id, "Por favor, selecciona una membresía válida: CrossFit, Musculación o Ambos.")
            return
        USER_STATE[message.chat.id]["membership"] = message.text
        save_user(USER_STATE[message.chat.id])
        save_client_to_db(USER_STATE[message.chat.id])
        bot.send_message(message.chat.id, "¡Registro completado con éxito! 🎉")
        del USER_STATE[message.chat.id]
        show_client_commands(bot, message.chat.id)