"""Render a folder of .wav files instead of playing them.

The only example that needs no audio device, so it also runs on a build
machine. This is the library as an asset pipeline: the sounds a game ships
are a script, not a folder someone dragged in.

uv run examples/save_a_pack.py
"""

from pathlib import Path

from blip8 import (
    SAMPLE_RATE,
    Samples,
    at,
    envelope,
    layer,
    melody,
    save,
    sfx,
    square,
    triangle,
)

OUT = Path("pack")

PACK: dict[str, Samples] = {
    "ui/blip": sfx.blip(),
    "ui/select": sfx.select(),
    "ui/back": sfx.back(),
    "pickups/coin": sfx.coin(),
    "player/jump": sfx.jump(),
    "player/hurt": sfx.hurt(),
    "weapons/laser": sfx.laser(),
    "weapons/explosion": sfx.explosion(),
    "drums/kick": sfx.kick(),
    "drums/snare": sfx.snare(),
    "drums/hat": sfx.hat(),
    "drums/crash": sfx.crash(),
    "jingles/powerup": sfx.powerup(),
    "jingles/chime": sfx.chime(),
}

PACK["player/land"] = envelope(
    triangle(freq=(200, 60), length=0.18), attack=0.001, decay=0.18, sustain=0.0
)
PACK["jingles/title"] = melody("C5 E5 G5 C6 . G5 E5 .", bpm=150, voice=square, duty=0.25)
PACK["drums/groove"] = layer(
    at(0.0, sfx.kick()),
    at(0.25, sfx.hat()),
    at(0.5, sfx.snare()),
    at(0.75, sfx.hat()),
)

for name, samples in PACK.items():
    path = OUT / f"{name}.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    save(samples, str(path))
    print(f"{path}  {len(samples) / SAMPLE_RATE:5.2f}s")

print(f"\n{len(PACK)} files under {OUT}/, mono 16-bit at {SAMPLE_RATE} Hz")
print("change a number, run it again, and the whole pack is different")
