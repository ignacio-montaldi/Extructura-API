import cv2
import pytesseract
from fuzzywuzzy import fuzz


def getFooterCurrency(img_file):
    image = cv2.imread(img_file)
    ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    ocr_result = ocr_result.replace("\n\x0c", "")
    ocr_result = ocr_result.replace("\n", " ")
    ocr_result = ocr_result[ocr_result.find(":") + 1 : :].strip()

    if fuzz.ratio(ocr_result, "$") > fuzz.ratio(ocr_result, "USD"):
        ocr_result = "ARS"
    else:
        ocr_result = "USD"
    return ocr_result
