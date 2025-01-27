import re
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import save_client_to_db, save_user, get_payment_date, check_user, save_progress, last_progress, get_user_data
from datetime import datetime

def save_user_progress(bot, chat_id):
    """
    Solicita y guarda el progreso inicial del usuario.
    """
    bot.send_message(chat_id, "Por favor, ingresa tu peso en kilogramos (ejemplo: 70):")
    bot.register_next_step_handler_by_chat_id(chat_id, get_weight, bot)

def get_weight(message, bot):
    chat_id = message.chat.id
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError("El peso debe ser mayor a 0.")
        bot.send_message(chat_id, "Por favor, ingresa tu altura en metros (ejemplo: 1.75):")
        bot.register_next_step_handler_by_chat_id(chat_id, get_height, bot, weight)
    except ValueError:
        bot.send_message(chat_id, "Por favor, ingresa un peso válido en kilogramos.")
        save_user_progress(bot, chat_id)

def get_height(message, bot, weight):
    chat_id = message.chat.id
    try:
        height = float(message.text)
        if height <= 0:
            raise ValueError("La altura debe ser mayor a 0.")
        #bot.send_message(chat_id, "Por favor, ingresa tu edad en años (ejemplo: 25):")
        #bot.register_next_step_handler_by_chat_id(chat_id, get_age, bot, weight, height)
        bmi = weight / (height ** 2)
        body_fat = 0
        try:
            user_data = get_user_data(chat_id)
        except Exception as e:
            bot.send_message(chat_id, e)
        gender = user_data[0]
        #age = user_data[1]
        ci_year = int(user_data[1][:2])  # First 2 digits of CI
        birth_year = 1900 + ci_year if ci_year >= 50 else 2000 + ci_year
        birth_month = int(user_data[1][2:4])
        birth_day = int(user_data[1][4:6])
        birth_date = datetime(birth_year, birth_month, birth_day)
        age = (datetime.now() - birth_date).days // 365
        if gender == "Masculino":
            body_fat = 1.20 * bmi + 0.23 * age - 16.2
        else:
            body_fat = 1.20 * bmi + 0.23 * age - 5.4
        try:
            save_progress({"chat_id": chat_id, "weight": weight, "height": height, "age": age, "bmi": bmi, "body_fat": body_fat})
        except Exception as e:
            bot.send_message(chat_id, e)
            print(e)
        bot.send_message(chat_id, f"¡Progreso registrado con éxito! 🎉\nIMC: {round(bmi, 2)}\nGrasa corporal: {round(body_fat, 2)}%")
        show_client_commands(bot, chat_id)
    except ValueError:
        bot.send_message(chat_id, "Por favor, ingresa una altura válida en metros.")
        save_user_progress(bot, chat_id)


