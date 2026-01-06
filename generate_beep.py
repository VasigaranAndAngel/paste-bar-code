import winsound
from pathlib import Path

import numpy as np
from scipy.io import wavfile

sample_rate = 44100
duration = 0.300
freq = 5000

t = np.linspace(0, duration, int(sample_rate * duration), False)
tone = np.sin(2 * np.pi * freq * t)
fade = np.exp(-t * 30)  # Exponential decay (adjust 15 for fade speed)
faded_tone = tone * fade * 32767  # 16-bit range
faded_tone = faded_tone.astype(np.int16)

resource_dir = Path("src/resources/")
resource_dir.mkdir(parents=True, exist_ok=True)
wave_file = resource_dir.joinpath("beep_sound.wav")

wavfile.write(wave_file.as_posix(), sample_rate, faded_tone)
winsound.PlaySound(wave_file.as_posix(), winsound.SND_FILENAME)
