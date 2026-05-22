"""Approximate Hamilton Medical ventilator audible cues.

The alarm cadence follows public HAMILTON-C1 operator manual descriptions:
- high priority: a 5-beep sequence, repeated until reset
- medium priority: a 3-beep sequence, repeated periodically
- low priority: two beep sequences, not repeated
- technical fault: high-priority alarm when possible, otherwise a continuous buzzer

The exact pitches and timbre are synthetic approximations for simulation and UI
prototyping. No proprietary Hamilton recordings are used or redistributed.
"""

import numpy as np
from scipy.io import wavfile


class HamiltonVentilatorSoundSynthesizer:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

        self.alarm_profiles = {
            "high": {
                "frequencies": (1046.5, 1046.5, 1046.5, 932.3, 1046.5),
                "beep_ms": 105,
                "gap_ms": 78,
                "group_pause_after": 2,
                "group_pause_ms": 260,
                "phrase_gap_ms": 1050,
                "default_repeats": 4,
                "peak": 0.86,
                "sweep_cents": 10.0,
            },
            "medium": {
                "frequencies": (880.0, 880.0, 784.0),
                "beep_ms": 125,
                "gap_ms": 120,
                "phrase_gap_ms": 3750,
                "default_repeats": 3,
                "peak": 0.76,
                "sweep_cents": 7.0,
            },
            "low": {
                "frequencies": (659.25, 659.25),
                "beep_ms": 140,
                "gap_ms": 125,
                "sequence_gap_ms": 620,
                "default_repeats": 1,
                "peak": 0.68,
                "sweep_cents": 5.0,
            },
        }

    def _samples(self, duration_ms):
        return max(0, int(round(self.sample_rate * duration_ms / 1000.0)))

    def _time_vector(self, duration_ms):
        length = self._samples(duration_ms)
        if length <= 0:
            return np.array([], dtype=float)
        return np.arange(length, dtype=float) / self.sample_rate

    def _silence(self, duration_ms):
        return np.zeros(self._samples(duration_ms), dtype=float)

    def _envelope(self, duration_ms, attack_ms=7, release_ms=18):
        length = self._samples(duration_ms)
        if length <= 0:
            return np.array([], dtype=float)

        envelope = np.ones(length, dtype=float)
        attack_len = min(self._samples(attack_ms), length)
        release_len = min(self._samples(release_ms), length)

        if attack_len > 0:
            x = np.linspace(0.0, 1.0, attack_len, endpoint=False)
            envelope[:attack_len] = np.sin(x * np.pi / 2) ** 1.6

        if release_len > 0:
            x = np.linspace(0.0, 1.0, release_len, endpoint=False)
            envelope[-release_len:] *= np.cos(x * np.pi / 2) ** 1.8

        return envelope

    def _tone(
        self,
        freq,
        duration_ms,
        harmonics=((1, 1.0), (2, 0.18), (3, 0.08)),
        attack_ms=7,
        release_ms=18,
        sweep_cents=0.0,
        tremolo_hz=0.0,
        tremolo_depth=0.0,
    ):
        t = self._time_vector(duration_ms)
        if len(t) == 0:
            return t

        duration_sec = duration_ms / 1000.0
        if sweep_cents:
            start_freq = freq * 2 ** (sweep_cents / 1200.0)
            end_freq = freq * 2 ** (-sweep_cents / 1200.0)
            slope = (end_freq - start_freq) / duration_sec
            base_phase = start_freq * t + 0.5 * slope * t**2
        else:
            base_phase = freq * t

        wave = np.zeros_like(t)
        for multiplier, amplitude in harmonics:
            harmonic_freq = freq * multiplier
            if harmonic_freq < self.sample_rate / 2:
                wave += amplitude * np.sin(2 * np.pi * base_phase * multiplier)

        if tremolo_hz and tremolo_depth:
            wave *= 1.0 + tremolo_depth * np.sin(2 * np.pi * tremolo_hz * t)

        envelope = self._envelope(
            duration_ms, attack_ms=attack_ms, release_ms=release_ms
        )
        return wave * envelope

    def _beep_sequence(self, frequencies, beep_ms, gap_ms, sweep_cents=0.0, **kwargs):
        segments = []
        group_pause_after = kwargs.get("group_pause_after")
        group_pause_ms = kwargs.get("group_pause_ms", gap_ms)

        for index, freq in enumerate(frequencies):
            segments.append(
                self._tone(
                    freq,
                    beep_ms,
                    attack_ms=kwargs.get("attack_ms", 6),
                    release_ms=kwargs.get("release_ms", 18),
                    sweep_cents=sweep_cents,
                )
            )

            if index < len(frequencies) - 1:
                if group_pause_after == index:
                    segments.append(self._silence(group_pause_ms))
                else:
                    segments.append(self._silence(gap_ms))

        return np.concatenate(segments) if segments else np.array([], dtype=float)

    def _fit_length(self, wave_data, target_length):
        if target_length <= 0:
            return np.array([], dtype=float)
        if len(wave_data) == 0:
            return np.zeros(target_length, dtype=float)
        if len(wave_data) >= target_length:
            return wave_data[:target_length]

        repeats = int(np.ceil(target_length / len(wave_data)))
        return np.tile(wave_data, repeats)[:target_length]

    def generate_alarm_loop_once(self, priority="high"):
        priority = priority.lower()
        if priority not in self.alarm_profiles:
            raise ValueError("priority must be one of: high, medium, low")

        profile = self.alarm_profiles[priority]

        if priority == "low":
            first = self._beep_sequence(
                profile["frequencies"],
                profile["beep_ms"],
                profile["gap_ms"],
                sweep_cents=profile["sweep_cents"],
            )
            second = self._beep_sequence(
                profile["frequencies"],
                profile["beep_ms"],
                profile["gap_ms"],
                sweep_cents=profile["sweep_cents"],
            )
            return np.concatenate(
                [first, self._silence(profile["sequence_gap_ms"]), second]
            )

        phrase = self._beep_sequence(
            profile["frequencies"],
            profile["beep_ms"],
            profile["gap_ms"],
            group_pause_after=profile.get("group_pause_after"),
            group_pause_ms=profile.get("group_pause_ms", profile["gap_ms"]),
            sweep_cents=profile["sweep_cents"],
        )
        return np.concatenate([phrase, self._silence(profile["phrase_gap_ms"])])

    def generate_alarm(self, priority="high", repeats=None):
        priority = priority.lower()
        if priority not in self.alarm_profiles:
            raise ValueError("priority must be one of: high, medium, low")

        repeat_count = repeats
        if repeat_count is None:
            repeat_count = self.alarm_profiles[priority]["default_repeats"]

        loop_once = self.generate_alarm_loop_once(priority)
        if repeat_count <= 1:
            return loop_once

        return np.concatenate([loop_once for _ in range(repeat_count)])

    def generate_high_priority_alarm(self, repeats=4):
        return self.generate_alarm("high", repeats=repeats)

    def generate_medium_priority_alarm(self, repeats=3):
        return self.generate_alarm("medium", repeats=repeats)

    def generate_low_priority_alarm(self):
        return self.generate_alarm("low", repeats=1)

    def generate_continuous_buzzer(self, duration_sec=8.0):
        return self._tone(
            620.0,
            duration_sec * 1000,
            harmonics=((1, 1.0), (3, 0.34), (5, 0.12)),
            attack_ms=45,
            release_ms=90,
            tremolo_hz=7.5,
            tremolo_depth=0.12,
        )

    def generate_technical_fault(self, duration_sec=8.0, include_high_alarm=True):
        buzzer = self.generate_continuous_buzzer(duration_sec=duration_sec)
        if not include_high_alarm:
            return buzzer

        high_repeats = max(1, int(np.ceil(duration_sec / 2.0)))
        high_alarm = self.generate_high_priority_alarm(repeats=high_repeats)
        high_alarm = self._fit_length(high_alarm, len(buzzer))

        return buzzer * 0.78 + high_alarm * 0.52

    def generate_touch_key(self):
        return self._tone(
            1280.0,
            42,
            harmonics=((1, 1.0), (2, 0.09)),
            attack_ms=3,
            release_ms=8,
            sweep_cents=3.0,
        ) * 0.34

    def generate_screen_locked_beep(self):
        beep = self._tone(
            960.0,
            95,
            harmonics=((1, 1.0), (2, 0.12), (3, 0.06)),
            attack_ms=5,
            release_ms=18,
            sweep_cents=4.0,
        )
        return beep * 0.52

    def generate_prompt_confirm(self):
        first = self._tone(
            960.0,
            72,
            harmonics=((1, 1.0), (2, 0.1)),
            attack_ms=5,
            release_ms=12,
            sweep_cents=4.0,
        )
        second = self._tone(
            1280.0,
            92,
            harmonics=((1, 1.0), (2, 0.08)),
            attack_ms=5,
            release_ms=16,
            sweep_cents=4.0,
        )
        return np.concatenate([first * 0.38, self._silence(58), second * 0.4])

    def generate_prompt_warning(self):
        first = self._tone(
            780.0,
            120,
            harmonics=((1, 1.0), (2, 0.14), (3, 0.06)),
            attack_ms=7,
            release_ms=20,
            sweep_cents=-4.0,
        )
        second = self._tone(
            620.0,
            150,
            harmonics=((1, 1.0), (2, 0.12), (3, 0.07)),
            attack_ms=7,
            release_ms=24,
            sweep_cents=-5.0,
        )
        return np.concatenate([first * 0.46, self._silence(95), second * 0.46])

    def _normalize(self, wave_data, peak=0.82):
        if len(wave_data) == 0:
            return wave_data.astype(np.int16)

        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            return wave_data.astype(np.int16)
        return (wave_data / max_value * peak * 32767).astype(np.int16)

    def export_audio(self, wave_data, filename, peak=None):
        if peak is None:
            peak = 0.78
            for priority, profile in self.alarm_profiles.items():
                if f"_{priority}" in filename:
                    peak = profile["peak"]
                    break
            if "technical_fault" in filename or "continuous_buzzer" in filename:
                peak = 0.88

        pcm_16bit = self._normalize(wave_data, peak=peak)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")


HamiltonMedicalVentilatorSoundSynthesizer = HamiltonVentilatorSoundSynthesizer
