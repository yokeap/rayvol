from app import create_app
# from flask_socketio import SocketIO

app = create_app()
app.run(host='0.0.0.0', port=5000, debug=False)
