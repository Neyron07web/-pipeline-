import cv2

images = [
    "images/level1.png",
    "images/level2.png",
    "images/level3.png",
    "images/level4.png",
    "images/level5.png"
]

index = 0
original = cv2.imread(images[index])

cv2.namedWindow("Image Processing Lab")


def nothing(x):
    pass


# создаём ползунки
cv2.createTrackbar("Contrast", "Image Processing Lab", 0, 20, nothing)
cv2.createTrackbar("Blur", "Image Processing Lab", 0, 10, nothing)
cv2.createTrackbar("Median", "Image Processing Lab", 0, 10, nothing)
cv2.createTrackbar("Edges", "Image Processing Lab", 0, 200, nothing)
cv2.createTrackbar("Threshold", "Image Processing Lab", 120, 140, nothing)


print("N - следующая картинка")
print("ESC - выход")

while True:

    contrast = 1 + cv2.getTrackbarPos("Contrast", "Image Processing Lab") / 10
    blur = cv2.getTrackbarPos("Blur", "Image Processing Lab")
    median = cv2.getTrackbarPos("Median", "Image Processing Lab")
    edges = cv2.getTrackbarPos("Edges", "Image Processing Lab")
    threshold = cv2.getTrackbarPos("Threshold", "Image Processing Lab")

    img = original.copy()

    # contrast
    img = cv2.convertScaleAbs(img, alpha=contrast, beta=0)

    # blur
    if blur > 0:
        k = blur * 4 + 1
        img = cv2.GaussianBlur(img, (k, k), 0)

    # median
    if median > 0:
        k = median * 4 + 1
        img = cv2.medianBlur(img, k)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # threshold
    if threshold > 0:
        _, gray = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    # edges
    if edges > 0:
        gray = cv2.Canny(gray, 50 + edges * 10, 100 + edges * 20)

    cv2.putText(gray, f"Level {index+1}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    cv2.imshow("Image Processing Lab", gray)

    key = cv2.waitKey(30)

    if key == 27:
        break

    if key == ord('n'):

        index = (index + 1) % len(images)

        original = cv2.imread(images[index])

        # сброс ползунков
        cv2.setTrackbarPos("Contrast", "Image Processing Lab", 10)
        cv2.setTrackbarPos("Blur", "Image Processing Lab", 0)
        cv2.setTrackbarPos("Median", "Image Processing Lab", 0)
        cv2.setTrackbarPos("Edges", "Image Processing Lab", 0)
        cv2.setTrackbarPos("Threshold", "Image Processing Lab", 0)

cv2.destroyAllWindows()