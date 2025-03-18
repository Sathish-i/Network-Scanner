from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO
from flask import send_from_directory
import subprocess
import eventlet
import re
import os

# Patch for real-time WebSocket communication
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

RESULT_FILE = "scan_results.txt"

# IP/Domain validation
def is_valid_ip_or_domain(value):
    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
    domain_pattern = r"^(?!-)(?:[a-zA-Z0-9-]{1,63}\.?)+(?:[a-zA-Z]{2,})$"
    return re.match(ip_pattern, value) or re.match(domain_pattern, value)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/css/index.css')
def static_files(index.css):
    return send_from_directory('static',index.css)

@app.route('/basic')
def basic_scan():
    return render_template('basic.html')

@socketio.on('start_scan')
def handle_scan():
    try:
        process = subprocess.Popen(['netdiscover', '-P'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        with open(RESULT_FILE, 'w') as f:
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    socketio.emit('scan_output', {'data': line.strip()})
                    f.write(line.strip() + "\n")
                    eventlet.sleep(0.1)
        socketio.emit('scan_complete')
    except Exception as e:
        socketio.emit('scan_output', {'data': f'Error: {str(e)}'})

@app.route('/start_basic_scan', methods=['POST'])
def start_basic_scan():
    ip_address = request.form.get('ip_address')
    whole_network = request.form.get('whole_network') == 'on'

    if not whole_network and not is_valid_ip_or_domain(ip_address):
        return jsonify({'error': 'Invalid IP address or domain name'}), 400

    try:
        scan_command = ['nmap', '-sV', ip_address] if not whole_network else ['netdiscover', '-P']
        process = subprocess.run(scan_command, capture_output=True, text=True)
        
        with open(RESULT_FILE, 'w') as f:
            f.write(process.stdout)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_results')
def download_results():
    if os.path.exists(RESULT_FILE):
        return send_file(RESULT_FILE, as_attachment=True)
    return "No scan results found", 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
