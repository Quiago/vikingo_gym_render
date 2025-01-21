from fastapi import FastAPI, Request
import telebot
import uvicorn
import toml

CONF = toml.load("config.toml")
TOKEN = CONF["telegram"]["token"]
WEBHOOK_URL = CONF["url"]["render"]

bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    json_str = await request.body()
    update = telebot.types.Update.de_json(json_str.decode("utf-8"))
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy tu bot de Telegram.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

@app.on_event("startup")
async def on_startup():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
