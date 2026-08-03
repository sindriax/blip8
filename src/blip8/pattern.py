"""Turning strings of note names into music.

A pattern is a string of tokens separated by spaces, one token per step in
time:

    "C4 E4 G4 C5"      four notes, one per step
    "C4 . . . E4 . . ." two notes, each held for four steps
    "C4 - E4 -"        two notes with a silent step after each

Three kinds of token:
    a note name   play it   ("C4", "F#5", "Eb3")
    "."           hold      (extend the note before it)
    "-"           rest      (silence)

That's a **tracker**, which is what chiptune musicians actually use — a grid of
rows scrolling down the screen, one row per step. It's a strange format if
you're used to a piano roll, and it turns out to be the obvious one once you're
representing music as text.

Steps are timed from `bpm` (beats per minute) and `steps_per_beat`. The default
of 4 means each token is a sixteenth note, which is the usual tracker
resolution.
"""

from collections.abc import Callable

import numpy as np

from .notes import note
from .shape import envelope
from .wave import SAMPLE_RATE, square

# A "voice" is any oscillator that can be called with freq, length and volume.
# square and triangle qualify; noise doesn't (no pitch), and wavetable needs
# its table supplied first (use functools.partial).
Voice = Callable[..., np.ndarray]


def silence(length: float) -> np.ndarray:
    """`length` seconds of nothing. An array of zeros is genuine silence —
    the speaker cone sitting still."""
    return np.zeros(int(SAMPLE_RATE * length))


def sequence(*sounds: np.ndarray) -> np.ndarray:
    """Play sounds one after another."""
    return np.concatenate(sounds)


def at(time: float, sound: np.ndarray) -> np.ndarray:
    """Delay a sound so it starts `time` seconds in.

    Pointless alone — useful with `layer`, because between them you can place
    anything anywhere:

        layer(at(0.0, kick), at(0.5, snare), at(0.5, hat))

    Two sounds at the same offset play together; different offsets is rhythm.
    That's the whole of arrangement, in two functions.
    """
    return sequence(silence(time), sound)


def layer(*sounds: np.ndarray) -> np.ndarray:
    """Play sounds at the same time, mixed together.

    Plain `a + b` only works when both arrays are the same length — NumPy
    refuses to add mismatched shapes. This pads everything out to the longest,
    so you can layer a 2-second bassline under a 0.3-second drum hit.

    Watch your volumes: three sounds peaking at 0.5 each will sum to 1.5 and
    clip on save.
    """
    longest = max(len(sound) for sound in sounds)
    mixed = np.zeros(longest)
    for sound in sounds:
        # Slice assignment: add each sound into the front of the buffer.
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
    """Play a pattern string as a single line of music.

        melody("E4 E4 F4 G4", bpm=120)
        melody("C2 . . . G2 . . .", voice=triangle)   # a bassline
        melody("C5 - C5 -", duty=0.125)               # extra kwargs reach the voice

    Anything unrecognised in `voice_options` is passed straight through to the
    oscillator, which is how `duty` works above.
    """
    step = 60.0 / bpm / steps_per_beat
    tokens = pattern.split()
    if not tokens:
        return silence(0)

    parts = []
    index = 0
    while index < len(tokens):
        token = tokens[index]

        # Look ahead: every "." immediately after this token extends it, so a
        # note plus three dots is one note lasting four steps.
        held = 1
        while index + held < len(tokens) and tokens[index + held] == ".":
            held += 1
        length = step * held

        if token == "-":
            parts.append(silence(length))
        elif token == ".":
            # A "." with no note before it — treat as a rest rather than
            # crashing, since it's a natural way to indent a pattern.
            parts.append(silence(length))
        else:
            sound = voice(freq=note(token), length=length, volume=volume, **voice_options)
            # A short fade at both ends: without it every step would click.
            # The release scales with the note so short notes stay punchy.
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
    """Play several notes at once.

        chord("C4 E4 G4")

    The NES physically could not do this with more than a couple of notes —
    each note costs a whole voice, and there were only four. Modern code has no
    such limit, so this is blip8 being more capable than the hardware it's
    imitating. Compare it with `arpeggio` below.

    Note the low default volume: three notes at 0.15 peak at 0.45 together.
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
    """Play the notes of a chord one at a time, very fast, on repeat.

        arpeggio("C4 E4 G4")

    This is the single most recognisable chiptune technique, and it exists
    purely because of the four-voice limit: you can't hold a chord, so you
    cycle through its notes fast enough that the ear fuses them into one.

    `rate` is how long each note gets. Around 0.02–0.04 reads as a chord with
    a shimmer; slow it to 0.1 and you hear it as a fast melodic run instead.
    Worth sweeping to hear where your ear flips between the two.
    """
    freqs = [note(name) for name in notes.split()]
    step_count = max(1, round(length / rate))

    parts = [
        # Cycle through the chord with %, wrapping back to the first note.
        voice(freq=freqs[i % len(freqs)], length=rate, volume=volume, **voice_options)
        for i in range(step_count)
    ]
    return envelope(sequence(*parts), attack=0.004, release=0.03)
