"""The first actual music. Run me with:

    uv run examples/melody.py

Up to now everything has been single sound effects. This is where blip8 starts
making tunes, and where the NES's four-voice limit stops being trivia and
starts being a constraint you can hear.
"""

from blip8 import (
    arpeggio,
    at,
    chord,
    crunch,
    layer,
    melody,
    note,
    play,
    sfx,
    silence,
    square,
    triangle,
)

# --------------------------------------------------------------------------
# 1. Names instead of numbers
# --------------------------------------------------------------------------

print("1a. a C major scale, written as note names")
play(melody("C4 D4 E4 F4 G4 A4 B4 C5", bpm=120, steps_per_beat=2))

print(f"1b. the same A4 two ways: note('A4') = {note('A4')} Hz")
play(square(freq=note("A4"), length=0.4))
play(square(freq=440, length=0.4))


# --------------------------------------------------------------------------
# 2. A tune. Ode to Joy, because it's out of copyright and everyone knows it
# --------------------------------------------------------------------------
# "." holds the previous note for another step, "-" is a rest.

TUNE = "E4 E4 F4 G4 G4 F4 E4 D4 C4 C4 D4 E4 E4 . D4 ."

print("2a. the melody, on the square voice")
play(melody(TUNE, bpm=140, steps_per_beat=2))

print("2b. same notes on the triangle voice — softer, and wrong for a lead")
play(melody(TUNE, bpm=140, steps_per_beat=2, voice=triangle))

print("2c. same notes, thin duty — this is the classic NES lead sound")
play(melody(TUNE, bpm=140, steps_per_beat=2, duty=0.125))


# --------------------------------------------------------------------------
# 3. Chord vs arpeggio: the four-voice limit, made audible
# --------------------------------------------------------------------------
# A chord needs three voices at once. The NES had four in total, and needed
# them for melody, bass and drums — so composers couldn't afford it.

print("3a. chord('C4 E4 G4') — three notes at once. The NES could not do this.")
play(chord("C4 E4 G4", length=0.8))

print("3b. arpeggio('C4 E4 G4') — the same notes one at a time, fast. One voice.")
play(arpeggio("C4 E4 G4", length=0.8))

print("3c. the same arpeggio slowed down, so you can hear the trick")
play(arpeggio("C4 E4 G4", length=0.8, rate=0.12))

print("3d. and sped up past where your ear can separate them")
play(arpeggio("C4 E4 G4", length=0.8, rate=0.012))


# --------------------------------------------------------------------------
# 4. Four voices at once — an actual arrangement
# --------------------------------------------------------------------------
# One line per NES channel, exactly as a 1987 composer would have budgeted it:
#
#   pulse 1  → melody       (square, thin duty so it cuts through)
#   pulse 2  → harmony      (arpeggios, faking chords)
#   triangle → bassline
#   noise    → drums
#
# Volumes are deliberately low. Four voices at 0.4 each would sum past 1.0 and
# clip; the mix below peaks under 1.0, which the print at the end confirms.

BEAT = 60.0 / 140  # seconds per beat at 140 bpm

lead = melody(TUNE, bpm=140, steps_per_beat=2, duty=0.125, volume=0.25)

bass = melody(
    "C2 . . . G2 . . . C2 . . . G2 . . .",
    bpm=140,
    steps_per_beat=2,
    voice=triangle,
    volume=0.28,
)

harmony = layer(
    at(0, arpeggio("C4 E4 G4", length=BEAT * 4, volume=0.10)),
    at(BEAT * 4, arpeggio("G3 B3 D4", length=BEAT * 4, volume=0.10)),
)

# The sfx recipes are tuned to be heard alone, so they're too loud in a mix.
# Multiplying an array by a number scales its volume — this is a fader.
DRUM_LEVEL = 0.6

drums = layer(
    *[
        sound
        for beat in range(8)
        for sound in (
            at(beat * BEAT, (sfx.kick() if beat % 2 == 0 else sfx.snare()) * DRUM_LEVEL),
            at(beat * BEAT + BEAT / 2, sfx.hat() * DRUM_LEVEL),
        )
    ]
)

song = layer(lead, bass, harmony, drums)

# Mixing is mostly this: adding things up and then discovering it's too loud.
# The first version of this example peaked at 1.13, which clips — everything
# above 1.0 gets flattened on save and you hear crackle. The volumes above are
# the fix. Print the peak so the problem is visible rather than a surprise.
peak = float(max(abs(song.min()), abs(song.max())))

print("\n4. all four voices together")
play(song)
print(f"   peak {peak:.2f} — {'clipping!' if peak > 1.0 else 'clean, room to spare'}")

print("\n5. the same song through a real Game Boy's 4-bit output")
play(crunch(song, bits=4))

print("\n6. and at 2 bits, for laughs")
play(layer(crunch(song, bits=2), silence(0.1)))
