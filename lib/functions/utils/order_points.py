import numpy as np


def order_points(pts):
    # initializing the list of coordinates to be ordered
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    # top-left point will have the smallest sum
    rect[0] = pts[np.argmin(s)]
    # bottom-right point will have the largest sum
    rect[2] = pts[np.argmax(s)]

    """computing the difference between the points, the
	top-right point will have the smallest difference,
	whereas the bottom-left will have the largest difference"""
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # returns ordered coordinates
    return rect
