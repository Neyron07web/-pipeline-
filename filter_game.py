import cv2
import numpy as np
import random
import time
from PIL import ImageFont, ImageDraw, Image

# --- изображения ---
images = [
    "images/c63.jpg",
    "images/cat.jpg",
    "images/city.jpg",
    "images/m5f10.jpg",
    "images/x5m.jpg"
]

# --- фильтры с уменьшенной глубиной и более понятным эффектом ---
def apply_filter(img, f):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if f == 1:  # Размытие
        return cv2.GaussianBlur(img,(5,5),0)  # мягкое размытие
    if f == 2:  # Контуры
        edges = cv2.Canny(gray,120,180)  # лёгкое выделение контуров
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    if f == 3:  # Чёрно-белый
        _, th = cv2.threshold(gray,180,255,cv2.THRESH_BINARY)
        return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)
    if f == 4:  # Инверсия
        return cv2.bitwise_not(img)
    if f == 5:  # Резкость
        kernel = np.array([[0,-0.3,0],[-0.3,2,-0.3],[0,-0.3,0]])
        return cv2.filter2D(img,-1,kernel)
    if f == 6:  # Тиснение
        kernel = np.array([[-0.5,-0.5,0],[-0.5,1,0.5],[0,0.5,0.5]])
        return cv2.filter2D(img,-1,kernel)
    if f == 7:  # Мультяшный
        blur = cv2.medianBlur(img,5)
        edges = cv2.Canny(cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY),120,180)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.bitwise_and(blur,edges)
    return img

def apply_pipeline(img, filters):
    out = img.copy()
    for f in filters:
        out = apply_filter(out,f)
    return out

# --- панель ---
def put_text_pil(img, text_lines, score, timer, font_path="arial.ttf", font_size=16):
    h, w = img.shape[:2]
    panel_height = 300
    panel = np.ones((panel_height, w, 3), dtype=np.uint8) * 255
    pil_img = Image.fromarray(panel)
    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype(font_path, font_size)
    y = 5
    for line in text_lines:
        if line:
            draw.text((10, y), line, font=font, fill=(0,0,0))
            y += font_size + 5
    draw.text((10, y), f"Баллы: {score} | Время: {timer} сек", font=font, fill=(0,0,0))
    panel = np.array(pil_img)
    combined = np.vstack((panel, img))
    return combined

# --- игра ---
score = 0
num_correct = 0
max_photos = 5
first_image = True

