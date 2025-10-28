from pathlib import Path
from time import perf_counter

import cv2
import pyautogui
from cv2.typing import MatLike
from pyzbar.pyzbar import decode

from app import app, set_callback, socketio


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


def main() -> None:
    # test_image_path2 = Path("./barcode-scanner-756x557.webp").resolve()
    # test_image_path = Path("./ezgifcom-crop.png").resolve()
    # image = cv2.imread(test_image_path.as_posix())
    # detect_and_decode_barcode(image)
    # camera = cv2.VideoCapture(0)
    # ret, frame = camera.read()
    # current_code = ""
    # while ret:
    # ret, frame = camera.read()
    # code, frame = read_code(frame)
    # cv2.imshow("code", frame)
    # if cv2.waitKey(1) & 0xFF == 27:
    # break
    # if code and code != current_code:
    # current_code = code
    # pyautogui.typewrite(code)

    # camera.release()
    # cv2.destroyAllWindows()

    # set_callback(handle_frame)
    cert_path: Path = Path("./src/cert.pem").absolute()
    key_path: Path = Path("./src/key.pem").absolute()
    _ = socketio.run(
        app, host="0.0.0.0", port=5000, debug=True, certfile=cert_path, keyfile=key_path
    )


if __name__ == "__main__":
    st = perf_counter()
    main()
    print(f"t: {perf_counter() - st}")
