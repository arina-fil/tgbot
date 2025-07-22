import telegram
print(f"PTB version: {telegram.__version__}")

from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

# 🔐 Твой Telegram ID, чтобы получать уведомления
AUTHOR_ID = 1143620060 # ← замени на свой настоящий ID

# Состояния
ASK_NAME, ASK_PHONE = range(2)

# /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Начать регистрацию")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! 👋\nНажми кнопку ниже, чтобы начать регистрацию:",
        reply_markup=reply_markup
    )

# Начало регистрации
async def handle_registration_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Убираем старые кнопки
    await update.message.reply_text(
        "ℹ️ 30.07 с 15:00 до 16:30 пройдет мастер-класс (стоимость 3500₸).\n"
        "Будем изучать тело, движение, хореографию и технику. Будет оператор для записи процесса.",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text("Пожалуйста, напиши своё имя и фамилию:")
    return ASK_NAME

# Получаем имя и фамилию
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text

    # Кнопка запроса контакта + возможность ввода вручную
    contact_button = KeyboardButton("📲 Отправить номер телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button], ["✏️ Ввести номер вручную"]],
        resize_keyboard=True, one_time_keyboard=True
    )

    await update.message.reply_text(
        "Теперь отправь свой номер телефона.\n\n"
        "Ты можешь нажать кнопку или ввести его вручную (в формате +77774567890):",
        reply_markup=reply_markup
    )
    return ASK_PHONE

# Получаем номер телефона и уведомляем автора
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Определяем, как получен номер
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
        # Проверка на корректный формат
        if not phone.startswith('+') or not phone[1:].isdigit():
            await update.message.reply_text("⚠️ Пожалуйста, введи номер в правильном формате: +77774567890")
            return ASK_PHONE

    context.user_data['phone'] = phone
    name = context.user_data['name']

    # ✅ Отправка автору уведомления о регистрации
    await context.bot.send_message(
        chat_id=AUTHOR_ID,
        text=f"🔔 Новая регистрация:\n\nИмя: {name}\nТелефон: {phone}"
    )

    # Ответ пользователю и удаление клавиатуры
    await update.message.reply_text(
        f"✅ Спасибо, {name}!\n"
        f"Мы свяжемся с тобой по номеру: {phone}.\n"
        f"Следи за сторис — там будет вся актуальная информация!",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# Обработка /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Регистрация отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Запуск
def main():
    app = ApplicationBuilder().token("8183598594:AAGJTrTFQ9wn7GqEqdjhDZkrCsGCAKACVIk").build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Начать регистрацию"), handle_registration_start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
