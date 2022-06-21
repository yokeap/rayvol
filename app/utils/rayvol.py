from operator import length_hint
from this import d
from app.utils.camera import Camera
from app.utils.streamer import Streamer
from app.utils import segmentation
from app.utils import reconstruct
import cv2
from threading import Thread
import datetime
import time
import os
import json
from sys import platform
import numpy as np
import math
from jsonmerge import merge

class Rayvol(object):
    def __init__(self, socket, config, offline):
        self.config = config
        self.socket = socket
        self.offline = offline
        # self.setConfigDefault(self.config)
        # self.config = config
        # self.imageDiffBinThreshold = self.config["imageDiffBinTreshold"]

        self.objReconstruct = reconstruct.reconstruct(1, config)

        if self.offline == False:
            self.camera = Camera()
        # self.raw_stream = Streamer()

        time.sleep(1)
        self.set_camera_init_config()
        time.sleep(1)

        self.raw_frame = None
        self.raw_stream_enable = False
        self.obj_stream_enable = False
        self.obj_hsv_stream_enable = False
        self.shadow_stream_enable = False
        self.skeleton_stream_enable = False
        self.config_stream_enable = False
        self.config_hsv_enable = False
        self.imgBg = cv2.cvtColor(cv2.imread("./app/ref/background_400.jpg"), cv2.COLOR_BGR2GRAY)
        self.feedStatus = 'realtime'
        self.is_socketConnecting = None
        self.stopped_process_image = None
        self.subtractTreshVal = self.config['imgDiffBinTreshold']
        # self.objHue = config["hue"]
        # self.objSaturation = config["saturation"]
        # self.objValue = config["value"]

        # self.camera_start()

        self.intrinsic_matrix = np.array(self.config["intrinsicMatrix"])
        self.distortion_coefficient = np.array(self.config["distortionCoe"])

        self.thread_process_image = Thread(target=self.process_image, daemon=True, args=())

    def __del__(self):
        print('delete')
        # self.camera.release()

    def set_camera_init_config(self):
        if self.offline == False:
            self.camera.set_initial_config(self.config)
    
    def read_config(self):
        # load config
        with open('./config.json', 'r') as f:
            self.config = json.load(f)
        ret = self.camera_set_initial_config(self.config)
        return ret

    def get_params_home(self):
        objJson= {
            'subtractTreshVal': self.subtractTreshVal
        }
        return objJson

    def get_config(self):
        objJson = self.camera.get_config()
        # self.socket.emit('data-config-params', json.dumps(objJson))
        return objJson

    # save_config is used for both home and config
    def save_config(self):
        objJson = self.camera.get_config()
        self.config['imgDiffBinTreshold'] = self.subtractTreshVal
        result = merge(self.config, objJson)
        with open('./config.json', 'w') as f:
            json.dump(result, f)

    def camera_start(self):
        if self.offline == False:
            self.camera.start()

    def camera_stop(self):
        self.camera.stop()

    def camera_set_config(self, config):
        ret = self.camera.set_config(config)
        return True

    def start_process_image(self):
        self.imgBg = cv2.cvtColor(cv2.imread("./app/ref/background_400.jpg"), cv2.COLOR_BGR2GRAY)
        if self.offline == False:
            self.stopped_process_image = False
            if not self.thread_process_image.is_alive():
                self.thread_process_image.start()
                print("thread process image has been started")

    def stop_process_image(self):
        self.stopped_process_image = True

    def set_feed_status(self, status='realtime'):
        print(status)
        if status == 'realtime':
            self.stopped_process_image = False
            print('realtime')
        if status == 'shot':
            self.stopped_process_image = True

    def capture_background(self):
        # now = datetime.datetime.now()
        p = os.path.sep.join(
            ['./app/ref', "background_400.jpg"])
        print(p)
        raw_frame = cv2.undistort(self.camera.read(), self.intrinsic_matrix, self.distortion_coefficient, None)
        cv2.imwrite(p, raw_frame)

    def capture_all(self, sample_number):
        now = datetime.datetime.now()
        p = os.path.sep.join(
            ['./app/capture', sample_number + "_{}".format(str(now).replace(":", ''))])
        try:
            os.makedirs(p)
        except OSError as error:
            print(error)
        text = sample_number + ", " + str(self.volume) + "cm^3" + ", " + str(round(self.length, 2)) + ", " + str(round(self.width, 2)) + ", " + str(round(self.height, 2))
        # raw_with_measured = self.raw_frame.copy()
        raw_frame = cv2.undistort(self.camera.read(), self.intrinsic_matrix, self.distortion_coefficient, None)
        cv2.putText(self.overlay_frame, text, (80, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imwrite(os.path.join(p, "imageraw.jpg"), raw_frame )
        cv2.imwrite(os.path.join(p, "imageraw_overlay.jpg"), self.overlay_frame)
        cv2.imwrite(os.path.join(p, "imagediff.jpg"), self.imageDiff)
        cv2.imwrite(os.path.join(p, "imagediffbin.jpg"), self.imageDiffBin)
        cv2.imwrite(os.path.join(p, "imagediffmorph.jpg"), self.imageDiffMorph)
        with open(os.path.join(p, "process_data.json"), 'w') as f:
            objJson = {
                'subtractTreshVal': self.subtractTreshVal,
                'crop': self.posCrop[0],
                'imageObjHSV': self.objHsvRange,
            }
            json.dump(objJson, f)
        with open(os.path.join(p, "camera_params.json"), 'w') as f:
            objJson = self.camera.get_config()
            json.dump(objJson, f)
        try:
            cv2.imwrite(os.path.join(p, "iamgeroi.jpg"),  self.imageROI[0])
            cv2.imwrite(os.path.join(p, "iamgeObj.jpg"), self.imageObj)
            cv2.imwrite(os.path.join(p, "imageshadow.jpg"), self.imageShadow)
            cv2.imwrite(os.path.join(p, "imageskeleton.jpg"), self.imageSkeleton)
            
            with open(os.path.join(p, "reconstruct.json"), 'w') as f:
                json.dump(self.objJson, f)

            objJson = {
                'volume': self.objJson["volume"],
                "length": self.objJson["length"],
                "width": self.objJson["width"],
                "height": self.objJson["height"],
                "computeTime": self.objJson["computeTime"]
            }
            with open(os.path.join(p, "result_" + sample_number + ".json"), 'w') as f:
                json.dump(objJson , f)
        except:
            pass

    def process_image(self):
        while True:
            try:         
                if self.stopped_process_image == True:
                    pass
                else:
                    start_time = time.time()
                    # self.raw_frame = self.camera.read()
                    self.raw_frame = cv2.undistort(self.camera.read(), self.intrinsic_matrix, self.distortion_coefficient, None)
                    self.overlay_frame = self.overlay_lightsource_projection(self.raw_frame)
                    self.overlay_frame = self.overlay_measure_area(self.overlay_frame)
                    self.imageDiff =  cv2.absdiff(cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2GRAY), self.imgBg)
                    ret, self.imageDiffBin = cv2.threshold(
                                self.imageDiff, 5, 255, cv2.THRESH_BINARY)
                    self.imageDiffMorph = cv2.morphologyEx(
                                self.imageDiffBin, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(7,7)))
                    self.imageROI, self.posCrop = segmentation.singleObjShadow(self.raw_frame, self.imageDiffMorph)
                    self.imageObjColor, self.imageObj, self.imageShadow, self.imageSkeleton, self.objHsvRange = segmentation.obj_shadow_skeleton(self.imageROI[0])
                    # self.imageObjColor, self.imageObj, self.imageShadow, self.imageSkeleton, self.objHsvRange = segmentation.shadow_obj_skeleton(self.imageROI[0])
                    self.objReconstruct.reconstruct(self.raw_frame, self.imageObj, self.imageSkeleton, self.imageShadow, self.posCrop )
                    ptCloud, self.volume, self.length, self.width, self.height = self.objReconstruct.reconstructVolume(0.05)
                    end_time = time.time()
                    if self.is_socketConnecting == True:
                        self.objJson = {
                            "ptCloud" : {
                                "x": ptCloud[:, 0].tolist(),
                                "y": ptCloud[:, 1].tolist(),
                                "z": ptCloud[:, 2].tolist(),
                            },
                            "volume": self.volume,
                            "length": self.length,
                            "width": self.width,
                            "height": self.height,
                            "computeTime": (end_time - start_time)
                        }
                        self.socket.emit('reconstruction-data', json.dumps(self.objJson))
                    # process_time = end_time - start_time
                    # if process_time < 0.03 :
                    #     # print(0.03-process_time)
                    #     time.sleep(0.03-process_time)
            except Exception as e:
                print("process image error: ", e)
                pass

    def stop_process_image(self):
        self.stopped_process_image = True

    def get_raw_frame(self):
        return self.camera.read()
        
    def get_hsv(self, imageHSV):
        objJson = {}
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
            try:
                yield (self.msg_image_gen(self.overlay_frame))
                prefix = "\r\n"
                # time.sleep(1 / 30)
            except Exception as e:
                # print(e)
                pass

    def obj_stream(self):
        while self.obj_stream_enable == True:
            # msg, jpeg_bytes = self.msg_image_gen(self.raw_frame)
            try:
                if self.obj_hsv_stream_enable == True:
                    objJson = self.get_hsv(self.imageObjColor)
                    self.socket.emit('hsv-obj-data', json.dumps(objJson))
                yield (self.msg_image_gen(self.imageObj))
                prefix = "\r\n"
            except Exception as e:
                print(e)
                pass
            time.sleep(1 / 30)

    def shadow_stream(self):
        while self.shadow_stream_enable == True:
            # msg, jpeg_bytes = self.msg_image_gen(self.raw_frame)
            try:
                yield (self.msg_image_gen(self.imageShadow))
                prefix = "\r\n"
                # time.sleep(1 / 30)
            except Exception as e:
                # print(e)
                pass

    def skeleton_stream(self):
        while self.skeleton_stream_enable == True:
            # msg, jpeg_bytes = self.msg_image_gen(self.raw_frame)
            try:
                yield (self.msg_image_gen(self.imageSkeleton))
                prefix = "\r\n"
                # time.sleep(1 / 30)
            except Exception as e:
                # print(e)
                pass

    def config_stream(self):
        while self.config_stream_enable == True:
            raw_frame = self.camera.read()
            raw_frame = cv2.undistort(raw_frame, self.intrinsic_matrix, self.distortion_coefficient, None)
            if self.config_hsv_enable == True:
                imageHSV = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2HSV_FULL)
                objJson = self.get_hsv(imageHSV)
                self.socket.emit('hsv-config-data', json.dumps(objJson))
            overlay_raw_frame = self.overlay_measure_area(raw_frame)
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

    def overlay_lightsource_projection(self, image):
        # image + light source position with some offset
        lightsource_offset = [int(abs(self.config["virLightPosImg"][1])), image.shape[1] - int(self.config["virLightPosImg"][0])]
        # full_image is image + lightsource origin
        full_image = np.zeros((image.shape[0] + abs(lightsource_offset[0]), image.shape[1], 3), np.uint8)

        # overlay input image with fullimage
        height, width, channels = full_image.shape 
        full_image[lightsource_offset[0]:lightsource_offset[0]+height] = image

        cv2.line(full_image , (lightsource_offset[1] , 0), (lightsource_offset[1], height), (255, 0, 0), 2)

        length = 5000

        ref_line_angle = 90
        step = 10
        angle = 0

        for i in range(5):
            angle = step + angle
            p2 = [int(lightsource_offset[1] + length * math.cos((ref_line_angle - angle) * math.pi / 180.0)), int(lightsource_offset[0] + length * math.sin((ref_line_angle - angle) * math.pi / 180.0))]
            cv2.line(full_image , (lightsource_offset[1] , 0), (p2[0], p2[1]), (255, 0, 0), 1)
            p3 = [int(lightsource_offset[1] + length * math.cos((ref_line_angle + angle) * math.pi / 180.0)), int(lightsource_offset[0] + length * math.sin((ref_line_angle + angle) * math.pi / 180.0))]
            cv2.line(full_image , (lightsource_offset[1] , 0), (p3[0], p3[1]), (255, 0, 0), 1)

        crop_image = full_image[lightsource_offset[0]:lightsource_offset[0]+height, 0:image.shape[1]]

        return crop_image

    def overlay_measure_area(self, image):
        overlay_image = image
        cv2.circle(overlay_image ,(159, 96), 10, (0,0,255), -1)
        cv2.circle(overlay_image ,(1041, 100), 10, (0,0,255), -1)
        cv2.circle(overlay_image ,(148, 807), 10, (0,0,255), -1)
        cv2.circle(overlay_image ,(1054, 803), 10, (0,0,255), -1)
        return overlay_image