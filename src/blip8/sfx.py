"""Ready-made game sounds, built from the oscillators and shapers.

Each recipe returns an array rather than playing it, so they can be mixed with
`+`, joined with `sequence`, placed with `at` and `layer`, or saved to a file.
"""

import numpy as np

from .shape import envelope
from .wave import SINE_TABLE, noise, square, triangle, wavetable


def blip(freq: float = 880, length: float = 0.06) -> np.ndarray:
    """A short neutral beep for menu movement or advancing text."""
    return envelope(
        square(freq=freq, length=length, duty=0.5, volume=0.4),
        attack=0.001,
        release=0.02,
    )


def select() -> np.ndarray:
    """Two rising notes: confirm."""
    return _join(blip(freq=660, length=0.05), blip(freq=990, length=0.09))


def back() -> np.ndarray:
    """Two falling notes: cancel."""
    return _join(blip(freq=660, length=0.05), blip(freq=440, length=0.09))


def coin() -> np.ndarray:
    """A short high note followed by a longer one above it."""
    return _join(
        envelope(square(freq=988, length=0.07, volume=0.4), attack=0.001, release=0.01),
        envelope(square(freq=1319, length=0.35, volume=0.4), attack=0.001, release=0.2),
    )


def jump() -> np.ndarray:
    """A fast rise on a thin duty cycle."""
    return envelope(
        square(freq=(400, 900), length=0.12, duty=0.125, volume=0.4),
        attack=0.001,
        release=0.03,
    )


def powerup() -> np.ndarray:
    """A major chord arpeggiated upwards."""
    return _join(*[blip(freq=f, length=0.06) for f in (523, 659, 784, 1047)])


def laser() -> np.ndarray:
    """Pitch falling steeply. Shooting, zapping, dashing."""
    return envelope(
        square(freq=(1800, 200), length=0.25, duty=0.25, volume=0.45),
        attack=0.001,
        release=0.05,
    )


def hurt() -> np.ndarray:
    """Falling and deliberately harsh, on the thinnest duty setting."""
    return envelope(
        square(freq=(440, 110), length=0.2, duty=0.125, volume=0.45),
        attack=0.001,
        release=0.06,
    )


def explosion() -> np.ndarray:
    """Noise for the debris layered with a low falling triangle for the thump."""
    debris = envelope(
        noise(length=0.9, volume=0.35), attack=0.001, decay=0.9, sustain=0.0, release=0.0
    )
    thump = envelope(
        triangle(freq=(140, 30), length=0.9, volume=0.3),
        attack=0.001,
        decay=0.5,
        sustain=0.0,
        release=0.0,
    )
    return debris + thump


def chime() -> np.ndarray:
    """A pure tone with a long fade. Checkpoint or puzzle solved."""
    return envelope(
        wavetable(SINE_TABLE, freq=1047, length=1.0, volume=0.4),
        attack=0.005,
        decay=1.0,
        sustain=0.0,
        release=0.0,
    )


def kick() -> np.ndarray:
    """A triangle dropping from 120 Hz to 40 Hz."""
    return envelope(
        triangle(freq=(120, 40), length=0.25, volume=0.5),
        attack=0.001,
        decay=0.25,
        sustain=0.0,
        release=0.0,
    )


def snare() -> np.ndarray:
    """Fast-decaying noise with a low tone underneath for body."""
    body = envelope(
        noise(length=0.15, volume=0.35), attack=0.001, decay=0.15, sustain=0.0, release=0.0
    )
    tone = envelope(
        triangle(freq=180, length=0.15, volume=0.15),
        attack=0.001,
        decay=0.08,
        sustain=0.0,
        release=0.0,
    )
    return body + tone


def hat() -> np.ndarray:
    """A very short tick of noise.

    A real hi-hat is high-passed noise; with no filter available, keeping it
    extremely short is the closest approximation.
    """
    return envelope(
        noise(length=0.03, volume=0.3), attack=0.001, decay=0.03, sustain=0.0, release=0.0
    )


def crash() -> np.ndarray:
    """The same noise as `snare` over 1.5 seconds instead of 0.15."""
    return envelope(
        noise(length=1.5, volume=0.35), attack=0.001, decay=1.5, sustain=0.0, release=0.0
    )


def _join(*sounds: np.ndarray) -> np.ndarray:
    return np.concatenate(sounds)
