from telegram import Update
from telegram.ext import Application, CommandHandler
import os

# Получение токена из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Функция обработки команды /start
async def start(update: Update, context):
    unique_link = f"https://t.me/AirRushBot?start={update.effective_user.id}"
    await update.message.reply_text(
        f"Привет! Приглашай друзей и участвуй в розыгрыше. Используй свою ссылку: {unique_link}"
    )

# Основной код
def main():
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
