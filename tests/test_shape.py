"""Tests for the envelope.

The envelope's job is to control volume over time, so every test here is about
where the sound is loud and where it's quiet.
"""

import numpy as np
import pytest

from blip8 import SAMPLE_RATE, SINE_TABLE, crunch, envelope, square, triangle, wavetable


def test_envelope_does_not_change_the_length():
    """It reshapes volume; it must not add or remove samples."""
    samples = square(freq=440, length=0.5)
    assert len(envelope(samples)) == len(samples)


def test_envelope_starts_and_ends_at_silence():
    """This is the anti-click test — the whole reason envelopes exist here.

    A sound that starts or ends at full amplitude makes the speaker jump, and
    you hear that jump as a tick.
    """
    shaped = envelope(square(freq=440, length=0.5), attack=0.01, release=0.05)
    assert shaped[0] == pytest.approx(0.0, abs=0.01)
    assert shaped[-1] == pytest.approx(0.0, abs=0.01)


def test_raw_wave_does_not_start_at_silence():
    """The other half of the previous test: proves the problem was real.

    Without an envelope, sample zero is already at full volume.
    """
    raw = square(freq=440, length=0.5, volume=0.5)
    assert abs(raw[0]) == pytest.approx(0.5)


def test_attack_fades_in_gradually():
    """During the attack the sound should be getting louder, not be loud."""
    shaped = envelope(square(freq=440, length=0.5, volume=0.5), attack=0.1)

    quarter_way_in = int(0.025 * SAMPLE_RATE)
    halfway_in = int(0.05 * SAMPLE_RATE)

    # Compare peaks in small windows rather than single samples, because a
    # square wave is only at its peak half the time.
    early = np.max(np.abs(shaped[quarter_way_in : quarter_way_in + 100]))
    later = np.max(np.abs(shaped[halfway_in : halfway_in + 100]))

    assert early < later < 0.5


def test_sustain_zero_means_the_sound_dies():
    """A drum hit: loud at the start, actually silent by the end."""
    shaped = envelope(
        square(freq=440, length=0.5), attack=0.001, decay=0.2, sustain=0.0, release=0.0
    )
    assert np.max(np.abs(shaped[:1000])) > 0.4  # loud at the start
    assert np.max(np.abs(shaped[-1000:])) == pytest.approx(0.0, abs=0.001)  # gone


def test_envelope_never_makes_a_sound_louder():
    """Gain is always 0.0..1.0, so this can only ever attenuate. If it could
    amplify, sounds would clip on save without warning."""
    raw = square(freq=440, length=0.3, volume=0.5)
    shaped = envelope(raw)
    assert np.max(np.abs(shaped)) <= np.max(np.abs(raw))


def test_stages_longer_than_the_sound_get_squeezed_not_crashed():
    """A 5-second release on a 0.1-second beep is an easy accident. It should
    still produce a correctly-sized, silent-at-both-ends result."""
    shaped = envelope(square(freq=440, length=0.1), attack=2.0, decay=3.0, release=5.0)

    assert len(shaped) == int(SAMPLE_RATE * 0.1)
    assert shaped[0] == pytest.approx(0.0, abs=0.01)
    assert shaped[-1] == pytest.approx(0.0, abs=0.01)


def test_no_attack_or_release_leaves_the_sound_alone():
    """With every stage switched off, the envelope should be a no-op."""
    raw = square(freq=440, length=0.2)
    shaped = envelope(raw, attack=0.0, decay=0.0, sustain=1.0, release=0.0)
    assert np.array_equal(raw, shaped)


# --------------------------------------------------------------------------
# crunch — bit reduction, the lo-fi grit
# --------------------------------------------------------------------------


def test_crunch_reduces_the_number_of_distinct_values():
    """The whole definition of the effect: fewer volume levels allowed.

    A triangle slides smoothly through hundreds of values; at 4 bits it may
    only use 16-ish of them.
    """
    smooth = triangle(freq=440, length=0.1)
    crushed = crunch(smooth, bits=4)

    assert len(np.unique(smooth)) > 100
    assert len(np.unique(crushed)) <= 17


def test_crunch_keeps_the_length():
    samples = wavetable(SINE_TABLE, freq=440, length=0.2)
    assert len(crunch(samples)) == len(samples)


def test_fewer_bits_means_fewer_levels():
    """Monotonic: 2 bits must be coarser than 4, which is coarser than 8."""
    smooth = triangle(freq=440, length=0.1)
    counts = [len(np.unique(crunch(smooth, bits=b))) for b in (2, 4, 8)]
    assert counts[0] < counts[1] < counts[2]


def test_crunch_stays_in_speaker_range():
    """Rounding must never push a sample past 1.0 and cause clipping."""
    loud = triangle(freq=440, length=0.1, volume=1.0)
    assert np.max(np.abs(crunch(loud, bits=4))) <= 1.0


def test_crunch_is_roughly_faithful():
    """It should add grit, not replace the sound. Each sample stays close to
    where it started — within half a level."""
    smooth = triangle(freq=440, length=0.1)
    error = np.max(np.abs(crunch(smooth, bits=4) - smooth))
    assert error <= 1 / 16  # half of one 4-bit step
