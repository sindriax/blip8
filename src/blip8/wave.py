"""Oscillators: functions that generate raw waveforms as float arrays."""

import numpy as np

SAMPLE_RATE = 44100

#: A steady pitch in Hz, or a (start, end) pair to glide between two.
Pitch = float | tuple[float, float]

#: One cycle of a sine at the Game Boy wave channel's 32-sample resolution.
SINE_TABLE = np.sin(2 * np.pi * np.arange(32) / 32)

#: A sine with a quieter octave mixed in, which reads as a bell.
BELL_TABLE = 0.7 * np.sin(2 * np.pi * np.arange(32) / 32) + 0.3 * np.sin(
    4 * np.pi * np.arange(32) / 32
)


def square(freq: Pitch, length: float, duty: float = 0.5, volume: float = 0.5) -> np.ndarray:
    """Generate a square wave — the NES melody voice.

    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    duty:   fraction of each cycle spent high. 0.5 is hollow, 0.125 is nasal.
    volume: 0.0 to 1.0
    """
    phase = _phase(freq, length)
    return np.where(phase < duty, 1.0, -1.0) * volume


def triangle(freq: Pitch, length: float, volume: float = 0.5) -> np.ndarray:
    """Generate a triangle wave — the NES bassline voice.

    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    phase = _phase(freq, length)
    # abs(phase - 0.5) is a V from 0.5 down to 0.0 and back; scaled to -1..1.
    return (4.0 * np.abs(phase - 0.5) - 1.0) * volume


def noise(length: float, volume: float = 0.5) -> np.ndarray:
    """Generate white noise — the NES percussion voice.

    Takes no pitch: with no repeating cycle there is no frequency.

    length: duration in seconds
    volume: 0.0 to 1.0
    """
    return np.random.uniform(-1.0, 1.0, size=int(SAMPLE_RATE * length)) * volume


def wavetable(
    table: np.ndarray | list[float],
    freq: Pitch,
    length: float,
    volume: float = 0.5,
) -> np.ndarray:
    """Generate a wave from a caller-supplied shape — the Game Boy wave channel.

    table:  values describing one cycle, each -1.0 to 1.0. SINE_TABLE and
            BELL_TABLE are provided; [1.0, -1.0] is a square wave.
    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    table = np.asarray(table, dtype=np.float64)
    slots = (_phase(freq, length) * len(table)).astype(np.int64) % len(table)
    return table[slots] * volume


def _phase(freq: Pitch, length: float) -> np.ndarray:
    """Position within the current cycle for every sample, wrapping 0.0 to 1.0."""
    count = int(SAMPLE_RATE * length)

    if isinstance(freq, (tuple, list)):
        # A changing frequency has to accumulate: how far through the wave we
        # are depends on the whole history, not the current pitch.
        start, end = freq
        return np.cumsum(np.linspace(start, end, count) / SAMPLE_RATE) % 1.0

    return (np.arange(count) / SAMPLE_RATE * freq) % 1.0
