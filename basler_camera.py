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


            # setup center scan line
            self.cam.Height = self.cam.Height.Max
            self.cam.Width = self.cam.Width.Max
            self.cam.CenterX = True
            self.cam.CenterY = True

            # setup for
            # self.cam.PixelFormat = "BGR8"
            # self.cam.Gain = 20
            self.cam.ExposureTimeAbs = 20000
        except Exception as e:
            print(e)

        self.is_grubbed = False

    @thread
    def start_grubbing(self, event):
        self.is_grubbed = True
        self.cam.Open()

        self.cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        converter = pylon.ImageFormatConverter()

        # converting to opencv bgr format
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        while self.is_grubbed:
            grab_result = self.cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grab_result.GrabSucceeded():
                # Access the image data
                image = converter.Convert(grab_result)
                img = image.GetArray()
                event(img)
            grab_result.Release()

        # Releasing the resource
        self.cam.StopGrabbing()

    def stop_grubbing(self):
        self.cam.Close()
        self.is_grubbed = False