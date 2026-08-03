"""Note names, patterns and a four-voice arrangement.

uv run examples/melody.py
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
    square,
    triangle,
)

TUNE = "E4 E4 F4 G4 G4 F4 E4 D4 C4 C4 D4 E4 E4 . D4 ."
BEAT = 60.0 / 140

print("1a. a C major scale, written as note names")
play(melody("C4 D4 E4 F4 G4 A4 B4 C5", bpm=120, steps_per_beat=2))

print(f"1b. note('A4') = {note('A4')} Hz, the same as writing freq=440")
play(square(freq=note("A4"), length=0.4))

print("2a. Ode to Joy on the square voice")
play(melody(TUNE, bpm=140, steps_per_beat=2))

print("2b. the same notes on the triangle voice — softer, wrong for a lead")
play(melody(TUNE, bpm=140, steps_per_beat=2, voice=triangle))

print("2c. the same notes on a thin duty — the classic NES lead")
play(melody(TUNE, bpm=140, steps_per_beat=2, duty=0.125))

print("3a. chord('C4 E4 G4') — three notes at once, which the NES could not do")
play(chord("C4 E4 G4", length=0.8))

print("3b. arpeggio('C4 E4 G4') — the same notes cycled fast, on one voice")
play(arpeggio("C4 E4 G4", length=0.8))

print("3c. the same arpeggio slowed down until you hear the individual notes")
play(arpeggio("C4 E4 G4", length=0.8, rate=0.12))

print("3d. and sped up past where the ear can separate them")
play(arpeggio("C4 E4 G4", length=0.8, rate=0.012))

# One line per NES channel: pulse 1 melody, pulse 2 harmony, triangle bass,
# noise drums. Levels are low so four voices sum to under 1.0.
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
peak = float(max(abs(song.min()), abs(song.max())))

print("\n4. all four voices together")
play(song)
print(f"   peak {peak:.2f} — {'clipping!' if peak > 1.0 else 'clean, room to spare'}")

print("\n5. the same song through a Game Boy's 4-bit output")
play(crunch(song, bits=4))

print("\n6. and at 2 bits")
play(crunch(song, bits=2))
