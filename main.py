from fastapi import FastAPI, Request
import telebot
import uvicorn
import toml

CONF = toml.load("config.toml")
token = CONF["telegram"]["token"]
url = CONF["url"]["render"]
print(url)
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

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
