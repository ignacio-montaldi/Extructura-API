import cv2
import imutils

from lib.functions.utils.image_cleaning import imageCleaning
from lib.functions.utils.perspective_transform import perspectiveTransform


def preprocess_image(original_img):
    copy = original_img.copy()

    # The resized height in hundreds
    ratio = original_img.shape[0] / 1684.0
    img_resize = imutils.resize(original_img, height=1684)

    gray_image = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)

    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edged_img = cv2.Canny(blurred_image, 75, 200)
    cnts, _ = cv2.findContours(edged_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            doc = approx
            break

    warped_image = perspectiveTransform(copy, doc.reshape(4, 2) * ratio)

    cv2.imwrite("images/data/page_wrapeed.png", warped_image)

    finalResult = imageCleaning(warped_image)

    cv2.imwrite("images/data/page_preprocessed.png", finalResult)
    return finalResult
