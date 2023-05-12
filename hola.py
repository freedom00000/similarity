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
        self._speed = [0] * 5
        self._speed_cnt = 0
        self.speed_no_changes_cnt = 0
        self.prev_time = datetime.now()

    @property
    def speed(self):
        return round(statistics.fmean(self._speed), 1)

    @speed.setter
    def speed(self, value):
        self._speed[self._speed_cnt] = value
        self._speed_cnt = self._speed_cnt + 1 if self._speed_cnt < len(self._speed) - 1 else 0

    @thread
    def __listener_loop(self, event):
        self.hola.write(b'a')
        while self.hola.isOpen():
            size = self.hola.inWaiting()
            if size:
                data = self.hola.read(size)
                if data == b'#':
                    now = datetime.now()
                    self.speed = 500.0 / (now - self.prev_time).total_seconds()
                    self.prev_time = now
                    self.speed_no_changes_cnt = 0
                    event()
            else:
                self.speed_no_changes_cnt += 1
                if self.speed_no_changes_cnt > self.MAX_SPEED_NO_CHANGES:
                    self.speed = 0

    def start(self, event):
        self.__listener_loop(event)

    def stop(self):
        self.hola.write(b'a')
        self.hola.close()


def test():
    print(hola.speed)


if __name__ == "__main__":
    hola = Hola()
    hola.start(test)
