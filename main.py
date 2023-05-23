import os
import sys
import time
import shutil
from datetime import timedelta

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QSplashScreen

import design.main_window
import utils
from worker import Worker
import const


class SplashScreen(QSplashScreen):
    def __init__(self):
        super(QSplashScreen, self).__init__()
        # self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        pixmap = QPixmap("assets/fractal-icon-8-removebg-preview.png")
        self.setPixmap(pixmap)


class SimilarityApp(QtWidgets.QMainWindow, design.main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('assets/fractal-icon-8-removebg-preview.ico'))
        self.showMaximized()

        self.stopButton.setDisabled(True)

        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.templateButton.clicked.connect(self.make_template)
        self.clearButton.clicked.connect(self.clear_records)

        self.redButton.clicked.connect(self.__red_click)
        self.greenButton.clicked.connect(self.__green_click)
        self.zoomerButton.clicked.connect(self.__zoomer_click)

        self.checkBoxRecord.clicked.connect(self.change_record_status)

        self.worker = Worker()
        self.worker.status_trigger.connect(self.__change_status)
        self.worker.top_left_trigger.connect(self.__change_top_left_image)
        self.worker.top_right_trigger.connect(self.__change_top_right_image)
        self.worker.btm_left_trigger.connect(self.__change_btm_left_image)
        self.worker.btm_right_trigger.connect(self.__change_btm_right_image)

        self.start_time = time.time()
        self.fps_start = time.time()
        self.fps_cnt = 0
        self.fps = 0

        self.speed_list = [0] * 100
        self.x_list = list(range(len(self.speed_list)))
        self.speed_cnt = 0

    def __red_click(self):
        self.worker.hola.switch_red_light()
        state = self.worker.hola.red_state
        style = f"background-color: rgba(255, 0, 0, {0.7 if state else 0.2})"
        self.redButton.setStyleSheet(style)
        self.redButton.setText(f'Red {"On" if state else "Off"}')

    def __green_click(self):
        self.worker.hola.switch_green_light()
        state = self.worker.hola.green_state
        style = f"background-color: rgba(0, 255, 0, {0.7 if state else 0.2})"
        self.greenButton.setStyleSheet(style)
        self.greenButton.setText(f'Green {"On" if state else "Off"}')

    def __zoomer_click(self):
        self.worker.hola.switch_zoomer()
        state = self.worker.hola.zoomer_state
        style = f"background-color: rgba(0, 0, 255, {0.7 if state else 0.2})"
        self.zoomerButton.setStyleSheet(style)
        self.zoomerButton.setText(f'Zoomer {"On" if state else "Off"}')

    def __change_status(self):
        self.labelSpeed.setText(str(self.worker.hola.speed))
        td = timedelta(seconds=time.time() - self.start_time)
        self.labelUptime.setText(str(td))

        self.speed_list.pop(0)
        self.speed_list.append(self.worker.hola.speed)
        if self.speed_cnt % 5 == 0:
            self.__set_plot_values()

        fps = f'left: {round(self.worker.left_cam.cam.ResultingFrameRateAbs.GetValue(), 1)} | ' \
              f'right: {round(self.worker.right_cam.cam.ResultingFrameRateAbs.GetValue(), 1)} | ' \
              f'computed: {round(self.fps, 1)}'
        self.labelFps.setText(fps)

    def __set_plot_values(self):
        self.plotWidget.clear()
        self.plotWidget.plot(self.x_list, self.speed_list)

    def __change_top_left_image(self, img):
        self.topLeftLabel.setPixmap(utils.cv_to_qt_image(img))
        if self.fps_cnt > 30:
            self.fps = round(self.fps / self.fps_cnt)
            self.fps_cnt = 0

        self.fps += 1.0 / (time.time() - self.fps_start)
        self.fps_start = time.time()
        self.fps_cnt += 1

    def __change_top_right_image(self, img):
        self.topRightLabel.setPixmap(utils.cv_to_qt_image(img))

    def __change_btm_left_image(self, img):
        self.btmLeftLabel.setPixmap(utils.cv_to_qt_image(img))

    def __change_btm_right_image(self, img):
        self.btmRightLabel.setPixmap(utils.cv_to_qt_image(img))

    def start1(self):
        self.start_time = time.time()
        self.worker.start_work()

    def stop1(self):
        self.worker.stop_work()

    def start(self):
        self.stopButton.setDisabled(False)
        self.startButton.setDisabled(True)
        self.start_time = time.time()
        self.worker.start_work()

    def stop(self):
        self.stopButton.setDisabled(True)
        self.startButton.setDisabled(False)
        self.worker.stop_work1()

    def make_template(self):
        self.worker.make_template()

        self.topRightLabel_3.setPixmap(utils.cv_to_qt_image(self.worker.top_right_processor.src_template))
        self.topLeftLabel_3.setPixmap(utils.cv_to_qt_image(self.worker.top_left_processor.src_template))
        self.btmRightLabel_3.setPixmap(utils.cv_to_qt_image(self.worker.btm_right_processor.src_template))
        self.btmLeftLabel_3.setPixmap(utils.cv_to_qt_image(self.worker.btm_left_processor.src_template))

    def clear_records(self):
        self.worker.record_mode = False
        shutil.rmtree(const.OUTPUT_DIR)
        create_output_dirs()
        self.change_record_status()

    def change_record_status(self):
        self.worker.record_mode = self.checkBoxRecord.isChecked()


def create_output_dirs():
    dirs = [const.TEMPLATE_DIR, const.TOP_LEFT_DIR, const.TOP_RIGHT_DIR, const.BTM_LEFT_DIR, const.BTM_RIGHT_DIR]
    for d in dirs:
        directory = f'{const.OUTPUT_DIR}/{d}'
        if not os.path.exists(directory):
            os.makedirs(directory)


if __name__ == '__main__':
    create_output_dirs()

    app = QtWidgets.QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    window = SimilarityApp()
    window.show()
    splash.finish(window)

    app.exec()
