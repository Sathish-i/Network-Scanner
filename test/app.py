from flask import Flask, render_template
from flask_socketio import SocketIO
import subprocess
import eventlet

# Patch for real-time WebSocket communication
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_scan')
def handle_scan():
    try:
        process = subprocess.Popen(['netdiscover', '-P'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():  # Only send non-empty lines
                socketio.emit('scan_output', {'data': line.strip()})
                eventlet.sleep(0.1)  # Prevents blocking
    except Exception as e:
        socketio.emit('scan_output', {'data': f'Error: {str(e)}'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
