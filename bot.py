from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Токен твоего бота
TOKEN = "7696894088:AAFKfBmcsPQ5x8aEcTmNfce4q253sd6MFF0"

def start(update, context):
    update.message.reply_text("Привет! Приглашай друзей и участвуй в розыгрыше. Используй свою ссылку: https://t.me/AirRushBot?start=" + str(update.effective_user.id))

# Запуск бота
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
updater.start_polling()
updater.idle()
