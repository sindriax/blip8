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

# A pitch can be one steady number (440) or a glide between two (880, 110).
# `float | tuple` is Python's "either of these types" — like a union type in
# TypeScript. It's documentation for humans and editors; nothing enforces it
# at runtime.
Pitch = float | tuple[float, float]


def _phase(freq: Pitch, length: float) -> np.ndarray:
    """Where are we inside the current cycle, for every sample? (0.0 → 1.0)

    Both square() and triangle() need this exact ramp and then shape it
    differently, so it lives here once. Leading underscore = internal, not part
    of the public API.

    The interesting half is the sweep. For a steady pitch you can just
    multiply: after t seconds at 440 Hz you've been through t * 440 cycles.
    That shortcut breaks the moment the frequency changes over time, because
    "how many cycles have I done" now depends on the whole history, not just
    the current pitch.

    So instead you *accumulate*: work out how much of a cycle each individual
    sample advances by (freq / SAMPLE_RATE), then add them all up as you go.
    np.cumsum is the running total. This is called phase accumulation and it's
    how every real synthesizer tracks pitch.
    """
    count = int(SAMPLE_RATE * length)

    if isinstance(freq, (tuple, list)):
        start, end = freq
        # One target frequency per sample, sliding evenly from start to end.
        freqs = np.linspace(start, end, count)
        advance_per_sample = freqs / SAMPLE_RATE
        return np.cumsum(advance_per_sample) % 1.0

    # Steady pitch: the multiply shortcut is fine, and easier to read.
    t = np.arange(count) / SAMPLE_RATE
    return (t * freq) % 1.0


def square(freq: Pitch, length: float, duty: float = 0.5, volume: float = 0.5) -> np.ndarray:
    """Generate a square wave — THE chiptune sound (NES melody channels).

    freq:   pitch in Hz (440 = the A above middle C), or a (start, end) pair
            to glide between two pitches: (110, 880) rises, (880, 110) falls.
    length: duration in seconds
    duty:   fraction of each cycle spent "up". The NES offered 0.125, 0.25
            and 0.5 — this one knob is why Mega Man and Zelda sound
            different on the same chip. 0.5 = hollow/round, 0.125 = thin/nasal.
    volume: 0.0 to 1.0
    """
    # phase says where we are inside each cycle (0.0 to 1.0).
    # First `duty` fraction of the cycle → +1 (speaker pushed out),
    # the rest → -1 (pulled in). That hard jump IS the square-wave buzz.
    phase = _phase(freq, length)
    wave = np.where(phase < duty, 1.0, -1.0)

    return wave * volume


def triangle(freq: Pitch, length: float, volume: float = 0.5) -> np.ndarray:
    """Generate a triangle wave — the NES bassline voice.

    Same pitch as a square at the same freq, but soft and flute-like instead
    of buzzy, because it ramps between -1 and +1 instead of jumping. That
    makes it sit *under* a melody without fighting it. No `duty` knob here —
    that's a square-wave-only thing.

    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    # Same phase ramp as square: 0.0 → 1.0 once per cycle.
    phase = _phase(freq, length)

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
