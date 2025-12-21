import logging
import sys

from PySide6.QtWidgets import QApplication

from capture_api import CaptureAPI
from ui import MainWindow

logging.basicConfig(level=logging.DEBUG)

def main() -> int:
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    capture_api = CaptureAPI()
    capture_api.set_frame_callback(win.update_frame)

    available_options = capture_api.get_options()
    win.set_option_change_callback(capture_api.set_option)
    win.update_options(available_options)
    capture_api.start_capturing()

    _ = app.aboutToQuit.connect(capture_api.stop_capturing)

    return app.exec()


if __name__ == "__main__":
    exit(main())
