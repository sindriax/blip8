"""Real game sounds, from the same three waveforms. Run me with:

    uv run examples/sound_design.py

The point of this file: nothing here adds a new *waveform*. Every sound below
is square, triangle or noise with its volume or pitch shaped over time. That
shaping is most of what sound design actually is.
"""

import numpy as np

from blip8 import envelope, noise, play, square, triangle

# --------------------------------------------------------------------------
# 1. The click, and how to kill it
# --------------------------------------------------------------------------
# A raw wave stops wherever it happens to be — usually mid-cycle, with the
# speaker cone shoved out to one side. It snaps back to rest instantly, and
# that snap is an audible tick at the end of every note.

print("1a. raw square — listen for the tick at the end")
play(square(freq=440, length=0.4))

print("1b. same note with a fade in and out — clean")
play(envelope(square(freq=440, length=0.4), attack=0.01, release=0.05))


# --------------------------------------------------------------------------
# 2. Percussion: noise + a fast fade
# --------------------------------------------------------------------------
# Identical raw material both times. The only difference is how quickly the
# volume falls to zero, and that alone decides which instrument you hear.

print("2a. snare — noise, gone in 150ms")
play(envelope(noise(length=0.15), attack=0.001, decay=0.15, sustain=0.0, release=0.0))

print("2b. cymbal crash — the same noise, taking 1.5s to die")
play(envelope(noise(length=1.5), attack=0.001, decay=1.5, sustain=0.0, release=0.0))

print("2c. kick drum — a triangle sliding down fast, not noise at all")
play(
    envelope(
        triangle(freq=(120, 40), length=0.25),
        attack=0.001,
        decay=0.25,
        sustain=0.0,
        release=0.0,
    )
)


# --------------------------------------------------------------------------
# 3. Pitch sweeps: pass (start, end) instead of one number
# --------------------------------------------------------------------------

print("3a. laser — pitch falling off a cliff")
play(envelope(square(freq=(1800, 200), length=0.25, duty=0.25), release=0.05))

print("3b. power-up — the same idea upside down")
play(envelope(square(freq=(200, 1600), length=0.4, duty=0.5), release=0.05))

print("3c. jump — a short rise, thin duty")
play(envelope(square(freq=(400, 900), length=0.12, duty=0.125), release=0.03))


# --------------------------------------------------------------------------
# 4. Two notes are enough to be recognisable
# --------------------------------------------------------------------------
# The classic coin sound: a short high note, then a longer one above it.
# Adding two arrays plays them at the SAME time. To play them one AFTER the
# other you join them end-to-end with np.concatenate. That distinction is the
# whole difference between a chord and a melody, and it's what phase 3 builds on.

coin = np.concatenate(
    [
        envelope(square(freq=988, length=0.07, duty=0.5), attack=0.001, release=0.01),
        envelope(square(freq=1319, length=0.35, duty=0.5), attack=0.001, release=0.2),
    ]
)
print("4. coin")
play(coin)


# --------------------------------------------------------------------------
# 5. All of it at once
# --------------------------------------------------------------------------
# Adding arrays mixes them, the way a mixing desk sums channels. Note the
# lowered volumes: three sounds at 0.5 each would sum past 1.0 and clip.

print("5. bass + melody + snare together")
bar = (
    triangle(freq=110, length=0.6, volume=0.4)
    + envelope(square(freq=440, length=0.6, duty=0.25, volume=0.25), attack=0.01, release=0.1)
    + envelope(noise(length=0.6, volume=0.2), attack=0.001, decay=0.12, sustain=0.0, release=0.0)
)
play(bar)
