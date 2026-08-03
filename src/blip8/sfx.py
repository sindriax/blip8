"""Ready-made game sounds.

Everything else in blip8 is raw material. This is the cookbook: the sounds you
actually reach for, already tuned, one call each.

    from blip8 import play, sfx

    play(sfx.coin())
    play(sfx.laser())
    play(sfx.blip(freq=440))

The recipes underneath are only oscillators plus envelopes plus sweeps — the
same three ingredients from wave.py and shape.py. Nothing new happens here;
the value is that the numbers are already chosen. Read any function to see
what a given sound is actually made of.

Every recipe *returns* an array rather than playing it, so you can mix them
(`sfx.kick() + sfx.hat()`), chain them, or `save()` them to a file.
"""

import numpy as np

from .shape import envelope
from .wave import SINE_TABLE, noise, square, triangle, wavetable


def _join(*sounds: np.ndarray) -> np.ndarray:
    """Play sounds one after another, back to back.

    *sounds means "any number of arguments, collected into a tuple" — the same
    idea as ...rest in JavaScript.
    """
    return np.concatenate(sounds)


# --------------------------------------------------------------------------
# Interface sounds
# --------------------------------------------------------------------------


def blip(freq: float = 880, length: float = 0.06) -> np.ndarray:
    """A short neutral beep. Menu movement, text advancing, generic feedback."""
    return envelope(
        square(freq=freq, length=length, duty=0.5, volume=0.4),
        attack=0.001,
        release=0.02,
    )


def select() -> np.ndarray:
    """Two quick rising notes — the "yes, confirmed" sound."""
    return _join(blip(freq=660, length=0.05), blip(freq=990, length=0.09))


def back() -> np.ndarray:
    """The same idea falling instead of rising, which reads as "cancel".

    Rising means yes and falling means no, in every game menu ever made. Worth
    knowing that the convention is this cheap to implement.
    """
    return _join(blip(freq=660, length=0.05), blip(freq=440, length=0.09))


def coin() -> np.ndarray:
    """The classic pickup: a short high note, then a longer one above it."""
    return _join(
        envelope(square(freq=988, length=0.07, volume=0.4), attack=0.001, release=0.01),
        envelope(square(freq=1319, length=0.35, volume=0.4), attack=0.001, release=0.2),
    )


# --------------------------------------------------------------------------
# Player actions
# --------------------------------------------------------------------------


def jump() -> np.ndarray:
    """A fast rise. Thin duty keeps it out of the way of the music."""
    return envelope(
        square(freq=(400, 900), length=0.12, duty=0.125, volume=0.4),
        attack=0.001,
        release=0.03,
    )


def powerup() -> np.ndarray:
    """Four notes climbing — an arpeggio.

    This is the NES trick: four voices can't hold a chord, so you play the
    notes one at a time, fast, and the ear hears it as one triumphant event.
    C, E, G, C — a major chord taken apart and served in sequence.
    """
    return _join(*[blip(freq=f, length=0.06) for f in (523, 659, 784, 1047)])


def laser() -> np.ndarray:
    """Pitch falling off a cliff. Shooting, zapping, dashing."""
    return envelope(
        square(freq=(1800, 200), length=0.25, duty=0.25, volume=0.45),
        attack=0.001,
        release=0.05,
    )


def hurt() -> np.ndarray:
    """Taking damage: falling, and deliberately harsh.

    duty=0.125 is the thinnest, most nasal setting — unpleasant on purpose.
    """
    return envelope(
        square(freq=(440, 110), length=0.2, duty=0.125, volume=0.45),
        attack=0.001,
        release=0.06,
    )


def explosion() -> np.ndarray:
    """Noise for the debris, plus a low falling triangle for the thump.

    Layering is the real lesson here: one waveform rarely sells a big sound.
    Both layers are the same length so they can be added together.
    """
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
    """A soft bell, using the Game Boy's wavetable voice instead of a square.

    A long slow fade on a pure tone reads as "puzzle solved" or "checkpoint".
    """
    return envelope(
        wavetable(SINE_TABLE, freq=1047, length=1.0, volume=0.4),
        attack=0.005,
        decay=1.0,
        sustain=0.0,
        release=0.0,
    )


# --------------------------------------------------------------------------
# Drums — all noise or triangle, distinguished only by their envelopes
# --------------------------------------------------------------------------


def kick() -> np.ndarray:
    """A triangle dropping fast from 120 Hz to 40 Hz. No noise involved."""
    return envelope(
        triangle(freq=(120, 40), length=0.25, volume=0.5),
        attack=0.001,
        decay=0.25,
        sustain=0.0,
        release=0.0,
    )


def snare() -> np.ndarray:
    """Noise gone in 150ms, with a little tone under it for body."""
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

    Honestly a compromise: a real hi-hat is noise with the low frequencies
    filtered out, and blip8 has no filter yet. Making it extremely short is
    the trick that gets you most of the way there.
    """
    return envelope(
        noise(length=0.03, volume=0.3), attack=0.001, decay=0.03, sustain=0.0, release=0.0
    )


def crash() -> np.ndarray:
    """The same noise as `snare`, taking 1.5 seconds to die instead of 0.15."""
    return envelope(
        noise(length=1.5, volume=0.35), attack=0.001, decay=1.5, sustain=0.0, release=0.0
    )
