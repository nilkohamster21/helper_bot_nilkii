from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import CommandHandler, Application
from config import BOT_TOKEN


async def start(update, context):
    await update.message.reply_text(
        "Здравствуйте, я бот, который быстро сделает вам презентацию. Чтобы создать новую нажмите команду /new_presentation на клавиатуре",
        reply_markup=markup
    )


async def new_presentation(update, context):
    await update.message.reply_text(
        "Для начала выбери шаблон по которому я буду делать презентацию:")
    IMAGE_LINKS = [
        "https://informatikaexpert.ru/wp-content/uploads/2022/05/oge-inf-stat-25042022-z13.1.png",  # Прямая ссылка на JPG
        "https://easy-exam.ru/static/main_page/image/tasks/892.png",  # Прямая ссылка на PNG
        "https://pvolgin-task.ru/wp-content/uploads/2024/05/131.jpg"
    ]

    media_group = [InputMediaPhoto(link) for link in IMAGE_LINKS]
    await update.message.reply_media_group(media=media_group)


async def help(update, context):
    await update.message.reply_text(
        "тут скоро будет инструкция")


reply_keyboard = ['/help']
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new_presentation", new_presentation))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("close", close_keyboard))
    print("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
