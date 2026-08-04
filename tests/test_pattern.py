"""Tests for patterns, chords and arrangement, mostly about timing."""

import numpy as np
import pytest

from blip8 import (
    SAMPLE_RATE,
    arpeggio,
    at,
    chord,
    layer,
    melody,
    note,
    sequence,
    silence,
    square,
    triangle,
)

# --------------------------------------------------------------------------
# Timing
# --------------------------------------------------------------------------


def test_four_sixteenth_notes_make_one_beat() -> None:
    """At 120 bpm a beat is half a second, and the default is 4 steps."""
    sound = melody("C4 D4 E4 F4", bpm=120)
    assert len(sound) / SAMPLE_RATE == pytest.approx(0.5, abs=0.01)


def test_doubling_the_bpm_halves_the_duration() -> None:
    slow = melody("C4 D4 E4 F4", bpm=120)
    fast = melody("C4 D4 E4 F4", bpm=240)
    assert len(fast) == pytest.approx(len(slow) / 2, rel=0.01)


def test_steps_per_beat_changes_the_resolution() -> None:
    quarters = melody("C4 D4", bpm=120, steps_per_beat=1)
    sixteenths = melody("C4 D4", bpm=120, steps_per_beat=4)
    assert len(quarters) == pytest.approx(len(sixteenths) * 4, rel=0.01)


def test_a_hold_extends_the_previous_note() -> None:
    """ "C4 . . ." is one note lasting three steps, not three notes."""
    one_step = melody("C4", bpm=120)
    three_steps = melody("C4 . .", bpm=120)
    assert len(three_steps) == pytest.approx(len(one_step) * 3, rel=0.01)


def test_a_held_note_is_continuous_not_repeated() -> None:
    """A repeat fades out and back in between steps, so it dips to silence in
    the middle; a hold does not."""
    held = melody("C4 .", bpm=120)
    repeated = melody("C4 C4", bpm=120)

    middle = len(held) // 2
    window = slice(middle - 200, middle + 200)

    assert np.max(np.abs(held[window])) > 0.3  # still going
    assert np.min(np.abs(repeated[window])) < 0.01  # dipped through zero


# --------------------------------------------------------------------------
# Rests and silence
# --------------------------------------------------------------------------


def test_a_rest_is_actually_silent() -> None:
    sound = melody("- - - -", bpm=120)
    assert len(sound) > 0
    assert np.all(sound == 0.0)


def test_a_rest_takes_up_its_step() -> None:
    """Rests must occupy time, or everything after them arrives early."""
    with_rest = melody("C4 - C4 -", bpm=120)
    without = melody("C4 C4 C4 C4", bpm=120)
    assert len(with_rest) == pytest.approx(len(without), rel=0.01)


def test_empty_pattern_gives_empty_sound() -> None:
    assert len(melody("")) == 0


def test_bad_note_in_a_pattern_raises() -> None:
    with pytest.raises(ValueError, match="not a note name"):
        melody("C4 H9 E4")


# --------------------------------------------------------------------------
# Pitch actually follows the pattern
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["A4", "C4", "E5", "G3"])
def test_the_notes_come_out_at_the_right_pitch(name: str) -> None:
    """End to end: a name in the pattern produces a wave at the frequency
    note() promises."""
    sound = melody(f"{name} . . . . . . .", bpm=60, steps_per_beat=4)  # 8 steps = 2s
    expected_cycles = note(name) * (len(sound) / SAMPLE_RATE)
    assert _count_cycles(sound) == pytest.approx(expected_cycles, rel=0.02)


def test_extra_keyword_arguments_reach_the_oscillator() -> None:
    """`duty` is not a melody() parameter; it is forwarded to square()."""
    thin = melody("C4 C4 C4 C4", duty=0.125, volume=0.5)
    fraction_up = np.count_nonzero(thin > 0) / len(thin)
    assert fraction_up < 0.2  # nowhere near the 0.5 of a default square


