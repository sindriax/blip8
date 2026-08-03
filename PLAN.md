# blip8 — the plan

NES-style sound and music from code. Four voices, no samples. The library I
should have written the first time, instead of the throwaway synth scripts in
ho-chi-run and mua-mua.

**The other goal of this repo, stated plainly: I'm learning Python with it.**
Rules of engagement for any AI session in here:
- Explain things in junior terms — I know TypeScript/Go/Kotlin, not Python.
- I write the phase code myself; Claude explains, reviews, and unblocks.
  Scaffolding whole phases for me defeats the point of the repo.
- Every phase must end with something I can HEAR.

## How the NES made sound (the 60-second version)

The NES audio chip had 4 usable voices, each stuck with one waveform:

| Voice | Waveform | Used for | blip8 status |
|---|---|---|---|
| Pulse 1 | square wave | melody | ✅ `square()` exists |
| Pulse 2 | square wave | harmony | ✅ same function |
| Triangle | triangle wave | basslines | ⬜ phase 1 |
| Noise | random static | drums, crashes, explosions | ⬜ phase 1 |

Square waves have one knob, `duty` (how much of each cycle is spent "up"):
0.5 sounds round, 0.125 sounds thin. That knob is most of the NES's personality.

## Phases

- [x] **Phase 0 — first beep** (scaffolded). `uv run examples/first_beep.py`
      plays two square-wave notes. Read `src/blip8/wave.py` top to bottom —
      it's short and heavily commented; it's the whole idea of the library
      in 40 lines.
- [ ] **Phase 1 — the other two voices + the crash sound.** Write
      `triangle(freq, length)` and `noise(length)` in `wave.py`, then make
      them *feel* like something with two tools: an envelope (fade-out so
      notes stop clicking at the end) and a pitch sweep (noise falling from
      high to low = a crash; rising square = a power-up).
      *Python learned: writing functions, NumPy array math, slicing.*
- [ ] **Phase 2 — the sfx recipe API.** A friendly layer like
      `sfx.blip(freq=880)`, `sfx.crash()`, `sfx.powerup()` so game repos read
      like recipes, not math homework.
      *Python learned: modules, dataclasses, keyword arguments, defaults.*
- [ ] **Phase 3 — notes and patterns.** Note names ("E5") → frequencies, a
      pattern format, arpeggios. First actual melody comes out.
      *Python learned: dicts, parsing strings, classes.*
- [ ] **Phase 4 — plant the flag.** Publish 0.1.0 to PyPI (`uv publish`) —
      the name stays free only until someone claims it. Add one game recipe
      file (mua-mua's UI sounds) to prove the workflow.
      *Python learned: packaging, versioning, what `pip install blip8` does.*
- [ ] **Phase 5 — the party trick.** MIDI import (`mido` library) +
      auto-arrangement onto the four voices + `blip8 cover song.mid` CLI.
      *Python learned: third-party libs, argparse, real file parsing.*
- [ ] **Phase 6 — someday/maybe.** Vibrato, live playground with hot reload,
      procedural radio for vaultwave-fm.

## Cost

€0 forever, structurally: no APIs, no hosting, no accounts (PyPI is free).
Pure Python + NumPy, runs on this laptop, output is .wav files.
