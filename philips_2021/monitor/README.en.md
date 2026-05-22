# Philips 2021 Monitor Sound Notes

This file documents how the monitor sounds in `philips_2021/monitor.py` are synthesized and what situations they are intended to simulate. These use cases are for simulation and prototyping only; they do not replace real device configuration, hospital alarm policy, or vendor documentation.

## Alarm Priority Synthesis Model

The project analyzed `source/updated_sound_high.wav`, `source/updated_sound_medium.wav`, and `source/updated_sound_low.wav` using spectral, narrow-band envelope, and timing analysis. The resulting approximation is summarized below.

### High alarm

Use case: high-priority red alarms requiring immediate attention. Suitable simulated examples include ventricular fibrillation, ventricular tachycardia, asystole, extreme oxygen desaturation, severe bradycardia/tachycardia, and severe apnea. Actual triggering conditions depend on monitor configuration and institutional policy.

Synthesis parameters:

- Fundamental: `960 Hz`
- Strong third harmonic: `2880 Hz`
- Harmonic amplitude: approximately `0.82` for the fundamental and `1.0` for the third harmonic
- Single loop period: `1000 ms`
- Default full alarm: `500 ms` initial delay, repeated `7` times
- Envelope: about `48 ms` smooth attack, about `230 ms` hold, then a smooth release toward the end of the period

Output files:

- `philips_2021_alarm_high.wav`
- `philips_2021_alarm_high_loop_once.wav`

### Medium alarm

Use case: medium-priority alarms that require timely attention but are not necessarily immediately life-threatening. Examples include moderate oxygen desaturation, heart-rate limit violations, abnormal respiratory rate, blood-pressure limit violations, or other monitored-parameter excursions.

Synthesis parameters:

- Main frequency: `720 Hz`
- Timbre: near-pure tone
- Audible tone length: `1200 ms`
- Repetition period: `4000 ms`
- Default full alarm: `500 ms` initial delay, repeated `5` times
- Envelope: about `34 ms` smooth attack, short hold, then decays close to zero within about `1.1-1.2 s`, followed by silence

Output files:

- `philips_2021_alarm_medium.wav`
- `philips_2021_alarm_medium_loop_once.wav`

### Low alarm

Use case: low-priority or advisory alerts. Suitable simulated examples include mild parameter limit violations, advisory physiological alarms, or some lower-urgency technical states. On real systems, low-priority, technical, and INOP categories may vary by model and configuration.

Synthesis parameters:

- Main frequency: `480 Hz`
- Timbre: near-pure tone
- Audible tone length: `1700 ms`
- Repetition period: `6000 ms`
- Default full alarm: `500 ms` initial delay, repeated `4` times
- Envelope: about `55 ms` smooth attack, about `340 ms` hold, then decays close to zero within about `1.5-1.7 s`, followed by silence

Output files:

- `philips_2021_alarm_low.wav`
- `philips_2021_alarm_low_loop_once.wav`

## Loop Files

The `*_loop_once.wav` files contain one complete loop period and do not include the initial 500 ms delay.

- high loop: `1.0 s`
- medium loop: `4.0 s`
- low loop: `6.0 s`

The medium and low loop files include both the audible tone and the period silence. This makes them suitable for seamless repeated playback in a game engine, simulation system, or interaction prototype.

## Auxiliary Monitor Sounds

These sounds are not directly measured from Philips 2021 alarm samples. They are project utilities synthesized in the same general acoustic family.

### SpO2 pulse

Method: maps oxygen saturation to pitch. Lower SpO2 produces a lower pitch. The tone is short, rounded, and near-pure.

Output files:

- `philips_2021_spo2_98_hr72.wav`
- `philips_2021_spo2_90_hr110.wav`

### QRS beep

Method: uses a short near-pure tone around `720 Hz`, repeated according to heart rate. It is intended to simulate an ECG QRS cue.

Output file:

- `philips_2021_qrs_hr75.wav`

### UI prompts

Method: short tones in the same acoustic family for confirmation, error, and key feedback.

Output files:

- `philips_2021_prompt_ok.wav`
- `philips_2021_prompt_error.wav`
- `philips_2021_key.wav`

## Generation

Run from the project root:

```powershell
python -m philips_2021.output
```

Output directory:

```text
output/philips/monitor
```

## References

- Philips Sounds technology: https://www.usa.philips.com/healthcare/technology/patient-monitoring-sounds
- User-Centered Redesign of Monitoring Alarms, Healthcare 2025: https://www.mdpi.com/2227-9032/13/23/3033
- Local analyzed samples in this project: `source/updated_sound_high.wav`, `source/updated_sound_medium.wav`, `source/updated_sound_low.wav`
