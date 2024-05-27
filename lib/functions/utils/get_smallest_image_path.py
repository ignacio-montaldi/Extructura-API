import os
import cv2


def getSmallestImagePath(dir, fileNamePrefix):
    directory_in_str = "./" + dir
    directory = os.fsencode(directory_in_str)

    smallest_box = float("inf")
    smallest_box_image_path = ""

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(fileNamePrefix):
            img_file = dir + "/" + filename
            image = cv2.imread(img_file)
            imageArea = image.shape[0] * image.shape[1]
            if imageArea < smallest_box:
                smallest_box = imageArea
                smallest_box_image_path = img_file

    return smallest_box_image_path
