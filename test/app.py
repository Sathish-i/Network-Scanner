from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_scan')
def handle_scan():
    try:
        process = subprocess.Popen(['netdiscover', '-r', '192.168.1.0/24'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in iter(process.stdout.readline, ''):
            socketio.emit('scan_output', {'data': line.strip()})
    except Exception as e:
        socketio.emit('scan_output', {'data': f'Error: {str(e)}'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
