from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import subprocess
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template('dashboard.html')

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

# @socketio.on('start_download')
# def handle_start(data):
#     # Optional: could be used to manually trigger scripts, but not needed here
    pass

if __name__ == '__main__':
    
    threading.Thread(target=run_script_loop, args=('Admin', 'admin/admin.py'), daemon=True).start()
    threading.Thread(target=run_script_loop, args=('Detection', 'detection/classD.py'), daemon=True).start()
    threading.Thread(target=run_script_loop, args=('Verification', 'verification/classV.py'), daemon=True).start()
    threading.Thread(target=run_script_loop, args=('Observation', 'observation/classO.py'), daemon=True).start()

    socketio.run(app, debug=True)
