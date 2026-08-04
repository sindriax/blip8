"""Oscillators: functions that generate raw waveforms as float arrays."""

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt

SAMPLE_RATE = 44100

#: An array of audio samples, each between -1.0 and 1.0.
Samples = npt.NDArray[np.float64]

#: A steady pitch in Hz, or a (start, end) pair to glide between two.
Pitch = float | tuple[float, float]

#: One cycle of a sine at the Game Boy wave channel's 32-sample resolution.
SINE_TABLE = np.sin(2 * np.pi * np.arange(32) / 32)

#: A sine with a quieter octave mixed in, which reads as a bell.
BELL_TABLE = 0.7 * np.sin(2 * np.pi * np.arange(32) / 32) + 0.3 * np.sin(
    4 * np.pi * np.arange(32) / 32
)


def square(freq: Pitch, length: float, duty: float = 0.5, volume: float = 0.5) -> Samples:
    """Generate a square wave, the NES melody voice.

    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    duty:   fraction of each cycle spent high, between 0 and 1 exclusive.
            0.5 is hollow, 0.125 is nasal.
    volume: 0.0 to 1.0
    """
    if not 0.0 < duty < 1.0:
        raise ValueError(f"duty must be between 0 and 1 exclusive, got {duty}")
    _check_volume(volume)

    phase = _phase(freq, length)
    wave: Samples = np.where(phase < duty, 1.0, -1.0) * volume
    return wave


def triangle(freq: Pitch, length: float, volume: float = 0.5) -> Samples:
    """Generate a triangle wave, the NES bassline voice.

    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    _check_volume(volume)

    phase = _phase(freq, length)
    # abs(phase - 0.5) is a V from 0.5 down to 0.0 and back; scaled to -1..1.
    wave: Samples = (4.0 * np.abs(phase - 0.5) - 1.0) * volume
    return wave


def noise(length: float, volume: float = 0.5, seed: int | None = None) -> Samples:
    """Generate white noise, the NES percussion voice.

    Takes no pitch: with no repeating cycle there is no frequency.

    length: duration in seconds
    volume: 0.0 to 1.0
    seed:   fix it to get the same noise every call, which makes a sound built
            on noise reproducible. Left None, every call differs.
    """
    _check_length(length)
    _check_volume(volume)

    rng = np.random.default_rng(seed)
    wave: Samples = rng.uniform(-1.0, 1.0, size=int(SAMPLE_RATE * length)) * volume
    return wave


def wavetable(
    table: Samples | Sequence[float],
    freq: Pitch,
    length: float,
    volume: float = 0.5,
) -> Samples:
    """Generate a wave from a caller-supplied shape, the Game Boy wave channel.

    table:  values describing one cycle, each -1.0 to 1.0. SINE_TABLE and
            BELL_TABLE are provided; [1.0, -1.0] is a square wave.
    freq:   pitch in Hz, or a (start, end) pair to glide
    length: duration in seconds
    volume: 0.0 to 1.0
    """
    _check_volume(volume)

    shape = np.asarray(table, dtype=np.float64)
    if shape.size == 0:
        raise ValueError("table must contain at least one value")

    slots = (_phase(freq, length) * shape.size).astype(np.int64) % shape.size
    wave: Samples = shape[slots] * volume
    return wave


def _phase(freq: Pitch, length: float) -> Samples:
    """Position within the current cycle for every sample, wrapping 0.0 to 1.0."""
    _check_length(length)
    count = int(SAMPLE_RATE * length)

    if isinstance(freq, tuple | list):
        start, end = freq
        _check_freq(start)
        _check_freq(end)
        # A changing frequency has to accumulate: how far through the wave we
        # are depends on the whole history, not the current pitch.
        swept: Samples = np.cumsum(np.linspace(start, end, count) / SAMPLE_RATE) % 1.0
        return swept

    _check_freq(freq)
    steady: Samples = (np.arange(count) / SAMPLE_RATE * freq) % 1.0
    return steady


def _check_freq(freq: float) -> None:
    if freq <= 0:
        raise ValueError(f"freq must be greater than 0 Hz, got {freq}")
    if freq > SAMPLE_RATE / 2:
        raise ValueError(
            f"freq must be below the Nyquist limit of {SAMPLE_RATE // 2} Hz, got {freq}"
        )


def _check_length(length: float) -> None:
    if length < 0:
        raise ValueError(f"length must not be negative, got {length}")


def _check_volume(volume: float) -> None:
    if not 0.0 <= volume <= 1.0:
        raise ValueError(f"volume must be between 0.0 and 1.0, got {volume}")
