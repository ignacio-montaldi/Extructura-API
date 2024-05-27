import cv2


def edgeCleaning(
    image,
    path,
    paddingToPaint=10,
    top=False,
    left=False,
    right=False,
    bottom=False,
    all=False,
):
    if left or all:
        cv2.rectangle(
            image, (0, 0), (paddingToPaint, image.shape[0]), (255, 255, 255), -1
        )
    if top or all:
        cv2.rectangle(
            image, (0, 0), (image.shape[1], paddingToPaint), (255, 255, 255), -1
        )
    if right or all:
        cv2.rectangle(
            image,
            (image.shape[1] - paddingToPaint, 0),
            (image.shape[1], image.shape[0]),
            (255, 255, 255),
            -1,
        )
    if bottom or all:
        cv2.rectangle(
            image,
            (0, image.shape[0] - paddingToPaint),
            (image.shape[1], image.shape[0]),
            (255, 255, 255),
            -1,
        )
    cv2.imwrite(path, image)
    return image
