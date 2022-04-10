from flask import session, render_template, redirect, url_for, Response

# import namespace from app root (__init__.py)
from app import socketio
from app import rayvol

@socketio.on('connect')
def connect_event():
    print('socket has been connected')

@socketio.on('my event')
def my_event_handle(message):
    print(message)