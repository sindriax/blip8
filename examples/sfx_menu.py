"""The whole cookbook, plus the Game Boy voice. Run me with:

    uv run examples/sfx_menu.py

Compare this file to examples/sound_design.py. Same sounds, but there the
recipe was spelled out every time; here each one is a single call. That's all
phase 2 is — the numbers moved into the library so they stop cluttering the
place where you actually use them.
"""

import numpy as np

from blip8 import (
    BELL_TABLE,
    SAMPLE_RATE,
    SINE_TABLE,
    crunch,
    envelope,
    play,
    sfx,
    triangle,
    wavetable,
)

# --------------------------------------------------------------------------
# 1. The cookbook
# --------------------------------------------------------------------------

for name in ("blip", "select", "back", "coin"):
    print(f"ui        → sfx.{name}()")
    play(getattr(sfx, name)())

for name in ("jump", "powerup", "laser", "hurt", "explosion", "chime"):
    print(f"action    → sfx.{name}()")
    play(getattr(sfx, name)())

for name in ("kick", "snare", "hat", "crash"):
    print(f"drum      → sfx.{name}()")
    play(getattr(sfx, name)())


# --------------------------------------------------------------------------
# 2. The Game Boy's fourth voice: waveforms you define yourself
# --------------------------------------------------------------------------

print("\nwavetable → SINE_TABLE: the purest possible tone, no character")
play(envelope(wavetable(SINE_TABLE, freq=440, length=0.6), release=0.1))

print("wavetable → BELL_TABLE: a sine with an octave mixed in")
play(envelope(wavetable(BELL_TABLE, freq=440, length=0.6), release=0.1))

print("wavetable → four numbers of your own: [1, 0.3, -0.3, -1]")
play(envelope(wavetable([1.0, 0.3, -0.3, -1.0], freq=440, length=0.6), release=0.1))


# --------------------------------------------------------------------------
# 3. crunch(): the 4-bit grit
# --------------------------------------------------------------------------
# Same note four times, allowed fewer and fewer volume levels each time.
# 4 bits is what the real Game Boy had.

for bits in (16, 4, 3, 2):
    print(f"crunch    → {bits} bits ({2**bits} volume levels)")
    smooth = wavetable(SINE_TABLE, freq=330, length=0.5)
    play(envelope(crunch(smooth, bits=bits), release=0.1))


# --------------------------------------------------------------------------
# 4. A drum groove, to prove the recipes actually combine
# --------------------------------------------------------------------------
# Sounds get *placed* into a fixed-length buffer at a time offset. Adding
# arrays at the same offset mixes them; adding at different offsets is rhythm.
# This is the seed of phase 3.

bar = np.zeros(int(SAMPLE_RATE * 2.0))


def place(sound: np.ndarray, at: float) -> None:
    """Mix `sound` into `bar`, starting `at` seconds in."""
    start = int(at * SAMPLE_RATE)
    end = min(start + len(sound), len(bar))
    # `+=` on a slice adds in place — it mixes rather than overwrites.
    bar[start:end] += sound[: end - start]


for beat in (0.0, 1.0):  # two beats' worth, repeated
    place(sfx.kick(), beat + 0.0)
    place(sfx.snare(), beat + 0.25)
    place(sfx.kick(), beat + 0.5)
    place(sfx.snare(), beat + 0.75)
    for eighth in range(8):
        place(sfx.hat(), beat + eighth * 0.125)

# A bassline under it, using the triangle voice the way the NES did.
place(envelope(triangle(freq=55, length=0.5, volume=0.3), release=0.1), 0.0)
place(envelope(triangle(freq=82, length=0.5, volume=0.3), release=0.1), 0.5)
place(envelope(triangle(freq=55, length=0.5, volume=0.3), release=0.1), 1.0)
place(envelope(triangle(freq=110, length=0.5, volume=0.3), release=0.1), 1.5)

print("\ngroove    → kick, snare, hats and a bassline, all from sfx recipes")
play(bar)
print(f"(peak level {np.max(np.abs(bar)):.2f} — under 1.0, so nothing clips)")
