"""Game sounds from three waveforms. Run with: uv run examples/sound_design.py

Nothing here adds a new waveform. Every sound is square, triangle or noise with
its volume or pitch shaped over time.
"""

from blip8 import envelope, noise, play, sequence, square, triangle

print("1a. raw square — listen for the tick at the end")
play(square(freq=440, length=0.4))

print("1b. same note with a fade in and out")
play(envelope(square(freq=440, length=0.4), attack=0.01, release=0.05))

print("2a. snare — noise, gone in 150ms")
play(envelope(noise(length=0.15), attack=0.001, decay=0.15, sustain=0.0, release=0.0))

print("2b. cymbal crash — the same noise over 1.5s")
play(envelope(noise(length=1.5), attack=0.001, decay=1.5, sustain=0.0, release=0.0))

print("2c. kick drum — a falling triangle, no noise involved")
play(
    envelope(
        triangle(freq=(120, 40), length=0.25),
        attack=0.001,
        decay=0.25,
        sustain=0.0,
        release=0.0,
    )
)

print("3a. laser — falling pitch")
play(envelope(square(freq=(1800, 200), length=0.25, duty=0.25), release=0.05))

print("3b. power-up — rising pitch")
play(envelope(square(freq=(200, 1600), length=0.4, duty=0.5), release=0.05))

print("3c. jump — a short rise on a thin duty")
play(envelope(square(freq=(400, 900), length=0.12, duty=0.125), release=0.03))

print("4. coin — two notes end to end")
play(
    sequence(
        envelope(square(freq=988, length=0.07), attack=0.001, release=0.01),
        envelope(square(freq=1319, length=0.35), attack=0.001, release=0.2),
    )
)

print("5. bass, melody and a snare mixed together")
play(
    triangle(freq=110, length=0.6, volume=0.4)
    + envelope(square(freq=440, length=0.6, duty=0.25, volume=0.25), attack=0.01, release=0.1)
    + envelope(noise(length=0.6, volume=0.2), attack=0.001, decay=0.12, sustain=0.0, release=0.0)
)
