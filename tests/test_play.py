"""Tests for saving audio to disk.

`play()` is untested: it shells out to macOS `afplay`, which has nothing to
assert and would not run on CI's Linux machines.
"""

import wave as wavfile
from pathlib import Path

import numpy as np

from blip8 import SAMPLE_RATE, save, square


def test_save_writes_a_valid_wav_file(tmp_path: Path) -> None:
    path = tmp_path / "beep.wav"
    save(square(freq=440, length=0.5), str(path))

    assert path.exists()

    with wavfile.open(str(path), "rb") as f:
        assert f.getnchannels() == 1
        assert f.getsampwidth() == 2
        assert f.getframerate() == SAMPLE_RATE
        assert f.getnframes() == int(SAMPLE_RATE * 0.5)


def test_save_converts_floats_to_16_bit_ints(tmp_path: Path) -> None:
    """A float 0.5 must land as roughly half of int16's maximum."""
    path = tmp_path / "half.wav"
    save(square(freq=440, length=0.1, volume=0.5), str(path))

    with wavfile.open(str(path), "rb") as f:
        written = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

    assert written.dtype == np.int16
    assert np.max(written) == 16383  # 0.5 * 32767, rounded down


def test_save_clips_instead_of_wrapping_around(tmp_path: Path) -> None:
    """Without the clip, 1.5 becomes 49150, overflows int16 and wraps to a
    large negative number — the speaker slams the wrong way and crackles."""
    too_loud = np.array([2.0, -2.0, 0.0, 5.0])
    path = tmp_path / "loud.wav"
    save(too_loud, str(path))

    with wavfile.open(str(path), "rb") as f:
        written = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

    assert list(written) == [32767, -32767, 0, 32767]
