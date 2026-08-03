"""blip8 — NES-style sound and music from code. Four voices, no samples."""

# Re-exports: this is what makes `from blip8 import square, play` work
# without users needing to know which internal file things live in.
from . import sfx
from .notes import midi_to_freq, note, note_to_midi
from .pattern import arpeggio, at, chord, layer, melody, sequence, silence
from .play import play, save
from .shape import crunch, envelope
from .wave import BELL_TABLE, SAMPLE_RATE, SINE_TABLE, noise, square, triangle, wavetable

__all__ = [
    "BELL_TABLE",
    "SAMPLE_RATE",
    "SINE_TABLE",
    "arpeggio",
    "at",
    "chord",
    "crunch",
    "envelope",
    "layer",
    "melody",
    "midi_to_freq",
    "noise",
    "note",
    "note_to_midi",
    "play",
    "save",
    "sequence",
    "sfx",
    "silence",
    "square",
    "triangle",
    "wavetable",
]
