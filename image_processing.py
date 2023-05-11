import cv2
import numpy as np
from skimage.metrics import structural_similarity


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
        self.src_template = template
        self.src_template = cv2.rectangle(self.src_template, (130, 100), (1380, 1000), (0,0,255), 2)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.template = template[130: 1000, 100: 1380]

    def __get_processing_area(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        w, h = self.template.shape[::-1]

        res = cv2.matchTemplate(img_gray, self.template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res == np.max(res))
        pt = loc[::-1]

        x = int(pt[0])
        y = int(pt[1])

        crop = img[y: y + h, x: x + w]

        return crop

    def compare(self, img):
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
        diff_box = cv2.merge([diff, diff, diff])

        # Threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=3)
        thresh = cv2.dilate(thresh, kernel, iterations=3)

        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        mask = np.zeros(before_gray.shape, dtype='uint8')
        filled_after = after_gray.copy()

        for c in contours:
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(before_gray, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(after_gray, (x, y), (x + w, y + h), (36, 255, 12), 2)
                cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36, 255, 12), 2)

                # x_n, y_n = coordinate_conversion((x, y), img.shape, after.shape)
                #
                # cv2.rectangle(img, (x_n, y_n), (x_n + w, y_n + h), (36, 255, 12), 2)
                cv2.drawContours(mask, [c], 0, (255, 255, 255), 2)
                cv2.drawContours(filled_after, [c], 0, (0, 255, 0), 2)

        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
