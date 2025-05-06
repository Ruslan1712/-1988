from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = '7908352799:AAHgUSgXCEpcxHXhyvCzq6joUYxne-ZYYLk'

# Подробные тексты по кнопкам
services = {
    "Замена линз": (
        "🔧 *Замена линз в фарах:*",
        "\n\n".join([
            "🔹 Lixiang L-серии — 100 000 ₽",
            "🔹 Твёрдый герметик с адаптивом (AFS, AFL) или с доп. работами — 19 500 ₽",
            "🔹 Твёрдый герметик — 17 500 ₽",
            "🔹 Мягкий герметик — 14 500 ₽",
            "🔹 Мягкий герметик с адаптивом (AFS, AFL) или с доп. работами — 16 500 ₽",
        ])
    ),
    "Установка линз": (
        "🔧 *Установка линз в фары:*",
        "\n\n".join([
            "🔹 Квадробилед (мягкий герметик, шпилька) — 34 000 ₽",
            "🔹 Квадробилед (твёрдый герметик, гайка) — 32 000 ₽",
            "🔹 Квадробилед (твёрдый герметик, шпилька) — 42 000 ₽",
            "🔹 Квадробилед (мягкий герметик, гайка) — 28 000 ₽",
            "🔹 Твёрдый герметик, гайка — 20 500 ₽",
            "🔹 Твёрдый герметик, шпилька — 22 500 ₽",
            "🔹 Твёрдый герметик, шпилька + доп. работы — 26 500 ₽",
            "🔹 Мягкий герметик, гайка — 15 500 ₽",
            "🔹 Мягкий герметик, шпилька — 17 500 ₽",
        ])
    ),
    "Устранение запотевания": (
        "💨 *Устранение запотевания:*",
        "\n\n".join([
            "🔹 Дефектовка — 2 000 ₽",
            "🔹 Очистка стекла (внутри) — 2 000 ₽",
            "🔹 Ремонт 1-го крепления — 3 000 ₽",
            "🔹 Ремонт трещины до 2 см — 2 500 ₽",
            "🔹 Ремонт трещины 2–4 см — 5 000 ₽",
            "🔹 Шов мягкий герметик — 5 000 ₽",
            "🔹 Шов мягкий герметик (премиум, W222 дорест.) — 14 000 ₽",
            "🔹 Шов твёрдый герметик (премиум, W222 рест.) — 18 000 ₽",
            "🔹 Шов твёрдый герметик с сохранением стекла — 12 000 ₽",
        ])
    ),
    "Полировка и бронирование фар": (
        "✨ *Полировка и бронирование:*",
        "Полировка от мутности + защита пленкой — от 1 500 ₽ за фару."
    ),
    "Замена стекол": (
        "🔁 *Замена стекол фар:*",
        "\n\n".join([
            "🔹 Мягкий герметик + новый герметик — 4 000 ₽",
            "🔹 Твёрдый герметик + новый герметик — 8 000 ₽",
            "🔹 Твёрдый герметик (премиум) — 12 000 ₽",
        ])
    )
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text, callback_data=text)] for text in services
    ] + [
        [InlineKeyboardButton("📩 Оставить заявку", callback_data="contact")],
        [InlineKeyboardButton("📱 WhatsApp", url="https://wa.me/79801666725")],
        [InlineKeyboardButton("📍 Адрес и график", callback_data="location")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Добро пожаловать! Выберите услугу:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text("Добро пожаловать! Выберите услугу:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in services:
        title, description = services[data]
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(f"{title}\n\n{description}", reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "contact":
        contact_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Отправить номер телефона", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await query.message.reply_text("Пожалуйста, отправьте номер телефона:", reply_markup=contact_keyboard)

    elif data == "location":
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "\U0001F4CD *Адрес:*\n"
            "М.О. Село Павловская Слобода, ул. Ленина, 76/4\n"
            "\U0001F9ED Ориентир: Автосервис «888»\n"
            "\U0001F552 Время работы: Пн–Сб: 10:00–20:00, Вс: выходной\n\n"
            "\U0001F4CC [Открыть на карте](https://yandex.ru/maps/?text=Павловская%20Слобода%20улица%20Ленина%2076%2F4)",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    elif data == "main":
        await start(update, context)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    await update.message.reply_text(f"✅ Спасибо! Мы получили ваш номер: {contact.phone_number}\nСкоро свяжемся с вами!")

    # Уведомление владельцу бота (замени ID на свой)
    ADMIN_ID = 123456789  # 👉 замените на ваш Telegram ID
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 Новый номер от клиента: {contact.phone_number}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    print("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
