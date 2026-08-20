# blip8

[![PyPI](https://img.shields.io/pypi/v/blip8)](https://pypi.org/project/blip8/)
[![Python](https://img.shields.io/pypi/pyversions/blip8)](https://pypi.org/project/blip8/)

Chiptune sound synthesis from code: the four voices of the NES and the Game
Boy, generated from scratch. No samples, no recordings, no dependencies beyond
NumPy. Every sound is arithmetic.

```sh
pip install blip8      # or: uv add blip8
```

```python
from blip8 import melody, play, sfx

play(melody("E4 E4 F4 G4 G4 F4 E4 D4", bpm=140))   # a tune, in one line
play(sfx.coin())
play(sfx.kick() + sfx.hat())                        # adding arrays mixes them
```

Or build sounds yourself from the raw waveforms:

```python
from blip8 import envelope, noise, play, square, triangle

play(square(freq=440, length=0.5))              # 1983 in one line
play(square(freq=440, length=0.5, duty=0.125))  # same note, thinner (the NES knob)
play(square(freq=440, length=0.5) + triangle(freq=220, length=0.5))  # melody + bass

play(square(freq=(1800, 200), length=0.25))     # a (start, end) pitch = laser
play(envelope(noise(length=1.5), decay=1.5, sustain=0.0))  # noise + fade = cymbal
```

## the blip8 shelf

- 🏠 [blip8.sindriax.dev](https://blip8.sindriax.dev): the front door, all three in one place
- 🦇 [blip8](https://github.com/sindriax/blip8): the Python chiptune synthesis library. `pip install blip8`
- 🧪 [blip8 lab](https://blip8.sindriax.dev/lab/): make 8-bit sounds in your browser ([source](https://github.com/sindriax/blip8-lab))
- 📦 [blip8 sounds](https://sindriax.itch.io/blip8-sounds): free CC0 chiptune SFX packs, generated from code ([source](https://github.com/sindriax/blip8-sounds))

## Why I made this

Every time I built a game I ended up writing the same throwaway script again:
forty lines of NumPy to make a coin sound, pasted into the repo, tweaked until
it was close enough, then forgotten. The next game started from zero.

So I wrote the library I should have written the first time. Now it is
`pip install blip8` and `sfx.coin()`.

It is also my first real Python project, coming from TypeScript and Go, and an
excuse to explore how synthesis actually works. The NES had four voices and no
way to play a recording, which makes it a small enough system to build from
first principles and understand completely.

## Hear it

```sh
uv run examples/first_beep.py     # two square waves, and the duty knob
uv run examples/four_voices.py    # square vs triangle vs noise
uv run examples/sound_design.py   # snare, crash, kick, laser, power-up, coin
uv run examples/sfx_menu.py       # every recipe, the wave channel, a drum groove
uv run examples/melody.py         # actual music: four voices, chords vs arpeggios
uv run examples/see_it.py         # print the waveforms instead of playing them
uv run examples/save_a_pack.py    # write 17 .wav files, no audio device needed
```

`uv` sets up Python and installs NumPy on first run, so there is nothing else
to do. `save()` writes a `.wav` anywhere. `play()` shells out to whichever
player the platform has (`afplay` on macOS, `aplay`, `paplay` or `ffplay` on
Linux, `winsound` on Windows) and raises a clear error if none is present.

## The voices

The NES sound chip had four, each locked to one waveform. The Game Boy's had
four too, with a twist.

| Voice    | Shape             | Sounds like          | Used for             | Status           |
| -------- | ----------------- | -------------------- | -------------------- | ---------------- |
| Pulse    | square            | buzzy, electronic    | melody, harmony      | ✅ `square()`    |
| Triangle | ramp up/down      | soft, flute-ish      | basslines            | ✅ `triangle()`  |
| Noise    | random            | static               | drums, explosions    | ✅ `noise()`     |
| Wave     | anything you draw | whatever you make it | the Game Boy's trick | ✅ `wavetable()` |

Square waves have one knob, `duty`, which is how much of each cycle is spent
"up". `0.5` sounds round and hollow, `0.125` thin and nasal. Same pitch,
different character. That knob is most of the NES's personality.

## Shaping

The waveforms are the raw material. Shaping them over time is what makes them
recognisable as *things*.

**`envelope()`** controls volume over time, the ADSR curve every synth has.
It's why a drum and a piano playing the same note are unmistakable. It also
stops notes ending in a click, since they now finish at silence instead of
mid-cycle.

**Pitch sweeps** come free: pass `freq=(start, end)` instead of one number and
the note glides. Falling is a laser, rising is a power-up.

Between them, the same `noise()` becomes a snare (fast fade) or a cymbal
(slow fade), and a `triangle()` sliding from 120 Hz to 40 Hz becomes a kick
drum. `examples/sound_design.py` plays all of it.

**`crunch()`** throws precision away on purpose. `bits=4` allows only 16 volume
levels, which is what the Game Boy actually had. Producers call this
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
`save()`. Every one is built only from the waveforms and shapers above. Open
`src/blip8/sfx.py` to see exactly what any given sound is made of.

## Music

Nobody thinks in Hz, so `note("E5")` converts names to frequencies. An octave
up doubles the frequency, and a semitone is the twelfth root of two.

Patterns are strings, one token per step in time. A note name plays, `.` holds
the note before it, `-` rests:

```python
melody("C4 E4 G4 C5", bpm=120)                    # four sixteenth notes
melody("C2 . . . G2 . . .", voice=triangle)       # a bassline, notes held
melody("C5 - C5 -", duty=0.125)                   # extra kwargs reach the voice
```

That's a **tracker**, the text-grid format chiptune musicians actually use,
arrived at because it's the obvious way to write music as a string.

`chord("C4 E4 G4")` plays notes together; `arpeggio("C4 E4 G4")` plays them one
at a time, fast, until your ear fuses them into a chord. The second one exists
because the NES only had four voices and couldn't spare three for one chord,
which is why chiptune has that frantic bubbling sound.

Arrangement is two functions. `at(time, sound)` delays; `layer(*sounds)` mixes,
padding to the longest:

```python
layer(at(0.0, sfx.kick()), at(0.5, sfx.snare()))
```

## See it

GitHub can't play audio, so `show()` draws the waveform in your terminal:
min/max per column, the way an audio editor does. Zoom in on a few cycles to
see the shape, or out to a whole sound to see its envelope.

```python
from blip8 import show, square
show(square(freq=440, length=0.007), "three cycles")
```

```
square, zoomed in on three cycles
███████████         ███████████         ███████████           ██
          █         █         █         █         █           █ 
          █         █         █         █         █           █ 
          █         █         █         █         █           █ 
          █         █         █         █         █           █ 
──────────█─────────█─────────█─────────█─────────█───────────█─
          █         █         █         █         █           █ 
          █         █         █         █         █           █ 
          █         █         █         █         █           █ 
          █         █         █         █         █           █ 
          ███████████         ███████████         █████████████ 

triangle, the same three cycles
█                  ██                  ██                    ██ 
██                ████                ████                  ██ █
 ██              ██  ██              ██  ██                ██   
  ██            ██    ██            ██    ██              ██    
   ██          ██      ██          ██      ██           ██      
────██────────██────────██────────██────────██─────────██───────
     ██      ██          ██      ██          ██       ██        
      ██    ██            ██    ██            ██     ██         
       ██  ██              ██  ██              ██  ██           
        ████                ████                ████            
         ██                  ██                  ██             

a cymbal crash, zoomed out to 1.2 seconds
███                                                             
█████████████████                                               
███████████████████████████████                                 
████████████████████████████████████████████                    
██████████████████████████████████████████████████████████      
████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████      
████████████████████████████████████████████                    
██████████████████████████████                                  
█████████████████                                               
███                                                             

```

`uv run examples/see_it.py` prints all four voices, the duty knob, envelopes,
sweeps and bit crushing.

## Develop

```sh
uv run pytest         # 241 tests, all asserting things you can hear
uv run mypy src tests # type check, strict
uv run ruff check .   # lint
uv run ruff format .  # format
```

CI runs all four on Linux, macOS and Windows across Python 3.12 and 3.13, then
builds the package and installs the wheel into a clean environment to prove it
imports.

The package ships `py.typed`, so the annotations reach your editor rather than
stopping at the package boundary. `Samples` and `Pitch` are exported for
annotating your own code.

The test suite is worth a read if you want to know how you test a *sound*:
every claim in the docstrings turns out to be a claim about numbers.

Releases go out from a version tag through PyPI Trusted Publishing, so no API
token exists to leak. Design decisions with real tradeoffs are recorded in
[docs/decisions](docs/decisions/).

## Status

All four voices, envelopes, sweeps, bit crushing, 14 ready-made game sounds,
note names, patterns, chords, arpeggios and arrangement. It makes music now.

The roadmap ends with `blip8 cover song.mid` turning any MIDI file into an
8-bit cover.

