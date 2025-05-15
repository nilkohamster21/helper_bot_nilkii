import os
from pptx import Presentation
from pptx.util import Cm, Pt  # Используем Cm вместо Inches
from pptx.dml.color import RGBColor

# Конфигурация
TEMPLATES_DIR = "templates"  # Папка с шаблонами
IMAGES_DIR = "images"  # Папка с изображениями
DEFAULT_TEMPLATE = "template1.pptx"  # Шаблон по умолчанию


def get_user_input():
    """Запрашиваем у пользователя данные."""
    presentation_name = input("Введите название презентации (без .pptx): ").strip()

    # Показываем доступные шаблоны
    templates = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".pptx")]
    print("\nДоступные шаблоны:")
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template}")

    template_choice = int(input("Выберите номер шаблона: ")) - 1
    selected_template = templates[template_choice] if 0 <= template_choice < len(templates) else DEFAULT_TEMPLATE

    return presentation_name, selected_template


def create_presentation(presentation_name, template_name, text_blocks, img_width_cm=10, img_left_cm=2,
                        img_top_start_cm=4, spacing_cm=1.5):
    # Загружаем выбранный шаблон
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    prs = Presentation(template_path)

    # 1. Добавляем текстовые блоки (если нужно)
    for text_data in text_blocks:
        slide = prs.slides.add_slide(prs.slide_layouts[5])  # Или другой макет

        left = Cm(text_data['left'])
        top = Cm(text_data['top'])
        width = Cm(text_data.get('width', 15))  # 15 см по умолчанию
        height = Cm(text_data.get('height', 2))  # 2 см по умолчанию

        text_box = slide.shapes.add_textbox(left, top, width, height)
        tf = text_box.text_frame

        p = tf.add_paragraph()
        p.text = text_data['text']
        p.font.bold = text_data.get('bold', False)
        p.font.size = Pt(text_data.get('font_size', 18))
        p.font.color.rgb = RGBColor(*text_data.get('color', (0, 0, 0)))

    # 2. Добавляем изображения из папки
    if os.path.exists(IMAGES_DIR):
        img_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for i, img_file in enumerate(img_files):
            slide = prs.slides.add_slide(prs.slide_layouts[5])  # Или другой макет
            img_path = os.path.join(IMAGES_DIR, img_file)

            left = Cm(img_left_cm)
            top = Cm(img_top_start_cm + i * (img_width_cm + spacing_cm))
            width = Cm(img_width_cm)

            slide.shapes.add_picture(img_path, left, top, width)
    else:
        print(f"⚠ Папка {IMAGES_DIR} не найдена. Изображения не добавлены.")

    # Сохраняем презентацию
    output_path = f"{presentation_name}.pptx"
    prs.save(output_path)
    print(f"✅ Презентация сохранена: {output_path}")


if __name__ == "__main__":
    # 1. Запрашиваем у пользователя данные
    presentation_name, selected_template = get_user_input()

    # 2. Пример текстовых блоков (можно загружать из JSON)
    text_blocks = [
        {
            'text': 'Пример заголовка',
            'left': 3,  # 3 см от левого края
            'top': 2,  # 2 см от верха
            'bold': True,
            'font_size': 24,
            'color': (0, 100, 200)  # RGB-цвет
        }
    ]

    # 3. Генерируем презентацию
    create_presentation(
        presentation_name,
        selected_template,
        text_blocks,
        img_width_cm=12,  # Ширина изображений (см)
        img_left_cm=3,  # Отступ слева (см)
        img_top_start_cm=4,  # Стартовая позиция Y (см)
        spacing_cm=1.5  # Расстояние между изображениями (см)
    )