from platform import release
from tkinter import E
import cv2
from threading import Thread
import datetime
import time
import os
import json
from sys import platform

class Camera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        time.sleep(1)
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        # self.config = config
        # self.setConfigDefault(self.config)
        self.is_feeding = None
        self.is_socketConnecting = None

        # reading a single frame  for initializing 
        self.ret, self.frame = self.cap.read()
        if self.ret is False :
            print('[Exiting] No more frames to read')
            exit(0)

        self.stopped = True
            
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        
    def __del__(self):
        self.cap.release()

    # def setConfig(self, config):
    #     if not self.cap.isOpened():
    #         raise IOError("Cannot open webcam")
    #     self.cap.set(cv2.CAP_PROP_EXPOSURE, config['exposure'])
    #     self.cap.set(cv2.CAP_PROP_BRIGHTNESS, config['brightness'])
    #     self.cap.set(cv2.CAP_PROP_CONTRAST, config['contrast'])
    #     self.cap.set(cv2.CAP_PROP_HUE, config['hue'])
    #     self.cap.set(cv2.CAP_PROP_SATURATION, config['saturation'])
    #     self.cap.set(cv2.CAP_PROP_SHARPNESS, config['sharpness'])

    # start thread 
    def start(self):
        self.stopped = False
        self.t.start()

    def update(self):
        while True:
            try:
                if self.stopped is True :
                    break
                self.ret, self.frame = self.cap.read()
                if self.ret is False :
                    print('[Error] No more frames to read')
                    exit(0)

            except Exception as e:
                print("Error has been occured in gen_frame: ",e)
                break
        self.cap.release()

    def set_initial_config(self, config):
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['height'])

        if platform == "linux" or platform == "linux2":
            self.set_manual_exposure(0, config['exposure'])

        elif platform == "darwin":
            self.set_manual_exposure(0, config['exposure'])

        elif platform == "win32":
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, -1)  # manual mode
            self.cap.set(cv2.CAP_PROP_EXPOSURE, config['exposure'])

        self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)  # manual mode
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, config['brightness'])
        self.cap.set(cv2.CAP_PROP_CONTRAST, config['contrast'])
        self.cap.set(cv2.CAP_PROP_HUE, config['hue'])
        self.cap.set(cv2.CAP_PROP_SATURATION, config['saturation'])
        self.cap.set(cv2.CAP_PROP_SHARPNESS, config['sharpness'])

        return True

    def set_config(self, config):
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        self.cap.set(cv2.CAP_PROP_EXPOSURE, config['exposure'])
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, config['brightness'])
        self.cap.set(cv2.CAP_PROP_CONTRAST, config['contrast'])
        self.cap.set(cv2.CAP_PROP_HUE, config['hue'])
        self.cap.set(cv2.CAP_PROP_SATURATION, config['saturation'])
        self.cap.set(cv2.CAP_PROP_SHARPNESS, config['sharpness'])
        return True

    def get_config(self):
        objJson = {}
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        objJson['width'] = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        objJson['height'] = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        objJson['exposure'] = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        objJson['brightness'] = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
        objJson['contrast'] = self.cap.get(cv2.CAP_PROP_CONTRAST)
        objJson['hue'] = self.cap.get(cv2.CAP_PROP_HUE)
        objJson['saturation'] = self.cap.get(cv2.CAP_PROP_SATURATION)
        objJson['sharpness'] = self.cap.get(cv2.CAP_PROP_SHARPNESS)
        return objJson

    def set_manual_exposure(self, dev_video_id, exposure_time):
        commands = [
            ("v4l2-ctl --device /dev/video"+str(dev_video_id)+" -c exposure_auto=3"),
            ("v4l2-ctl --device /dev/video"+str(dev_video_id)+" -c exposure_auto=1"),
            ("v4l2-ctl --device /dev/video"+str(dev_video_id)+" -c exposure_absolute="+str(exposure_time))
        ]
        for c in commands: 
            print(c)
            os.system(c)

    # return latest read frame 
    def read(self):
        return self.frame

    # stopped reading frames 
    def stopped(self):
        self.stopped = True