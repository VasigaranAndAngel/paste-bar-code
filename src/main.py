import sys
import threading
from pathlib import Path

import cv2
from cv2.typing import MatLike
from PySide6.QtWidgets import QApplication
from pyzbar.pyzbar import decode

from capture_api import CaptureAPI
from capture_api.local_capturer import LocalCapturer
# from flask_app import app, set_callback, socketio
from ui import MainWindow


def detect_and_decode_barcode(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect barcodes in the grayscale image
    barcodes = decode(gray)

    # Loop over detected barcodes
    for barcode in barcodes:
        # Extract barcode data and type
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        # Print barcode data and type
        print("Barcode Data:", barcode_data)
        print("Barcode Type:", barcode_type)

        # Draw a rectangle around the barcode
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Put barcode data and type on the image
        cv2.putText(
            image,
            f"{barcode_data} ({barcode_type})",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2,
        )

    # Convert image from BGR to RGB (Matplotlib uses RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # plt.imshow(image_rgb)
    # plt.axis("off")
    # plt.show()


def read_code(frame):
    barcodes = decode(frame)
    code = ""
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        code: str = barcode.data.decode("utf-8")
        _ = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        font = cv2.FONT_HERSHEY_DUPLEX
        _ = cv2.putText(frame, code, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

    return code, frame


current_code: str = ""
interval = 100


def change_fps(fps: int) -> None:
    global interval
    if fps <= 0:
        fps = 1
    interval = int(1000 / fps)


current_code = ""


def handle_frame(frame: MatLike) -> None:
    global current_code
    code, frame = read_code(frame)
    cv2.imshow("frames", frame)
    if cv2.waitKey(1) == ord("q"):
        cv2.destroyAllWindows()
        quit()
    if code and code != current_code:
        current_code = code
        print(code)


# def start_flask() -> None:
#     cert_path: Path = Path("./src/cert.pem").absolute()
#     key_path: Path = Path("./src/key.pem").absolute()
#     print(cert_path, key_path)
#     set_callback(handle_frame)
#     _ = socketio.run(  # pyright: ignore[reportUnknownMemberType]
#         app,
#         host="0.0.0.0",
#         port=5000,
#         debug=True,
#         certfile=cert_path,
#         keyfile=key_path,
#         use_reloader=False,
#     )


def main() -> int:
    # initialize QApplication
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    capturer = CaptureAPI.get_available_capturing_methods()[0]
    capturer = LocalCapturer
    capture_api = CaptureAPI()
    capture_api.start_capturing(capturer)
    capture_api.set_frame_callback(win.update_frame)

    _ = app.aboutToQuit.connect(capture_api.stop_capturing)

    return app.exec()


if __name__ == "__main__":
    exit(main())
