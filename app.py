import os
import time
import threading
import subprocess

from flask import Flask, send_file, send_from_directory, render_template
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='web')
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------- ROUTES -------------------

@app.route("/")
def index():
    return send_file('templates/dashboard.html')

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('templates', path)

# ------------------- SCRIPT LOOP -------------------

def run_script_loop(name, path, delay=20):
    while True:
        socketio.emit('log', {'stage': name, 'message': f'Running {path}...'})

        try:
            result = subprocess.run(
                ['python3', path],
                capture_output=True,
                text=True
            )
            output = result.stdout
            error = result.stderr

            if output:
                for line in output.splitlines():
                    socketio.emit('log', {'stage': name, 'message': line})
            if error:
                socketio.emit('log', {'stage': f'{name}-Error', 'message': error})

        except Exception as e:
            socketio.emit('log', {'stage': f'{name}-Exception', 'message': str(e)})

        socketio.emit('log', {'stage': name, 'message': f'Waiting {delay} sec before next run...'})
        time.sleep(delay)

# ------------------- MAIN -------------------

if __name__ == "__main__":
    # Start script loops in background
    threading.Thread(target=run_script_loop, args=('Admin', 'admin/admin.py'), daemon=True).start()
    time.sleep(10)
    threading.Thread(target=run_script_loop, args=('Detection', 'detection/classD.py'), daemon=True).start()
    time.sleep(10)
    threading.Thread(target=run_script_loop, args=('Verification', 'verification/classV.py'), daemon=True).start()
    time.sleep(10)
    threading.Thread(target=run_script_loop, args=('Observation', 'observation/classO.py'), daemon=True).start()
    time.sleep(10)
    socketio.run(app, debug=True)
