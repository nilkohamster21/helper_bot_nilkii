from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import CommandHandler, Application, MessageHandler, filters
from config import BOT_TOKEN

selected_template = ''  # сюда будет записываться номер выбранного шаблона


# Старт
async def start(update, context):
    await update.message.reply_text(
        "Здравствуйте, я бот, который быстро сделает вам презентацию. Чтобы создать новую нажмите команду /new_presentation на клавиатуре",
        reply_markup=markup
    )


# Функция создания новой презентации
async def new_presentation(update, context):
    # клавиатура1
    reply_keyboard1 = [['1', '2', '3', '4'], ['5', '6', '7', '8'], ['9', '10', 'ещё шаблоны']]
    markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Для начала выберите шаблон по которому я буду делать презентацию:", reply_markup=markup1)

    IMAGE_LINKS1 = [  # Ссылки на изображения чтобы не скачивать изображеня
        'https://easy-exam.ru/static/main_page/image/tasks/880.png',
        'https://easy-exam.ru/static/main_page/image/tasks/881.png',
        'https://easy-exam.ru/static/main_page/image/tasks/882.png',
        'https://easy-exam.ru/static/main_page/image/tasks/883.png',
        'https://easy-exam.ru/static/main_page/image/tasks/884.png',
        'https://easy-exam.ru/static/main_page/image/tasks/884.png',
        'https://easy-exam.ru/static/main_page/image/tasks/885.png',
        'https://easy-exam.ru/static/main_page/image/tasks/886.png',
        'https://easy-exam.ru/static/main_page/image/tasks/887.png',
        'https://easy-exam.ru/static/main_page/image/tasks/888.png'

    ]

    media_group = [InputMediaPhoto(link) for link in IMAGE_LINKS1]
    await update.message.reply_media_group(media=media_group)  # Высылаются изображения - шаблоны лдя презентаций


async def more_templates(update, context):
    template_response = update.message.text
    if template_response == 'ещё шаблоны':
        # клавиатура2
        reply_keyboard2 = [['11', '12', '13', '14'], ['15', '16', '17', '18'], ['19', '20', 'назад']]
        markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            'Может тут есть нужный вам шаблон?🤔', reply_markup=markup2)

        IMAGE_LINKS2 = [  # Ссылки на изображения чтобы не скачивать изображеня
            'https://easy-exam.ru/static/main_page/image/tasks/889.png',
            'https://easy-exam.ru/static/main_page/image/tasks/890.png',
            'https://easy-exam.ru/static/main_page/image/tasks/891.png',
            'https://easy-exam.ru/static/main_page/image/tasks/892.png',
            'https://easy-exam.ru/static/main_page/image/tasks/893.png',
            'https://easy-exam.ru/static/main_page/image/tasks/894.png',
            'https://easy-exam.ru/static/main_page/image/tasks/896.png',
            'https://easy-exam.ru/static/main_page/image/tasks/897.png',
            'https://easy-exam.ru/static/main_page/image/tasks/898.png',
            'https://easy-exam.ru/static/main_page/image/tasks/899.png'

        ]
        media_group = [InputMediaPhoto(link) for link in IMAGE_LINKS2]
        await update.message.reply_media_group(media=media_group)  # Высылаются изображения - шаблоны лдя презентаций
    elif template_response.isdigit() and 1 <= int(template_response) <= 20:


    else:
        await update.message.reply_text("ошибка, нажмите на кнопку")


# Функция помощи
async def help(update, context):
    await update.message.reply_text(
        "тут скоро будет инструкция")


# клавиатура
reply_keyboard = [['/help']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


# закрытие клавиатуры
async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new_presentation", new_presentation))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, more_templates))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("close", close_keyboard))
    print("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
