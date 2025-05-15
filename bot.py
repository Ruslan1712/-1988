import os
import sqlite3
from datetime import datetime, timedelta
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, 
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
                          MessageHandler, ContextTypes, filters)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 757638983
DB_FILE = "database.db"

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    phone TEXT,
                    service TEXT,
                    date TEXT,
                    time TEXT,
                    status TEXT
                )''')
    conn.commit()
    conn.close()

# --- UTILS ---
def get_available_dates(days=5):
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]

def get_available_times(date):
    all_slots = ['10:00', '12:00', '14:00', '16:00']
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT time FROM bookings WHERE date=?", (date,))
    booked = [row[0] for row in c.fetchall()]
    conn.close()
    return [t for t in all_slots if t not in booked]

# --- STATE MANAGEMENT ---
user_data = {}

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(s, callback_data=f"service:{s}")] for s in services]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите услугу:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data.startswith("service:"):
        service = data.split(":", 1)[1]
        user_data[uid] = {"service": service}
        dates = get_available_dates()
        keyboard = [[InlineKeyboardButton(d, callback_data=f"date:{d}")] for d in dates]
        await query.message.edit_text(f"Вы выбрали: {service}\nВыберите дату:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("date:"):
        date = data.split(":", 1)[1]
        user_data[uid]["date"] = date
        times = get_available_times(date)
        keyboard = [[InlineKeyboardButton(t, callback_data=f"time:{t}")] for t in times]
        await query.message.edit_text(f"Дата: {date}\nВыберите время:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("time:"):
        time = data.split(":", 1)[1]
        user_data[uid]["time"] = time
        contact_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Отправить номер телефона", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await query.message.reply_text("Отправьте свой номер телефона:", reply_markup=contact_keyboard)

    elif data.startswith("status:") and uid == ADMIN_ID:
        parts = data.split(":")
        booking_id, new_status = parts[1], parts[2]
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT chat_id, service FROM bookings WHERE id=?", (booking_id,))
        row = c.fetchone()
        if row:
            chat_id, service = row
            c.execute("UPDATE bookings SET status=? WHERE id=?", (new_status, booking_id))
            conn.commit()
            await context.bot.send_message(chat_id=chat_id, text=f"📢 Статус вашей записи на '{service}' изменён: {new_status}")
            await query.message.edit_text("Статус обновлён.")
        conn.close()

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    uid = update.message.from_user.id
    data = user_data.get(uid, {})
    if not data:
        await update.message.reply_text("Что-то пошло не так. Попробуйте сначала /start.")
        return
    service = data["service"]
    date = data["date"]
    time = data["time"]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO bookings (chat_id, phone, service, date, time, status) VALUES (?, ?, ?, ?, ?, ?)",
              (contact.user_id, contact.phone_number, service, date, time, "🆕 Новая"))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Вы записаны на {date} в {time}\nУслуга: {service}")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 Новая заявка:\n{contact.phone_number}\n{service}, {date} {time}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, phone, service, date, time, status FROM bookings ORDER BY date, time")
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Нет заявок.")
        return
    for row in rows:
        bid, phone, service, date, time, status = row
        buttons = [
            InlineKeyboardButton("🔧 В работу", callback_data=f"status:{bid}:🔧 В работе"),
            InlineKeyboardButton("✅ Готово", callback_data=f"status:{bid}:✅ Готово")
        ]
        msg = f"📋 Заявка #{bid}\n{phone}\n{service}\n{date} {time}\nСтатус: {status}"
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup([buttons]))

# --- MAIN ---
services = {
    "Замена линз": "🔧 Замена линз в фарах",
    "Установка линз": "🔧 Установка линз в фары",
    "Устранение запотевания": "💨 Устранение запотевания",
    "Полировка фар": "✨ Полировка и бронирование",
    "Замена стекол": "🔁 Замена стекол фар"
}

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    print("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
