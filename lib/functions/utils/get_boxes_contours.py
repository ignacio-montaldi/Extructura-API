import cv2
import numpy as np

from lib.functions.utils.sort_contours import sortContours


def getBoxesContours(
    img,
    originalName,
    savePreprocessingImages=False,
    verticalDialationIterations=3,
    horizontalDialationIterations=3,
    verticalErotionIterations=3,
    horizontalErotionIterations=3,
):
    # Thresholding the image
    (thresh, img_bin) = cv2.threshold(
        img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )
    # Invert the image
    img_bin = 255 - img_bin

    # Defining a kernel length
    kernel_length = np.array(img).shape[1] // 80

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv2.erode(
        img_bin, verticle_kernel, iterations=verticalErotionIterations
    )
    verticle_lines_img = cv2.dilate(
        img_temp1, verticle_kernel, iterations=verticalDialationIterations
    )

    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=horizontalErotionIterations)
    horizontal_lines_img = cv2.dilate(
        img_temp2, hori_kernel, iterations=horizontalDialationIterations
    )

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(
        verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0
    )
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(
        img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )

    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(
        img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    # Sort all the contours by top to bottom.
    contours = sortContours(contours, method="top-to-bottom")

    if savePreprocessingImages:
        cv2.imwrite("images/pretemp/" + originalName + "_binirized_image.jpg", img_bin)
        cv2.imwrite(
            "images/pretemp/" + originalName + "_verticle_lines.jpg", verticle_lines_img
        )
        cv2.imwrite(
            "images/pretemp/" + originalName + "_horizontal_lines.jpg",
            horizontal_lines_img,
        )
        cv2.imwrite(
            "images/pretemp/" + originalName + "_combined_lines.jpg", img_final_bin
        )

    return contours
