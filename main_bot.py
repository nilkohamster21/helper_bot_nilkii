import os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler, CallbackContext
import requests
import json
from docx import Document
from database import init_db, save_user, save_in_bd_presentation_title, get_presentations_by_user
from presentation_builder import generate_presentation
import ast

BOT_TOKEN = os.getenv("87967552141:AAFi8g5TorVs9OfUXj8x2C5gacS8eoWSIE0")
TOGETHER_API_KEY = os.getenv("tgp_v1_Wfv8OnRcWyx81O8bpK-oUhjHMCkC6onP9QYMfGb-sps")  # мой api ключ для запросов https://together.ai

selected_template = ''  # сюда будет записываться номер выбранного шаблона
PHOTO_DIR = '/tmp/photos'
SELECT_TEMPLATE, WAITING_TEXT, WAITING_PHOTOS, WAITING_TITLE, CONFIRMATION = range(5)  # состояния

# создаем директорию для фото, если ее нет
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# далее в коде обращение в нейросети
together_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",  # заголовок авторизации с api ключом
    "Content-Type": "application/json"  # указываем, что отправляем данные в формате json
}


# функция обращается к нейросети и разделяет текст на блоки
def split_text_into_blocks(text):
    prompt = (
            "Ты — помощник, который строго форматирует текст для презентации.\n"
            "Выполни следующие шаги:\n"
            "1. Прочитай текст ниже.\n"
            "2. Сформируй один Python-список из ровно 6 строк:\n"
            "   - Первый элемент — короткий заголовок (название презентации).\n"
            "   - Последующие 5 элементов — логически законченные текстовые блоки, каждый не длиннее 200 символов.\n"
            "3. Блоки должны идти в том же порядке, как в исходном тексте, без изменений, пропусков или повторов.\n"
            "4. Если текст слишком длинный, сокращай блоки, сохраняя смысл и полноту.\n"
            "5. Возвращай строго ОДИН Python-список.\n"
            "6. НЕ добавляй никаких пояснений, заголовков, пустых строк или других списков.\n\n"
            "Текст для обработки:\n\n"
            + text
    )

    # запрос для нейросети, как обработать текст

    data = {
        "model": together_model,  # используемая модель
        "prompt": prompt,  # текст запроса
        "max_tokens": 1024,  # максимальное количество токенов в ответе
        "temperature": 0.7,  # степень креативности
        "top_p": 0.9,  # ограничение вероятностного распределения для контроля разнообразия
        "stop": None,  # отсутствие специальных символов, останавливающих генерацию
    }

    response = requests.post(
        "https://api.together.xyz/v1/completions",  # адрес, куда отправляется запрос
        headers=headers,  # заголовки запроса
        data=json.dumps(data)  # тело запроса в формате json
    )

    if response.status_code == 200:
        orig_output = response.json()["choices"][0]["text"]

        clean_output = orig_output[orig_output.find('['):orig_output.rfind(']') + 1]

        try:
            blocks = json.loads(clean_output)
        except json.JSONDecodeError:
            try:
                blocks = ast.literal_eval(clean_output)
            except Exception as e:
                print(f"Ошибка разбора ответа от модели: {e}")
                return None

        # Проверка результата
        if isinstance(blocks, list) and all(isinstance(x, str) for x in blocks) and len(blocks) == 6:
            return blocks
        else:
            print(f"Получен некорректный формат блоков: {blocks}")
            return None
    else:
        print("Ошибка запроса:", response.status_code, response.text)
        return None


# инициализация БД
init_db()


# Старт
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton('Новая презентация', callback_data='new_presentation')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    save_user(user)
    await update.message.reply_text(
        "Здравствуйте, я бот, который быстро сделает вам презентацию. Чтобы создать новую нажмите нажмите на кнопку ниже",
        reply_markup=reply_markup
    )
    return SELECT_TEMPLATE


# обработка нажатия на кнопку
async def new_presentation_is_pressed(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'new_presentation':
        await select_template(query.message, context)


# Функция создания новой презентации
async def select_template(message, context):
    # клавиатура
    reply_keyboard = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9']
    ]
    markup1 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await message.reply_text(
        "Выберите шаблон для презентации:", reply_markup=markup1)

    IMAGE_LINKS1 = [  # Ссылки на изображения чтобы не скачивать изображения
        'https://easy-exam.ru/static/main_page/image/tasks/880.png',
        'https://easy-exam.ru/static/main_page/image/tasks/881.png',
        'https://easy-exam.ru/static/main_page/image/tasks/882.png',
        'https://easy-exam.ru/static/main_page/image/tasks/883.png',
        'https://easy-exam.ru/static/main_page/image/tasks/884.png',
        'https://easy-exam.ru/static/main_page/image/tasks/886.png',
        'https://easy-exam.ru/static/main_page/image/tasks/888.png',
        'https://easy-exam.ru/static/main_page/image/tasks/894.png',
        'https://easy-exam.ru/static/main_page/image/tasks/898.png'

    ]

    media_group = [InputMediaPhoto(link) for link in IMAGE_LINKS1]
    await message.reply_media_group(media=media_group)  # Высылаются изображения - шаблоны лдя презентаций
    return SELECT_TEMPLATE


