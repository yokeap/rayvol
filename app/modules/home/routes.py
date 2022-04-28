from flask import session, render_template, redirect, url_for, Response
from app.modules.home import home_blu

# import namespace from app root (__init__.py)
from app import socketio
from app import rayvol

@home_blu.route('/')
def index():
    # bar = create_plot()
    return render_template('index2.html')

@home_blu.route('/config')
def config():
    # bar = create_plot()
    return render_template('config.html')

@home_blu.route('/raw_feed')
def raw_feed():
    rayvol.raw_stream_enable = True
    rayvol.config_stream_enable = False
    return Response(rayvol.raw_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")

@home_blu.route('/image_obj_feed')
def obj_feed():
    rayvol.obj_stream_enable = True
    return Response(rayvol.obj_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")

@home_blu.route('/image_shadow_feed')
def shadow_feed():
    rayvol.shadow_stream_enable = True
    return Response(rayvol.shadow_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")

@home_blu.route('/image_skeleton_feed')
def skeleton_feed():
    rayvol.skeleton_stream_enable = True
    return Response(rayvol.skeleton_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")

@home_blu.route('/config_feed')
def config_feed():
    rayvol.raw_stream_enable = False
    rayvol.config_stream_enable = True
    return Response(rayvol.config_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")