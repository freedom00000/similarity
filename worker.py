import time
from datetime import datetime, timedelta
import cv2
from PyQt6.QtCore import pyqtSignal, QThread

import basler_camera
import const
import utils
from hola import Hola
from image_processing import ImageProcessor

MIN_WHITE_VALUE = 25

POINTS_X = [1350, 1400, 1350, 1400]
POINTS_Y = [225, 225, 245, 245]

MAX_SPEED_NO_CHANGES = 200
SKIP_AFTER_POINT = 12


def get_time_ms():
    return datetime.now()


class Worker(QThread):
    status_trigger = pyqtSignal()
    top_left_trigger = pyqtSignal(object)
    top_right_trigger = pyqtSignal(object)
    btm_left_trigger = pyqtSignal(object)
    btm_right_trigger = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.is_worked = None
        self._record_mode = False
        # self.speed = 0
        self.grub_time = get_time_ms()

        self.hola = Hola()

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

    @property
    def record_mode(self):
        return self._record_mode and self.hola.speed > 600

    @record_mode.setter
    def record_mode(self, val):
        self._record_mode = val

    # @utils.thread
    # def __calc_speed(self, img):
    #     if self.need_skip > 0:
    #         self.need_skip -= 1
    #     else:
    #         white_points = 0
    #         for x, y in zip(POINTS_X, POINTS_Y):
    #             pixel = img[y, x]
    #             if pixel[0] >= MIN_WHITE_VALUE and pixel[1] >= MIN_WHITE_VALUE and pixel[2] >= MIN_WHITE_VALUE:
    #                 white_points += 1
    #
    #         if white_points > 2:
    #             now = get_time_ms()
    #             self.speed = round(500.0 / (now - self.prev_time).total_seconds(), 1)
    #             self.prev_time = now
    #             self.need_skip = SKIP_AFTER_POINT
    #
    #             self.grabbed_top_l = self.grabbed_top_r = self.grabbed_btm_l = self.grabbed_btm_r = False
    #             self.speed_no_changes = 0
    #         else:
    #             self.speed_no_changes += 1
    #
    #         if self.speed_no_changes > MAX_SPEED_NO_CHANGES:
    #             self.speed = 0
    #
    #     self.speed_trigger.emit(self.speed)

    def __calc_totals(self):
        if self.hola.speed > 0:
            t1 = 200 / self.hola.speed
            t2 = t1 + 105 / self.hola.speed

            top_total = (datetime.now() - self.hola.prev_time - timedelta(milliseconds=t1)).total_seconds()
            btm_total = (datetime.now() - self.hola.prev_time - timedelta(milliseconds=t2)).total_seconds()
            print('top', top_total, 'btm', btm_total)
            return top_total, btm_total
        else:
            return 0, 0.5

    @utils.thread
    def __left_cam_event_handler(self, img):
        # self.__calc_speed(img)
        self.status_trigger.emit(self.hola.speed)
        if self.hola.speed > 0 >= self.need_skip:
            top_total, btm_total = self.__calc_totals()
            if top_total >= 0 and not self.grabbed_top_l:
                self.top_left_image = img
                self.grabbed_top_l = True
                if self.top_left_processor.has_template():
                    cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TOP_LEFT_DIR}/{time.time()}.jpg', img)
                    img_t = self.top_left_processor.compare(img)
                    self.top_left_trigger.emit(img_t)

                    return
                else:
                    self.top_left_trigger.emit(img)

            elif btm_total >= 0 and not self.grabbed_btm_l:
                self.btm_left_image = img
                self.grabbed_btm_l = True
                if self.btm_left_processor.has_template():
                    cv2.imwrite(f'{const.OUTPUT_DIR}/{const.BTM_LEFT_DIR}/{time.time()}.jpg', img)
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
        if self.hola.speed > 0 >= self.need_skip:
            top_total, btm_total = self.__calc_totals()
            if top_total >= 0 and not self.grabbed_top_r:
                self.top_right_image = img
                self.grabbed_top_r = True
                if self.top_right_processor.has_template():
                    cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TOP_RIGHT_DIR}/{time.time()}.jpg', img)
                    img_t = self.top_right_processor.compare(img)
                    self.top_right_trigger.emit(img_t)

                    return
                else:
                    self.top_right_trigger.emit(img)

            elif btm_total >= 0 and not self.grabbed_btm_r:
                self.btm_right_image = img
                self.grabbed_btm_r = True
                if self.btm_right_processor.has_template():
                    cv2.imwrite(f'{const.OUTPUT_DIR}/{const.BTM_RIGHT_DIR}/{time.time()}.jpg', img)
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

            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TEMPLATE_DIR}/top_left.jpg', self.top_left_processor.src_template)
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TEMPLATE_DIR}/top_right.jpg', self.top_right_processor.src_template)
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TEMPLATE_DIR}/btm_left.jpg', self.btm_left_processor.src_template)
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TEMPLATE_DIR}/btm_right.jpg', self.btm_right_processor.src_template)

        except Exception as e:
            print(e)

    def start_work1(self):
        self.is_worked = True
        self.left_cam.start_grabbing(self.__left_cam_event_handler)
        self.right_cam.start_grabbing(self.__right_cam_event_handler)

    # -------- 2 ------------

    def __left_top_handler(self, img):
        if self.record_mode:
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TOP_LEFT_DIR}/{time.time()}.jpg', img)
        if self.top_left_processor.has_template():
            drawing = self.top_left_processor.compare(img)
        else:
            drawing = img.copy()
        self.top_left_image = img
        self.top_left_trigger.emit(drawing)

    def __right_top_handler(self, img):
        if self.record_mode:
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.TOP_RIGHT_DIR}/{time.time()}.jpg', img)
        if self.top_right_processor.has_template():
            drawing = self.top_right_processor.compare(img)
        else:
            drawing = img.copy()

        self.top_right_image = img
        self.top_right_trigger.emit(drawing)

    @utils.thread
    def __left_btm_handler(self, img):
        if self.record_mode:
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.BTM_LEFT_DIR}/{time.time()}.jpg', img)
        if self.btm_left_processor.has_template():
            drawing = self.btm_left_processor.compare(img)
        else:
            drawing = img.copy()
        self.btm_left_image = img
        self.btm_left_trigger.emit(drawing)

    @utils.thread
    def __right_btm_handler(self, img):
        if self.record_mode:
            cv2.imwrite(f'{const.OUTPUT_DIR}/{const.BTM_RIGHT_DIR}/{time.time()}.jpg', img)
        if self.btm_right_processor.has_template():
            drawing = self.btm_right_processor.compare(img)
        else:
            drawing = img.copy()
        self.btm_right_image = img
        self.btm_right_trigger.emit(drawing)

    def worker2(self):
        # top, btm = self.__calc_totals()
        # threads = [self.left_cam.grab_one(self.__left_top_handler),
        #            self.right_cam.grab_one(self.__right_top_handler)]
        # for t in threads:
        #     t.join()
        self.left_cam.grab_one(self.__left_top_handler)
        self.right_cam.grab_one(self.__right_top_handler)
        if self.hola.speed > 450:
            time.sleep(190 / self.hola.speed)
            # pass
        else:
            time.sleep(0.2)
        self.left_cam.grab_one(self.__left_btm_handler)
        self.right_cam.grab_one(self.__right_btm_handler)

    def stop_work1(self):
        self.is_worked = False
        self.hola.stop()
        self.left_cam.stop_grabbing()
        self.right_cam.stop_grabbing()

    @utils.thread
    def __status_update_loop(self):
        while self.is_worked:
            self.status_trigger.emit()
            time.sleep(0.5)

    def start_work(self):
        self.is_worked = True
        self.__status_update_loop()
        self.worker2()
        self.hola.start(self.worker2)
