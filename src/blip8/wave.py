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


def triangle(freq: float, length: float, volume: float = 0.5) -> np.ndarray:
    """Generate a triangle wave — the NES bassline voice.

    Same pitch as a square at the same freq, but soft and flute-like instead
    of buzzy, because it ramps between -1 and +1 instead of jumping. That
    makes it sit *under* a melody without fighting it. No `duty` knob here —
    that's a square-wave-only thing.

    freq:   pitch in Hz
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    t = np.arange(int(SAMPLE_RATE * length)) / SAMPLE_RATE

    # Same phase trick as square: 0.0 → 1.0 once per cycle.
    phase = (t * freq) % 1.0

    # Now shape it into a ramp up and back down instead of a hard jump.
    # abs(phase - 0.5) is a V: 0.5 at the cycle's start, 0.0 in the middle,
    # 0.5 again at the end. Times 4 makes it 2.0 → 0.0 → 2.0, minus 1 makes
    # it 1.0 → -1.0 → 1.0. That gradual slide is the whole difference.
    wave = 4.0 * np.abs(phase - 0.5) - 1.0

    return wave * volume


def noise(length: float, volume: float = 0.5) -> np.ndarray:
    """Generate white noise — the NES percussion/explosion voice.

    No `freq` argument, because static has no pitch: there's no repeating
    cycle to have a pitch. Every sample is an independent random number, so
    the speaker jitters unpredictably and you hear a hiss. On its own it's a
    boring "shhh" — it becomes a snare, a crash or an explosion once you
    shape its volume over time (envelopes and sweeps, still to come).

    length: duration in seconds
    volume: 0.0 to 1.0
    """
    # Note the missing `/ SAMPLE_RATE`: we don't need timestamps here, just a
    # count of how many random samples to make.
    count = int(SAMPLE_RATE * length)

    # A flat spread across the full speaker range. `uniform` means every
    # value in -1.0..1.0 is equally likely — that even spread across all
    # frequencies is what "white" in white noise means.
    wave = np.random.uniform(-1.0, 1.0, size=count)

    return wave * volume
