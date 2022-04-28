from flask import session, render_template, redirect, url_for, Response
import json

# import namespace from app root (__init__.py)
from app import socketio
# from app.utils import rayvol
from app import rayvol

@socketio.on('config-connect')
def config_connect_event(message):
    print('config has been connected')    
    rayvol.config_hsv_enable = True
    # send out config loaded to html
    rayvol.is_socketConnecting = True
    socketio.emit('data-config-params', json.dumps(rayvol.get_config()))

@socketio.on('capture-background')
def capture_handle(jsonData):
    pyObj = json.loads(jsonData)
    if pyObj['capture'] == True:
        rayvol.capture_background()
        print("background image is captured")

@socketio.on('save-config')
def save_config_handle(jsonData):
    pyObj = json.loads(jsonData)
    if pyObj['saveConfigs'] == True:
        rayvol.save_config()
        print("config has been saved")

@socketio.on('config-value')
def config_value_handle(jsonData):
    pyObj = json.loads(jsonData)
    print(pyObj)
    rayvol.camera_set_config(pyObj)
