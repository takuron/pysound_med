import os

import numpy as np
from scipy.io import wavfile


class Philips2021SoundSynthesizer:
    """
    Synthesize Philips 2021-style audible alarms from measured source examples.

    The source samples in ./source show a simple priority mapping:
    - high: repeated 960 Hz + strong 2880 Hz tone, about every 1 second
    - medium: repeated 720 Hz near-pure tone, about every 4 seconds
    - low: repeated 480 Hz near-pure tone, about every 6 seconds

    This is an approximation for simulation and UI prototyping. It does not use
    or redistribute proprietary Philips samples.
    """

    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

        self.priority_profiles = {
            "high": {
                "fundamental": 960.0,
                "period_ms": 1000,
                "start_delay_ms": 500,
                "repeats": 7,
                "harmonics": ((1, 0.82), (3, 1.0)),
                "attack_ms": 48,
                "hold_ms": 230,
                "release_decay": 1.05,
                "peak": 0.9,
            },
            "medium": {
                "fundamental": 720.0,
                "duration_ms": 1200,
                "period_ms": 4000,
                "start_delay_ms": 500,
                "repeats": 5,
                "harmonics": ((1, 1.0),),
                "attack_ms": 34,
                "hold_ms": 55,
                "release_decay": 3.3,
                "peak": 0.78,
            },
            "low": {
                "fundamental": 480.0,
                "duration_ms": 1700,
                "period_ms": 6000,
                "start_delay_ms": 500,
                "repeats": 4,
                "harmonics": ((1, 1.0),),
                "attack_ms": 55,
                "hold_ms": 340,
                "release_decay": 3.7,
                "peak": 0.72,
            },
        }

    def _time_vector(self, duration_ms):
        length = int(round(self.sample_rate * duration_ms / 1000))
        if length <= 0:
            return np.array([], dtype=float)
        return np.arange(length, dtype=float) / self.sample_rate

    def _silence(self, duration_ms):
        length = int(round(self.sample_rate * duration_ms / 1000))
        return np.zeros(max(0, length), dtype=float)

    def _philips_2021_envelope(self, duration_ms, attack_ms, hold_ms, release_decay):
        length = int(round(self.sample_rate * duration_ms / 1000))
        if length <= 0:
            return np.array([], dtype=float)

        attack_len = int(round(self.sample_rate * attack_ms / 1000))
        hold_len = int(round(self.sample_rate * hold_ms / 1000))
        attack_len = min(attack_len, length)
        hold_end = min(length, attack_len + hold_len)

        envelope = np.ones(length, dtype=float)

        if attack_len > 0:
            x = np.linspace(0.0, 1.0, attack_len, endpoint=False)
            envelope[:attack_len] = np.sin(x * np.pi / 2) ** 1.7

        if hold_end > attack_len:
            envelope[attack_len:hold_end] = 1.0

        if hold_end < length:
            tail_len = length - hold_end
            x = np.linspace(0.0, 1.0, tail_len, endpoint=False)
            decay = np.exp(-release_decay * x)
            taper = np.cos(x * np.pi / 2) ** 0.62
            envelope[hold_end:] = decay * taper

        return envelope

    def _priority_tone(self, profile):
        duration_ms = (
            profile["duration_ms"] if "duration_ms" in profile else profile["period_ms"]
        )
        fundamental = profile["fundamental"]
        t = self._time_vector(duration_ms)
        if len(t) == 0:
            return t

        wave = np.zeros_like(t)
        for harmonic, amplitude in profile["harmonics"]:
            phase = 2 * np.pi * fundamental * harmonic * t
            wave += amplitude * np.sin(phase)

        # The examples are very stable tones. This tiny motion prevents synthetic
        # beating from sounding perfectly static while remaining below audibility.
        wave *= 1.0 + 0.004 * np.sin(2 * np.pi * 5.0 * t)

        envelope = self._philips_2021_envelope(
            duration_ms=duration_ms,
            attack_ms=profile["attack_ms"],
            hold_ms=profile["hold_ms"],
            release_decay=profile["release_decay"],
        )

        return wave * envelope

    def _normalize(self, wave_data, peak=0.9):
        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            return wave_data.astype(np.int16)
        return (wave_data / max_value * peak * 32767).astype(np.int16)

    def generate_alarm(self, priority="high", repeats=None, include_initial_delay=True):
        profile = self.priority_profiles[priority]
        tone = self._priority_tone(profile)
        tone_ms = (
            profile["duration_ms"] if "duration_ms" in profile else profile["period_ms"]
        )
        gap_ms = max(0, profile["period_ms"] - tone_ms)
        total_repeats = repeats if repeats is not None else profile["repeats"]

        segments = []
        if include_initial_delay and profile["start_delay_ms"] > 0:
            segments.append(self._silence(profile["start_delay_ms"]))

        for index in range(total_repeats):
            segments.append(tone)
            if index < total_repeats - 1 and gap_ms > 0:
                segments.append(self._silence(gap_ms))

        return np.concatenate(segments)

    def generate_alarm_loop_once(self, priority="high"):
        profile = self.priority_profiles[priority]
        tone = self._priority_tone(profile)
        tone_ms = (
            profile["duration_ms"] if "duration_ms" in profile else profile["period_ms"]
        )
        gap_ms = max(0, profile["period_ms"] - tone_ms)

        if gap_ms > 0:
            return np.concatenate([tone, self._silence(gap_ms)])
        return tone

    def generate_spo2_pulse(self, spo2=98, heart_rate=72, beats=12):
        """
        Philips 2021 alarm samples are priority tones, not SpO2 beeps. This keeps
        the project utility sound but maps it to the same pure, rounded family.
        """
        pulse_ms = 90
        interval_ms = 60000.0 / heart_rate
        gap_ms = max(0.0, interval_ms - pulse_ms)
        freq = min(960.0, max(480.0, 900.0 - (100 - spo2) * 18.0))

        profile = {
            "fundamental": freq,
            "duration_ms": pulse_ms,
            "harmonics": ((1, 1.0),),
            "attack_ms": 18,
            "hold_ms": 20,
            "release_decay": 3.5,
        }

        tone = self._priority_tone(profile) * 0.48
        segments = []
        for _ in range(beats):
            segments.append(tone)
            segments.append(self._silence(gap_ms))
        return np.concatenate(segments)

    def generate_qrs_beep(self, heart_rate=75, beats=10):
        pulse_ms = 60
        interval_ms = 60000.0 / heart_rate
        gap_ms = max(0.0, interval_ms - pulse_ms)
        profile = {
            "fundamental": 720.0,
            "duration_ms": pulse_ms,
            "harmonics": ((1, 1.0),),
            "attack_ms": 12,
            "hold_ms": 12,
            "release_decay": 4.2,
        }

        tone = self._priority_tone(profile) * 0.42
        segments = []
        for _ in range(beats):
            segments.append(tone)
            segments.append(self._silence(gap_ms))
        return np.concatenate(segments)

    def generate_prompt_ok(self):
        first = self._priority_tone(
            {
                "fundamental": 720.0,
                "duration_ms": 95,
                "harmonics": ((1, 1.0),),
                "attack_ms": 18,
                "hold_ms": 25,
                "release_decay": 3.4,
            }
        )
        second = self._priority_tone(
            {
                "fundamental": 960.0,
                "duration_ms": 120,
                "harmonics": ((1, 0.9), (3, 0.22)),
                "attack_ms": 20,
                "hold_ms": 34,
                "release_decay": 3.2,
            }
        )
        return np.concatenate([first * 0.42, self._silence(55), second * 0.42])

    def generate_prompt_error(self):
        first = self._priority_tone(
            {
                "fundamental": 480.0,
                "duration_ms": 180,
                "harmonics": ((1, 1.0),),
                "attack_ms": 28,
                "hold_ms": 60,
                "release_decay": 2.2,
            }
        )
        second = self._priority_tone(
            {
                "fundamental": 360.0,
                "duration_ms": 210,
                "harmonics": ((1, 1.0),),
                "attack_ms": 30,
                "hold_ms": 70,
                "release_decay": 2.0,
            }
        )
        return np.concatenate([first * 0.5, self._silence(90), second * 0.48])

    def generate_prompt_key(self):
        profile = {
            "fundamental": 720.0,
            "duration_ms": 45,
            "harmonics": ((1, 1.0),),
            "attack_ms": 8,
            "hold_ms": 10,
            "release_decay": 5.0,
        }
        return self._priority_tone(profile) * 0.28

    def export_audio(self, wave_data, filename, peak=None):
        priority = None
        for name in self.priority_profiles:
            if f"_{name}" in os.path.basename(filename):
                priority = name
                break

        if peak is None and priority:
            peak = self.priority_profiles[priority]["peak"]
        elif peak is None:
            peak = 0.76

        pcm_16bit = self._normalize(wave_data, peak=peak)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")


PhilipsMonitorSoundSynthesizer = Philips2021SoundSynthesizer
