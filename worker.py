import time
from datetime import datetime, timedelta
import cv2
from PyQt6.QtCore import pyqtSignal, QThread

import basler_camera
import utils
from image_processing import ImageProcessor

MIN_WHITE_VALUE = 25

POINTS_X = [1350, 1400, 1350, 1400]
POINTS_Y = [225, 225, 275, 275]

MAX_SPEED_NO_CHANGES = 200
SKIP_AFTER_POINT = 12


def get_time_ms():
    return datetime.now()


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
        self.grub_time = get_time_ms()

        self.top_left_processor = ImageProcessor()
        self.top_right_processor = ImageProcessor()
        self.btm_left_processor = ImageProcessor()
        self.btm_right_processor = ImageProcessor()

        self.left_cam = basler_camera.BaslerCamera(basler_camera.CAM_LEFT)
        self.right_cam = basler_camera.BaslerCamera(basler_camera.CAM_RIGHT)

        self.prev_time = get_time_ms()
        self.speed_no_changes = 0
        self.need_skip = 0

        self.grabbed_top_l = False
        self.grabbed_top_r = False
        self.grabbed_btm_l = False
        self.grabbed_btm_r = False

    @utils.thread
    def __calc_speed(self, img):
        if self.need_skip > 0:
            self.need_skip -= 1
        else:
            white_points = 0
            for x, y in zip(POINTS_X, POINTS_Y):
                pixel = img[y, x]
                if pixel[0] >= MIN_WHITE_VALUE and pixel[1] >= MIN_WHITE_VALUE and pixel[2] >= MIN_WHITE_VALUE:
                    white_points += 1

            if white_points > 2:
                now = get_time_ms()
                self.speed = round(500.0 / (now - self.prev_time).total_seconds(), 1)
                self.prev_time = now
                self.need_skip = SKIP_AFTER_POINT

                self.grabbed_top_l = self.grabbed_top_r = self.grabbed_btm_l = self.grabbed_btm_r = False
                self.speed_no_changes = 0
            else:
                self.speed_no_changes += 1

            if self.speed_no_changes > MAX_SPEED_NO_CHANGES:
                self.speed = 0

        self.speed_trigger.emit(self.speed)

    def __calc_totals(self):
        t1 = 200 / self.speed
        t2 = (t1 + 105) / self.speed

        top_total = (get_time_ms() - self.prev_time + timedelta(milliseconds=t1)).total_seconds()
        btm_total = (get_time_ms() - self.prev_time + timedelta(milliseconds=t2)).total_seconds()
        print('top', top_total, 'btm', btm_total)
        return top_total, btm_total

    @utils.thread
    def __left_cam_event_handler(self, img):
        self.__calc_speed(img)
        if self.speed > 0 >= self.need_skip:
            top_total, btm_total = self.__calc_totals()
            if top_total >= 0 and not self.grabbed_top_l:
                self.top_left_image = img
                self.grabbed_top_l = True
                if self.top_left_processor.has_template():
                    img_t = self.top_left_processor.compare(img)
                    self.top_left_trigger.emit(img_t)
                    return
                else:
                    self.top_left_trigger.emit(img)

            elif btm_total >= 0 and not self.grabbed_btm_l:
                self.btm_left_image = img
                self.grabbed_btm_l = True
                if self.btm_left_processor.has_template():
                    img_b = self.btm_left_processor.compare(img)
                    self.btm_left_trigger.emit(img_b)
                    return
                else:
                    self.btm_left_trigger.emit(img)
        elif self.need_skip <= 0:
            self.top_left_image = img
            self.btm_left_image = img
            self.top_left_trigger.emit(img)
            self.btm_left_trigger.emit(img)

    @utils.thread
    def __right_cam_event_handler(self, img):
        if self.speed > 0 >= self.need_skip:
            top_total, btm_total = self.__calc_totals()
            if top_total >= 0 and not self.grabbed_top_r:
                self.top_right_image = img
                self.grabbed_top_r = True
                if self.top_right_processor.has_template():
                    img_t = self.top_right_processor.compare(img)
                    self.top_right_trigger.emit(img_t)
                    return
                else:
                    self.top_right_trigger.emit(img)

            elif btm_total >= 0 and not self.grabbed_btm_r:
                self.btm_right_image = img
                self.grabbed_btm_r = True
                if self.btm_right_processor.has_template():
                    img_b = self.btm_right_processor.compare(img)
                    self.btm_right_trigger.emit(img_b)
                    return
                else:
                    self.btm_right_trigger.emit(img)
        elif self.need_skip <= 0:
            self.top_right_image = img
            self.btm_right_image = img
            self.top_right_trigger.emit(img)
            self.btm_right_trigger.emit(img)

    def make_template(self):
        try:
            self.top_left_processor.make_template(self.top_left_image)
            self.top_right_processor.make_template(self.top_right_image)
            self.btm_left_processor.make_template(self.btm_left_image)
            self.btm_right_processor.make_template(self.btm_right_image)
        except Exception as e:
            print(e)

    def start_work(self):
        self.is_worked = True
        self.left_cam.start_grubbing(self.__left_cam_event_handler)
        self.right_cam.start_grubbing(self.__right_cam_event_handler)

    def stop_work(self):
        self.is_worked = False
        self.left_cam.stop_grubbing()
        self.right_cam.stop_grubbing()
