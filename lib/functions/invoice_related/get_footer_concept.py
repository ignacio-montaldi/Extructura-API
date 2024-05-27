import cv2
import pytesseract


def getFooterConcept(img_file):
    image = cv2.imread(img_file)
    try:
        ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    except:
        return
    ocr_result = ocr_result.replace("\n\x0c", "")
    ocr_result = ocr_result.replace("\n", " ")
    return ocr_result
