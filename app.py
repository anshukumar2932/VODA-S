from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import subprocess
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('dashboard.html')

@socketio.on('start_download')
def handle_download(data):
    query = data['query']
    threading.Thread(target=run_download_task, args=(query,)).start()

def run_download_task(query):
    socketio.emit('log', {'stage': 'Observation', 'message': f'Starting observation script for: {query}'})

    try:
        result = subprocess.run(
            ['python', 'observation/analyse.py'],  # You can pass args if needed
            capture_output=True,
            text=True
        )
        output = result.stdout
        error = result.stderr

        if output:
            for line in output.splitlines():
                socketio.emit('log', {'stage': 'Observation', 'message': line})
        if error:
            socketio.emit('log', {'stage': 'Error', 'message': error})

    except Exception as e:
        socketio.emit('log', {'stage': 'Error', 'message': str(e)})

    socketio.emit('log', {'stage': 'Observation', 'message': 'Observation task completed.'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
