from time import perf_counter

import cv2
import pyautogui
from cv2.typing import MatLike
from cv2_enumerate_cameras import enumerate_cameras
from PIL import Image, ImageTk
from pyzbar.pyzbar import Decoded, decode

from main_window import MainWindow


def read_code(frame: MatLike) -> tuple[str, MatLike]:
    barcodes: list[Decoded] = decode(frame)
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


def update_next_frame(camera: cv2.VideoCapture, window: MainWindow) -> None:
    global current_code
    ret, frame = camera.read()
    if not ret:
        window.destroy()
    else:
        code, altered_frame = read_code(frame)
        rgb_image = cv2.cvtColor(altered_frame, cv2.COLOR_BGR2RGB)
        pil_iamge = Image.fromarray(rgb_image)
        imagetk = ImageTk.PhotoImage(pil_iamge)
        window.frame_label["image"] = imagetk
        window.frame_label.image = imagetk
        if code and code != current_code:
            print(f"Captured Code: {code}")
            current_code = code
            with open("barcode_results.txt", "a") as f:
                _ = f.write(code + "\n")
            pyautogui.typewrite(code)
        _ = window.after(interval, update_next_frame, camera, window)


def change_fps(fps: int) -> None:
    global interval
    if fps <= 0:
        fps = 1
    interval = int(1000 / fps)

def update_cameras(window: MainWindow) -> None:
    cameras = enumerate_cameras()
    for camera in cameras:
        print(camera.name)


def main() -> None:
    window = MainWindow()

    window.on_fps_change_command = change_fps

    camera = cv2.VideoCapture(1)
    window.before_quit.append(camera.release)

    _ = window.after(100, update_next_frame, camera, window)

    window.mainloop()


if __name__ == "__main__":
    st = perf_counter()
    main()
    print(f"t: {perf_counter() - st}")
