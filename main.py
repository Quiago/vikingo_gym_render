

import logging
import fastapi
import uvicorn
import telebot
import toml
import logging
from handlers import handle_start, handle_role_selection
from client import handle_client_registration, show_client_commands, handle_fecha_pago, handle_progreso
from worker import handle_worker_registration, show_worker_commands
from trainer import handle_trainer_registration, show_trainer_commands
from database import initialize_db, get_role
telebot.logger.setLevel(logging.DEBUG)


CONF = toml.load('config.toml')
TOKEN = CONF['telegram']['token']
URL = CONF['url']['railway']
API_TOKEN = TOKEN
WEBHOOK_HOST = URL
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
WEBHOOK_URL_BASE = "https://{}".format(WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)
USER_STATE = {}
initialize_db()
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = fastapi.FastAPI(docs=None, redoc_url=None)

@app.get('/')
def root():
    return 'Hello, World!'

@app.post(f'/{API_TOKEN}/')
async def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return


# Comandos del bot
@bot.message_handler(commands=['start'])
def start_command(message):
    handle_start(bot, message, USER_STATE)

@bot.message_handler(func=lambda message: message.chat.id in USER_STATE and USER_STATE[message.chat.id]["step"] == "role_selection")
def role_selection_handler(message):
    handle_role_selection(bot, message, USER_STATE)

@bot.message_handler(func=lambda message: message.chat.id in USER_STATE and USER_STATE[message.chat.id]["role"] == "cliente")
def client_registration_handler(message):
    handle_client_registration(bot, message, USER_STATE)

@bot.message_handler(func=lambda message: message.chat.id in USER_STATE and USER_STATE[message.chat.id]["role"] == "trabajador")
def worker_registration_handler(message):
    handle_worker_registration(bot, message, USER_STATE)

@bot.message_handler(func=lambda message: message.chat.id in USER_STATE and USER_STATE[message.chat.id]["role"] == "entrenador")
def trainer_registration_handler(message):
    handle_trainer_registration(bot, message, USER_STATE)

@bot.message_handler(func=lambda message: message.text == "Mi Fecha de pago 💰")
def fecha_pago(message):
    handle_fecha_pago(bot, message)

@bot.message_handler(func=lambda message: message.text == "Mis Marcas y Progreso 📊")
def progreso(message):
    handle_progreso(bot, message)

@bot.message_handler(commands=['menu'])
def show_menu_command(message):
    role = get_role(message.chat.id)
    if not role:
        bot.send_message(message.chat.id, "Not user register please register")
        start_command(message)
    else:
        if role == "cliente":
            show_client_commands(bot, message.chat.id)
        elif role == "trabajador":
            show_worker_commands(bot, message.chat.id)
        elif role == "entrenador":
            show_trainer_commands(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, "Por favor, regístrate primero usando /start.")


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(
    url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
    #certificate=open(WEBHOOK_SSL_CERT, 'r')
)


uvicorn.run(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT
    #ssl_certfile=WEBHOOK_SSL_CERT,
    #ssl_keyfile=WEBHOOK_SSL_PRIV
)