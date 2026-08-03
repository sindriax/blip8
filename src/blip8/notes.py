"""Note names to frequencies, via MIDI note numbers.

Twelve equal semitones per octave, anchored on A4 = MIDI 69 = 440 Hz.
"""

import re

SEMITONES = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

A4_MIDI = 69
A4_HZ = 440.0

_NOTE_PATTERN = re.compile(r"([A-Ga-g])([#b]?)(-?\d+)")


def note_to_midi(name: str) -> int:
    """Convert a note name to a MIDI number: "A4" -> 69, "C4" -> 60.

    The letter is case-insensitive; the accidental is not, since "b" means flat.
    """
    match = _NOTE_PATTERN.fullmatch(name.strip())
    if match is None:
        raise ValueError(f"{name!r} is not a note name — try 'A4', 'C#5' or 'Eb3'")

    letter, accidental, octave = match.groups()
    # MIDI octaves start at -1, so C-1 is 0 and C0 is 12.
    return (int(octave) + 1) * 12 + SEMITONES[letter.upper() + accidental]


def midi_to_freq(midi: float) -> float:
    """Convert a MIDI number to Hz. Accepts fractions for bends and vibrato."""
    return A4_HZ * 2 ** ((midi - A4_MIDI) / 12)


def note(name: str) -> float:
    """Convert a note name to Hz: "A4" -> 440.0, "E5" -> 659.26."""
    return midi_to_freq(note_to_midi(name))
