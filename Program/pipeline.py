import cv2, numpy as np

def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def blur(gray):
    return cv2.GaussianBlur(gray, (5,5), 0)

def threshold(blur):
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return thresh

def distance(thresh):
    dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    return cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def marker(thresh):
    kernel = np.ones((3,3), np.uint8)
    sure_bg = cv2.dilate(thresh, kernel, iterations=3)
    dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers+1
    markers[unknown==255] = 0
    return markers

def watershed(img, markers):
    markers = cv2.watershed(img, markers.copy())
    img[markers == -1] = [0,0,255]
    return img
