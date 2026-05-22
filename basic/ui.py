import numpy as np
from scipy.io import wavfile


class BasicUISoundSynthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def _generate_pure_tone(self, freq, duration_sec, fade_ms=5):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), False)
        wave = np.sin(2 * np.pi * freq * t)

        fade_samples = int(fade_ms * self.sample_rate / 1000)
        envelope = np.ones_like(wave)
        if len(wave) > fade_samples * 2:
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        return wave * envelope

    def generate_startup(self):
        tone_1 = self._generate_pure_tone(261.63, 0.2)
        gap = np.zeros(int(0.075 * self.sample_rate))
        tone_2 = self._generate_pure_tone(329.63, 0.2)
        tone_3 = self._generate_pure_tone(392.00, 0.45)
        return np.concatenate([tone_1, gap, tone_2, gap, tone_3])

    def generate_click_normal(self):
        return self._generate_pure_tone(400, 0.03, fade_ms=2)

    def generate_click_success(self):
        tone_1 = self._generate_pure_tone(800, 0.08)
        gap = np.zeros(int(0.04 * self.sample_rate))
        tone_2 = self._generate_pure_tone(1000, 0.12)
        return np.concatenate([tone_1, gap, tone_2])

    def generate_click_error(self):
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(2 * np.pi * 150 * t)
        wave = np.clip(wave * 1.5, -1, 1)

        fade = int(10 * self.sample_rate / 1000)
        wave[:fade] *= np.linspace(0, 1, fade)
        wave[-fade:] *= np.linspace(1, 0, fade)
        return wave

    def generate_system_notification(self):
        tone_1 = self._generate_pure_tone(600, 0.2)
        tone_2 = self._generate_pure_tone(800, 0.4)
        return np.concatenate([tone_1, tone_2])

    def export_audio(self, wave_data, filename, peak=1.0):
        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            pcm_16bit = wave_data.astype(np.int16)
        else:
            pcm_16bit = (wave_data / max_value * peak * 32767).astype(np.int16)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
        print(f"Exported: {filename}")
