import threading

import cv2
from PyQt6.QtGui import QImage, QPixmap


def thread(fn):
    def execute(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.start()
        return t

    return execute


def show(img, name='image', delay=0):
    cv2.imshow(name, resize_image(img))
    cv2.waitKey(delay)


def resize_image(img, scale=60):
    width = int(img.shape[1] * scale / 100)
    height = int(img.shape[0] * scale / 100)
    dim = (width, height)

    # resize image
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized


def cv_to_qt_image(img):
    convert = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format.Format_BGR888)
    return QPixmap.fromImage(convert)
