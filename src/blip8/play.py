"""Writing samples to disk and to the speakers."""

import subprocess
import tempfile
import wave as wavfile

import numpy as np

from .wave import SAMPLE_RATE


def save(samples: np.ndarray, path: str) -> None:
    """Write samples to a mono 16-bit .wav file.

    Values outside -1.0..1.0 are clipped. Without the clip they would overflow
    int16 and wrap to the opposite sign, which sounds like a loud crackle.
    """
    ints = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)

    with wavfile.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(ints.tobytes())


def play(samples: np.ndarray) -> None:
    """Play samples through the speakers, blocking until finished.

    Writes a temporary .wav and hands it to macOS `afplay`, which keeps the
    library dependency-free at the cost of being platform-specific.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        save(samples, tmp.name)
        subprocess.run(["afplay", tmp.name], check=False)