def test_melody_accepts_a_different_voice() -> None:
    """The same pattern on the triangle voice should be smooth, not buzzy."""
    buzzy = melody("C4 C4", voice=square)
    smooth = melody("C4 C4", voice=triangle)
    assert np.max(np.abs(np.diff(smooth))) < np.max(np.abs(np.diff(buzzy)))


# --------------------------------------------------------------------------
# chord vs arpeggio
# --------------------------------------------------------------------------


def test_chord_plays_notes_simultaneously() -> None:
    """A chord lasts as long as one note, not three."""
    assert len(chord("C4 E4 G4", length=0.5)) == pytest.approx(SAMPLE_RATE * 0.5, rel=0.01)


def test_chord_is_louder_than_one_of_its_notes() -> None:
    """Three waves summed must peak higher than one alone."""
    one = square(freq=note("C4"), length=0.5, volume=0.15)
    three = chord("C4 E4 G4", length=0.5, volume=0.15)
    assert np.max(np.abs(three)) > np.max(np.abs(one)) * 1.5


def test_chord_leaves_headroom() -> None:
    assert np.max(np.abs(chord("C4 E4 G4 C5"))) <= 1.0


def test_arpeggio_has_the_requested_duration() -> None:
    assert len(arpeggio("C4 E4 G4", length=0.5)) == pytest.approx(SAMPLE_RATE * 0.5, rel=0.05)


def test_arpeggio_cycles_through_the_notes() -> None:
    """Slowed right down, each chunk should hold one note of the chord."""
    slow = arpeggio("C4 E4 G4", length=0.9, rate=0.3)
    third = len(slow) // 3

    for index, name in enumerate(("C4", "E4", "G4")):
        chunk = slow[index * third : (index + 1) * third]
        cycles = _count_cycles(chunk)
        expected = note(name) * (len(chunk) / SAMPLE_RATE)
        assert cycles == pytest.approx(expected, rel=0.05)


def test_arpeggio_and_chord_use_the_same_notes_differently() -> None:
    """Same input and duration, different construction."""
    assert len(arpeggio("C4 E4 G4", length=0.5)) == pytest.approx(
        len(chord("C4 E4 G4", length=0.5)), rel=0.05
    )


# --------------------------------------------------------------------------
# Arrangement: silence, sequence, at, layer
# --------------------------------------------------------------------------


def test_silence_is_the_right_length_and_actually_silent() -> None:
    quiet = silence(0.25)
    assert len(quiet) == int(SAMPLE_RATE * 0.25)
    assert np.all(quiet == 0.0)


def test_sequence_adds_lengths_together() -> None:
    a, b = melody("C4"), melody("E4")
    assert len(sequence(a, b)) == len(a) + len(b)


def test_at_delays_a_sound() -> None:
    sound = melody("C4")
    delayed = at(0.5, sound)

    assert len(delayed) == int(SAMPLE_RATE * 0.5) + len(sound)
    assert np.all(delayed[: int(SAMPLE_RATE * 0.5)] == 0.0)  # silence first


def test_layer_pads_to_the_longest_sound() -> None:
    """Plain `+` refuses to add mismatched lengths."""
    short, long = melody("C4"), melody("C4 C4 C4 C4")

    with pytest.raises(ValueError):
        short + long  # NumPy will not broadcast these

    assert len(layer(short, long)) == len(long)


def test_layer_actually_mixes() -> None:
    sound = melody("C4 C4 C4 C4", volume=0.2)
    assert np.max(np.abs(layer(sound, sound))) == pytest.approx(np.max(np.abs(sound)) * 2, rel=0.01)


def test_at_and_layer_together_place_sounds_in_time() -> None:
    """Two hits half a second apart, with silence between them."""
    hit = melody("C4", bpm=240)  # short
    track = layer(at(0.0, hit), at(0.5, hit))

    gap = track[len(hit) + 100 : int(SAMPLE_RATE * 0.5) - 100]
    assert np.all(gap == 0.0)
    assert np.max(np.abs(track[int(SAMPLE_RATE * 0.5) :])) > 0.1


def _count_cycles(samples: np.ndarray) -> int:
    positive = samples > 0
    return int(np.count_nonzero(~positive[:-1] & positive[1:]))
