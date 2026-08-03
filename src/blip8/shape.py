"""Shaping sound over time.

wave.py *makes* sound. This file *shapes* it — takes an array that already
exists and changes how it behaves from start to finish.

Right now that means one thing: the envelope. It's the difference between a
sound and a *noise you recognise*. Hit a piano key and a drum with the same
force and the volume behaves completely differently over the next second — the
drum is instantly loud then gone, the piano blooms and rings. Neither is about
pitch. That shape is the envelope, and your ear uses it to identify what
something is.
"""

import numpy as np

from .wave import SAMPLE_RATE


def envelope(
    samples: np.ndarray,
    attack: float = 0.01,
    decay: float = 0.0,
    sustain: float = 1.0,
    release: float = 0.05,
) -> np.ndarray:
    """Shape a sound's volume over time. This is ADSR, on every synth ever made.

    Four stages, in order:

        attack   ┌╮                 how long to fade IN from silence
        decay    │╰──╮              how long to settle down to `sustain`
        sustain  │   ────────╮      the level it holds at (0.0 to 1.0)
        release  └           ╰─╮    how long to fade OUT to silence
                 ╰─a─╯╰d╯╰─s──╯╰r╯

    All times are in seconds. `sustain` is a *level*, not a time — it's the
    odd one out, and it fills whatever length is left over.

    Why you want it, concretely:
      - notes stop clicking, because they now end at zero instead of mid-jump
      - `attack=0.001, decay=0.15, sustain=0.0` = a drum hit
      - `attack=0.3` = something soft that swells in, like a pad

    If the stages you asked for are longer than the sound itself, they get
    shrunk proportionally rather than raising an error — a 5-second release on
    a 0.1-second beep is a reasonable thing to ask for by accident.
    """
    count = len(samples)

    # Convert seconds into "how many samples is that". This is the conversion
    # that happens all over audio code: seconds * SAMPLE_RATE = sample count.
    attack_len = int(attack * SAMPLE_RATE)
    decay_len = int(decay * SAMPLE_RATE)
    release_len = int(release * SAMPLE_RATE)

    # Don't let the stages overflow the sound. Scale them all down together so
    # their proportions stay recognisable.
    total_stages = attack_len + decay_len + release_len
    if total_stages > count:
        squeeze = count / total_stages
        attack_len = int(attack_len * squeeze)
        decay_len = int(decay_len * squeeze)
        release_len = int(release_len * squeeze)

    # Sustain gets whatever's left. Can be 0, which is normal for drums.
    sustain_len = count - attack_len - decay_len - release_len

    # Build a "gain" array — one volume multiplier per sample, same length as
    # the sound. np.linspace(a, b, n) is "n evenly spaced numbers from a to b",
    # which is exactly a fade. np.full(n, x) is "n copies of x".
    gain = np.concatenate(
        [
            np.linspace(0.0, 1.0, attack_len),  # fade in
            np.linspace(1.0, sustain, decay_len),  # settle down
            np.full(sustain_len, sustain),  # hold
            np.linspace(sustain, 0.0, release_len),  # fade out
        ]
    )

    # Element-wise multiply: sample 0 gets gain 0, sample 1 gets gain 1...
    # NumPy does all `count` multiplications in one operation, no loop.
    #
    # (These fades are straight lines. Real instruments decay in a curve —
    # fast at first, then trailing off. Good enough for now; it's on the
    # someday list in PLAN.md.)
    return samples * gain
