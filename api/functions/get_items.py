import os
import cv2
import pytesseract

from lib.enums.invoice_type_enum import InvoiceType

from lib.models.invoice_type_a_item import AItem
from lib.models.invoice_type_c_item import CItem

from lib.functions.utils.process_image import processImage

# Devuelve el detalle de los productos

def getItems(invoice_type: InvoiceType, imageName: str):
    directory_in_str = "images/temp"
    directory = os.fsencode(directory_in_str)

    items = []
    printXYWHIteration=0

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("item"):
            printXYWHIteration= printXYWHIteration + 1
            processImage(
                imageToProcessPath=("images/temp/" + filename),
                rectDimensions=(10, 100),
                startingIndex=1,
                boxWidthTresh=14,
                boxHeightTresh=0,
                folder="images/temp",
                outputImagePrefix="value",
                savePreprocessingImages=False,
                reverseSorting=True,
                imageName=imageName,
                imageTypeName= invoice_type.name,
                printXYWH=True,
                printXYWHIteration=printXYWHIteration
            )

            directory_in_str = "images/temp"
            directory = os.fsencode(directory_in_str)

            valuesStr = []

            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.startswith("value"):
                    img_file = "images/temp/" + filename
                    image = cv2.imread(img_file)
                    ocr_result = pytesseract.image_to_string(
                        image, lang="spa", config="--psm 6"
                    )
                    ocr_result = ocr_result.replace("\n\x0c", "")
                    ocr_result = ocr_result.replace("\n", " ")
                    valuesStr.append(ocr_result)
            if invoice_type == InvoiceType.A:
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
