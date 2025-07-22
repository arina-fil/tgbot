from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

# Состояния
ASK_NAME, ASK_PHONE = range(2)

# /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Начать регистрацию")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! \n ",
          reply_markup=reply_markup
    )

# Начало регистрации
async def handle_registration_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\n 30.07. 15:00-16:30  Пройдет Мастер-класс,стоимость 3500 тенге. На мастер-классе мы будем изучать наше тело, движение. Цель мастера-класса улучшить технику своего танца, Body work  ( разогрев, подкачка, мобильность суставов, работа со стабилизацией). Изучим несколько технических инструментов, которые исследуем в импро, поиске. Изучим хореографию на основе изученных инструментов. На протяжении всего мастер-класса будет присутствовать оператор, который зафиксирует наш рабочий процесс. Это в первую очередь делается для того, чтобы вы смогли проанализировать и поработать после с материалом.",
    )
    await update.message.reply_text("Пожалуйста, напиши своё имя и фамилию:")
    return ASK_NAME

# Получаем имя и фамилию
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text

    # Кнопка запроса контакта + возможность ввода вручную
    contact_button = KeyboardButton("Отправить номер телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button], ["Ввести номер вручную"]],
        resize_keyboard=True, one_time_keyboard=True
    )

    await update.message.reply_text(
        "Теперь отправь свой номер телефона.\n\n"
        "Ты можешь нажать кнопку или ввести его вручную (в формате +77774567890):",
        reply_markup=reply_markup
    )
    return ASK_PHONE

# Получаем номер телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если номер пришёл как контакт
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    context.user_data['phone'] = phone
    name = context.user_data['name']

    await update.message.reply_text(f" Отлично, {name}!\n Мы свяжемся с тобой по номеру: {phone}, \n Подробная инфоромация о мастер-классе будет у меня в сторис, следи и не пропусти!")
    return ConversationHandler.END

# Обработка /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена.")
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
