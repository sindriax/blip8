# blip8

[![CI](https://github.com/sindriax/blip8/actions/workflows/ci.yml/badge.svg)](https://github.com/sindriax/blip8/actions/workflows/ci.yml)

Chiptune sound synthesis from code — the four voices of the NES and the Game
Boy, generated from scratch. No samples, no recordings, no dependencies beyond
NumPy. Every sound is arithmetic.

```python
from blip8 import play, sfx

play(sfx.coin())
play(sfx.laser())
play(sfx.kick() + sfx.hat())   # adding arrays mixes them
```

Or build sounds yourself from the raw waveforms:

```python
from blip8 import envelope, noise, play, square, triangle

play(square(freq=440, length=0.5))              # 1983 in one line
play(square(freq=440, length=0.5, duty=0.125))  # same note, thinner — the NES knob
play(square(freq=440, length=0.5) + triangle(freq=220, length=0.5))  # melody + bass

play(square(freq=(1800, 200), length=0.25))     # a (start, end) pitch = laser
play(envelope(noise(length=1.5), decay=1.5, sustain=0.0))  # noise + fade = cymbal
```

## Why

Digital audio is just a very long list of numbers describing where a speaker
cone should be. Sounds that defined a generation of games came out of chips
that could only make four shapes. That's a small enough system to build from
first principles and understand completely — so this builds it, one voice at a
time, and every function is commented with what it's actually doing to your
ears.

## Hear it

```sh
uv run examples/first_beep.py     # two square waves, and the duty knob
uv run examples/four_voices.py    # square vs triangle vs noise
uv run examples/sound_design.py   # snare, crash, kick, laser, power-up, coin
uv run examples/sfx_menu.py       # every recipe, the wave channel, a drum groove
```

`uv` sets up Python and installs NumPy on first run — nothing else to do.
Playback shells out to macOS `afplay`; `save()` writes a `.wav` anywhere.

## The voices

The NES sound chip had four, each locked to one waveform. The Game Boy's had
four too, with a twist.

| Voice    | Shape             | Sounds like          | Used for             | Status          |
| -------- | ----------------- | -------------------- | -------------------- | --------------- |
| Pulse    | square            | buzzy, electronic    | melody, harmony      | ✅ `square()`   |
| Triangle | ramp up/down      | soft, flute-ish      | basslines            | ✅ `triangle()` |
| Noise    | random            | static               | drums, explosions    | ✅ `noise()`    |
| Wave     | anything you draw | whatever you make it | the Game Boy's trick | ✅ `wavetable()` |

Square waves have one knob, `duty` — how much of each cycle is spent "up".
`0.5` sounds round and hollow, `0.125` thin and nasal. Same pitch, different
character. That knob is most of the NES's personality.

## Shaping

The waveforms are the raw material; shaping them over time is what makes them
recognisable as *things*.

**`envelope()`** controls volume over time — the ADSR curve every synth has.
It's why a drum and a piano playing the same note are unmistakable. It also
stops notes ending in a click, since they now finish at silence instead of
mid-cycle.

**Pitch sweeps** come free: pass `freq=(start, end)` instead of one number and
the note glides. Falling is a laser, rising is a power-up.

Between them, the same `noise()` becomes a snare (fast fade) or a cymbal
(slow fade), and a `triangle()` sliding from 120 Hz to 40 Hz becomes a kick
drum. `examples/sound_design.py` plays all of it.

**`crunch()`** throws precision away on purpose — `bits=4` allows only 16
volume levels, which is what the Game Boy actually had. Producers call this
bitcrushing and reach for it deliberately.

## Recipes

`sfx` is the cookbook: 14 game sounds with the numbers already chosen.

```python
sfx.blip()   sfx.select()  sfx.back()   sfx.coin()
sfx.jump()   sfx.powerup() sfx.laser()  sfx.hurt()
sfx.explosion()  sfx.chime()
sfx.kick()   sfx.snare()   sfx.hat()    sfx.crash()
```

Each returns an array rather than playing it, so they mix (`+`), chain, and
`save()`. Every one is built only from the waveforms and shapers above — open
`src/blip8/sfx.py` to see exactly what any given sound is made of.

## Develop

```sh
uv run pytest        # 140 tests, all asserting things you can hear
uv run ruff check .  # lint
uv run ruff format . # format
```

The test suite is worth a read if you want to know how you test a *sound*:
every claim in the docstrings turns out to be a claim about numbers.

## Status

All four voices, envelopes, pitch sweeps, bit crushing, and 14 ready-made game
sounds. Next up: note names ("E5") instead of raw frequencies, and a pattern
format — the point where melodies start coming out instead of single effects.

The roadmap ends with `blip8 cover song.mid` turning any MIDI file into an
8-bit cover.
