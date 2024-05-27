import cv2

# Agrega bordes blancos a imagen


def addBorder(image, path):
    color = [255, 255, 255]
    top, bottom, left, right = [20] * 4
    image_with_border = cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    cv2.imwrite(path, image_with_border)
