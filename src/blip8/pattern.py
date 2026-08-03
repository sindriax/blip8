"""Pattern strings, chords and arrangement.

A pattern is space-separated tokens, one per step in time:

    "C4 E4 G4 C5"        four notes
    "C4 . . . E4 . . ."  two notes, each held for four steps
    "C4 - E4 -"          two notes, each followed by a rest

A note name plays it, "." holds the previous note, "-" rests. Step duration
comes from `bpm` and `steps_per_beat`.
"""

from collections.abc import Callable

import numpy as np

from .notes import note
from .shape import envelope
from .wave import SAMPLE_RATE, square

#: Any oscillator callable with freq, length and volume keyword arguments.
Voice = Callable[..., np.ndarray]


def silence(length: float) -> np.ndarray:
    """Return `length` seconds of silence."""
    return np.zeros(int(SAMPLE_RATE * length))


def sequence(*sounds: np.ndarray) -> np.ndarray:
    """Join sounds end to end."""
    return np.concatenate(sounds)


def at(time: float, sound: np.ndarray) -> np.ndarray:
    """Delay a sound so it starts `time` seconds in. Use with `layer`."""
    return sequence(silence(time), sound)


def layer(*sounds: np.ndarray) -> np.ndarray:
    """Mix sounds together, padding to the length of the longest.

    Unlike `a + b`, this accepts mismatched lengths. Levels still add up, so
    watch for clipping.
    """
    longest = max(len(sound) for sound in sounds)
    mixed = np.zeros(longest)
    for sound in sounds:
        mixed[: len(sound)] += sound
    return mixed


def melody(
    pattern: str,
    bpm: float = 120,
    steps_per_beat: int = 4,
    voice: Voice = square,
    volume: float = 0.4,
    **voice_options,
) -> np.ndarray:
    """Play a pattern string as one line of music.

        melody("E4 E4 F4 G4", bpm=120)
        melody("C2 . . . G2 . . .", voice=triangle)
        melody("C5 - C5 -", duty=0.125)

    Unrecognised keyword arguments are forwarded to the oscillator.
    """
    step = 60.0 / bpm / steps_per_beat
    tokens = pattern.split()
    if not tokens:
        return silence(0)

    parts = []
    index = 0
    while index < len(tokens):
        token = tokens[index]

        held = 1
        while index + held < len(tokens) and tokens[index + held] == ".":
            held += 1
        length = step * held

        if token in ("-", "."):
            parts.append(silence(length))
        else:
            sound = voice(freq=note(token), length=length, volume=volume, **voice_options)
            parts.append(envelope(sound, attack=0.004, release=min(0.04, length * 0.3)))

        index += held

    return sequence(*parts)


def chord(
    notes: str,
    length: float = 0.5,
    voice: Voice = square,
    volume: float = 0.15,
    **voice_options,
) -> np.ndarray:
    """Play several notes simultaneously: chord("C4 E4 G4").

    The default volume is low because the notes sum together.
    """
    voices = [
        voice(freq=note(name), length=length, volume=volume, **voice_options)
        for name in notes.split()
    ]
    return envelope(layer(*voices), attack=0.01, release=0.05)


def arpeggio(
    notes: str,
    length: float = 0.5,
    rate: float = 0.025,
    voice: Voice = square,
    volume: float = 0.4,
    **voice_options,
) -> np.ndarray:
    """Cycle through a chord's notes one at a time: arpeggio("C4 E4 G4").

    At a `rate` around 0.02-0.04 the ear fuses the notes into a chord; slower
    and it becomes an audible melodic run. This is how a single voice fakes a
    chord, which is why chiptune uses it constantly.
    """
    freqs = [note(name) for name in notes.split()]
    step_count = max(1, round(length / rate))

    parts = [
        voice(freq=freqs[i % len(freqs)], length=rate, volume=volume, **voice_options)
        for i in range(step_count)
    ]
    return envelope(sequence(*parts), attack=0.004, release=0.03)
