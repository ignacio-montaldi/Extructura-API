import cv2


def getVerticalLinePosition(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[
        1
    ]
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    sum = 0

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        sum += x

    return sum
