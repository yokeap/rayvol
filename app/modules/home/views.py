from tkinter import Frame
from flask import session, render_template, redirect, url_for, Response
from app.modules.home import home_blu
# from app.utils import camera
# from app.utils.camera import Camera
from app.utils.streamer import Streamer


# import namespace from app root (__init__.py)
from app import socketio
from app import rayvol

# @home_blu.route('/')
# def index():
#     return 'Hello, World!'

# raw_stream = Streamer(rayvol.get_raw_frame)

@home_blu.route('/')
def index():
    # bar = create_plot()
    return render_template('index.html')

@home_blu.route('/raw_feed')
def raw_feed():
    rayvol.raw_stream_enable = True
    return Response(rayvol.raw_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")
    

# @home_blu.route('/segment_crop_feed')
# def imgsegentedcrop():
#     return Response(camera.segmented_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @home_blu.route('/roi_feed')
# def imgsegentedcrop():
#     return Response(camera.segmented_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def connect_event():
    print('socket has been connected')

@socketio.on('my event')
def my_event_handle(message):
    print(message)