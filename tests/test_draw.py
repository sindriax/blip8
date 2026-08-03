"""Tests for the ASCII waveform plots."""

import numpy as np
import pytest

from blip8 import envelope, noise, plot, show, silence, square, triangle


def _lines(*args, **kwargs) -> list[str]:
    return plot(*args, **kwargs).split("\n")


# --------------------------------------------------------------------------
# Shape of the output
# --------------------------------------------------------------------------


def test_plot_has_the_requested_dimensions():
    lines = _lines(square(freq=440, length=0.1), width=40, height=11)
    assert len(lines) == 11
    assert all(len(line) == 40 for line in lines)


def test_height_is_forced_odd_so_there_is_a_centre_row():
    assert len(_lines(square(freq=440, length=0.1), height=10)) == 11


@pytest.mark.parametrize("height", [1, 2, 3])
def test_tiny_heights_do_not_crash(height):
    assert len(_lines(square(freq=440, length=0.1), height=height)) == 3


def test_short_sounds_use_one_column_per_sample_at_most():
    lines = _lines(square(freq=440, length=0.0002), width=72)
    assert all(len(line) <= 72 for line in lines)
    assert len(lines[0]) == 8


def test_empty_input_gives_empty_output():
    assert plot(np.array([])) == ""


# --------------------------------------------------------------------------
# What the plot actually shows
# --------------------------------------------------------------------------


def test_silence_draws_a_flat_line_at_zero():
    """The waveform sits exactly on the axis, so the centre row is the wave."""
    lines = _lines(silence(0.1), width=20, height=11)
    assert lines[5] == "█" * 20
    assert all(line.strip() == "" for index, line in enumerate(lines) if index != 5)


def test_the_axis_shows_through_at_high_zoom():
    """Zoomed in far enough that a column sits entirely above or below zero,
    the centre row stays visible as an axis. Zoomed out, every column spans
    both halves of the wave and covers it."""
    zoomed = _lines(square(freq=440, length=0.007), width=60, height=13)
    zoomed_out = _lines(square(freq=440, length=1.0), width=60, height=13)

    assert "─" in zoomed[6]
    assert "─" not in zoomed_out[6]


def test_a_loud_square_reaches_the_top_and_bottom_rows():
    lines = _lines(square(freq=440, length=0.1, volume=1.0), width=40, height=11)
    assert "█" in lines[0]
    assert "█" in lines[-1]


def test_a_quiet_sound_stays_near_the_middle():
    """With normalize off, the plot shows true amplitude."""
    lines = _lines(square(freq=440, length=0.1, volume=0.2), width=40, height=21)
    assert "█" not in lines[0]
    assert "█" not in lines[-1]
    assert "█" in lines[10]


def test_normalize_scales_a_quiet_sound_to_full_height():
    quiet = square(freq=440, length=0.1, volume=0.05)
    assert "█" not in _lines(quiet, height=11)[0]
    assert "█" in _lines(quiet, height=11, normalize=True)[0]


def test_normalize_survives_pure_silence():
    """Guards a division by zero: the peak of silence is 0."""
    assert plot(silence(0.05), normalize=True) != ""


# --------------------------------------------------------------------------
# The plots distinguish the things they're meant to distinguish
# --------------------------------------------------------------------------


def test_square_fills_more_than_triangle():
    """A square sits at its extremes; a triangle spends most of its time in
    between, so it paints fewer blocks in the outer rows."""
    seconds = 0.007
    square_top = _lines(square(freq=440, length=seconds, volume=1.0), width=60)[0]
    triangle_top = _lines(triangle(freq=440, length=seconds, volume=1.0), width=60)[0]
    assert square_top.count("█") > triangle_top.count("█") * 3


def test_a_decaying_sound_narrows_towards_the_end():
    """The envelope becomes visible: tall at the start, thin at the end."""
    crash = envelope(noise(length=1.0), attack=0.001, decay=1.0, sustain=0.0, release=0.0)
    lines = _lines(crash, width=40, height=21)

    filled_per_column = [sum(line[column] == "█" for line in lines) for column in range(40)]
    assert filled_per_column[0] > filled_per_column[20] > filled_per_column[-1]


def test_plotting_a_long_sound_shows_its_envelope_not_noise():
    """Every column of a sustained tone should be filled to the same height."""
    tone = square(freq=440, length=2.0, volume=0.8)
    lines = _lines(tone, width=40, height=21)
    heights = {sum(line[column] == "█" for line in lines) for column in range(40)}
    assert len(heights) == 1


# --------------------------------------------------------------------------
# show()
# --------------------------------------------------------------------------


def test_show_prints_the_plot(capsys):
    """`capsys` is a pytest fixture that captures stdout."""
    show(square(freq=440, length=0.01), width=20, height=5)
    assert "█" in capsys.readouterr().out


def test_show_prints_the_label_first(capsys):
    show(square(freq=440, length=0.01), label="a square", width=20, height=5)
    assert capsys.readouterr().out.startswith("a square\n")
