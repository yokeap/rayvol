from flask import session, render_template, redirect, url_for, Response
from app.modules.home import home_blu

# import namespace from app root (__init__.py)
from app import socketio
from app import rayvol

@home_blu.route('/')
def index():
    # bar = create_plot()
    return render_template('index.html')

@home_blu.route('/raw_feed')
def raw_feed():
    rayvol.raw_stream_enable = True
    return Response(rayvol.raw_stream(), mimetype="multipart/x-mixed-replace; boundary=jpgboundary")