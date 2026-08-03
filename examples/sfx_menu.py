"""Every sfx recipe, the wave channel and crunch.

uv run examples/sfx_menu.py
"""

import numpy as np

from blip8 import (
    BELL_TABLE,
    SINE_TABLE,
    at,
    crunch,
    envelope,
    layer,
    play,
    sfx,
    triangle,
    wavetable,
)

for name in ("blip", "select", "back", "coin"):
    print(f"ui        → sfx.{name}()")
    play(getattr(sfx, name)())

for name in ("jump", "powerup", "laser", "hurt", "explosion", "chime"):
    print(f"action    → sfx.{name}()")
    play(getattr(sfx, name)())

for name in ("kick", "snare", "hat", "crash"):
    print(f"drum      → sfx.{name}()")
    play(getattr(sfx, name)())

print("\nwavetable → SINE_TABLE: the purest tone, no character")
play(envelope(wavetable(SINE_TABLE, freq=440, length=0.6), release=0.1))

print("wavetable → BELL_TABLE: a sine with an octave mixed in")
play(envelope(wavetable(BELL_TABLE, freq=440, length=0.6), release=0.1))

print("wavetable → four numbers of your own: [1, 0.3, -0.3, -1]")
play(envelope(wavetable([1.0, 0.3, -0.3, -1.0], freq=440, length=0.6), release=0.1))

for bits in (16, 4, 3, 2):
    print(f"crunch    → {bits} bits ({2**bits} volume levels)")
    play(envelope(crunch(wavetable(SINE_TABLE, freq=330, length=0.5), bits=bits), release=0.1))

BASS = ((0.0, 55), (0.5, 82), (1.0, 55), (1.5, 110))

groove = layer(
    *[
        at(beat + offset, sound)
        for beat in (0.0, 1.0)
        for offset, sound in (
            [(0.0, sfx.kick()), (0.25, sfx.snare())]
            + [(0.5, sfx.kick()), (0.75, sfx.snare())]
            + [(eighth * 0.125, sfx.hat()) for eighth in range(8)]
        )
    ],
    *[
        at(time, envelope(triangle(freq=freq, length=0.5, volume=0.3), release=0.1))
        for time, freq in BASS
    ],
)

print("\ngroove    → kick, snare, hats and a bassline")
play(groove)
print(f"(peak {np.max(np.abs(groove)):.2f})")
