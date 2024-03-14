import os
import cv2
import pytesseract

from lib.enums.invoice_type_enum import Invoice_type

from lib.models.invoice_type_a_item import AItem
from lib.models.invoice_type_c_item import CItem

from lib.functions.utils.process_image import processImage

# Devuelve el detalle de los productos

def getItems(invoice_type: Invoice_type):
    directory_in_str = "./temp"
    directory = os.fsencode(directory_in_str)

    items = []

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("item"):
            img_file = "temp/" + filename
            image = cv2.imread(img_file)
            processImage(
                imageToProcess=image,
                rectDimensions=(10, 100),
                startingIndex=1,
                boxWidthTresh=14,
                boxHeightTresh=0,
                folder="temp",
                outputImagePrefix="value",
                savePreprocessingImages=False,
                reverseSorting=True,
            )

            directory_in_str = "./temp"
            directory = os.fsencode(directory_in_str)

            valuesStr = []

            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.startswith("value"):
                    img_file = "temp/" + filename
                    image = cv2.imread(img_file)
                    ocr_result = pytesseract.image_to_string(
                        image, lang="spa", config="--psm 6"
                    )
                    ocr_result = ocr_result.replace("\n\x0c", "")
                    ocr_result = ocr_result.replace("\n", " ")
                    valuesStr.append(ocr_result)
            if invoice_type == Invoice_type.A:
                item = AItem(
                    valuesStr[0],
                    valuesStr[1],
                    valuesStr[2],
                    valuesStr[3],
                    valuesStr[4],
                    valuesStr[5],
                    valuesStr[6],
                    valuesStr[7],
                    valuesStr[8],
                )
            else:
                item = CItem(
                    valuesStr[0],
                    valuesStr[1],
                    valuesStr[2],
                    valuesStr[3],
                    valuesStr[4],
                    valuesStr[5],
                    valuesStr[6],
                    valuesStr[7],
                )

            items.append(item)
        else:
            continue
    return items
