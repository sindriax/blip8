# blip8

NES-style sound and music from code. Four voices, no samples.

I kept writing throwaway scripts to synthesize sound for my games
([ho-chi-run](https://sindriax.itch.io/ho-chi-run), mua-mua). This is the
library I should have written the first time.

```python
from blip8 import play, square

play(square(freq=440, length=0.5))          # 1983 in one line
play(square(freq=440, length=0.5, duty=0.125))  # same note, thinner — the NES knob
```

## Run the first beep

```sh
uv run examples/first_beep.py
```

That's it — `uv` handles the environment and dependencies on first run.

## Status

Phase 0 of [PLAN.md](PLAN.md). The roadmap ends with `blip8 cover song.mid`
turning any MIDI file into an 8-bit cover, and with my games pulling their
soundtracks from this package instead of copy-pasted scripts.
