# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

While the major version is 0, the API may change in any minor release.

## [Unreleased]

## [0.1.0] - 2026-08-04

First release. Four voices, envelopes, patterns and a recipe library.

### Added

- **Oscillators**: `square()`, `triangle()`, `noise()` and `wavetable()`, the
  four voices of the NES and the Game Boy. `SINE_TABLE` and `BELL_TABLE` ship as
  wavetable presets.
- **Pitch sweeps**: any oscillator takes `freq=(start, end)` to glide.
- **Shapers**: `envelope()` applies an ADSR volume curve; `crunch()` reduces bit
  depth for the Game Boy's grit.
- **Recipes**: `sfx` provides 14 ready-made game sounds, from `sfx.coin()` to
  `sfx.explosion()`.
- **Notes and patterns**: `note("E5")` converts names to frequencies, `melody()`
  reads tracker-style pattern strings, and `chord()` and `arpeggio()` handle
  several notes at once.
- **Arrangement**: `at()` places a sound in time and `layer()` mixes sounds of
  unequal length.
- **Output**: `save()` writes a mono 16-bit `.wav`; `play()` plays through the
  speakers on macOS, Linux and Windows.
- **Visualisation**: `plot()` and `show()` render a waveform as ASCII, using
  min/max per column so the same call is useful zoomed in on cycles or zoomed
  out on an envelope.
- **Typing**: the package ships `py.typed`, and exports the `Samples` and
  `Pitch` aliases for annotating your own code.
- `noise()` accepts a `seed` for reproducible output.

[Unreleased]: https://github.com/sindriax/blip8/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sindriax/blip8/releases/tag/v0.1.0
