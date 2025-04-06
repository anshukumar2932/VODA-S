from flask import Flask, render_template
from flask_socketio import SocketIO
import threading

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
    socketio.emit('log', {'stage': 'Download', 'message': f'Starting for {query}'})
    # simulate a step-by-step task
    time.sleep(1)
    socketio.emit('log', {'stage': 'Download', 'message': f'Downloaded 20 images for {query}'})
    time.sleep(1)
    socketio.emit('log', {'stage': 'Download', 'message': 'Completed download'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
