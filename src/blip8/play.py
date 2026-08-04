"""Writing samples to disk and to the speakers."""

import os
import shutil
import subprocess
import sys
import tempfile
import wave as wavfile

import numpy as np

from .wave import SAMPLE_RATE, Samples

# Tried in order; the first one present on PATH wins. afplay ships with macOS,
# the rest cover the common Linux audio stacks.
_PLAYERS: tuple[tuple[str, ...], ...] = (
    ("afplay",),
    ("aplay", "-q"),
    ("paplay",),
    ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"),
)


def save(samples: Samples, path: str) -> None:
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


def play(samples: Samples) -> None:
    """Play samples through the speakers, blocking until finished.

    Writes a temporary .wav and hands it to whatever player the platform has,
    which keeps the library free of audio dependencies.

    Raises RuntimeError if no player is available.
    """
    handle, path = tempfile.mkstemp(suffix=".wav")
    os.close(handle)
    try:
        save(samples, path)
        _play_file(path)
    finally:
        os.unlink(path)


def _play_file(path: str) -> None:
    if sys.platform == "win32":
        import winsound

        winsound.PlaySound(path, winsound.SND_FILENAME)
        return

    for command in _PLAYERS:
        if shutil.which(command[0]):
            subprocess.run([*command, path], check=False)
            return

    raise RuntimeError(
        "No audio player found. blip8 shells out to one of: "
        + ", ".join(command[0] for command in _PLAYERS)
        + ". Install one (on Debian or Ubuntu: apt install alsa-utils), "
        "or use save() to write a .wav file instead."
    )
