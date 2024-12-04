from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
import sqlite3

# Получение токена из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Создание базы данных для хранения информации о пользователях
def create_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        referrer_id INTEGER,
                        invites_count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Функция обработки команды /start
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    referrer_id = None

    # Если в аргументах есть ID пригласившего, то записываем его
    if context.args:
        referrer_id = int(context.args[0])  # Получаем ID пригласившего

    # Создаём уникальную ссылку для перехода в твой канал
    ref_link = f"https://t.me/AirRush?start={user_id}"  # Изменить "MyChannel" на имя твоего канала
    
    # Добавляем пользователя в базу данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username, referrer_id, invites_count) VALUES (?, ?, ?, ?)",
                   (user_id, update.effective_user.username, referrer_id, 0))
    conn.commit()

    # Если был реферальный код, увеличиваем количество приглашений у реферера
    if referrer_id:
        cursor.execute("UPDATE users SET invites_count = invites_count + 1 WHERE user_id = ?", (referrer_id,))
        conn.commit()

    conn.close()

    await update.message.reply_text(f"Привет! Вот твоя реферальная ссылка для приглашения в канал: {ref_link}")

# Функция для проверки статистики
async def stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT invites_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        invites_count = result[0]
        await update.message.reply_text(f"Ты пригласил {invites_count} человек!")
    else:
        await update.message.reply_text("Ты не зарегистрирован.")
    
    conn.close()

# Основной код
def main():
    create_db()  # Создаём базу данных

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
