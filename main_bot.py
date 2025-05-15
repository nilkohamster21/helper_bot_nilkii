import os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
import requests
import json
from docx import Document
import sqlite3

selected_template = ''  # сюда будет записываться номер выбранного шаблона
PHOTO_DIR = 'photos'

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)
# далее в коде обращение в нейросети
TOGETHER_API_KEY = "tgp_v1_WK-V6_Yk_HsXUP4gbSZoOilz9Q-L-RJc1tEmJlvGnGk"  # мой api ключ для запросов https://together.ai
together_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"

headers = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",  # заголовок авторизации с api ключом
    "Content-Type": "application/json"  # указываем, что отправляем данные в формате json
}


# функция обращается к нейросети и разделяет текст на блоки
def split_text_into_blocks(text):
    prompt = (
            "Ты — помощник, который строго форматирует текст для презентации. "
            "Вот что ты ДОЛЖЕН сделать:\n"
            "1. Прочитай текст ниже.\n"
            "2. Раздели его строго на 5 логически законченных смысловых блоков (по 1–2 предложения каждый).\n"
            "3. Блоки идут строго по порядку текста. Не меняй их местами, не пересобирай, не пропускай и не повторяй.\n"
            "4. Перед блоками добавь заголовок — короткую фразу, подходящую как название презентации (например, 'Домовая мышь: особенности и поведение').\n"
            "5. Все 6 элементов (заголовок + 5 блоков) запиши в Python-список строк.\n\n"
            "Обязательные правила:\n"
            "- ТОЛЬКО ОДИН Python-список.\n"
            "- Ровно 6 строк внутри списка: 1 заголовок + 5 блоков.\n"
            "- НЕ добавляй никаких пояснений, заголовков, комментариев, пустых строк или других списков.\n"
            "- НЕ дублируй блоки, НЕ делай продолжения в следующих списках. Один текст — один список.\n\n"
            "Вот текст:\n\n"
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
        orig_output = response.json()["choices"][0]["text"]  # если всё ок, возвращаем текст из ответа
        clean_output = orig_output[
                       orig_output.find('['):orig_output.rfind(']') + 1]  # обрезаем только список на всякий случай
        return clean_output # ВОЗВРАЩЕНИЕ СПИСКА ТЕКСТА
    else:
        print("Ошибка:", response.status_code, response.text)  # выводим ошибку, если что-то не так
        return None


# создание таблицы
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT
    )
''')
conn.commit()


# функция для сохранения пользователя
def save_user(user):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
    ''', (user.id, user.first_name, user.last_name, user.username))
    conn.commit()
    conn.close()


# Старт
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton('новая презентация', callback_data='new_presentation')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    save_user(user)
    await update.message.reply_text(
        f"Здравствуйте, я бот, который быстро сделает вам презентацию. Чтобы создать новую нажмите нажмите на кнопку ниже",
        reply_markup=reply_markup
    )


# обработка нажатия на кнопку
async def new_presentation_is_pressed(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'new_presentation':
        await new_presentation(query.message, context)


# Функция создания новой презентации
async def new_presentation(message, context):
    # клавиатура1
    reply_keyboard1 = [['1', '2', '3', '4'], ['5', '6', '7', '8'], ['9', '10', 'ещё шаблоны']]
    markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True, resize_keyboard=True)

    await message.reply_text(
        "Для начала выберите шаблон по которому я буду делать презентацию:", reply_markup=markup1)

    IMAGE_LINKS1 = [  # Ссылки на изображения чтобы не скачивать изображения
        'https://easy-exam.ru/static/main_page/image/tasks/880.png',
        'https://easy-exam.ru/static/main_page/image/tasks/881.png',
        'https://easy-exam.ru/static/main_page/image/tasks/882.png',
        'https://easy-exam.ru/static/main_page/image/tasks/883.png',
        'https://easy-exam.ru/static/main_page/image/tasks/884.png',
        'https://easy-exam.ru/static/main_page/image/tasks/885.png',
        'https://easy-exam.ru/static/main_page/image/tasks/886.png',
        'https://easy-exam.ru/static/main_page/image/tasks/887.png',
        'https://easy-exam.ru/static/main_page/image/tasks/888.png',
        'https://easy-exam.ru/static/main_page/image/tasks/889.png'

    ]

    media_group = [InputMediaPhoto(link) for link in IMAGE_LINKS1]
    await message.reply_media_group(media=media_group)  # Высылаются изображения - шаблоны лдя презентаций


