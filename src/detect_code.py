import cv2
from cv2.typing import MatLike
from pyzbar.pyzbar import decode

__all__ = ["detect_code"]


def detect_code(frame: MatLike) -> tuple[str, MatLike]:
    barcodes = decode(frame)  # pyright: ignore[reportUnknownVariableType]
    code = ""
    for barcode in barcodes:  # pyright: ignore[reportUnknownVariableType]
        x, y, w, h = barcode.rect  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        code: str = barcode.data.decode("utf-8")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        _ = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # pyright: ignore[reportUnknownArgumentType]

        font = cv2.FONT_HERSHEY_DUPLEX
        _ = cv2.putText(frame, code, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)  # pyright: ignore[reportUnknownArgumentType]

    return code, frame  # pyright: ignore[reportUnknownVariableType]
