import cv2
import imutils
import numpy as np
from skimage.filters import threshold_local


def imageCleaning(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(
        gray, 15, offset=6, method="gaussian"
    )  # generic, mean, median, gaussian
    thresh = (gray > T).astype("uint8") * 255
    thresh = ~thresh

    # Dilation
    kernel = np.ones((1, 1), np.uint8)
    ero = cv2.erode(thresh, kernel, iterations=1)
    img_dilation = cv2.dilate(ero, kernel, iterations=1)
    # Remove noise
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        img_dilation, None, None, None, 8, cv2.CV_32S
    )
    sizes = stats[1:, -1]  # get CC_STAT_AREA component
    final = np.zeros((labels.shape), np.uint8)
    for i in range(0, nlabels - 1):
        if sizes[i] >= 3:  # filter small dotted regions
            final[labels == i + 1] = 255

    resizedFinalResult = imutils.resize(~final, height=1684)

    return resizedFinalResult
