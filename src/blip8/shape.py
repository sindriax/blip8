"""Shapers: functions that transform an existing array of samples."""

import numpy as np

from .wave import SAMPLE_RATE, Samples


def envelope(
    samples: Samples,
    attack: float = 0.01,
    decay: float = 0.0,
    sustain: float = 1.0,
    release: float = 0.05,
) -> Samples:
    """Apply an ADSR volume curve.

        attack   ┌╮                 seconds to fade in from silence
        decay    │╰──╮              seconds to settle to `sustain`
        sustain  │   ────────╮      level held for the remaining time
        release  └           ╰─╮    seconds to fade out to silence

    `sustain` is a level from 0.0 to 1.0; the others are durations in seconds.
    Stages longer than the sound are scaled down proportionally rather than
    raising.

    Fades are linear. Real instruments decay on a curve.
    """
    if not 0.0 <= sustain <= 1.0:
        raise ValueError(f"sustain is a level between 0.0 and 1.0, got {sustain}")
    if min(attack, decay, release) < 0:
        raise ValueError("attack, decay and release must not be negative")

    count = len(samples)

    attack_len = int(attack * SAMPLE_RATE)
    decay_len = int(decay * SAMPLE_RATE)
    release_len = int(release * SAMPLE_RATE)

    total_stages = attack_len + decay_len + release_len
    if total_stages > count:
        squeeze = count / total_stages
        attack_len = int(attack_len * squeeze)
        decay_len = int(decay_len * squeeze)
        release_len = int(release_len * squeeze)

    sustain_len = count - attack_len - decay_len - release_len

    gain = np.concatenate(
        [
            np.linspace(0.0, 1.0, attack_len),
            np.linspace(1.0, sustain, decay_len),
            np.full(sustain_len, sustain),
            np.linspace(sustain, 0.0, release_len),
        ]
    )
    shaped: Samples = samples * gain
    return shaped


def crunch(samples: Samples, bits: int = 4) -> Samples:
    """Quantise samples to 2**bits levels, which is bitcrushing.

    bits=4 matches the Game Boy's wave channel. Lower is grittier. Below 2 the
    result is silence rather than grit, so it is rejected.
    """
    if bits < 2:
        raise ValueError(f"bits must be at least 2, got {bits}")

    half = 2**bits / 2
    crushed: Samples = np.round(samples * half) / half
    return crushed