def show_client_commands(bot, chat_id):
    """
    Muestra el menú de comandos para clientes.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("Mi Fecha de pago 💰"), KeyboardButton("Mis Marcas y Progreso 📊"))
    #markup.add(KeyboardButton("Pedir en la Cafeteria"))
    bot.send_message(chat_id, "Aquí están tus comandos disponibles como cliente:", reply_markup=markup)

def handle_progreso(bot, message):
    """
    Maneja el flujo de opciones para el progreso del usuario.
    """
    chat_id = message.chat.id

    if not check_user(chat_id):
        # Si el usuario no está registrado, solicita datos iniciales
        bot.send_message(chat_id, "Aún no has registrado tu progreso. Vamos a comenzar.")
        save_user_progress(bot, chat_id)
    else:
        # Si el usuario está registrado, ofrece opciones del menú
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Agregar nuevos datos"), KeyboardButton("Ver datos más recientes"), KeyboardButton("Atrás"))
        bot.send_message(chat_id, "¿Qué deseas hacer?", reply_markup=markup)
        # Registrar el próximo manejador
        bot.register_next_step_handler_by_chat_id(chat_id, handle_progress_options, bot)


def handle_progress_options(message, bot):
    """
    Maneja las opciones seleccionadas por el usuario en el menú de progreso.
    """
    chat_id = message.chat.id
    option = message.text  # Texto de la opción seleccionada

    if option == "Agregar nuevos datos":
        # Guardar nuevos datos del usuario
        bot.send_message(chat_id, "Vamos a agregar nuevos datos.")
        save_user_progress(bot, chat_id)

    elif option == "Ver datos más recientes":
        # Mostrar los datos más recientes del usuario
        try:
            result = last_progress(chat_id)
            if result:
                bot.send_message(
                    chat_id,
                    f"Tu progreso más reciente 📊:\n"
                    f"Peso: {result[3]} kg ⚖️\n"
                    f"Altura: {result[4]} m 📏\n"
                    f"Edad: {result[2]} años 🎂\n"
                    f"IMC: {result[5]} 📈\n"
                    f"Grasa corporal: {result[6]}% 💪\n"
                    f"Fecha de medición: {datetime.strptime(result[1], '%Y-%m-%d').strftime('%d/%m/%Y')} 📅"
                )
                show_client_commands(bot, chat_id)
            else:
                bot.send_message(chat_id, "No se encontraron datos de progreso.")
                show_client_commands(bot, chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"Ocurrió un error al obtener los datos: {e}")

        # Volver al menú principal después de mostrar los datos
        handle_progreso(bot, message)

    elif option == "Atrás":
        # Regresar al menú principal del cliente
        #bot.send_message(chat_id, "Regresando al menú principal...")
        show_client_commands(bot, chat_id)

    else:
        # Opción no válida
        bot.send_message(chat_id, "Opción no válida. Por favor, selecciona una opción válida.")
        # Repetir las opciones del menú
        handle_progreso(bot, message)



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
        payment_day = date.day
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
        payment_msg = f"Tu fecha de pago es el día {next_payment.day} de cada mes 📅\nPróximo pago: {next_payment.strftime('%d/%m/%Y')} 💳\nDías restantes: {days_remaining} ⏳"
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
            bot.send_message(message.chat.id, "El nombre solo puede contener letras. Por favor, inténtalo de nuevo: 🔤")
            return
        USER_STATE[message.chat.id]["name"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_lastname"
        bot.send_message(message.chat.id, "Por favor, ingresa tu primer apellido: 👤")

    elif step == "get_lastname":
        # Validar que el apellido solo contenga letras y espacios
        if not re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$", message.text):
            bot.send_message(message.chat.id, "El apellido solo puede contener letras. Por favor, inténtalo de nuevo: 🔤")
            return
        USER_STATE[message.chat.id]["lastname"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_gender"
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Masculino", "Femenino")
        bot.send_message(message.chat.id, "Selecciona tu género: 👥", reply_markup=markup)

    elif step == "get_gender":
        # Validar género
        if message.text not in ["Masculino", "Femenino"]:
            bot.send_message(message.chat.id, "Por favor, selecciona un género válido: Masculino o Femenino 👥")
            return
        USER_STATE[message.chat.id]["gender"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_id_card"
        bot.send_message(message.chat.id, "Por favor, ingresa tu carnet de identidad (solo números): 📝")

    elif step == "get_id_card":
        # Validar que el carnet de identidad solo contenga números
        if not message.text.isdigit() or len(message.text) != 11:
            bot.send_message(message.chat.id, "El carnet de identidad debe contener exactamente 11 dígitos. Por favor, inténtalo de nuevo: 🔢")
            return
        USER_STATE[message.chat.id]["id_card"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_phone"
        bot.send_message(message.chat.id, "Por favor, ingresa tu número de teléfono móvil (solo números): 📱")

    elif step == "get_phone":
        # Validar que el número de teléfono solo contenga números
        if not message.text.isdigit() or len(message.text) != 8:
            bot.send_message(message.chat.id, "El número de teléfono debe contener 8 dígitos. Por favor, inténtalo de nuevo: 📞")
            return
        USER_STATE[message.chat.id]["phone"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_init_date"
        bot.send_message(message.chat.id, "Por favor, ingresa tu fecha de inscripción (DD/MM/YYYY): 📅")

    elif step == "get_init_date":
        # Validar que la fecha tenga el formato DD/MM/YYYY y sea válida
        try:
            datetime.strptime(message.text, '%d/%m/%Y')
        except ValueError:
            bot.send_message(message.chat.id, "La fecha debe estar en el formato DD/MM/YYYY y ser válida. Por favor, inténtalo de nuevo: 📆")
            return
        USER_STATE[message.chat.id]["init_date"] = message.text
        USER_STATE[message.chat.id]["step"] = "get_membership"
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("CrossFit", "Musculación", "Ambos")
        bot.send_message(message.chat.id, "Selecciona tu membresía: 💪", reply_markup=markup)

    elif step == "get_membership":
        # Validar que la membresía sea válida
        if message.text not in ["CrossFit", "Musculación", "Ambos"]:
            bot.send_message(message.chat.id, "Por favor, selecciona una membresía válida: CrossFit, Musculación o Ambos 🏋️‍♂️")
            return
        USER_STATE[message.chat.id]["membership"] = message.text
        try:
            save_user(USER_STATE[message.chat.id])
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, f"Error al guardar usuario: ❌ {e}")
            return
        try:
            save_client_to_db(USER_STATE[message.chat.id])
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, f"Error al guardar cliente: ❌ {e}")
            return
        bot.send_message(message.chat.id, "¡Registro completado con éxito! 🎉")
        del USER_STATE[message.chat.id]
        show_client_commands(bot, message.chat.id)