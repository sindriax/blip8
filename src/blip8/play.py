"""Getting arrays out of Python and into your ears.

Two exits: save to a .wav file (what games consume), or play right now
through the speakers (what sound-design sessions need).
"""

import subprocess
import tempfile
import wave as wavfile  # stdlib module for reading/writing .wav files

import numpy as np

from .wave import SAMPLE_RATE


def save(samples: np.ndarray, path: str) -> None:
    """Write an array of floats (-1.0..1.0) to a 16-bit .wav file."""
    # .wav files store 16-bit integers (-32768..32767), not floats, so we
    # scale up and convert. np.clip guards against any sample outside the
    # legal range blowing out into a nasty digital crackle.
    ints = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)

    with wavfile.open(path, "wb") as f:
        f.setnchannels(1)  # mono — the NES was mono, and we're proud of it
        f.setsampwidth(2)  # 2 bytes = 16 bits per sample
        f.setframerate(SAMPLE_RATE)
        f.writeframes(ints.tobytes())


def play(samples: np.ndarray) -> None:
    """Play an array through the speakers, blocking until it finishes.

    Cheap trick, zero extra dependencies: write a temporary .wav and hand it
    to macOS's built-in `afplay`. Good enough until real-time playback
    matters (that's a much later phase).
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        save(samples, tmp.name)
        subprocess.run(["afplay", tmp.name], check=False)
