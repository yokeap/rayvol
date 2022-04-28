import os
import json
from sys import platform


from flask import Flask
from flask_socketio import SocketIO
from app.utils.rayvol import Rayvol

socketio = SocketIO()

# load config
if platform == "linux" or platform == "linux2":
    with open('./app/setting_linux.json', 'r') as f:
        setting = json.load(f)

elif platform == "darwin":
    with open('./app/setting_osx.json', 'r') as f:
        setting = json.load(f)

elif platform == "win32":
    with open('./app/setting_win.json', 'r') as f:
        setting = json.load(f)

rayvol = Rayvol(socketio, setting, offline=False)

# rayvol.start_camera()
# rayvol.start_process_image()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_url_path="/", static_folder='./templates')
    app.config.from_mapping(
        SECRET_KEY='dev',

    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    from app.modules.home import home_blu
    app.register_blueprint(home_blu)

    socketio.init_app(app)

    # start capturing process
    rayvol.camera_start()

    return app
