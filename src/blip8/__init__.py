"""blip8 — NES-style sound and music from code. Four voices, no samples."""

from importlib.metadata import PackageNotFoundError, version

from . import sfx
from .draw import plot, show
from .notes import midi_to_freq, note, note_to_midi
from .pattern import arpeggio, at, chord, layer, melody, sequence, silence
from .play import play, save
from .shape import crunch, envelope
from .wave import BELL_TABLE, SAMPLE_RATE, SINE_TABLE, noise, square, triangle, wavetable

try:
    __version__ = version("blip8")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.0.0+unknown"

__all__ = [
    "BELL_TABLE",
    "SAMPLE_RATE",
    "SINE_TABLE",
    "__version__",
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
    "plot",
    "save",
    "sequence",
    "sfx",
    "show",
    "silence",
    "square",
    "triangle",
    "wavetable",
]