cv2.namedWindow("Filter Game", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Filter Game", 820, 800)

while num_correct < max_photos:
    path = random.choice(images)
    original = cv2.imread(path)
    if original is None:
        continue
    original = cv2.resize(original, (800,530))

    pipeline = random.sample(range(1,8), random.randint(1,3))
    remaining = pipeline.copy()
    total_filters = len(remaining)
    message = ""

    # --- первая картинка: ждём клавишу перед стартом таймера ---
    start_time = None
    if first_image:
        img = apply_pipeline(original, remaining)
        lines = [
            f"Фильтров на картинке: {total_filters}",
            "1. Размытие (Blur) - слегка размывает изображение",
            "2. Контуры (Edges) - выделяет контуры объектов, обнаруживает границы",
            "3. Порог (Threshold) - если пиксель ярче порога, он преобразуется в белый; если темнее - в чёрный,",
            "изображение становится чёрно-белым",
            "4. Инверсия (Invert) - цвета меняются на противоположные",
            "5. Резкость (Sharpen) - повышает чёткость деталей",
            "6. Тиснение (Emboss) - делает рельеф более заметным",
            "7. Мультяшный (Cartoon) - упрощает цвета + контуры",
            "Нажмите любую клавишу, чтобы стартовал таймер",
            "N - следующая картинка",
            "ESC - выход"
        ]
        combined = put_text_pil(img, lines, score, 30)
        cv2.imshow("Filter Game", combined)
        while True:
            key = cv2.waitKey(0)
            if key == 27:
                cv2.destroyAllWindows()
                exit()
            if key != -1:
                start_time = time.time()
                first_image = False
                break
    else:
        start_time = time.time()

    # --- цикл угадывания фильтров ---
    while True:
        elapsed = time.time() - start_time
        remaining_time = max(0, 30 - int(elapsed))

        # если время вышло
        if elapsed >= 30:
            message = "Время вышло! Следующая картинка"
            # показать сообщение 1 секунду перед переходом
            img_tmp = apply_pipeline(original, remaining)
            lines_tmp = [
                f"Фильтров на картинке: {total_filters}",
                "1. Размытие (Blur) - слегка размывает изображение",
                "2. Контуры (Edges) - выделяет контуры объектов, обнаруживает границы",
                "3. Порог (Threshold) - если пиксель ярче порога, он преобразуется в белый; если темнее - в чёрный,",
                "изображение становится чёрно-белым",
                "4. Инверсия (Invert) - цвета меняются на противоположные",
                "5. Резкость (Sharpen) - повышает чёткость деталей",
                "6. Тиснение (Emboss) - делает рельеф более заметным",
                "7. Мультяшный (Cartoon) - упрощает цвета + контуры",
                "Нажмите любую клавишу, чтобы стартовал таймер",
                "N - следующая картинка",
                "ESC - выход",
                message,
                "N - новая картинка"
            ]

            combined_tmp = put_text_pil(img_tmp, lines_tmp, score, remaining_time)
            cv2.imshow("Filter Game", combined_tmp)
            cv2.waitKey(5000)
            break

        # применяем текущие фильтры
        img = apply_pipeline(original, remaining)
        lines = [
            f"Фильтров на картинке: {total_filters}",
            "1. Размытие (Blur) - слегка размывает изображение",
            "2. Контуры (Edges) - выделяет контуры объектов, обнаруживает границы",
            "3. Порог (Threshold) - если пиксель ярче порога, он преобразуется в белый; если темнее - в чёрный,",
            "изображение становится чёрно-белым",
            "4. Инверсия (Invert) - цвета меняются на противоположные",
            "5. Резкость (Sharpen) - повышает чёткость деталей",
            "6. Тиснение (Emboss) - делает рельеф более заметным",
            "7. Мультяшный (Cartoon) - упрощает цвета + контуры",
            message if message else "",
            "N - следующая картинка",
            "ESC - выход"
        ]

        combined = put_text_pil(img, lines, score, remaining_time)
        cv2.imshow("Filter Game", combined)

        # читаем клавишу
        key = cv2.waitKey(50)
        if key == 27:  # ESC
            cv2.destroyAllWindows()
            exit()
        if key == ord('n'):  # новая картинка
            break
        if key in [ord(str(i)) for i in range(1, 8)]:
            guess = int(chr(key))
            if guess in remaining:  # правильный фильтр
                remaining.remove(guess)
                if remaining:
                    message = f"Правильно! Осталось найти {len(remaining)} фильтр(ов)"
                else:
                    message = "Все фильтры найдены!"
                    score += 1  # 1 балл за полностью угаданную картинку
                    num_correct += 1
                    break
            else:  # неправильный фильтр
                message = "Неправильно! Следующая картинка"
                # показать сообщение 1 секунду
                img_tmp = apply_pipeline(original, remaining)
                lines_tmp = [
                    f"Фильтров на картинке: {total_filters}",
                     "1. Размытие (Blur) - слегка размывает изображение",
                    "2. Контуры (Edges) - выделяет контуры объектов, обнаруживает границы",
                    "3. Порог (Threshold) - если пиксель ярче порога, он преобразуется в белый; если темнее - в чёрный,",
                    "изображение становится чёрно-белым",
                    "4. Инверсия (Invert) - цвета меняются на противоположные",
                    "5. Резкость (Sharpen) - повышает чёткость деталей",
                    "6. Тиснение (Emboss) - делает рельеф более заметным",
                    "7. Мультяшный (Cartoon) - упрощает цвета + контуры",
                    message,
                    "N - следующая картинка",
                    "ESC - выход"
                ]

                combined_tmp = put_text_pil(img_tmp, lines_tmp, score, remaining_time)
                cv2.imshow("Filter Game", combined_tmp)
                cv2.waitKey(1000)  # пауза перед следующей картинкой
                num_correct += 1
                break

cv2.destroyAllWindows()
print(f"Игра завершена!\nКартинок полностью угадано: {score} / {max_photos}\nБаллы: {score}")




