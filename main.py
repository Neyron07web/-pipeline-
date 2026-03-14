import cv2

# список изображений
images = [
    "images/level1.png",
    "images/level2.png",
    "images/level3.png",
    "images/level4.png",
    "images/level5.png"
]

index = 0

img = cv2.imread(images[index])
current = img.copy()

print("Управление:")
print("1 - contrast (контраст)")
print("2 - threshold (бинаризация)")
print("3 - blur (размытие)")
print("4 - median (шум)")
print("5 - edges (границы)")
print("r - reset image (начать заново)")
print("n - next image (следующая картинка)")
print("q - exit (выход)")

while True:

    cv2.imshow("Image Processing Lab", current)

    key = cv2.waitKey(0)

    if key == ord('1'):  # контраст
        current = cv2.convertScaleAbs(current, alpha=2.5, beta=-120)

    elif key == ord('2'):  # бинаризация
        gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        _, current = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    elif key == ord('3'):  # размытие
        current = cv2.GaussianBlur(current, (5, 5), 0)

    elif key == ord('4'):  # шум
        current = cv2.medianBlur(current, 5)

    elif key == ord('5'):  # поиск границ
        gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        current = cv2.Canny(gray, 80, 200)

    elif key == ord('r') or key == ord('к'):  # сброс
        img = cv2.imread(images[index])
        current = img.copy()

    elif key == ord('n') or key == ord('т'):  # следующая картинка
        index = (index + 1) % len(images)
        img = cv2.imread(images[index])
        current = img.copy()

    elif key == ord('q') or key == ord('й'):  # выход
        break

cv2.destroyAllWindows()