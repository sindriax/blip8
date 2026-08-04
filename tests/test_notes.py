"""Tests for note names.

Unlike the audio tests, these have objectively correct answers, so the
tolerances are tight.
"""

import pytest

from blip8 import midi_to_freq, note, note_to_midi

# --------------------------------------------------------------------------
# The anchor points
# --------------------------------------------------------------------------


def test_a4_is_exactly_440() -> None:
    """The reference pitch the whole system is defined against."""
    assert note("A4") == 440.0


def test_middle_c_is_261_hz() -> None:
    """C4, middle C, the note everyone counts from."""
    assert note("C4") == pytest.approx(261.63, abs=0.01)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("C4", 60),
        ("A4", 69),
        ("C0", 12),
        ("C-1", 0),
        ("G9", 127),
        ("F#5", 78),
        ("Eb3", 51),
    ],
)
def test_note_names_map_to_the_right_midi_numbers(name: str, expected: int) -> None:
    assert note_to_midi(name) == expected


# --------------------------------------------------------------------------
# The maths that defines Western tuning
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["C", "E", "A", "F#"])
def test_going_up_an_octave_doubles_the_frequency(name: str) -> None:
    """The rule everything else derives from."""
    assert note(f"{name}5") == pytest.approx(note(f"{name}4") * 2)


def test_going_down_an_octave_halves_it() -> None:
    assert note("A3") == pytest.approx(220.0)
    assert note("A2") == pytest.approx(110.0)


def test_one_semitone_is_the_twelfth_root_of_two() -> None:
    """Twelve equal steps that multiply to exactly 2."""
    assert note("A#4") / note("A4") == pytest.approx(2 ** (1 / 12))


def test_twelve_semitones_get_you_back_to_double() -> None:
    """Compounding the ratio twelve times must land exactly on the octave, so
    there is no rounding drift."""
    steps = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4", "C5"]
    assert note(steps[-1]) == pytest.approx(note(steps[0]) * 2)


def test_sharps_and_flats_can_be_the_same_note() -> None:
    """C# and Db are the same pitch, spelled two ways."""
    assert note("C#4") == note("Db4")
    assert note("F#3") == note("Gb3")
    assert note("A#5") == note("Bb5")


# --------------------------------------------------------------------------
# Input handling
# --------------------------------------------------------------------------


def test_the_letter_is_case_insensitive() -> None:
    assert note("a4") == note("A4")


def test_surrounding_whitespace_is_ignored() -> None:
    assert note("  E5  ") == note("E5")


@pytest.mark.parametrize("bad", ["", "H4", "A", "4A", "A4x", "A#b4", "hello", "C4 E4"])
def test_nonsense_raises_a_helpful_error(bad: str) -> None:
    """A typo in a pattern string must raise rather than become a wrong note."""
    with pytest.raises(ValueError, match="not a note name"):
        note(bad)


# --------------------------------------------------------------------------
# midi_to_freq
# --------------------------------------------------------------------------


def test_midi_to_freq_matches_the_note_names() -> None:
    assert midi_to_freq(69) == 440.0
    assert midi_to_freq(60) == pytest.approx(note("C4"))


def test_midi_to_freq_accepts_fractions() -> None:
    """Needed for vibrato and pitch bends, so it must not be integer-only."""
    halfway = midi_to_freq(69.5)
    assert note("A4") < halfway < note("A#4")
