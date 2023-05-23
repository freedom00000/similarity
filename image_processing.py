import glob

import cv2
import numpy as np
from skimage.metrics import structural_similarity

import utils

RECT = ((100, 100), (1000, 1340))


def coordinate_conversion(point, o_shape, c_shape):
    oh, ow = o_shape[:2]
    ch, cw = c_shape[:2]

    return int(point[0] * ow / cw), int(point[1] * oh / ch)


class ImageProcessor:
    def __init__(self):
        self.src_template = None
        self.template = None

    def has_template(self):
        try:
            return self.template.any()
        except:
            return False

    def make_template(self, template):
        self.src_template = template.copy()
        cv2.rectangle(self.src_template, (RECT[0][1], RECT[0][0]), (RECT[1][1], RECT[1][0]), (0, 0, 255), 1)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.template = template[RECT[0][0]: RECT[1][0], RECT[0][1]: RECT[1][1]]

    def __get_processing_area(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        w, h = self.template.shape[::-1]

        res = cv2.matchTemplate(img_gray, self.template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res == np.max(res))
        pt = loc[::-1]

        x = int(pt[0])
        y = int(pt[1])

        crop = img[y: y + h, x: x + w]
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 12), 2)
        return crop

    def compare(self, orig):
        img = orig.copy()
        before_gray = self.template
        after = self.__get_processing_area(img)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between the two images
        (score, diff) = structural_similarity(before_gray, after_gray, full=True)
        # print("Image Similarity: {:.4f}%".format(score * 100))

        # The diff image contains the actual image differences between the two images
        # and is represented as a floating point data type in the range [0,1]
        # so we must convert the array to 8-bit unsigned integers in the range
        # [0,255] before we can use it with OpenCV
        diff = (diff * 255).astype("uint8")
        # diff_box = cv2.merge([diff, diff, diff])

        # Threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        kernel = np.ones((7, 7), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=3)
        thresh = cv2.dilate(thresh, kernel, iterations=3)

        drawing = np.zeros(img.shape[:2], dtype=np.uint8)
        drawing[RECT[0][0]: RECT[1][0], RECT[0][1]: RECT[1][1]] = thresh

        contours = cv2.findContours(drawing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # mask = np.zeros(before_gray.shape, dtype='uint8')
        # filled_after = after_gray.copy()
        # drawing = cv2.cvtColor(drawing, cv2.COLOR_GRAY2BGR)
        for c in contours:
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(c)
                # cv2.rectangle(before_gray, (x, y), (x + w, y + h), (36, 255, 12), 2)
                # cv2.rectangle(after_gray, (x, y), (x + w, y + h), (36, 255, 12), 2)
                # cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36, 255, 12), 2)

                # cv2.rectangle(drawing, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 2)

                # cv2.drawContours(mask, [c], 0, (255, 255, 255), 2)
                # cv2.drawContours(filled_after, [c], 0, (0, 255, 0), 2)

        # return cv2.cvtColor(filled_after, cv2.COLOR_GRAY2BGR)
        return img


def test():
    template = cv2.imread('TestImages/output/template/top_left.jpg')

    pr = ImageProcessor()
    pr.make_template(template)
    files = glob.glob("TestImages/output/topLeft/*")
    for im_path in files:
        im = cv2.imread(im_path)
        res, diff = pr.compare(im)
        cv2.imshow('template', utils.resize_image(pr.src_template, scale=50))
        cv2.imshow('src', utils.resize_image(im, scale=50))
        cv2.imshow('res', utils.resize_image(res, scale=50))
        cv2.imshow('diff', utils.resize_image(diff, scale=50))
        cv2.waitKey(500)


if __name__ == "__main__":
    test()
