import glob

import cv2
import numpy as np
from skimage.metrics import structural_similarity

import utils

TEMP_MARGIN = 40


def detect_sheet(first_frame, test_frame):
    gray = cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=3)

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest_cnt = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)[0]
    (x, y, w, h) = cv2.boundingRect(biggest_cnt)
    # cv2.rectangle(test_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # return (x, y), (x + w, y + h)
    return x, y, w, h


class ImageProcessor:
    template_rect = [[100, 100], [1340, 1000]]

    def __init__(self, is_right=False, is_bottom=False):
        self.src_template = None
        self.template = None

        self.is_bottom = is_bottom
        path_to_empty_template = f'TestImages/empty_template_{"right" if is_right else "left"}.jpg'

        self.empty_template = cv2.imread(path_to_empty_template, cv2.IMREAD_GRAYSCALE)

    def has_template(self):
        try:
            return self.template.any()
        except:
            return False

    def make_template(self, template):
        self.src_template = template.copy()

        if self.is_bottom:
            x, y, w, h = detect_sheet(self.empty_template, self.src_template)
            mx = x - TEMP_MARGIN if x - TEMP_MARGIN >= 0 else TEMP_MARGIN
            my = y + TEMP_MARGIN if y + TEMP_MARGIN >= 0 else TEMP_MARGIN
            mw = x + w - TEMP_MARGIN if x + w - TEMP_MARGIN < self.src_template.shape[1] else self.src_template.shape[0]
            mh = y + h - TEMP_MARGIN if y + h - TEMP_MARGIN < self.src_template.shape[0] else self.src_template.shape[1]
            self.template_rect = (mx, my), (mw, mh)

        cv2.rectangle(self.src_template,
                      self.template_rect[0], self.template_rect[1],
                      (0, 255, 0),
                      2)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.template = template[self.template_rect[0][1]: self.template_rect[1][1],
                        self.template_rect[0][0]: self.template_rect[1][0]]

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

    def hist_compare(self, img):
        # Calculate the histogram and normalize it
        hist_img1 = cv2.calcHist([self.template], [0], None, [256], [0, 256], accumulate=False)
        cv2.normalize(hist_img1, hist_img1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        hist_img2 = cv2.calcHist([img], [0], None, [256], [0, 256], accumulate=False)
        cv2.normalize(hist_img2, hist_img2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        # find the metric value
        metric_types = {
            "HISTCMP_CORREL": cv2.HISTCMP_CORREL,
            "HISTCMP_CHISQR": cv2.HISTCMP_CHISQR,
            "HISTCMP_INTERSET": cv2.HISTCMP_INTERSECT,
            "HISTCMP_BHATTACHARYA": cv2.HISTCMP_BHATTACHARYYA,
            "HISTCMP_CHISQR_ALT": cv2.HISTCMP_CHISQR_ALT,
            "HISTCMP_KL_DIV": cv2.HISTCMP_KL_DIV
        }
        metrics = {}
        for t in metric_types.keys():
            metric_val = cv2.compareHist(hist_img1, hist_img2, metric_types[t])
            metrics[t] = metric_val
            print(t, metric_val)
        return metrics

    def compare(self, orig):
        img = orig.copy()
        before_gray = self.template
        after = self.__get_processing_area(img)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

        # hist_metrics = self.hist_compare(after_gray)

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
        drawing[self.template_rect[0][1]: self.template_rect[1][1],
        self.template_rect[0][0]: self.template_rect[1][0]] = thresh

        contours = cv2.findContours(drawing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # mask = np.zeros(before_gray.shape, dtype='uint8')
        # filled_after = after_gray.copy()
        # drawing = cv2.cvtColor(drawing, cv2.COLOR_GRAY2BGR)
        for c in contours:
            area = cv2.contourArea(c)
            if area > 250:
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

    pr = ImageProcessor(is_right=False, is_bottom=True)
    pr.make_template(template)
    files = glob.glob("TestImages/output/topLeft0/*")
    with open('test_histo.csv', 'w+') as file:
        file.write('file_name;'
                   'HISTCMP_CORREL;'
                   'HISTCMP_CHISQR;'
                   'HISTCMP_INTERSET;'
                   'HISTCMP_BHATTACHARYA;'
                   'HISTCMP_CHISQR_ALT;'
                   'HISTCMP_KL_DIV\n')

        for im_path in files:
            print(im_path)
            im = cv2.imread(im_path)
            res, diff, hist_metric = pr.compare(im)

            res = cv2.putText(res,
                              f'HISTCMP_CORREL:        {hist_metric["HISTCMP_CORREL"]}',
                              (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (100, 255, 255), 2, cv2.LINE_AA)
            res = cv2.putText(res,
                              f'HISTCMP_CHISQR:        {hist_metric["HISTCMP_CHISQR"]}',
                              (10, 75), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (0, 255, 255), 2, cv2.LINE_AA)
            res = cv2.putText(res,
                              f'HISTCMP_INTERSET:      {hist_metric["HISTCMP_INTERSET"]}',
                              (10, 100), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (0, 255, 255), 2, cv2.LINE_AA)
            res = cv2.putText(res,
                              f'HISTCMP_BHATTACHARYA: {hist_metric["HISTCMP_BHATTACHARYA"]}',
                              (10, 125), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (0, 255, 255), 2, cv2.LINE_AA)
            res = cv2.putText(res,
                              f'HISTCMP_CHISQR_ALT:    {hist_metric["HISTCMP_CHISQR_ALT"]}',
                              (10, 150), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (0, 255, 255), 2, cv2.LINE_AA)
            res = cv2.putText(res,
                              f'HISTCMP_KL_DIV:         {hist_metric["HISTCMP_KL_DIV"]}',
                              (10, 175), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (0, 255, 255), 2, cv2.LINE_AA)
            res = cv2.putText(res,
                              im_path,
                              (10, 200), cv2.FONT_HERSHEY_SIMPLEX,
                              0.8, (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('template', utils.resize_image(pr.src_template, scale=50))
            cv2.imshow('src', utils.resize_image(im, scale=50))
            cv2.imshow('res', utils.resize_image(res, scale=50))
            cv2.imshow('diff', utils.resize_image(diff, scale=50))
            cv2.waitKey(500)
            print('-' * 40)
            file.write(f'{im_path};{"".join([f"{hm};" for hm in hist_metric.values()])}\n')


if __name__ == "__main__":
    test()
