from fastapi import FastAPI, Request
import telebot

token = "8082269540:AAGOzwSoL2CLoi_kradgxPl6gN9nmK5zjRU"
url = "https://<your-app-name>.onrender.com/"

bot = telebot.TeleBot(token, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    json_str = await request.body()
    update = telebot.types.Update.de_json(json_str.decode("utf-8"))
    bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello, World!")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Help")
