import cv2
import imutils
from skimage.filters import threshold_local

def imageCleaning(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(gray, 15, offset=6, method="gaussian")
    warped = (gray > T).astype("uint8") * 255
    cv2.imwrite("./data/" + "page_preprocessed" + ".png", warped)
    resizedFinalResult = imutils.resize(warped, height=1684)
    return resizedFinalResult