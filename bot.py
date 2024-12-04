from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
import sqlite3

# Получение токена из переменной окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 718607328  # Заменить на свой Telegram ID

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
    ref_link = f"https://t.me/AirRushEn?start={user_id}"  # Заменить на имя твоего канала
    
    # Добавляем пользователя в базу данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Если пользователя нет в базе данных, добавляем
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, username, referrer_id, invites_count) VALUES (?, ?, ?, ?)",
                       (user_id, update.effective_user.username, referrer_id, 0))
    conn.commit()

    # Если был реферальный код, увеличиваем количество приглашений у реферера
    if referrer_id:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,))
        if cursor.fetchone():  # Проверяем, что реферер существует
            cursor.execute("UPDATE users SET invites_count = invites_count + 1 WHERE user_id = ?", (referrer_id,))
            conn.commit()

    conn.close()

    await update.message.reply_text(f"Привет! Вот твоя реферальная ссылка для приглашения в канал: {ref_link}")

# Функция для получения статистики по приглашениям
async def stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Получаем количество приглашений пользователя
    cursor.execute("SELECT invites_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        invites_count = result[0]
        await update.message.reply_text(f"Ты пригласил {invites_count} человек!")
    else:
        await update.message.reply_text("Ты не зарегистрирован.")
    
    conn.close()

# Функция для получения списка пользователей, которые пригласили кого-то
async def referrals(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Получаем всех пользователей, которые пригласили данного пользователя
    cursor.execute("SELECT user_id, username FROM users WHERE referrer_id = ?", (user_id,))
    referrals = cursor.fetchall()

    if referrals:
        referrals_list = "\n".join([f"User: {username}, ID: {ref_user_id}" for ref_user_id, username in referrals])
        await update.message.reply_text(f"Вот список людей, которых ты пригласил:\n{referrals_list}")
    else:
        await update.message.reply_text("Ты никого не пригласил.")
    
    conn.close()

# Функция для получения списка всех пользователей (только для админа) с приглашёнными
async def all_users(update: Update, context: CallbackContext):
    # Проверка, является ли пользователь администратором
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Получаем всех пользователей из базы данных
    cursor.execute("SELECT user_id, username, invites_count FROM users")
    users = cursor.fetchall()

    if users:
        users_list = ""
        for user_id, username, invites_count in users:
            # Получаем количество рефералов для каждого пользователя
            cursor.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
            referrals_count = cursor.fetchone()[0]  # Количество рефералов
            users_list += f"User: {username}, ID: {user_id}, Invites: {invites_count}, Referrals: {referrals_count}\n"

        await update.message.reply_text(f"Список всех пользователей:\n{users_list}")
    else:
        await update.message.reply_text("Нет зарегистрированных пользователей.")
    
    conn.close()

# Основной код
def main():
    create_db()  # Создаём базу данных

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("referrals", referrals))  # Команда для вывода списка рефералов
    application.add_handler(CommandHandler("all_users", all_users))  # Команда для вывода всех пользователей (для админа)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
