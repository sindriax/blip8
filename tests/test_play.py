"""Tests for saving audio to disk.

`play()` isn't tested — it shells out to macOS `afplay` and makes a noise;
there's nothing to assert and it wouldn't run on CI's Linux machines. `save()`
is the half that matters anyway, since .wav files are what other projects
consume.
"""

import wave as wavfile

import numpy as np

from blip8 import SAMPLE_RATE, save, square


def test_save_writes_a_valid_wav_file(tmp_path):
    """`tmp_path` is a pytest built-in: it hands you a fresh empty directory
    and deletes it afterwards, so tests never leave junk behind."""
    path = tmp_path / "beep.wav"
    save(square(freq=440, length=0.5), str(path))

    assert path.exists()

    # Re-open it with the stdlib reader and check the header we wrote.
    with wavfile.open(str(path), "rb") as f:
        assert f.getnchannels() == 1  # mono
        assert f.getsampwidth() == 2  # 16-bit
        assert f.getframerate() == SAMPLE_RATE
        assert f.getnframes() == int(SAMPLE_RATE * 0.5)


def test_save_converts_floats_to_16_bit_ints(tmp_path):
    """A float 0.5 must land as roughly half of int16's maximum (32767)."""
    path = tmp_path / "half.wav"
    save(square(freq=440, length=0.1, volume=0.5), str(path))

    with wavfile.open(str(path), "rb") as f:
        written = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

    assert written.dtype == np.int16
    assert np.max(written) == 16383  # 0.5 * 32767, rounded down


def test_save_clips_instead_of_wrapping_around(tmp_path):
    """The bug this guards against is nasty and worth spelling out.

    Without np.clip, a sample of 1.5 becomes 49150 — too big for int16, so it
    silently *wraps around* to a large negative number. The speaker slams the
    wrong direction and you get a loud crackle. Clipping to the maximum is
    ugly but survivable; wrapping is not.
    """
    too_loud = np.array([2.0, -2.0, 0.0, 5.0])
    path = tmp_path / "loud.wav"
    save(too_loud, str(path))

    with wavfile.open(str(path), "rb") as f:
        written = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

    assert list(written) == [32767, -32767, 0, 32767]
