from this import d
from app.utils.camera import Camera
from app.utils.streamer import Streamer
from app.utils import segmentation
import cv2
from threading import Thread
import datetime
import time
import json
import os
import numpy as np

class Rayvol(object):
    def __init__(self, socket, config):
        self.config = config
        self.socket = socket
        # self.setConfigDefault(self.config)
        # self.config = config
        # self.imageDiffBinThreshold = self.config["imageDiffBinTreshold"]

        self.camera = Camera()
        # self.raw_stream = Streamer()
        self.raw_frame = None
        self.raw_stream_enable = False
        self.config_stream_enable = False
        self.config_hsv_enable = False
        # self.imgBg = cv2.cvtColor(cv2.imread("./ref/background.jpg"), cv2.COLOR_BGR2GRAY)
        self.is_feeding = None
        self.is_socketConnecting = None
        self.stopped_process_image = None
        self.thread_process_image = Thread(target=self.process_image, daemon=True, args=())
        self.subtractTreshVal = 1
        # self.objHue = config["hue"]
        # self.objSaturation = config["saturation"]
        # self.objValue = config["value"]

        # self.camera_set_config(config)

    def __del__(self):
        print('delete')
        # self.camera.release()
        
    def read_config(self):
        # load config
        with open('./config.json', 'r') as f:
            self.config = json.load(f)
        ret = self.camera_set_initial_config(self.config)
        return ret

    def get_config(self):
        objJson = self.camera.get_config()
        self.socket.emit('data-config-params', json.dumps(objJson))

    def save_config(self):
        with open('./config.json', 'w') as f:
            json.dump(self.config, f)

    def camera_start(self):
        self.camera.start()

    def camera_stop(self):
        self.camera.stop()

    def camera_set_config(self, config):
        ret = self.camera.set_config(config)
        return True

    def start_process_image(self):
        self.stopped_process_image = False
        self.thread_process_image.start()

    def capture_all(self):
        if not self.camera.isOpened():
            raise IOError("Cannot open webcam")
        now = datetime.datetime.now()
        p = os.path.sep.join(
            ['./capture/', "{}".format(str(now).replace(":", ''))])
        try:
            os.mkdir(p)
        except OSError as error:
            pass
        cv2.imwrite(os.path.join(p, "imageraw.jpg"), self.raw_frame)
        cv2.imwrite(os.path.join(p, "imagediff.jpg"), self.imageDiff)
        cv2.imwrite(os.path.join(p, "imagediffbin.jpg"), self.imageDiffBin)
        cv2.imwrite(os.path.join(p, "imagediffmorph"), self.imageDiffMorph)
        try:
            cv2.imwrite(os.path.join(p, "iamgeroi.jpg"),  self.imageROI[0])
            cv2.imwrite(os.path.join(p, "iamgeObj.jpg"), self.self.imageObj)
            cv2.imwrite(os.path.join(p, "imageshadow.jpg"), self.imageShadow)
            cv2.imwrite(os.path.join(p, "imageskeleton.jpg"), self.imageSkeleton)
            with open(os.path.join(p, "reconstruct.json"), 'w') as f:
                json.dump(self.objJson, f)
        except:
            pass

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
                    # self.imageObj, self.imageShadow, self.imageSkeleton = segmentation.obj_shadow_skeleton(self.imgROI[0])
            except Exception as e:
                print(e)

    def stop_process_image(self):
        self.stopped_process_image = True

    def get_raw_frame(self):
        return self.camera.read()
        
    def get_hsv(self, image):
        objJson = {}
        imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
        h, s, v = imageHSV[:,:,0], imageHSV[:,:,1], imageHSV[:,:,2]
        h = np.transpose(cv2.calcHist([h],[0],None,[360],[0,360]))
        s = np.transpose(cv2.calcHist([s],[0],None,[256],[0,256]))
        v = np.transpose(cv2.calcHist([v],[0],None,[256],[0,256]))
        objJson['hist_h'] = h.tolist()
        objJson['hist_h_ymax'] = (np.mean(h) + 0.5 * np.std(h)).tolist()
        objJson['hist_s'] = s.tolist()
        objJson['hist_s_ymax'] = (np.mean(h) + 0.5 * np.std(h)).tolist()
        objJson['hist_v'] = v.tolist()
        objJson['hist_v_ymax'] = (np.mean(h) + 0.5 * np.std(h)).tolist()
        return objJson

    def raw_stream(self):
        while self.raw_stream_enable == True:
            # msg, jpeg_bytes = self.msg_image_gen(self.raw_frame)
            yield (self.msg_image_gen(self.camera.read()))
            prefix = "\r\n"
            # time.sleep(1 / 30)

    def config_stream(self):
        while self.config_stream_enable == True:
            raw_frame = self.camera.read()
            if self.config_hsv_enable == True:
                objJson = self.get_hsv(raw_frame)
                self.socket.emit('hsv-config-data', json.dumps(objJson))
            yield (self.msg_image_gen(raw_frame))
            prefix = "\r\n"
            time.sleep(1 / 30)

    def msg_image_gen(self, image):
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        """Encodes the OpenCV image to a 1280x720 image"""
        _, jpeg = cv2.imencode(".jpg", image, params=(cv2.IMWRITE_JPEG_QUALITY, 70),
        )
        jpeg_bytes = jpeg.tobytes()

        msg = (
            prefix
            + header
            + "Content-Length: {}\r\n\r\n".format(len(jpeg_bytes))
        )
        return msg.encode("utf-8") + jpeg_bytes
