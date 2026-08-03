"""All four NES voices, one after another. Run me with:

    uv run examples/four_voices.py

Listen for the point of the whole file: the square and the triangle play the
SAME note (220 Hz), and sound nothing alike.
"""

from blip8 import noise, play, square, triangle

print("pulse 1 — square, 220 Hz. Buzzy. This carries melodies.")
play(square(freq=220, length=0.6))

print("triangle — same 220 Hz. Soft, flute-ish. This carries basslines.")
play(triangle(freq=220, length=0.6))

print("...and both together, which is a chiptune bass + melody in two lines:")
play(square(freq=440, length=0.6) + triangle(freq=220, length=0.6))

print("noise — no pitch at all, just static. Raw material for drums.")
play(noise(length=0.6))
