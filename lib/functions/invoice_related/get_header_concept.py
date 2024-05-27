import cv2
import pytesseract

from lib.functions.utils.find_first_character_of_a_string import (
    findFirstCharacterOfAString,
)


def getHeaderConcept(img_file):
    image = cv2.imread(img_file)
    ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    ocr_result = ocr_result.replace("\n\x0c", "")
    ocr_result = ocr_result.replace("\n", " ")
    substrings = [":", ";", ","]
    ocr_result = ocr_result[
        findFirstCharacterOfAString(ocr_result, *substrings) + 1 : :
    ].strip()
    return ocr_result
