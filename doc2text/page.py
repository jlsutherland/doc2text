# coding=utf-8

import os
import traceback
import sys

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage.filters import rank_filter
import pytesseract


class Page(object):
    def __init__(self, im, page_num, lang=None):
        self.healthy = True
        self.err = False
        self.page_num = page_num
        self.orig_im = im
        self.orig_shape = self.orig_im.shape
        self.lang = lang

    def crop(self):
        try:
            self.image, self.num_tries = process_image(self.orig_im)
            self.crop_shape = self.image.shape
            return self.image
        except Exception as e:
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                print("Error in %s on line %d" % (fname, lineno))
                print(e)
            self.err = e
            self.healthy = False

    def deskew(self):
        try:
            self.image, self.theta_est = process_skewed_crop(self.image)
            return self.image
        except Exception as e:
            self.err = e
            self.healthy = False

    def extract_text(self):
        temp_path = 'text_temp.png'
        cv2.imwrite(temp_path, self.image)
        self.text = pytesseract.image_to_string(Image.open(temp_path), lang=self.lang)
        os.remove(temp_path)
        return self.text

    def save(self, out_path):
        if not self.healthy:
            print("There was an error when cropping")
            raise Exception(self.err)
        else:
            self.imwrite(out_path, self.image)


def auto_canny(image, sigma=0.33):
    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper, True)
    return edged


def dilate(image, kernel, iterations):
    dilated_image = cv2.dilate(image, kernel, iterations=iterations)
    return dilated_image


def downscale_image(im, max_dim=2048):
    """Shrink im until its longest dimension is <= max_dim.
    Returns new_image, scale (where scale <= 1)."""
    a, b = im.shape[:2]
    if max(a, b) <= max_dim:
        return 1.0, im

    scale = 1.0 * max_dim / max(a, b)
    new_im = cv2.resize(im, (int(b * scale), int(a * scale)), cv2.INTER_AREA)
    return scale, new_im


def find_components(im, max_components=16):
    """Dilate the image until there are just a few connected components.
    Returns contours for these components."""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilation = dilate(im, kernel, 6)

    count = 21
    n = 0
    sigma = 0.000

    while count > max_components:
        n += 1
        sigma += 0.005
        result = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(result) == 3:
            _, contours, hierarchy = result
        elif len(result) == 2:
            contours, hierarchy = result
        possible = find_likely_rectangles(contours, sigma)
        count = len(possible)

    return (dilation, possible, n)


def find_likely_rectangles(contours, sigma):
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    possible = []
    for c in contours:

        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, sigma * peri, True)
        box = make_box(approx)
        possible.append(box)

    return possible


def make_box(poly):
    x = []
    y = []
    for p in poly:
        for point in p:
            x.append(point[0])
            y.append(point[1])
    xmax = max(x)
    ymax = max(y)
    xmin = min(x)
    ymin = min(y)
    return (xmin, ymin, xmax, ymax)


def rect_union(crop1, crop2):
    """Union two (x1, y1, x2, y2) rects."""
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)


def rect_area(crop):
    x1, y1, x2, y2 = crop
    return max(0, x2 - x1) * max(0, y2 - y1)


def crop_image(im, rect, scale):
    xmin, ymin, xmax, ymax = rect
    crop = [xmin, ymin, xmax, ymax]
    xmin, ymin, xmax, ymax = [int(x / scale) for x in crop]
    cropped = im[ymin:ymax, xmin:xmax]
    return cropped


def reduce_noise_raw(im):
    bilat = cv2.bilateralFilter(im, 9, 75, 75)
    blur = cv2.medianBlur(bilat, 5)
    return blur


def reduce_noise_edges(im):
    structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    opening = cv2.morphologyEx(im, cv2.MORPH_OPEN, structuring_element)
    maxed_rows = rank_filter(opening, -4, size=(1, 20))
    maxed_cols = rank_filter(opening, -4, size=(20, 1))
    debordered = np.minimum(np.minimum(opening, maxed_rows), maxed_cols)
    return debordered


def rects_are_vertical(rect1, rect2):
    xmin1, ymin1, xmax1, ymax1 = rect1
    xmin2, ymin2, xmax2, ymax2 = rect2

    midpoint1 = (xmin1 + xmax1) / 2
    midpoint2 = (xmin2 + xmax2) / 2
    dist = abs(midpoint1 - midpoint2)

    rectarea1 = rect_area(rect1)
    rectarea2 = rect_area(rect2)
    if rectarea1 > rectarea2:
        thres = (xmax1 - xmin1) * 0.1
    else:
        thres = (xmax2 - xmin2) * 0.1
    if thres > dist:
        align = True
    else:
        align = False
    return align


def find_final_crop(im, rects):
    current = None
    for rect in rects:
        if current is None:
            current = rect
            continue

        aligned = rects_are_vertical(current, rect)

        if not aligned:
            continue

        current = rect_union(current, rect)
    return current


def process_image(orig_im):

    # Load and scale down image.
    scale, im = downscale_image(orig_im)

    # Reduce noise.
    blur = reduce_noise_raw(im.copy())

    # Edged.
    edges = auto_canny(blur.copy())

    # Reduce noise and remove thin borders.
    debordered = reduce_noise_edges(edges.copy())

    # Dilate until there are a few components.
    dilation, rects, num_tries = find_components(debordered, 16)

    # Find the final crop.
    final_rect = find_final_crop(dilation, rects)

    # Crop the image and smooth.
    cropped = crop_image(orig_im, final_rect, scale)
    kernel = np.ones((5, 5), np.float32) / 25
    smooth2d = cv2.filter2D(cropped, -1, kernel=kernel)

    return (smooth2d, num_tries)


def rad_to_deg(theta):
    return theta * 180 / np.pi


def rotate(image, theta):
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, theta, 1)
    rotated = cv2.warpAffine(image, M, (int(w), int(h)), cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return rotated


def estimate_skew(image):
    edges = auto_canny(image)
    lines = cv2.HoughLines(edges, 1, np.pi / 90, 200)
    new = edges.copy()

    thetas = []

    for line in lines:
        for rho, theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            if theta > np.pi / 3 and theta < np.pi * 2 / 3:
                thetas.append(theta)
                new = cv2.line(new, (x1, y1), (x2, y2), (255, 255, 255), 1)

    theta_mean = np.mean(thetas)
    theta = rad_to_deg(theta_mean) if len(thetas) > 0 else 0

    return theta


def compute_skew(theta):
    # We assume a perfectly aligned page has lines at theta = 90 deg
    diff = 90 - theta

    # We want to reverse the difference.
    return -diff


def process_skewed_crop(image):
    theta = compute_skew(estimate_skew(image))
    ret, thresh = cv2.threshold(image.copy(), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    rotated = rotate(thresh, theta)
    return (rotated, theta)
