import cv2
import numpy as np

from lib.functions.utils.check_if_image_is_gray import checkIfImageIsGray
from lib.functions.utils.get_boxes_contours import getBoxesContours
from lib.functions.utils.sort_contours import sortContours


def paintHeaderBox2TitleAndBox(image, imageWol):
    # Esquina
    image = checkIfImageIsGray(image)

    contours = getBoxesContours(
        image,
        "images/temp/header_box_2.png",
        verticalDialationIterations=5,
        horizontalDialationIterations=5,
        verticalErotionIterations=5,
        horizontalErotionIterations=5,
    )

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w == image.shape[1] or h == image.shape[0]:
            continue
        else:
            cv2.rectangle(imageWol, (x, y), (x + w, y + h), (255, 255, 255), -1)

    cv2.imwrite("images/temp/header_box_2_wol.png", imageWol)

    # Titulo
    gray = checkIfImageIsGray(imageWol)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (1000, 1))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 25:
            cv2.rectangle(imageWol, (x, y), (x + w, y + h), (255, 255, 255), -1)

    cv2.imwrite("images/temp/header_box_2_wol.png", imageWol)
