import cv2

from lib.functions.utils.check_if_image_is_gray import checkIfImageIsGray


def checkIfImageHasLines(image):
    doesImageHaveLines = False

    image = checkIfImageIsGray(image)

    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Find horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    remove_horizontal = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
    )
    cntsHor = cv2.findContours(
        remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cntsHor = cntsHor[0] if len(cntsHor) == 2 else cntsHor[1]

    # Find vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    remove_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    cntsVer = cv2.findContours(
        remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cntsVer = cntsVer[0] if len(cntsVer) == 2 else cntsVer[1]

    doesImageHaveLines = (len(cntsHor) > 0) or (len(cntsVer) > 0)

    return doesImageHaveLines
