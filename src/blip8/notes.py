"""Note names to frequencies. "A4" → 440.0

So far every pitch in blip8 has been a raw number, which is fine for a laser
and useless for a melody. Nobody thinks in Hz. Musicians think "E5", and this
file is the translation layer.

## The one piece of maths

Western music divides an octave into 12 equal steps (semitones). Going up an
octave *doubles* the frequency — A4 is 440 Hz, A5 is 880, A6 is 1760. So one
semitone must be the twelfth root of two, about 1.0595, because multiplying by
it twelve times gets you to exactly double.

That's it. Every note is 440 Hz multiplied by 1.0595 some number of times.

## Why MIDI numbers show up here

Rather than juggling letters and octaves, the whole system collapses to one
integer: MIDI note numbers, where middle C is 60 and A4 is 69. Note names
convert to a number, the number converts to a frequency. It's also exactly
what MIDI files contain, so this file is groundwork for reading them later.
"""

import re

# Semitones above C for every note name. Sharps and flats that land on the
# same key share a value — C# and Db are the same pitch, spelled differently.
# That's called enharmonic equivalence, and to a computer it's just a dict.
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

# A note name is a letter, an optional # or b, then an octave number which may
# be negative. Anchored with fullmatch so "C4nonsense" is rejected, not
# silently half-read.
_NOTE_PATTERN = re.compile(r"([A-Ga-g])([#b]?)(-?\d+)")

# The reference point the whole system hangs off: MIDI 69 is A4 is 440 Hz.
A4_MIDI = 69
A4_HZ = 440.0


def note_to_midi(name: str) -> int:
    """ "A4" → 69, "C4" → 60 (middle C), "F#5" → 78.

    Case-insensitive on the letter, so "a4" and "A4" both work. The accidental
    stays case-sensitive because "#" and "b" mean different things and "B" is
    already a note.
    """
    match = _NOTE_PATTERN.fullmatch(name.strip())
    if match is None:
        raise ValueError(f"{name!r} is not a note name — try 'A4', 'C#5' or 'Eb3'")

    letter, accidental, octave = match.groups()
    semitone = SEMITONES[letter.upper() + accidental]

    # +1 because MIDI's octaves start at -1: C-1 is MIDI 0, so C0 is 12.
    return (int(octave) + 1) * 12 + semitone


def midi_to_freq(midi: float) -> float:
    """69 → 440.0. Works for fractions too, which is how bends and vibrato
    will eventually be expressed."""
    # 2 ** (steps / 12) is "multiply by the twelfth root of two, `steps` times".
    return A4_HZ * 2 ** ((midi - A4_MIDI) / 12)


def note(name: str) -> float:
    """ "A4" → 440.0. The function you'll actually use.

        square(freq=note("E5"), length=0.5)

    Ranges worth knowing: C4 is middle C (261.6 Hz), the NES sat mostly
    between C2 and C7, and human hearing gives up around C10.
    """
    return midi_to_freq(note_to_midi(name))
