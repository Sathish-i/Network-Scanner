from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import re
import os
from datetime import datetime
import eventlet
from flask_socketio import SocketIO

# Patch for real-time WebSocket communication
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Validate IP address or domain name
def is_valid_input(value):
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    domain_pattern = r'^(?!-)([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}$'
    return re.match(ip_pattern, value) or re.match(domain_pattern, value)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/basic')
def basic_scan_page():
    return render_template('basic_scan.html')

@app.route('/start_basic_scan', methods=['POST'])
def start_basic_scan():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    whole_network = data.get('wholeNetwork', False)

    if not whole_network and not is_valid_input(ip):
        return jsonify({'message': 'Invalid input! Please enter a valid IP address or domain name.'}), 400

    scan_command = ['nmap', '-F', ip] if not whole_network else ['netdiscover', '-P']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f'static/scans/scan_{timestamp}.txt'

    try:
        with open(result_file, 'w') as output:
            subprocess.run(scan_command, stdout=output, stderr=subprocess.STDOUT, text=True)
        return jsonify({'message': 'Scan completed!', 'file': result_file})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/download_scan')
def download_scan():
    file_path = request.args.get('file')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'message': 'File not found'}), 404

@socketio.on('start_scan')
def handle_scan():
    try:
        process = subprocess.Popen(['netdiscover', '-P'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                socketio.emit('scan_output', {'data': line.strip()})
                eventlet.sleep(0.1)
    except Exception as e:
        socketio.emit('scan_output', {'data': f'Error: {str(e)}'})

if __name__ == '__main__':
    os.makedirs('static/scans', exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
