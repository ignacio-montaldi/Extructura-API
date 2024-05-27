import os
import cv2

from lib.functions.utils.delete_files_in_folder import deleteFilesInFolder
from lib.functions.utils.remove_lines_from_image import removeLinesFromImage


def reduceToBiggestByArea(folder, file_name_prefix):
    biggestArea = 0
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        if filename.startswith(file_name_prefix) and filename.find("wol") == -1:
            file_path = os.path.join(folder, filename)
            image = cv2.imread(file_path)
            if image.shape[0] * image.shape[1] > biggestArea:
                biggestArea = image.shape[0] * image.shape[1]
                imageToSave = image

    deleteFilesInFolder(folder, fileNamePrefix=file_name_prefix)
    cv2.imwrite(os.path.join(folder, file_name_prefix) + "_1.png", imageToSave)
    gray_image = cv2.cvtColor(imageToSave, cv2.COLOR_BGR2GRAY)
    invoiceWithoutLines = removeLinesFromImage(gray_image)
    cv2.imwrite(
        os.path.join(folder, file_name_prefix) + "_1_wol.png", invoiceWithoutLines
    )
