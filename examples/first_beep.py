"""Your first beep. Run me with:  uv run examples/first_beep.py"""

from blip8 import play, square

# 440 Hz = concert A. Half a second. Pure 1983.
beep = square(freq=440, length=0.5)
print("beep!")
play(beep)

# Same note, thinner duty cycle — hear the difference one knob makes.
# This is the knob the whole NES sound identity hangs on.
thin = square(freq=440, length=0.5, duty=0.125)
print("same note, duty 0.125 — thinner, more nasal:")
play(thin)
