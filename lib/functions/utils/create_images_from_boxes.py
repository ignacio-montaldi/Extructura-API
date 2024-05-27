import cv2

from lib.functions.utils.get_boxes_contours import getBoxesContours


def createImagesFromImageBoxes(
    imageToProcess,
    originalName,
    imageWoLines=None,
    check_function=None,
    savePreprocessingImages=False,
    verticalDialationIterations=3,
    horizontalDialationIterations=3,
    getIndexFunction=None,
):
    contours = getBoxesContours(
        imageToProcess,
        originalName,
        savePreprocessingImages,
        verticalDialationIterations=verticalDialationIterations,
        horizontalDialationIterations=horizontalDialationIterations,
    )

    idx = 0
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        if callable(check_function) and check_function(h, w):
            if callable(getIndexFunction):
                idx = getIndexFunction(x, y, w, h)
            else:
                idx += 1
            new_img = imageToProcess[y : y + h, x : x + w]
            cv2.imwrite(
                "images/temp/" + originalName + "_box_" + str(idx) + ".png", new_img
            )
            if imageWoLines is not None:
                new_img = imageWoLines[y : y + h, x : x + w]
                cv2.imwrite(
                    "images/temp/" + originalName + "_box_" + str(idx) + "_wol.png",
                    new_img,
                )
