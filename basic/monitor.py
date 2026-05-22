import numpy as np
from scipy.io import wavfile


class HeartbeatSoundSynthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def generate_single_beat(self, spo2, hr):
        max_freq = 800
        freq_drop_per_percent = 15
        freq = max_freq - (100 - spo2) * freq_drop_per_percent
        freq = max(200, freq)

        pulse_duration = 0.06
        t_pulse = np.linspace(
            0, pulse_duration, int(self.sample_rate * pulse_duration), False
        )
        wave = np.sin(2 * np.pi * freq * t_pulse)

        fade_samples = int(0.01 * self.sample_rate)
        if len(wave) > fade_samples * 2:
            wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
            wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        beat_interval = 60.0 / hr
        gap_duration = max(0, beat_interval - pulse_duration)
        gap = np.zeros(int(self.sample_rate * gap_duration))
        return np.concatenate([wave, gap])

    def generate_deteriorating_spo2_hr_sequence(self):
        patient_vitals = [
            {"spo2": 100, "hr": 60},
            {"spo2": 100, "hr": 62},
            {"spo2": 98, "hr": 65},
            {"spo2": 95, "hr": 75},
            {"spo2": 92, "hr": 85},
            {"spo2": 90, "hr": 95},
            {"spo2": 88, "hr": 105},
            {"spo2": 85, "hr": 115},
            {"spo2": 83, "hr": 125},
            {"spo2": 82, "hr": 140},
        ]

        segments = []
        for vitals in patient_vitals:
            segments.append(self.generate_single_beat(spo2=vitals["spo2"], hr=vitals["hr"]))

        return np.concatenate(segments)

    def export_audio(self, wave_data, filename, peak=1.0):
        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            pcm_16bit = wave_data.astype(np.int16)
        else:
            pcm_16bit = (wave_data / max_value * peak * 32767).astype(np.int16)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")
