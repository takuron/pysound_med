import numpy as np
from scipy.io import wavfile


class DefibrillatorSoundSynthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def _generate_standard_pulse(self, freq, duration_ms):
        t = np.linspace(
            0, duration_ms / 1000, int(self.sample_rate * duration_ms / 1000), False
        )

        harmonics = [1.0, 0.6, 0.4, 0.3, 0.2]
        wave = np.zeros_like(t)
        for index, amp in enumerate(harmonics):
            harmonic_freq = freq * (index + 1)
            if harmonic_freq < self.sample_rate / 2:
                wave += amp * np.sin(2 * np.pi * harmonic_freq * t)

        env_len = int(15 * self.sample_rate / 1000)
        envelope = np.ones_like(t)
        if len(t) > env_len * 2:
            envelope[:env_len] = np.linspace(0, 1, env_len)
            envelope[-env_len:] = np.linspace(1, 0, env_len)

        return wave * envelope

    def generate_charging(self, duration_sec=4.0, start_freq=300, end_freq=1200):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), False)
        slope = (end_freq - start_freq) / duration_sec
        phase = 2 * np.pi * (start_freq * t + 0.5 * slope * t**2)
        wave = np.sin(phase) + 0.6 * np.sin(2 * phase) + 0.4 * np.sin(3 * phase)

        envelope = np.ones_like(t)
        fade_in_samples = int(0.2 * self.sample_rate)
        envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
        return wave * envelope

    def generate_charge_complete(self, duration_sec=1.5, freq=1200):
        return self._generate_standard_pulse(freq, duration_sec * 1000)

    def generate_stand_clear(self, repeats=8, freq=1046.5):
        pulse_duration = 100
        gap_duration = 100
        tone = self._generate_standard_pulse(freq, pulse_duration)
        gap = np.zeros(int(self.sample_rate * gap_duration / 1000))

        segments = []
        for _ in range(repeats):
            segments.extend([tone, gap])

        return np.concatenate(segments)

    def export_audio(self, wave_data, filename, peak=1.0):
        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            pcm_16bit = wave_data.astype(np.int16)
        else:
            pcm_16bit = (wave_data / max_value * peak * 32767).astype(np.int16)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")
