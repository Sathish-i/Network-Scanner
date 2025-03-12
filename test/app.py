from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    scan_result = ""
    if request.method == 'POST':
        target = request.form.get('target')
        scan_type = request.form.get('scan_type')
        
        if target:
            command = ["nmap", scan_type, target]
            try:
                scan_result = subprocess.check_output(command, text=True)
            except subprocess.CalledProcessError as e:
                scan_result = f"Error: {e.output}"
    
    return render_template('index.html', scan_result=scan_result)

if __name__ == '__main__':
    app.run(debug=True)