# функция высылает ещё шаблоны
async def more_templates(update, context):
    template_response = update.message.text
    if template_response == 'ещё шаблоны':
        # клавиатура2
        reply_keyboard2 = [['11', '12', '13', '14'], ['15', '16', '17', '18'], ['19', '20', 'назад']]
        markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            'Может тут есть нужный вам шаблон?🤔', reply_markup=markup2)

        IMAGE_LINKS2 = [  # Ссылки на изображения чтобы не скачивать изображеня
            'https://easy-exam.ru/static/main_page/image/tasks/890.png',
            'https://easy-exam.ru/static/main_page/image/tasks/891.png',
            'https://easy-exam.ru/static/main_page/image/tasks/892.png',
            'https://easy-exam.ru/static/main_page/image/tasks/893.png',
            'https://easy-exam.ru/static/main_page/image/tasks/894.png',
            'https://easy-exam.ru/static/main_page/image/tasks/895.png',
            'https://easy-exam.ru/static/main_page/image/tasks/896.png',
            'https://easy-exam.ru/static/main_page/image/tasks/897.png',
            'https://easy-exam.ru/static/main_page/image/tasks/898.png',
            'https://easy-exam.ru/static/main_page/image/tasks/899.png'

        ]
        media_group = [InputMediaPhoto(link) for link in IMAGE_LINKS2]
        await update.message.reply_media_group(media=media_group)  # Высылаются изображения - шаблоны лдя презентаций

    elif template_response == 'назад':
        await new_presentation(update, context)

    elif template_response.isdigit() and 1 <= int(template_response) <= 20:
        context.user_data['selected_template'] = template_response  # сохраняем результат во временное хранилище

        await update.message.reply_text(
            f"Вы выбрали шаблон №{template_response}. Теперь отправьте текст для слайдов в формате .txt или .docx.")

    else:
        await update.message.reply_text("Ошибка, нажмите на кнопку")


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
            return

        await update.message.reply_text("Обрабатываю текст...")

        blocks = split_text_into_blocks(text)  # разделение на блоки
        context.user_data['presentation_text'] = blocks  # сохраняем результат во временное хранилище

        await update.message.reply_text(
            "Текст успешно обработан! Теперь пришлите изображения которые нужно вставить в презентацию")

        print(blocks)


    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке файла: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def getting_the_photo(update, context):
    photo = update.message.photo[-1]  # берём фото самого большого размера
    file = await photo.get_file()  # получаем объект файла
    file_path = os.path.join(PHOTO_DIR, f"{file.file_id}.jpg")  # путь сохранения
    await file.download_to_drive(file_path)  # загрузка файла
    context.user_data.setdefault('photo_paths', []).append(file_path)  # добавляем путь к фото в данные пользователя
    await update.message.reply_text("Фото получено!")

def handle_document(update, context):
    document = update.message.document
    file_name = document.file_name.lower()
    file_extension = os.path.splitext(file_name)[-1]

    # поддерживаемые расширения
    text_extensions = ['.txt', '.docx']
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    file = document.get_file()
    file_path = os.path.join("downloads", file_name)

    # создаём папку, если нет
    os.makedirs("downloads", exist_ok=True)
    file.download(file_path)

    if file_extension in text_extensions:
        try:
            if file_extension == ".txt":
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            elif file_extension == ".docx":
                import docx
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])

            result = split_text_into_blocks(content)
            if result:
                context.user_data['presentation_text'] = result
                update.message.reply_text("Текст из документа обработан. Теперь отправь фото.")
            else:
                update.message.reply_text("Ошибка при обработке текста.")
        except Exception as e:
            update.message.reply_text("Ошибка при чтении документа.")
            print(e)

    elif file_extension in image_extensions:
        # Перемещаем файл в папку фото
        photo_path = os.path.join(PHOTO_DIR, file_name)
        os.rename(file_path, photo_path)
        context.user_data.setdefault('photo_paths', []).append(photo_path)
        update.message.reply_text("Изображение получено! Чтобы собрать презентацию, отправь /make.")
    else:
        os.remove(file_path)
        update.message.reply_text("Формат файла не поддерживается. Пришлите .txt, .docx или изображение.")


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
    application.add_handler(CallbackQueryHandler(new_presentation_is_pressed))
    application.add_handler(CommandHandler("new_presentation", new_presentation))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, more_templates))
    application.add_handler(MessageHandler(filters.Document.ALL, getting_the_text))
    application.add_handler(MessageHandler(filters.PHOTO, getting_the_photo))
    application.add_handler(MessageHandler(filters.Document, handle_document))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("close", close_keyboard))
    print("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
