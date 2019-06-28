# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 15:09:12 2019

@author: ThinkPad
"""

import cv2
import numpy as np
def preprocess(dir):
    img = cv2.imread(dir,1)

    rows, cols = img.shape[:2]

    pts1 = np.float32([[250, 255], [940, 430], [250, 1135], [980, 1120]])

    pts2 = np.float32([[0, 0], [750, 0], [0, 600], [750, 600]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    dst = cv2.warpPerspective(img, M, (750, 600))
    return dst

