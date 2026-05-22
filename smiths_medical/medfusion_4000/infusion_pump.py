"""Approximate Medfusion 4000 syringe pump audible cues.

The public operator manual describes alarm priorities and audible behavior:
- high priority: repeating audible signal
- medium priority: repeating audible signal
- low priority: non-repeating audible signal
- limit priority: three-tone non-repeating signal tied to key-click loudness
- selected system or motor faults: continuous two-tone audible alarm

The manual does not publish exact pitches or waveforms. These tones are
synthetic approximations for simulation, education, and UI prototyping. They
are not Medfusion device recordings.
"""

import os

import numpy as np
from scipy.io import wavfile


class Medfusion4000PumpSoundSynthesizer:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate

        self.alarm_profiles = {
            "high": {
                "frequencies": (1318.5, 1318.5, 1568.0, 1318.5, 1046.5),
                "beep_ms": 115,
                "gap_ms": 75,
                "group_pause_after": 2,
                "group_pause_ms": 220,
                "phrase_gap_ms": 850,
                "default_repeats": 5,
                "peak": 0.86,
                "sweep_cents": 12.0,
            },
            "medium": {
                "frequencies": (988.0, 1174.7, 988.0),
                "beep_ms": 125,
                "gap_ms": 125,
                "phrase_gap_ms": 2550,
                "default_repeats": 4,
                "peak": 0.76,
                "sweep_cents": 8.0,
            },
            "low": {
                "frequencies": (784.0, 659.25),
                "beep_ms": 150,
                "gap_ms": 170,
                "default_repeats": 1,
                "peak": 0.66,
                "sweep_cents": -5.0,
            },
            "limit": {
                "frequencies": (880.0, 1108.7, 880.0),
                "beep_ms": 70,
                "gap_ms": 55,
                "default_repeats": 1,
                "peak": 0.5,
                "sweep_cents": 4.0,
            },
        }

        self.key_click_peaks = {
            2: 0.18,
            3: 0.26,
            4: 0.34,
            5: 0.42,
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

    def _envelope(self, duration_ms, attack_ms=5, release_ms=14):
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
            envelope[-release_len:] *= np.cos(x * np.pi / 2) ** 1.7

        return envelope

    def _tone(
        self,
        freq,
        duration_ms,
        harmonics=((1, 1.0), (2, 0.18), (3, 0.08), (5, 0.025)),
        attack_ms=5,
        release_ms=14,
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
            phase_cycles = start_freq * t + 0.5 * slope * t**2
        else:
            phase_cycles = freq * t

        wave = np.zeros_like(t)
        for multiplier, amplitude in harmonics:
            harmonic_freq = freq * multiplier
            if harmonic_freq < self.sample_rate / 2:
                wave += amplitude * np.sin(2 * np.pi * phase_cycles * multiplier)

        if tremolo_hz and tremolo_depth:
            wave *= 1.0 + tremolo_depth * np.sin(2 * np.pi * tremolo_hz * t)

        return wave * self._envelope(
            duration_ms, attack_ms=attack_ms, release_ms=release_ms
        )

    def _beep_sequence(self, profile):
        segments = []
        frequencies = profile["frequencies"]

        for index, freq in enumerate(frequencies):
            segments.append(
                self._tone(
                    freq,
                    profile["beep_ms"],
                    sweep_cents=profile.get("sweep_cents", 0.0),
                )
            )

            if index < len(frequencies) - 1:
                if profile.get("group_pause_after") == index:
                    segments.append(self._silence(profile["group_pause_ms"]))
                else:
                    segments.append(self._silence(profile["gap_ms"]))

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
            raise ValueError("priority must be one of: high, medium, low, limit")

        profile = self.alarm_profiles[priority]
        sequence = self._beep_sequence(profile)

        if priority in ("high", "medium"):
            return np.concatenate([sequence, self._silence(profile["phrase_gap_ms"])])
        return sequence

    def generate_alarm(self, priority="high", repeats=None):
        priority = priority.lower()
        if priority not in self.alarm_profiles:
            raise ValueError("priority must be one of: high, medium, low, limit")

        repeat_count = repeats
        if repeat_count is None:
            repeat_count = self.alarm_profiles[priority]["default_repeats"]

        loop_once = self.generate_alarm_loop_once(priority)
        if repeat_count <= 1:
            return loop_once

        if priority in ("low", "limit"):
            gap = self._silence(1100 if priority == "low" else 180)
            segments = []
            for index in range(repeat_count):
                segments.append(loop_once)
                if index < repeat_count - 1:
                    segments.append(gap)
            return np.concatenate(segments)

        return np.concatenate([loop_once for _ in range(repeat_count)])

    def generate_high_priority_alarm(self, repeats=5):
        return self.generate_alarm("high", repeats=repeats)

    def generate_medium_priority_alarm(self, repeats=4):
        return self.generate_alarm("medium", repeats=repeats)

    def generate_low_priority_alarm(self):
        return self.generate_alarm("low", repeats=1)

    def generate_limit_alert(self, key_click_level=4):
        if key_click_level in (0, "off", "Off", None):
            return np.array([], dtype=float)

        level = int(key_click_level)
        if level not in self.key_click_peaks:
            raise ValueError("key_click_level must be one of: off, 2, 3, 4, 5")

        profile = self.alarm_profiles["limit"]
        base = self._beep_sequence(profile)
        return base * (self.key_click_peaks[level] / self.key_click_peaks[4])

    def generate_key_click(self, level=3):
        if level in (0, "off", "Off", None):
            return np.array([], dtype=float)

        level = int(level)
        if level not in self.key_click_peaks:
            raise ValueError("level must be one of: off, 2, 3, 4, 5")

        click = self._tone(
            1760.0,
            22,
            harmonics=((1, 1.0), (2, 0.22), (4, 0.08)),
            attack_ms=1.4,
            release_ms=5,
            sweep_cents=18.0,
        )
        return click * self.key_click_peaks[level]

    def generate_user_callback_alarm(self):
        return self.generate_alarm("medium", repeats=2)

    def generate_syringe_near_empty_alarm(self, priority="medium"):
        priority = priority.lower()
        if priority not in ("medium", "low"):
            raise ValueError("priority must be medium or low")

        repeats = 2 if priority == "medium" else 1
        return self.generate_alarm(priority, repeats=repeats)

    def generate_syringe_volume_near_empty_alarm(self):
        return self.generate_alarm("medium", repeats=2)

    def generate_syringe_empty_alarm(self):
        return self.generate_alarm("high", repeats=3)

    def generate_kvo_in_progress_alarm(self):
        return self.generate_alarm("medium", repeats=2)

    def generate_system_advisory_alarm(self):
        return self.generate_alarm("low", repeats=1)

    def generate_continuous_two_tone_alarm(
        self,
        duration_sec=8.0,
        low_freq=620.0,
        high_freq=932.3,
        segment_ms=230,
    ):
        total_ms = int(round(duration_sec * 1000))
        segments = []
        elapsed_ms = 0
        index = 0

        while elapsed_ms < total_ms:
            this_ms = min(segment_ms, total_ms - elapsed_ms)
            freq = low_freq if index % 2 == 0 else high_freq
            segments.append(
                self._tone(
                    freq,
                    this_ms,
                    harmonics=((1, 1.0), (2, 0.24), (3, 0.12), (5, 0.04)),
                    attack_ms=3,
                    release_ms=4,
                    sweep_cents=3.0,
                    tremolo_hz=10.0,
                    tremolo_depth=0.05,
                )
            )
            elapsed_ms += this_ms
            index += 1

        return np.concatenate(segments) if segments else np.array([], dtype=float)

    def generate_system_fault_alarm(self, duration_sec=8.0):
        return self.generate_continuous_two_tone_alarm(duration_sec=duration_sec)

    def generate_motor_fault_alarm(self, duration_sec=8.0):
        base = self.generate_continuous_two_tone_alarm(
            duration_sec=duration_sec,
            low_freq=554.37,
            high_freq=880.0,
            segment_ms=190,
        )
        high_alarm = self._fit_length(
            self.generate_alarm("high", repeats=max(1, int(np.ceil(duration_sec / 2)))),
            len(base),
        )
        return base * 0.86 + high_alarm * 0.22

    def _normalize(self, wave_data, peak=0.78):
        if len(wave_data) == 0:
            return wave_data.astype(np.int16)

        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            return wave_data.astype(np.int16)
        return (wave_data / max_value * peak * 32767).astype(np.int16)

    def export_audio(self, wave_data, filename, peak=None):
        if peak is None:
            basename = os.path.basename(filename)
            peak = 0.78
            for priority, profile in self.alarm_profiles.items():
                if f"_{priority}" in basename:
                    peak = profile["peak"]
                    break
            if "system_fault" in basename or "motor_fault" in basename:
                peak = 0.88
            elif "key_click_level2" in basename:
                peak = 0.38
            elif "key_click_level5" in basename:
                peak = 0.58

        pcm_16bit = self._normalize(wave_data, peak=peak)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")


MedfusionModel4000PumpSoundSynthesizer = Medfusion4000PumpSoundSynthesizer
