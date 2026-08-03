"""Print the waveforms instead of playing them.

uv run examples/see_it.py
"""

from blip8 import (
    BELL_TABLE,
    SINE_TABLE,
    crunch,
    envelope,
    noise,
    sfx,
    show,
    square,
    triangle,
    wavetable,
)

WIDTH = 72
HEIGHT = 13
CYCLES = 0.007  # about three cycles at 440 Hz

print("=" * WIDTH)
print("THE FOUR VOICES, zoomed in on three cycles")
print("=" * WIDTH)

show(
    square(freq=440, length=CYCLES, volume=1.0),
    "\nsquare — jumps between two values",
    WIDTH,
    HEIGHT,
)
show(
    triangle(freq=440, length=CYCLES, volume=1.0), "\ntriangle — slides between them", WIDTH, HEIGHT
)
show(wavetable(SINE_TABLE, freq=440, length=CYCLES, volume=1.0), "\nsine table", WIDTH, HEIGHT)
show(wavetable(BELL_TABLE, freq=440, length=CYCLES, volume=1.0), "\nbell table", WIDTH, HEIGHT)
show(noise(length=CYCLES, volume=1.0), "\nnoise — no repeating shape at all", WIDTH, HEIGHT)

print("\n" + "=" * WIDTH)
print("THE DUTY KNOB, same pitch each time")
print("=" * WIDTH)

for duty in (0.5, 0.25, 0.125):
    show(
        square(freq=440, length=CYCLES, duty=duty, volume=1.0),
        f"\nduty={duty}",
        WIDTH,
        HEIGHT,
    )

print("\n" + "=" * WIDTH)
print("ENVELOPES, zoomed out to a whole sound")
print("=" * WIDTH)

show(square(freq=440, length=0.5, volume=0.9), "\nno envelope — a flat block", WIDTH, HEIGHT)
show(
    envelope(square(freq=440, length=0.5, volume=0.9), attack=0.15, release=0.15),
    "\nattack=0.15 release=0.15 — fades in and out",
    WIDTH,
    HEIGHT,
)
show(
    envelope(noise(length=1.2, volume=0.9), attack=0.001, decay=1.2, sustain=0.0, release=0.0),
    "\ncymbal crash — loud then dying away",
    WIDTH,
    HEIGHT,
)
show(sfx.kick(), "\nsfx.kick() — a fast thump", WIDTH, HEIGHT)
show(sfx.coin(), "\nsfx.coin() — two notes, the second one longer", WIDTH, HEIGHT)

print("\n" + "=" * WIDTH)
print("PITCH SWEEPS — watch the cycles bunch up")
print("=" * WIDTH)

show(square(freq=(200, 2000), length=0.02, volume=1.0), "\nrising 200 to 2000 Hz", WIDTH, HEIGHT)

print("\n" + "=" * WIDTH)
print("CRUNCH — fewer volume levels means visible steps")
print("=" * WIDTH)

for bits in (16, 3, 2):
    show(
        crunch(wavetable(SINE_TABLE, freq=440, length=CYCLES, volume=1.0), bits=bits),
        f"\n{bits} bits",
        WIDTH,
        HEIGHT,
    )
