# Philips 2021 Sound Design Notes

This directory contains synthesized Philips 2021-style patient monitor sounds, with the main implementation in `monitor.py`. The current implementation is intended for simulation, interaction prototypes, and audio previews. It does not contain or redistribute proprietary Philips audio samples.

## Design Basis

Philips' public material for Philips Sounds describes a redesigned patient-monitoring sound environment built around caregivers and patients. The stated direction is to soften the harsh edges of traditional monitoring sounds, reduce alarm fatigue, and preserve clinical recognizability.

A third-party clinical study also describes the Philips/Sen Sound redesign direction: low- and medium-priority alarms were refined to reduce auditory harshness, while high-priority alarms retained salient, attention-grabbing properties. The study's supplementary materials include audio examples of traditional and refined Philips alarm sounds. This project uses the local samples placed in `source/` for spectral and envelope analysis, then converts the findings into tunable synthesis parameters.

## Overall Design Principles

1. **Priority-driven, not IEC-melody-driven**
   The analyzed Philips 2021 samples are stable single-frequency or lightly harmonic events. Priority is expressed through frequency, repetition period, timbre, and envelope shape rather than IEC 60601 five-note melodies.

2. **Reduced burden for medium and low priorities**
   `medium` and `low` use near-pure tones with a smooth decay followed by true silence. This avoids a long audible tail and leaves more space in the clinical soundscape.

3. **High priority remains salient**
   `high` uses a 960 Hz fundamental plus a stronger 2880 Hz third harmonic. This keeps the high-priority alert more prominent than the lower-priority tones while still using a smooth envelope.

4. **Every event fades from zero to peak and back to zero**
   Alarm events use a smooth attack, hold, and combined exponential/cosine release. Medium and low tones do not fill their full repetition periods; high nearly fills its 1-second period.

5. **Synthesis instead of sampling**
   The project keeps only parameterized synthesis logic. This makes the sounds reproducible and adjustable while avoiding dependency on protected source audio.

## Directory Structure

- `monitor.py`: Philips 2021 patient monitor sound synthesizer.
- `output.py`: Quick preview generator for all sounds in this directory.
- `monitor/README.zh.md`: Chinese notes for the specific monitor sounds.
- `monitor/README.en.md`: English notes for the specific monitor sounds.

## Quick Generation

Run from the project root:

```powershell
python -m philips_2021.output
```

Generated files are written to:

```text
output/philips/monitor
```

The project-wide output entry point also includes these sounds:

```powershell
python output.py
```

## References

- Philips Sounds technology: https://www.usa.philips.com/healthcare/technology/patient-monitoring-sounds
- User-Centered Redesign of Monitoring Alarms, Healthcare 2025: https://www.mdpi.com/2227-9032/13/23/3033
- Local analyzed samples in this project: `source/updated_sound_high.wav`, `source/updated_sound_medium.wav`, `source/updated_sound_low.wav`
