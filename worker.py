import time

import cv2
from PyQt6.QtCore import pyqtSignal, QThread

import basler_camera
from image_processing import ImageProcessor

MIN_WHITE_VALUE = 25

POINTS_X = [1350, 1400, 1350, 1400]
POINTS_Y = [225, 225, 275, 275]

MAX_SPEED_NO_CHANGES = 200
SKIP_AFTER_POINT = 6


class Worker(QThread):
    speed_trigger = pyqtSignal(int)
    top_left_trigger = pyqtSignal(object)
    top_right_trigger = pyqtSignal(object)
    btm_left_trigger = pyqtSignal(object)
    btm_right_trigger = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.is_worked = None
        self.speed = 0
        self.grub_time = time.time()

        self.top_left_processor = ImageProcessor()
        self.top_right_processor = ImageProcessor()
        self.btm_left_processor = ImageProcessor()
        self.btm_right_processor = ImageProcessor()

        self.left_cam = basler_camera.BaslerCamera(basler_camera.CAM_LEFT)
        self.right_cam = basler_camera.BaslerCamera(basler_camera.CAM_RIGHT)

        self.prev_time = time.time()
        self.speed_no_changes = 0
        self.need_skip = 0

        self.grabbed_top_l = False
        self.grabbed_top_r = False
        self.grabbed_btm_l = False
        self.grabbed_btm_r = False

    def __calc_speed(self, img):
        white_points = 0
        for x, y in zip(POINTS_X, POINTS_Y):
            pixel = img[y, x]
            if pixel[0] >= MIN_WHITE_VALUE and pixel[1] >= MIN_WHITE_VALUE and pixel[2] >= MIN_WHITE_VALUE:
                white_points += 1

        if white_points >= 2:
            self.speed = 500.0 / (time.time() - self.prev_time)
            self.prev_time = time.time()
            self.need_skip = SKIP_AFTER_POINT

            self.grabbed_top_l = self.grabbed_top_r = self.grabbed_btm_l = self.grabbed_btm_r = False
        else:
            self.speed_no_changes += 1

        if self.speed_no_changes > MAX_SPEED_NO_CHANGES:
            self.speed = 0

        self.speed_trigger.emit(self.speed)

    def __calc_totals(self):
        t1 = 200 / self.speed
        t2 = t1 + 105 / self.speed

        top_total = time.time() - self.prev_time + t1
        btm_total = time.time() - self.prev_time + t2

        return top_total, btm_total

    def __left_cam_event_handler(self, img):
        self.__calc_speed(img)
        if self.speed > 0:
            top_total, btm_total = self.__calc_totals()
            if top_total >= 0 and not self.grabbed_top_l:
                self.top_left_image = img
                self.grabbed_top_l = True
                if self.top_left_processor.template:
                    img = self.top_left_processor.compare(img)
                self.top_left_trigger.emit(img)

            if btm_total >= 0 and not self.grabbed_btm_l:
                self.btm_left_image = img
                self.grabbed_btm_l = True
                if self.btm_left_processor.template:
                    img = self.btm_left_processor.compare(img)
                self.btm_left_trigger.emit(img)
        else:
            self.top_left_trigger.emit(img)
            self.btm_left_trigger.emit(img)

    def __right_cam_event_handler(self, img):
        if self.speed > 0:
            top_total, btm_total = self.__calc_totals()
            if top_total >= 0 and not self.grabbed_top_r:
                self.top_right_image = img
                self.grabbed_top_r = True
                if self.top_right_processor.template:
                    img = self.top_right_processor.compare(img)
                self.top_right_trigger.emit(img)

            if btm_total >= 0 and not self.grabbed_btm_r:
                self.btm_right_image = img
                self.grabbed_btm_r = True
                if self.btm_right_processor.template:
                    img = self.btm_right_processor.compare(img)
                self.btm_right_trigger.emit(img)
        else:
            self.top_right_trigger.emit(img)
            self.btm_right_trigger.emit(img)

    def make_template(self):
        self.top_left_processor.make_template(self.top_left_image)
        self.top_right_processor.make_template(self.top_right_image)
        self.btm_left_processor.make_template(self.btm_left_image)
        self.btm_right_processor.make_template(self.btm_right_image)

    def start_work(self):
        self.is_worked = True
        self.left_cam.start_grubbing(self.__left_cam_event_handler)
        self.right_cam.start_grubbing(self.__right_cam_event_handler)

    def stop_work(self):
        self.is_worked = False
        self.left_cam.stop_grubbing()
        self.right_cam.stop_grubbing()
