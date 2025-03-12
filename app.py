from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
import subprocess
import os
import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_nmap_scan(target, scan_type, custom_options=None):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(RESULTS_DIR, f"scan_{timestamp}.txt")
    
    if scan_type == "basic":
        command = ["nmap", "-F", target]
    else:  # advanced scan
        command = ["nmap"] + (custom_options.split() if custom_options else []) + [target]
    
    with open(result_file, "w") as f:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            socketio.emit("Scan update", {"line": line.strip()})
            f.write(line)
    
    return result_file

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/scan_portal')
def scan_portal():
    return render_template('scan_portal.html')
    
@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    scan_type = data.get("scanType")
    target_ip = data.get("targetIP")
    full_network = data.get("fullNetwork")
    custom_options = data.get("customOptions", "")
    
    target = target_ip if not full_network else "192.168.1.0/24"
    result_file = run_nmap_scan(target, scan_type, custom_options)
    
    minimal_results = []
    with open(result_file, "r") as f:
        for line in f.readlines():
            if "open" in line or "Nmap scan report for" in line:
                minimal_results.append(line.strip())
    
    return jsonify({
        "minimalResults": minimal_results,
        "downloadLink": f"/download/{os.path.basename(result_file)}"
    })

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(RESULTS_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
