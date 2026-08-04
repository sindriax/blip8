# 1. Sounds are plain NumPy arrays, not a Sound class

Status: accepted
Date: 2026-08-04

## Context

Every function in blip8 either produces or consumes audio. That audio needs a
representation, and the choice propagates into every signature in the library.

The obvious alternative is a `Sound` class wrapping the samples together with
their metadata:

```python
class Sound:
    samples: np.ndarray
    sample_rate: int
    channels: int
```

That is what most audio libraries do, and it is what a lot of style guides would
push you toward.

## Decision

A sound is a bare `numpy.ndarray` of float64 values between -1.0 and 1.0. The
sample rate is a module-level constant, `SAMPLE_RATE = 44100`. There is no
wrapper type. `Samples` is a type alias, not a class.

## Consequences

### What this buys

**Sounds compose with operators the language already has.**

```python
play(sfx.kick() + sfx.hat())          # mixing is addition
play(sfx.coin() * 0.5)                # a fader is multiplication
play(np.concatenate([a, b]))          # sequencing is concatenation
```

With a wrapper class, each of those needs a method or a dunder implementation,
and users have to learn which. Here it is the arithmetic they already know, and
it reads the way the operation is described: mixing two signals genuinely *is*
adding them sample by sample.

**Every NumPy and SciPy function works directly.** `np.max`, `np.clip`,
`np.fft`, `scipy.signal`, and anything else in the ecosystem accepts a blip8
sound with no unwrapping. A wrapper type would need either `.samples` access
everywhere or a large surface of delegating methods.

**Nothing to learn.** The type is documented in one sentence: an array of
numbers between -1 and 1. Anyone who knows NumPy already knows the whole data
model.

### What this costs

**A sound does not know its own sample rate.** Resampling, or supporting
anything other than 44.1 kHz, would mean passing the rate alongside every array
or reading the global constant. If blip8 ever needs variable sample rates, this
decision has to be revisited.

**There is no path to stereo.** A stereo sound is naturally a 2-D array or a
pair of channels, and the current contract says "1-D array of samples". Adding
stereo would either break that contract or bolt on a parallel API. This is the
real cost, and it is accepted knowingly: the NES and the Game Boy are the target
hardware, one of which was mono, and every recipe and oscillator in the library
is mono by design.

**Invalid states are representable.** Nothing stops a caller passing an array of
int16, or values at 5.0, or an empty array. Validation happens at the boundary
of the functions that generate sound rather than being enforced by a type. The
tests in `test_validation.py` cover the cases that matter.

## Revisit if

- Variable sample rates are needed, for resampling or for higher-quality output.
- Stereo becomes a requirement rather than a curiosity.

Either of those would justify a wrapper type. Neither is true today, and adding
the class in advance would cost the operator composition above for a benefit the
library does not use.
