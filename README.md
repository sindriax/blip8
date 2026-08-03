# blip8

[![CI](https://github.com/sindriax/blip8/actions/workflows/ci.yml/badge.svg)](https://github.com/sindriax/blip8/actions/workflows/ci.yml)

Chiptune sound synthesis from code — the four voices of the NES and the Game
Boy, generated from scratch. No samples, no recordings, no dependencies beyond
NumPy. Every sound is arithmetic.

```python
from blip8 import play, square, triangle

play(square(freq=440, length=0.5))              # 1983 in one line
play(square(freq=440, length=0.5, duty=0.125))  # same note, thinner — the NES knob
play(square(freq=440, length=0.5) + triangle(freq=220, length=0.5))  # melody + bass
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
uv run examples/first_beep.py    # two square waves, and the duty knob
uv run examples/four_voices.py   # square vs triangle vs noise
```

`uv` sets up Python and installs NumPy on first run — nothing else to do.
Playback shells out to macOS `afplay`; `save()` writes a `.wav` anywhere.

## The voices

The NES sound chip had four, each locked to one waveform. The Game Boy's had
four too, with a twist.

| Voice    | Shape           | Sounds like            | Used for            | Status |
| -------- | --------------- | ---------------------- | ------------------- | ------ |
| Pulse    | square          | buzzy, electronic      | melody, harmony     | ✅ `square()` |
| Triangle | ramp up/down    | soft, flute-ish        | basslines           | ✅ `triangle()` |
| Noise    | random          | static                 | drums, explosions   | ✅ `noise()` |
| Wave     | anything you draw | whatever you make it | the Game Boy's trick | ⬜ planned |

Square waves have one knob, `duty` — how much of each cycle is spent "up".
`0.5` sounds round and hollow, `0.125` thin and nasal. Same pitch, different
character. That knob is most of the NES's personality.

## Develop

```sh
uv run pytest        # 34 tests, all asserting things you can hear
uv run ruff check .  # lint
uv run ruff format . # format
```

The test suite is worth a read if you want to know how you test a *sound*:
every claim in the docstrings turns out to be a claim about numbers.

## Status

Early. Three of four voices exist and make noise. Next up is the envelope —
shaping volume over time, which is what turns raw static into a snare hit and
stops every note ending in a click.

The roadmap ends with `blip8 cover song.mid` turning any MIDI file into an
8-bit cover. See [PLAN.md](PLAN.md).
