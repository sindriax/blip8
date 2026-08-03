"""Shapers: functions that transform an existing array of samples."""

import numpy as np

from .wave import SAMPLE_RATE


def envelope(
    samples: np.ndarray,
    attack: float = 0.01,
    decay: float = 0.0,
    sustain: float = 1.0,
    release: float = 0.05,
) -> np.ndarray:
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
    return samples * gain


def crunch(samples: np.ndarray, bits: int = 4) -> np.ndarray:
    """Quantise samples to 2**bits levels — bitcrushing.

    bits=4 matches the Game Boy's wave channel. Lower is grittier.
    """
    half = 2**bits / 2
    return np.round(samples * half) / half
