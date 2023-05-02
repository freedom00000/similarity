import sys
import time
from datetime import timedelta

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QSplashScreen

import design.main_window
import utils
from worker import Worker


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

        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.templateButton.clicked.connect(self.make_template)

        self.worker = Worker()
        self.worker.speed_trigger.connect(self.__change_speed)
        self.worker.top_left_trigger.connect(self.__change_top_left_image)
        self.worker.top_right_trigger.connect(self.__change_top_right_image)
        self.worker.btm_left_trigger.connect(self.__change_btm_left_image)
        self.worker.btm_right_trigger.connect(self.__change_btm_right_image)

        self.start_time = time.time()
        self.fps_start = time.time()
        self.fps_cnt = 0
        self.fps = 0

    def __change_speed(self, speed):
        self.labelSpeed.setText(str(speed))
        td = timedelta(seconds=time.time() - self.start_time)
        self.labelUptime.setText(str(td))

    def __change_top_left_image(self, img):
        self.topLeftLabel.setPixmap(utils.cv_to_qt_image(img))
        if self.fps_cnt > 20:
            self.fps = round(self.fps / self.fps_cnt)
            self.labelFps.setText(str(self.fps))
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

    def start(self):
        self.start_time = time.time()
        self.worker.start_work()

    def stop(self):
        self.worker.stop_work()

    def make_template(self):
        self.worker.make_template()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    window = SimilarityApp()
    window.show()
    splash.finish(window)

    app.exec()
