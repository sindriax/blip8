"""blip8 — NES-style sound and music from code. Four voices, no samples."""

# Re-exports: this is what makes `from blip8 import square, play` work
# without users needing to know which internal file things live in.
from . import sfx
from .play import play, save
from .shape import crunch, envelope
from .wave import BELL_TABLE, SAMPLE_RATE, SINE_TABLE, noise, square, triangle, wavetable

__all__ = [
    "BELL_TABLE",
    "SAMPLE_RATE",
    "SINE_TABLE",
    "crunch",
    "envelope",
    "noise",
    "play",
    "save",
    "sfx",
    "square",
    "triangle",
    "wavetable",
]
