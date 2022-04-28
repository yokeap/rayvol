from flask import session, render_template, redirect, url_for, Response
import json

from numpy import False_

# import namespace from app root (__init__.py)
from app import socketio
# from app.utils import rayvol
from app import rayvol

@socketio.on('home-connect')
def connect_event(message):
    print('home has been connected')
    rayvol.start_process_image()
    # socketio.emit('m')    
    # send out config loaded to html
    rayvol.is_socketConnecting = True
    rayvol.set_feed_status('realtime')
    rayvol.obj_stream_enable = True
    rayvol.obj_hsv_stream_enable = True
    rayvol.shadow_stream_enable = True
    rayvol.skeleton_stream_enable = True
    socketio.emit('data-home-params', json.dumps(rayvol.get_params_home()))

@socketio.on('disconnect')
def disconnect_event():
    # rayvol.threadGenFrames.stop()
    rayvol.is_socketConnecting = False
    rayvol.config_hsv_enable = False
    rayvol.obj_stream_enable = False
    rayvol.shadow_stream_enable = False
    rayvol.skeleton_stream_enable = False
    rayvol.__del__()
    print('socket has been disconnected')

@socketio.on('get-data')
def get_data_handle(message):
    if message['message'] == 'process-data':
        objJson = {
            'subtractTreshVal': rayvol.subtractTreshVal
        }
        socketio.emit('data-process', json.dumps(objJson))
    if message['message'] == 'get-config':
        print('get config')

@socketio.on('feed-status')
def feed_status_handle(message):
    pyObj = json.loads(message) 
    rayvol.set_feed_status(str(pyObj['feedStatus']))
    print("main streaming has been changed to ", pyObj['feedStatus'])

@socketio.on('process-value')
def process_value_handle(jsonData):
    pyObj = json.loads(jsonData)
    rayvol.subtractTreshVal = int(pyObj['subtractTreshVal'])

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
        rayvol.capture_all(pyObj['sample_number'])
        print("All data have been captured")

@socketio.on('save-params')
def save_config_handle(jsonData):
    pyObj = json.loads(jsonData)
    if pyObj['saveParams'] == True:
        rayvol.save_config()
        print("config has been saved")