from this import d
from app.utils.camera import Camera
from app.utils.streamer import Streamer
from app.utils import segmentation
import cv2
from threading import Thread
import datetime
import time

class Rayvol(object):
    def __init__(self):
        # self.config = config
        # self.setConfigDefault(self.config)
        # self.config = config
        # self.imageDiffBinThreshold = self.config["imageDiffBinTreshold"]

        self.camera = Camera()
        # self.raw_stream = Streamer()
        self.raw_frame = None
        self.raw_stream_enable = False
        # self.imgBg = cv2.cvtColor(cv2.imread("./ref/background.jpg"), cv2.COLOR_BGR2GRAY)
        self.is_feeding = None
        self.is_socketConnecting = None
        self.stopped_process_image = None
        self.thread_process_image = Thread(target=self.process_image, daemon=True, args=())

    def __del__(self):
        pass

    def start_camera(self):
        self.camera.start()

    def stop_camera(self):
        self.camera.stop()

    def start_process_image(self):
        self.stopped_process_image = False
        self.thread_process_image.start()

    def process_image(self):
        while True :
            try:
                if self.stopped_process_image == True:
                    break
                else:
                    self.raw_frame = self.camera.read()
                    # self.imageDiff =  cv2.absdiff(cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY), self.imgBg)
                    # ret, self.imageDiffBin = cv2.threshold(
                    #             self.imageDiff, self.imageDiffBinThreshold, 255, cv2.THRESH_BINARY)
                    # self.imageDiffMorph = cv2.morphologyEx(
                    #             self.imageDiffBin, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(7,7)))
                    # self.imageROI, self.posCrop = segmentation.singleObjShadow(raw_frame, self.imageDiffMorph)
                    # self.imgObj, self.imgShadow, self.imgSkeleton = segmentation.obj_shadow_skeleton(self.imgROI[0])
            except Exception as e:
                print(e)

    def get_raw_frame(self):
        return self.raw_frame

    def stop_process_image(self):
        self.stopped_process_image = True

    def raw_stream(self):
        while self.raw_stream_enable == True:
            # msg, jpeg_bytes = self.msg_image_gen(self.raw_frame)
            yield (self.msg_image_gen(self.raw_frame))
            prefix = "\r\n"
            # time.sleep(1 / 30)

    def msg_image_gen(self, image):
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        """Encodes the OpenCV image to a 1280x720 image"""
        _, jpeg = cv2.imencode(".jpg", self.raw_frame, params=(cv2.IMWRITE_JPEG_QUALITY, 70),
        )
        jpeg_bytes = jpeg.tobytes()

        msg = (
            prefix
            + header
            + "Content-Length: {}\r\n\r\n".format(len(jpeg_bytes))
        )
        return msg.encode("utf-8") + jpeg_bytes
