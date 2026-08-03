"""Two square waves. Run with: uv run examples/first_beep.py"""

from blip8 import play, square

print("beep! 440 Hz, half a second")
play(square(freq=440, length=0.5))

print("same note, duty 0.125 — thinner, more nasal")
play(square(freq=440, length=0.5, duty=0.125))
