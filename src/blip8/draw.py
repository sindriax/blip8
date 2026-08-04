"""ASCII waveform plots for the terminal."""

import numpy as np

from .wave import Samples

BLOCK = "█"
AXIS = "─"


def plot(
    samples: Samples,
    width: int = 72,
    height: int = 17,
    normalize: bool = False,
) -> str:
    """Render samples as an ASCII waveform.

    Each column shows the range between the lowest and highest sample it
    covers, the way an audio editor draws a waveform. Short sounds reveal the
    shape of individual cycles; long ones show the envelope.

    normalize scales the plot to the loudest sample instead of to full range,
    which makes quiet sounds visible at the cost of hiding their true level.
    """
    if len(samples) == 0:
        return ""

    height = max(3, height | 1)
    middle = height // 2
    columns = min(width, len(samples))

    scale = float(np.max(np.abs(samples))) if normalize else 1.0
    if scale == 0.0:
        scale = 1.0

    grid = [[AXIS if row == middle else " " for _ in range(columns)] for row in range(height)]

    for column, bucket in enumerate(np.array_split(samples, columns)):
        top = _row_for(float(bucket.max()), middle, scale)
        bottom = _row_for(float(bucket.min()), middle, scale)
        for row in range(top, bottom + 1):
            grid[row][column] = BLOCK

    return "\n".join("".join(row) for row in grid)


def show(
    samples: Samples,
    label: str = "",
    width: int = 72,
    height: int = 17,
    normalize: bool = False,
) -> None:
    """Print a waveform plot, optionally with a heading."""
    if label:
        print(label)
    print(plot(samples, width=width, height=height, normalize=normalize))


def _row_for(value: float, middle: int, scale: float) -> int:
    """Map a sample value to a grid row, clamped to the plot."""
    row = round(middle - middle * (value / scale))
    return max(0, min(2 * middle, row))
