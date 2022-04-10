import time
import cv2
from threading import Thread
from flask import Flask, Response, render_template, request

class Streamer(object):
    def __init__(self, obj_stream):
        # Thread.__init__(self)
        # self.route = route
        # self.thread = None
        self.is_streaming = None
        self.obj_stream = obj_stream
        # self.port = 9000
        # self.flask_name = "{}_{}".format(__name__, self.port)
        # self.flask = Flask(self.flask_name)
        # self.blueprint = blueprint
        self.frame_rate = 30

    def gen(self):
        """A generator for the image."""
        self.is_streaming = True
        header = "--jpgboundary\r\nContent-Type: image/jpeg\r\n"
        prefix = ""
        while True:
            """Encodes the OpenCV image to a 1280x720 image"""
            _, jpeg = cv2.imencode(".jpg", self.obj_stream, params=(cv2.IMWRITE_JPEG_QUALITY, 70),
            )
            jpeg_bytes = jpeg.tobytes()

            msg = (
                prefix
                + header
                + "Content-Length: {}\r\n\r\n".format(len(jpeg_bytes))
            )

            yield (msg.encode("utf-8") + jpeg_bytes)
            prefix = "\r\n"
            # time.sleep(1 / self.frame_rate)
