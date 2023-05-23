import time
from datetime import datetime
import statistics
import serial

from utils import thread


class Hola:
    PORT = 'COM3'
    BAUD_RATE = 9600
    MAX_SPEED_NO_CHANGES = 200

    def __init__(self):
        self.hola = serial.Serial(port=self.PORT, baudrate=self.BAUD_RATE)

        self.red_state = True
        self.green_state = True
        self.zoomer_state = True

        self.switch_red_light()
        self.switch_green_light()
        self.switch_zoomer()

        self._speed = [0] * 5
        self._speed_cnt = 0
        self.speed_no_changes_cnt = 0
        self.prev_time = datetime.now()

    @property
    def speed(self):
        val = round(statistics.fmean(self._speed), 1)
        return val

    @speed.setter
    def speed(self, value):
        self._speed.pop(0)
        self._speed.append(value)
        # self._speed_cnt = self._speed_cnt + 1 if self._speed_cnt < len(self._speed) - 1 else 0

    @thread
    def __listener_loop(self, event):
        self.hola.write(b'a')
        while self.hola.isOpen():
            size = self.hola.inWaiting()
            if size:
                data = self.hola.read(size)
                if b'#' in data:
                    now = datetime.now()
                    self.speed = 500.0 / (now - self.prev_time).total_seconds()
                    self.prev_time = now
                    # print(datetime.now(), self._speed, self.speed_no_changes_cnt)
                    self.speed_no_changes_cnt = 0
                    event()
            else:
                self.speed_no_changes_cnt += 1
                if self.speed_no_changes_cnt > self.MAX_SPEED_NO_CHANGES:
                    self.speed = 0
            time.sleep(0.01)

    def start(self, event):
        if not self.hola.isOpen():
            self.hola.open()
        self.__listener_loop(event)

    def stop(self):
        # self.hola.write(b'a')
        self.hola.close()

    def switch_red_light(self):
        self.red_state = not self.red_state
        self.hola.write(b'R' if self.red_state else b'r')

    def switch_green_light(self):
        self.green_state = not self.green_state
        self.hola.write(b'G' if self.green_state else b'g')

    def switch_zoomer(self):
        self.zoomer_state = not self.zoomer_state
        self.hola.write(b'B' if self.zoomer_state else b'b')


def test():
    print(hola.speed)


if __name__ == "__main__":
    hola = Hola()
    hola.start(test)
