"""Approximate LIFEPAK-series defibrillator tones.

The tonal family is based on public LIFEPAK operating instructions:
- LIFEPAK 20e tone assignments for alarm priorities and prompt tones
- LIFEPAK 1000 documentation for audible prompt behavior

The charging cue is a synthesis approximation because the public manuals
describe the cue but do not publish a waveform.
"""

import numpy as np
from scipy.io import wavfile


class LifePakSeriesDefibrillatorSoundSynthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def _samples(self, duration_ms):
        return max(0, int(round(self.sample_rate * duration_ms / 1000.0)))

    def _time_vector(self, duration_ms):
        length = self._samples(duration_ms)
        if length <= 0:
            return np.array([], dtype=float)
        return np.arange(length, dtype=float) / self.sample_rate

    def _silence(self, duration_ms):
        return np.zeros(self._samples(duration_ms), dtype=float)

    def _envelope(self, duration_ms, attack_ms=8, release_ms=12):
        length = self._samples(duration_ms)
        if length <= 0:
            return np.array([], dtype=float)

        envelope = np.ones(length, dtype=float)

        attack_len = min(self._samples(attack_ms), length)
        release_len = min(self._samples(release_ms), length)

        if attack_len > 0:
            x = np.linspace(0.0, 1.0, attack_len, endpoint=False)
            envelope[:attack_len] = np.sin(x * np.pi / 2) ** 1.7

        if release_len > 0:
            x = np.linspace(0.0, 1.0, release_len, endpoint=False)
            envelope[-release_len:] *= np.cos(x * np.pi / 2) ** 1.7

        return envelope

    def _tone(
        self,
        freq,
        duration_ms,
        harmonics=((1, 1.0),),
        attack_ms=8,
        release_ms=12,
    ):
        t = self._time_vector(duration_ms)
        if len(t) == 0:
            return t

        wave = np.zeros_like(t)
        for multiplier, amplitude in harmonics:
            harmonic_freq = freq * multiplier
            if harmonic_freq < self.sample_rate / 2:
                wave += amplitude * np.sin(2 * np.pi * harmonic_freq * t)

        return wave * self._envelope(duration_ms, attack_ms=attack_ms, release_ms=release_ms)

    def _chirp(
        self,
        start_freq,
        end_freq,
        duration_ms,
        harmonics=((1, 1.0), (2, 0.26)),
        attack_ms=70,
        release_ms=120,
    ):
        duration_sec = duration_ms / 1000.0
        t = self._time_vector(duration_ms)
        if len(t) == 0:
            return t

        slope = (end_freq - start_freq) / duration_sec
        phase = 2 * np.pi * (start_freq * t + 0.5 * slope * t**2)

        wave = np.zeros_like(t)
        for multiplier, amplitude in harmonics:
            harmonic_phase = phase * multiplier
            wave += amplitude * np.sin(harmonic_phase)

        wave *= 1.0 + 0.02 * np.sin(2 * np.pi * 4.5 * t)
        return wave * self._envelope(duration_ms, attack_ms=attack_ms, release_ms=release_ms)

    def generate_priority1_alarm_loop_once(self, duration_sec=4.0):
        segment_ms = 125
        total_ms = int(round(duration_sec * 1000))
        segments = []
        segment_count = int(np.ceil(total_ms / segment_ms))

        for index in range(segment_count):
            freq = 440.0 if index % 2 == 0 else 880.0
            this_ms = min(segment_ms, total_ms - index * segment_ms)
            segments.append(
                self._tone(
                    freq,
                    this_ms,
                    harmonics=((1, 1.0), (2, 0.12)),
                    attack_ms=5,
                    release_ms=6,
                )
            )

        return np.concatenate(segments) if segments else np.array([], dtype=float)

    def generate_priority1_alarm(self, duration_sec=4.0):
        return self.generate_priority1_alarm_loop_once(duration_sec=duration_sec)

    def generate_priority1_alarm_loop(self, repeats=3, duration_sec=4.0):
        loop_once = self.generate_priority1_alarm_loop_once(duration_sec=duration_sec)
        if repeats <= 1:
            return loop_once

        return np.concatenate([loop_once for _ in range(repeats)])

    def generate_priority2_alarm(self, duration_sec=4.0):
        return self._tone(
            698.46,
            duration_sec * 1000,
            harmonics=((1, 1.0), (2, 0.08)),
            attack_ms=20,
            release_ms=24,
        )

    def generate_priority3_alarm(self, repeats=1, interval_sec=20.0):
        tone = self._tone(
            1046.5,
            100,
            harmonics=((1, 1.0), (3, 0.16)),
            attack_ms=6,
            release_ms=8,
        )
        burst = [
            tone,
            self._silence(150),
            tone,
            self._silence(150),
            tone,
            self._silence(200),
        ]

        if repeats <= 1:
            return np.concatenate(burst)

        burst_ms = 800
        gap_ms = max(0, int(round(interval_sec * 1000 - burst_ms)))
        segments = []
        for index in range(repeats):
            segments.extend(burst)
            if index < repeats - 1:
                segments.append(self._silence(gap_ms))

        return np.concatenate(segments)

    def generate_priority4_qrs(self):
        return self._tone(
            1397.0,
            100,
            harmonics=((1, 1.0), (3, 0.15)),
            attack_ms=4,
            release_ms=6,
        )

    def generate_key_click(self):
        return self._tone(
            1319.0,
            4,
            harmonics=((1, 1.0),),
            attack_ms=1,
            release_ms=1,
        )

    def generate_alert_tone(self):
        beep = self._tone(
            1000.0,
            100,
            harmonics=((1, 1.0), (3, 0.28), (5, 0.12)),
            attack_ms=4,
            release_ms=6,
        )
        return np.concatenate([beep, self._silence(100), beep, self._silence(140)])

    def generate_charge_tone(self, duration_sec=2.8):
        return self._chirp(
            440.0,
            1397.0,
            duration_sec * 1000,
            harmonics=((1, 0.92), (2, 0.28)),
            attack_ms=80,
            release_ms=140,
        )

    def generate_charge_complete(self):
        first = self._tone(
            1397.0,
            120,
            harmonics=((1, 1.0), (3, 0.12)),
            attack_ms=5,
            release_ms=10,
        )
        second = self._tone(
            1046.5,
            90,
            harmonics=((1, 1.0),),
            attack_ms=5,
            release_ms=10,
        )
        return np.concatenate([first, self._silence(60), second * 0.72])

    def _normalize(self, wave_data, peak=0.85):
        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            return wave_data.astype(np.int16)
        return (wave_data / max_value * peak * 32767).astype(np.int16)

    def export_audio(self, wave_data, filename, peak=0.85):
        pcm_16bit = self._normalize(wave_data, peak=peak)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")
