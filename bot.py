from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

import os

TOKEN = os.getenv("BOT_TOKEN")

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

    greeting = (
        "Добрый день! Вас приветствует *Студия авто света*.\n\n"
        "Мы занимаемся ретрофитом фар, ремонтом и устранением запотевания фар.\n"
        "🔧 Опыт работы более 5 лет.\n\n"
        "Выберите интересующую услугу:"
    )

    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(greeting, reply_markup=reply_markup, parse_mode="Markdown")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен ✅")
    app.run_polling()


if __name__ == "__main__":
    main()
