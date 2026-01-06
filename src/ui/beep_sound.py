import threading
from winsound import SND_FILENAME, PlaySound

from file_system import BEEP_SOUND_WAV


def _play_beep() -> None:
    if BEEP_SOUND_WAV is None:
        return
    PlaySound(BEEP_SOUND_WAV.as_posix(), SND_FILENAME)

def play_beep() -> None:
    thread = threading.Thread(target=_play_beep, name="Beep Player")
    thread.start()