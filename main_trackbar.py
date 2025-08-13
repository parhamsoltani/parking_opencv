# main_trackbar.py

import cv2
import pickle
import cvzone
import numpy as np

cap = cv2.VideoCapture('carPark.mp4')
width, height = 103, 43
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)


def empty(a):
    pass


cv2.namedWindow("Threshold Controls")
cv2.resizeWindow("Threshold Controls", 640, 240)

# More meaningful trackbar names:
# - BlockSize: adaptiveThreshold blockSize (must be odd, >=3)
# - C_value: constant subtracted from mean in adaptiveThreshold
# - MedianKsize: kernel size for medianBlur (must be odd, >=1)
cv2.createTrackbar("BlockSize", "Threshold Controls", 25, 51, empty)   # prefer odd values, 3..51
cv2.createTrackbar("C_value", "Threshold Controls", 16, 50, empty)    # small positive int (or range you prefer)
cv2.createTrackbar("MedianKsize", "Threshold Controls", 5, 31, empty) # prefer odd values, 1..31


def checkSpaces():
    spaces = 0
    for pos in posList:
        x, y = pos
        w, h = width, height

        imgCrop = imgThres[y:y + h, x:x + w]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 200, 0)
            thic = 5
            spaces += 1
        else:
            color = (0, 0, 200)
            thic = 2

        cv2.rectangle(img, (x, y), (x + w, y + h), color, thic)
        cv2.putText(img, str(cv2.countNonZero(imgCrop)), (x, y + h - 6),
                    cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

    cvzone.putTextRect(img, f'Free: {spaces}/{len(posList)}', (50, 60),
                       thickness=3, offset=20, colorR=(0, 200, 0))


while True:
    # Get image frame
    success, img = cap.read()
    if not success:
        break

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    # read trackbar values
    blockSize = cv2.getTrackbarPos("BlockSize", "Threshold Controls")
    C_value = cv2.getTrackbarPos("C_value", "Threshold Controls")
    medianKsize = cv2.getTrackbarPos("MedianKsize", "Threshold Controls")

    # enforce valid odd sizes for blockSize and medianKsize
    if blockSize < 3:
        blockSize = 3
    if blockSize % 2 == 0:
        blockSize += 1

    if medianKsize < 1:
        medianKsize = 1
    if medianKsize % 2 == 0:
        medianKsize += 1

    # Apply adaptive thresholding and median blur using the meaningful parameter names
    imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, blockSize, C_value)
    imgThres = cv2.medianBlur(imgThres, medianKsize)
    kernel = np.ones((3, 3), np.uint8)
    imgThres = cv2.dilate(imgThres, kernel, iterations=1)

    checkSpaces()

    # Display Output
    cv2.imshow("Image", img)
    # Optional debug windows:
    # cv2.imshow("Thresh", imgThres)
    # cv2.imshow("Blur", imgBlur)

    key = cv2.waitKey(1)
    if key == ord('r'):
        pass
