import cv2
import pytesseract

from app import findFirstCharacterOf


def getHeaderConcept(img_file):
    image = cv2.imread(img_file)
    ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    ocr_result = ocr_result.replace("\n\x0c", "")
    ocr_result = ocr_result.replace("\n", " ")
    substrings = [":", ";", ","]
    ocr_result = ocr_result[
        findFirstCharacterOf(ocr_result, *substrings) + 1 : :
    ].strip()
    return ocr_result