from collections import namedtuple

import numpy
import numpy as np
import cv2

# Based on https://github.com/pyxploiter/Barcode-Detection-and-Decoding

Region = namedtuple('Region', 'image rect box percent area shape box_percent')
debug = False


def detect_regions_multipage(images):
    results = []
    for image in images:
        res = detect_regions(image)
        results.append(res)
    return results


def detect_regions(pil_image, show=False, top_k=5):
    original_image = numpy.array(pil_image)
    image = numpy.array(pil_image)
    if debug:
        cv2.imshow("img processing", image)
        cv2.waitKey(0)

    # resize image
    image = cv2.resize(image, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)

    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # calculate x & y gradient
    gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)
    if show == 1:
        cv2.imshow("gradient-sub", cv2.resize(gradient, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC))

    # blur the image
    blurred = cv2.blur(gradient, (3, 3))

    # threshold the image
    (_, thresh) = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

    if show:
        cv2.imshow("threshed", cv2.resize(thresh, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC))

    # construct a closing kernel and apply it to the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (86, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    if show:
        cv2.imshow("morphology", cv2.resize(closed, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC))

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)

    if show:
        cv2.imshow("erode/dilate", cv2.resize(closed, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC))

    # find the contours in the thresholded image, then sort the contours
    # by their area, keeping only the largest one
    cnts, hierarchy = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    c_topk = sorted(cnts, key=cv2.contourArea, reverse=True)[:top_k]

    crops = []
    for idx, c in enumerate(c_topk):
        # compute the rotated bounding box of the largest contour
        rect = cv2.minAreaRect(c)
        box = np.int0(cv2.boxPoints(rect))

        image_crop, image_rot = crop_minAreaRect(image, rect)
        image_crop_thresh, _ = crop_minAreaRect(thresh, rect)

        area = cv2.contourArea(c)
        black_pixels = np.count_nonzero(image_crop_thresh)
        percent_dark = black_pixels / image_crop.size

        box = np.array(box, dtype=np.float64)
        box[:, 0] = box[:, 0] / image.shape[0]
        box[:, 1] = box[:, 1] / image.shape[1]
        crops.append(Region(image_crop, rect, box, percent_dark, area, image.shape, box))
    # logger.info(f"black pixels: {percent_dark}")

    crops_sorted = sorted(crops, key=lambda reg: (reg.rect[0][1], reg.rect[0][0]), reverse=False)

    for idx, region in enumerate(crops_sorted):
        rect = region.rect
        box = np.int0(cv2.boxPoints(region.rect))
        if show:
            cv2.imshow("cropped_" + str(idx), region.image)
        # draw a bounding box arounded the detected barcode and display the
        # image
        cv2.drawContours(image, [box], -1, (0, 255, 0), 3)

        percent = "{:.3f}".format(percent_dark)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, str(idx), (int(rect[0][0]), int(rect[0][1])), font, 4, (0, 255, 0), 2, cv2.LINE_AA)

    image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    if show:
        cv2.imshow("Image", image)
        cv2.waitKey(0)
    return crops_sorted


def crop_minAreaRect(img, rect):
    # get the parameter of the small rectangle
    center = rect[0]
    size = rect[1]
    angle = rect[2]

    if size[0] < size[1]:
        angle = angle - 90
        size = [size[1], size[0]]

    # inv = 1/0.7
    # center = (center[0]*inv,center[1]*inv)
    # size = (size[0]*inv,size[1]*inv)

    center, size = tuple(map(int, center)), tuple(map(int, size))

    w = 30
    h = 20
    size = (size[0] + w, size[1] + h)
    # get row and col num in img
    height, width = img.shape[0], img.shape[1]
    # print("width: {}, height: {}".format(width, height))

    M = cv2.getRotationMatrix2D(center, angle, 1)
    img_rot = cv2.warpAffine(img, M, (width, height))
    # cv2.imshow("img_rot", img_rot)
    # cv2.waitKey(0)

    img_crop = cv2.getRectSubPix(img_rot, size, center)
    # cv2.imshow("img_crop", img_crop)
    # cv2.waitKey(0)
    return img_crop, img_rot
