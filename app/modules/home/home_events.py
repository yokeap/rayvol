from flask import session, render_template, redirect, url_for, Response
import json

# import namespace from app root (__init__.py)
from app import socketio
# from app.utils import rayvol
# from app import rayvol

@socketio.on('connect')
def connect_event(message):
    print('some client has been connected')
    # socketio.emit('m')    
    # send out config loaded to html
    # rayvol.is_socketConnecting = True

# @socketio.on('disconnect')
# def disconnect_event():
#     # rayvol.threadGenFrames.stop()
#     # rayvol.is_socketConnecting = False
#     print('socket has been disconnected')

@socketio.on('get-data')
def get_data_handle(message):
    if message['message'] == 'get-image-process-data':
        print('get image process data')
    if message['message'] == 'get-config':
        print('get config')

@socketio.on('feed-status')
def feed_status_handle(message):
    pyObj = json.loads(message) 
    # rayvol.feedStatus = pyObj["feedStatus"]
    print("main streaming has been changed to ", pyObj["feedStatus"])

@socketio.on('process-value')
def process_value_handle(jsonData):
    pyObj = json.loads(jsonData)
    # rayvol.subtractTreshVal = int(pyObj['subtractTreshVal'])

@socketio.on('slider-obj-hsv')
def slider_obj_hsv_event(jsonData):
    pyObj = json.loads(jsonData)
    # rayvol.objHue = pyObj["hue"]
    # rayvol.objSaturation = pyObj["saturation"]
    # rayvol.objValue = pyObj["value"]

@socketio.on('capture')
def capture_handle(jsonData):
    pyObj = json.loads(jsonData)
    if pyObj['capture'] == True:
        # rayvol.capture()
        print("All data have been captured")

@socketio.on('save-params')
def save_config_handle(jsonData):
    pyObj = json.loads(jsonData)
    if pyObj['saveParams'] == True:
        # rayvol.save_config()
        print("config has been saved")