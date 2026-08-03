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


# --------------------------------------------------------------------------
# The Game Boy's fourth voice
# --------------------------------------------------------------------------
# The NES's four voices were all hard-wired. The Game Boy kept two squares and
# the noise, but replaced the fixed triangle with something better: a channel
# where YOU supply the waveform. You hand it 32 numbers describing one cycle of
# any shape you like and it loops them forever.
#
# That's a wavetable, and it's the same principle modern synths like Serum and
# Vital are built on — they just use thousands of samples instead of 32, and
# let you morph between tables.
#
# A "table" here is any list of numbers between -1.0 and 1.0. Short is fine;
# [1.0, -1.0] is a square wave, and 32 was the Game Boy's actual limit.

# One cycle of a sine, at the Game Boy's 32-sample resolution. A sine is the
# purest possible tone — no character at all, just the note. blip8 has no
# sine() function, so this is how you get one.
SINE_TABLE = np.sin(2 * np.pi * np.arange(32) / 32)

# A sine with a quieter copy an octave up mixed in, which reads as "bell" or
# "music box" to the ear. Adding a higher, quieter copy of a wave to itself is
# additive synthesis in its simplest form.
BELL_TABLE = 0.7 * np.sin(2 * np.pi * np.arange(32) / 32) + 0.3 * np.sin(
    4 * np.pi * np.arange(32) / 32
)


def wavetable(
    table: np.ndarray | list[float],
    freq: Pitch,
    length: float,
    volume: float = 0.5,
) -> np.ndarray:
    """Generate a wave from a shape you define — the Game Boy's wave channel.

    table:  the numbers describing one cycle, each -1.0 to 1.0. Try
            SINE_TABLE, BELL_TABLE, or your own: [1, 0.5, 0, -0.5, -1, ...]
    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    # np.asarray accepts a plain Python list OR an existing array and gives
    # back an array either way, so callers don't have to care which they have.
    table = np.asarray(table, dtype=np.float64)

    # Same 0.0 → 1.0 ramp every oscillator starts from.
    phase = _phase(freq, length)

    # Stretch that ramp across the table's length and truncate to whole
    # numbers, turning "43% through the cycle" into "table slot 13".
    slots = (phase * len(table)).astype(np.int64) % len(table)

    # Fancy indexing: handing NumPy an array of indices returns an array of the
    # values at those indices. One line, no loop, and it's how sample playback
    # works in every sampler ever written.
    return table[slots] * volume
