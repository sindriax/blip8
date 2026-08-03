"""Square, triangle and noise. Run with: uv run examples/four_voices.py"""

from blip8 import noise, play, square, triangle

print("square, 220 Hz — buzzy, carries melodies")
play(square(freq=220, length=0.6))

print("triangle, the same 220 Hz — soft, carries basslines")
play(triangle(freq=220, length=0.6))

print("both together: bass and melody")
play(square(freq=440, length=0.6) + triangle(freq=220, length=0.6))

print("noise — no pitch at all, raw material for drums")
play(noise(length=0.6))
