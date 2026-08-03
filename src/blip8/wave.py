"""The oscillators: functions that generate raw waveforms.

Digital audio is just a long list of numbers between -1.0 and 1.0, each one
telling the speaker where to be at that instant. We use 44100 numbers per
second (the "sample rate" — CD quality). A 2-second sound is an array of
88200 floats. That's all sound is. Everything in this library is
manufacturing those arrays.
"""

import numpy as np

# Samples per second. 44100 is the standard; don't change it casually —
# every duration calculation in the library assumes it.
SAMPLE_RATE = 44100


def square(freq: float, length: float, duty: float = 0.5, volume: float = 0.5) -> np.ndarray:
    """Generate a square wave — THE chiptune sound (NES melody channels).

    freq:   pitch in Hz (440 = the A above middle C)
    length: duration in seconds
    duty:   fraction of each cycle spent "up". The NES offered 0.125, 0.25
            and 0.5 — this one knob is why Mega Man and Zelda sound
            different on the same chip. 0.5 = hollow/round, 0.125 = thin/nasal.
    volume: 0.0 to 1.0
    """
    # t is an array of time stamps: [0, 1/44100, 2/44100, ...] up to `length`.
    t = np.arange(int(SAMPLE_RATE * length)) / SAMPLE_RATE

    # (t * freq) % 1.0 gives where we are inside each cycle (0.0 to 1.0).
    # First `duty` fraction of the cycle → +1 (speaker pushed out),
    # the rest → -1 (pulled in). That hard jump IS the square-wave buzz.
    phase = (t * freq) % 1.0
    wave = np.where(phase < duty, 1.0, -1.0)

    return wave * volume
