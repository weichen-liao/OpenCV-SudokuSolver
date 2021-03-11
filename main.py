# -*- coding: utf-8 -*-
# Author: Weichen Liao

import cv2
import numpy as np
import matplotlib.pyplot as plt
from functions import detect_text, modify_screenshot_new
from functions import SCREENSHOT_PATH
from PIL import Image

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    fig, ax = plt.subplots()
    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # save the original screenshot
        cv2.imwrite(SCREENSHOT_PATH, frame)

        # predict using Google Vision
        predicts = detect_text(SCREENSHOT_PATH)

        # load original screenshot from local system, modify it, and save it again
        image = modify_screenshot_new(predicts)

        # load the modified screenshot
        # image = cv2.imread(SCREENSHOT_PATH)

        #     ax.imshow(image)
        # cv2.imshow('modified screenshot', image)
        cv2.imshow('modified screenshot', np.asarray(image)[:, :, ::-1].copy())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
