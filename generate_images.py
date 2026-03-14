import cv2
import numpy as np
import os

os.makedirs("images", exist_ok=True)

h, w = 400, 600

# уровень 1 (почти невидимый код)
img = np.full((h, w), 126, dtype=np.uint8)
cv2.putText(img, "573", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 125, 5)
cv2.imwrite("images/level1.png", img)

# уровень 2 (шум)
img = np.full((h, w), 126, dtype=np.uint8)
cv2.putText(img, "842", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 124, 5)
noise = np.random.randint(0, 70, (h, w), dtype=np.uint8)
img = cv2.add(img, noise)
cv2.imwrite("images/level2.png", img)

# уровень 3 (тонкие линии)
img = np.zeros((h, w), dtype=np.uint8)
cv2.putText(img, "391", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 1)
cv2.imwrite("images/level3.png", img)

# уровень 4 (размытие + слабый контраст)
img = np.full((h, w), 125, dtype=np.uint8)
cv2.putText(img, "764", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 123, 5)
img = cv2.GaussianBlur(img, (11, 11), 0)
cv2.imwrite("images/level4.png", img)

# уровень 5 (шум + тонкие линии)
img = np.zeros((h, w), dtype=np.uint8)
cv2.putText(img, "258", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 1)
noise = np.random.randint(0, 120, (h, w), dtype=np.uint8)
img = cv2.add(img, noise)
cv2.imwrite("images/level5.png", img)

print("Images generated")