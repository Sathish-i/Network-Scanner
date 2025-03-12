from flask import Flask, render_template, request
import nmap

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    scan_result = None
    if request.method == 'POST':
        target = request.form['target']
        scan_result = perform_nmap_scan(target)
    return render_template('index.html', scan_result=scan_result)

def perform_nmap_scan(target):
    nm = nmap.PortScanner()
    nm.scan(hosts=target, arguments='-sV')  # -sV for version detection
    scan_result = []
    for host in nm.all_hosts():
        scan_result.append(f"Host: {host} ({nm[host].hostname()})")
        scan_result.append(f"State: {nm[host].state()}")
        for proto in nm[host].all_protocols():
            scan_result.append(f"Protocol: {proto}")
            lport = nm[host][proto].keys()
            for port in lport:
                scan_result.append(f"Port: {port}\tState: {nm[host][proto][port]['state']}\tService: {nm[host][proto][port]['name']}\tVersion: {nm[host][proto][port]['version']}")
    return "\n".join(scan_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
