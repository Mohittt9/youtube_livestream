from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
import signal
import sys

app = Flask(__name__)

# Store processes here
running_processes = {}

@app.route('/')
def index():
    # Clean dead processes
    dead = []
    for pid in running_processes:
        try:
            os.kill(pid, 0)
        except:
            dead.append(pid)

    for pid in dead:
        del running_processes[pid]

    return render_template('index.html', processes=running_processes)


@app.route('/start', methods=['POST'])
def start_stream():
    stream_key = request.form.get("stream_key")
    video_url = request.form.get("video_url")

    if not stream_key or not video_url:
        return redirect(url_for('index'))

    cmd = [sys.executable, "stream_worker.py", stream_key, video_url]
    proc = subprocess.Popen(cmd)

    running_processes[proc.pid] = {
        'key_hidden': "...." + stream_key[-4:],
        'url': video_url
    }

    return redirect(url_for("index"))


@app.route('/stop/<int:pid>')
def stop_stream(pid):
    if pid in running_processes:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass
        del running_processes[pid]

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
