import base64
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
from cv2.typing import MatLike
from flask import Flask, render_template
from flask_socketio import SocketIO

app: Flask = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
callback: Callable[[MatLike], None] = lambda x: print(x.shape)


def set_callback(_callback: Callable[[MatLike], None]) -> None:
    global callback
    callback = _callback


@app.route("/")
def index():
    return render_template("camera_stream.html")


@socketio.on("frame")
def handle_frame(data: str):
    # Data is base64 encoded image string
    _, encoded = data.split(",", 1)
    image_data = base64.b64decode(encoded)

    # Convert to numpy/OpenCV image
    np_img = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # For example, we could display or process the frame:
    # print("Received frame:", frame.shape)
    if frame is not None:
        callback(frame)

    # Optional: send response back (acknowledgment or processed info)
    # socketio.emit('server_response', {'msg': 'Frame received'})


if __name__ == "__main__":
    cert_path: Path = Path("./src/cert.pem").absolute()
    key_path: Path = Path("./src/key.pem").absolute()
    print(f"c: {cert_path}; k: {key_path}")
    _ = socketio.run(
        app, host="0.0.0.0", port=5000, debug=True, certfile=cert_path, keyfile=key_path
    )
