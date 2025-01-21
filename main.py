

import logging
import fastapi
import uvicorn
import telebot
import toml
import logging
import os
from telebot.types import ReplyKeyboardMarkup
from handlers import handle_start, handle_role_selection, handle_client_registration
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

@bot.message_handler(func=lambda message: message.chat.id in USER_STATE and USER_STATE[message.chat.id]["role"] == "Cliente")
def client_registration_handler(message):
    handle_client_registration(bot, message, USER_STATE)


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