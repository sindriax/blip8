"""blip8 — NES-style sound and music from code. Four voices, no samples."""

# Re-exports: this is what makes `from blip8 import square, play` work
# without users needing to know which internal file things live in.
from .play import play, save
from .shape import envelope
from .wave import SAMPLE_RATE, noise, square, triangle

__all__ = ["SAMPLE_RATE", "envelope", "noise", "play", "save", "square", "triangle"]
