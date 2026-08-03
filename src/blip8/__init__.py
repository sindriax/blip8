"""blip8 — NES-style sound and music from code. Four voices, no samples."""

# Re-exports: this is what makes `from blip8 import square, play` work
# without users needing to know which internal file things live in.
from .play import play, save
from .wave import SAMPLE_RATE, square

__all__ = ["SAMPLE_RATE", "play", "save", "square"]
