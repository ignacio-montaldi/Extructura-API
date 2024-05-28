import os
import cv2
import pytesseract

from lib.enums.invoice_type_enum import InvoiceType

from lib.functions.utils.preprocess_image import preprocess_image
from lib.functions.utils.process_image import processImage
from lib.models.invoice_type_a_item import AItem
from lib.models.invoice_type_c_item import CItem

from lib.functions.utils.delete_file import delete_file
from lib.functions.utils.process_item_image import processItemImage


# Devuelve el detalle de los productos


def getItems(invoice_type: InvoiceType, imageName: str):
    directory_in_str = "images/temp/items"
    directory = os.fsencode(directory_in_str)

    items = []
    printXYWHIteration = 0

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("item"):
            printXYWHIteration = printXYWHIteration + 1
            processImage(
                imageToProcessPath=("images/temp/items/" + filename),
                rectDimensions=(7, 250),
                boxWidthTresh=5,
                boxHeightTresh=0,
                outputImagePrefix="value",
                folder="images/temp/items/values",
                reverseSorting=True,
            )
            # processItemImage(
            #     imageToProcessPath=("images/temp/" + filename),
            #     rectDimensions=(7, 250),
            #     boxWidthTresh=5,
            #     boxHeightTresh=0,
            #     folder="images/temp",
            #     outputImagePrefix="value",
            #     reverseSorting=True,
            #     invoice_type=invoice_type,
            #     imageName=imageName,
            #     printXYWHIteration=printXYWHIteration,
            # )

            directory_in_str = "images/temp/items/values/"
            directory = os.fsencode(directory_in_str)

            valuesStr = []
            # valuesStr = {
            #     "1": "",
            #     "2": "",
            #     "3": "",
            #     "4": "",
            #     "5": "",
            #     "6": "",
            #     "7": "",
            #     "8": "",
            #     "9": "",
            # }
            # currentKey = 0

            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                img_file_path = "images/temp/items/values/" + filename
                image = cv2.imread(img_file_path)
                ocr_result = pytesseract.image_to_string(
                    image, lang="spa", config="--psm 6"
                )
                ocr_result = ocr_result.replace("\n\x0c", "")
                ocr_result = ocr_result.replace("\n", " ")
                # currentKey = filename[filename.index("_") + 1]
                valuesStr.append(ocr_result)
                # Elimino la imágen al terminar
                delete_file(img_file_path)
            if invoice_type == InvoiceType.A:
                if len(valuesStr) == 8:
                    item = AItem(
                        "",
                        valuesStr[0],
                        valuesStr[1],
                        valuesStr[2],
                        valuesStr[3],
                        valuesStr[4],
                        valuesStr[5],
                        valuesStr[6],
                        valuesStr[7],
                    )
                else:  # ==9
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
                if len(valuesStr) == 7:
                    item = CItem(
                        "",
                        valuesStr[0],
                        valuesStr[1],
                        valuesStr[2],
                        valuesStr[3],
                        valuesStr[4],
                        valuesStr[5],
                        valuesStr[6],
                    )
                else:  # ==8
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
