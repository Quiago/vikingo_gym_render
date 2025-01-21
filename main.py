#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with fastapi
# It echoes any incoming text messages and does not use the polling method.

import logging
import fastapi
import uvicorn
import telebot
import toml
import logging
import os
telebot.logger.setLevel(logging.DEBUG)


CONF = toml.load('config.toml')
TOKEN = CONF['telegram']['token']
#TOKEN = "8082269540:AAGOzwSoL2CLoi_kradgxPl6gN9nmK5zjRU"
URL = CONF['url']['render']
#URL = "46aa-139-177-200-40.ngrok-free.app"
API_TOKEN = TOKEN
PORT = int(os.environ.get("PORT", 8443))
print(PORT)
WEBHOOK_HOST = URL
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
print(URL)

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

#WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_BASE = "https://{}".format(WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)
print(WEBHOOK_URL_BASE)
print(WEBHOOK_URL_PATH)

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


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    """
    Handle '/start' and '/help'
    """
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    """
    Handle all other messages
    """
    bot.reply_to(message, message.text)


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