# функция получает текст и отправляет его на разделение по блокам
async def getting_the_text(update, context):
    document = update.message.document
    file = await document.get_file()  # получение файл
    file_name = document.file_name
    file_path = f"presentation_text_{document.file_unique_id}"  # путь файла с индивидуальным номером

    try:
        await file.download_to_drive(file_path)  # скачивается файл

        # чтение файла в зависимости от формата
        if file_name.endswith('.txt'):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()  # чтение файла

        elif file_name.endswith('.docx'):
            doc = Document(file_path)
            text = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

        else:
            await update.message.reply_text("Формат файла не поддерживается. Пришлите .txt или .docx.")
            return WAITING_TEXT

        # отправляем сообщение и сохраняем его ID для последующего удаления
        processing_msg = await update.message.reply_text("Обрабатываю текст...")

        blocks = split_text_into_blocks(text)  # разделение на блоки
        print(blocks)
        if not blocks:
            await update.message.reply_text("Не удалось обработать текст. Попробуйте еще раз.")
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
            return WAITING_TEXT

        context.user_data['presentation_text'] = blocks  # сохраняем результат во временное хранилище

        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
        await update.message.reply_text(
            "Текст успешно обработан! Теперь пришлите 5 изображений которые нужно вставить в презентацию")

        return WAITING_PHOTOS

    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке файла: {e}")
        return WAITING_TEXT
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def getting_the_photo(update, context):
    photo = update.message.photo[-1]  # берём фото самого большого размера
    file = await photo.get_file()  # получаем объект файла
    file_path = os.path.join(PHOTO_DIR, f"{file.file_id}.jpg")  # путь сохранения
    await file.download_to_drive(file_path)  # загрузка файла

    # инициализируем список, если его еще нет
    if 'photo_paths' not in context.user_data:
        context.user_data['photo_paths'] = []

    context.user_data['photo_paths'].append(file_path)  # добавляем путь к фото

    # проверяем, что все 5 фото уже получены
    if len(context.user_data['photo_paths']) >= 5:
        await update.message.reply_text(
            "Все изображения получены! Теперь пришлите название для презентации (без .pptx)"
        )
        return WAITING_TITLE


async def save_presentation_title(update, context):
    title = update.message.text.strip()
    if not title:
        await update.message.reply_text("Название не может быть пустым. Попробуйте еще раз.")
        return WAITING_TITLE

    context.user_data['presentation_title'] = title  # сохраняем название
    keyboard = [
        [InlineKeyboardButton("Создать презентацию", callback_data="create_presentation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Название презентации сохранено: «{title}»",
        reply_markup=reply_markup
    )
    return CONFIRMATION


async def button_make_presentation(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "create_presentation":
        await query.edit_message_text("Запускаю создание презентации...")
        await create_presentation(query, context)


async def create_presentation(query, context):
    try:
        user_data = context.user_data

        # проверяем, что все данные есть
        required_fields = ['presentation_text', 'photo_paths', 'selected_template']
        missing_fields = [field for field in required_fields if field not in user_data]

        if missing_fields:
            raise ValueError(f"Не хватает данных: {', '.join(missing_fields)}")

        # проверяем, что текст и фото не None
        if user_data['presentation_text'] is None:
            raise ValueError("Текст презентации не был обработан!")

        if not user_data['photo_paths'] or any(photo is None for photo in user_data['photo_paths']):
            raise ValueError("Фотографии не были загружены!")

        # если название не указано, используем "Презентация"
        title = user_data.get('presentation_title', 'Презентация') + ".pptx"

        # генерируем презентацию
        presentation_file = generate_presentation(
            user_data['presentation_text'],
            user_data['photo_paths'],
            f"templates/template_{user_data['selected_template']}.json",
            title
        )

        # проверяем, что файл создан
        if not os.path.exists(presentation_file):
            raise ValueError("Не удалось создать файл презентации!")

        # отправляем пользователю
        with open(presentation_file, 'rb') as f:
            await query.message.reply_document(f)

        # очищаем временные файлы
        for photo_path in user_data['photo_paths']:
            if os.path.exists(photo_path):
                os.remove(photo_path)
        if os.path.exists(presentation_file):
            os.remove(presentation_file)

        await query.edit_message_text("Презентация успешно создана!")

    except Exception as e:
        await query.edit_message_text(f"Ошибка: {str(e)}")


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Создание презентации отменено.',
        reply_markup=ReplyKeyboardRemove()
    )

    # очищаем временные файлы
    if 'photo_paths' in context.user_data:
        for photo_path in context.user_data['photo_paths']:
            if os.path.exists(photo_path):
                os.remove(photo_path)

    context.user_data.clear()
    return ConversationHandler.END


async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Инструкция по использованию бота:\n\n"
        "1. Нажмите /start для начала работы\n"
        "2. Выберите шаблон презентации\n"
        "3. Отправьте текстовый файл (.txt или .docx) с содержимым\n"
        "4. Отправьте 5 изображений для слайдов\n"
        "5. Укажите название презентации\n"
        "6. Подтвердите создание презентации\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/cancel - отменить текущее действие"
    )
    await update.message.reply_text(help_text)


# клавиатура
reply_keyboard = [['/help']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


# закрытие клавиатуры
async def close_keyboard(update, context):
    await update.message.reply_text(
        "Клавиатура скрыта.",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_TEMPLATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, getting_the_text),
                MessageHandler(filters.Document.ALL, getting_the_text)
            ],
            WAITING_TEXT: [
                MessageHandler(filters.Document.ALL, getting_the_text)
            ],
            WAITING_PHOTOS: [
                MessageHandler(filters.PHOTO, getting_the_photo)
            ],
            WAITING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_presentation_title)
            ],
            CONFIRMATION: [
                CallbackQueryHandler(button_make_presentation, pattern='^create_presentation$')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
        per_message=False
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(new_presentation_is_pressed))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("close", close_keyboard))

    # запускаем бота
    print("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()
