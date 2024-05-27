import cv2


def addBorders(cvImage, size, color):
    top, bottom, left, right = [size] * 4
    imageWithBorder = cv2.copyMakeBorder(
        cvImage, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return imageWithBorder
