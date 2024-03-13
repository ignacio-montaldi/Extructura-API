import os
import cv2
import pytesseract
from fuzzywuzzy import fuzz
from lib.functions.find_first_character_of import findFirstCharacterOf

from raw_scripts.raw_script_v2 import find_first_character_of


def getHeaderConceptImproved(key_to_match, file_name_prefix):
    directory_in_str = "./processing"
    directory = os.fsencode(directory_in_str)

    image_path_containing_key = ""
    max_ratio = 0

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(file_name_prefix):
            img_file_path = "processing/" + filename
            image = cv2.imread(img_file_path)
            ocr_result = pytesseract.image_to_string(
                image, lang="spa", config="--psm 6"
            )
            ocr_result = ocr_result.replace("\n\x0c", "")
            ocr_result = ocr_result.replace("\n", " ")
            substrings = [":", ";", ","]
            ocr_result = ocr_result[
                : find_first_character_of(ocr_result, *substrings) :
            ].strip()
            ratio = fuzz.ratio(ocr_result, key_to_match)
            if ratio > max_ratio:
                max_ratio = ratio
                image_path_containing_key = img_file_path

    image = cv2.imread(image_path_containing_key)
    ocr_result = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    ocr_result = ocr_result.replace("\n\x0c", "")
    ocr_result = ocr_result.replace("\n", " ")
    substrings = [":", ";", ","]
    ocr_result = ocr_result[
        findFirstCharacterOf(ocr_result, *substrings) + 1 : :
    ].strip()
    return ocr_result
