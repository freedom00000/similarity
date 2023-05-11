import time

from pypylon import pylon

from utils import thread

CAM_RIGHT = "40056496"
CAM_LEFT = "40039401"


class BaslerCamera:
    def __init__(self, serial_number):
        info = pylon.DeviceInfo()
        info.SetSerialNumber(serial_number)
        try:
            self.cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
        except Exception as e:
            print(e)

        self.is_grubbed = False
        self.__open()

    def __open(self):
        self.cam.Open()
        # setup center scan line
        self.cam.Height = self.cam.Height.Max
        self.cam.Width = self.cam.Width.Max
        self.cam.CenterX = True
        self.cam.CenterY = True

        # setup for
        self.cam.ExposureAuto = 'Off'
        self.cam.ExposureTimeAbs = 1000
        self.cam.AcquisitionFrameRateEnable = True
        self.cam.AcquisitionFrameRateAbs = 55

        self.converter = pylon.ImageFormatConverter()
        # converting to opencv bgr format
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    @thread
    def start_grabbing(self, event):
        self.is_grubbed = True
        self.__open()
        self.cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        while self.is_grubbed:
            grab_result = self.cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grab_result.GrabSucceeded():
                # Access the image data
                image = self.converter.Convert(grab_result)
                img = image.GetArray()
                event(img)
            grab_result.Release()

        # Releasing the resource
        self.cam.StopGrabbing()

    @thread
    def grab(self, event, cnt=1):
        if not self.cam.IsOpen():
            self.__open()
        if not self.cam.IsGrabbing():
            self.cam.StartGrabbingMax(cnt)
        while self.cam.IsGrabbing():
            # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
            grab_result = self.cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grab_result.GrabSucceeded():
                image = self.converter.Convert(grab_result)
                img = image.GetArray()
                event(img)
            else:
                print("Error: ", grab_result.ErrorCode, grab_result.ErrorDescription)
            grab_result.Release()


    def stop_grabbing(self):
        self.cam.Close()
        self.is_grubbed = False


def kek(im):
    print('kek')


if __name__ == "__main__":
    cam = BaslerCamera(CAM_LEFT)
    for i in range(30):
        start = time.time()
        cam.grab(kek)
        print(time.time() - start)

    cam.stop_grabbing()
