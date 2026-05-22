import numpy as np
from scipy.io import wavfile


class IEC60601SoundSynthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

        self.FREQS = {
            "C4": 261.63,
            "D4": 293.66,
            "E4": 329.63,
            "F4": 349.23,
            "G4": 392.00,
            "A4": 440.00,
            "B4": 493.88,
            "C5": 523.25,
            "D5": 587.33,
            "E5": 659.25,
            "F5": 698.46,
            "G5": 783.99,
        }

        self.MELODIES = {
            "General": ["C4", "C4", "C4", "C4", "C4"],
            "Cardiovascular": ["C4", "E4", "G4", "G4", "C5"],
            "Ventilation": ["C4", "A4", "F4", "A4", "F4"],
            "Oxygen": ["C4", "B4", "A4", "G4", "F4"],
            "Temperature": ["C4", "D4", "E4", "F4", "G4"],
            "DrugDelivery": ["C4", "D4", "G4", "C4", "D4"],
        }

    def _generate_pulse(self, freq, duration_ms, pitch_factor=1.0):
        actual_freq = freq * pitch_factor
        t = np.linspace(
            0, duration_ms / 1000, int(self.sample_rate * duration_ms / 1000), False
        )

        harmonics = [1.0, 0.6, 0.4, 0.3, 0.2]
        wave = np.zeros_like(t)
        for index, amp in enumerate(harmonics):
            harmonic_freq = actual_freq * (index + 1)
            if harmonic_freq < self.sample_rate / 2:
                wave += amp * np.sin(2 * np.pi * harmonic_freq * t)

        env_len = int(15 * self.sample_rate / 1000)
        envelope = np.ones_like(t)
        if len(t) > env_len * 2:
            envelope[:env_len] = np.linspace(0, 1, env_len)
            envelope[-env_len:] = np.linspace(1, 0, env_len)

        return wave * envelope

    def generate_alarm(self, alarm_type="General", urgency="high", bpm=120, pitch=1.0):
        melody_keys = self.MELODIES.get(alarm_type, self.MELODIES["General"])
        beat_ms = 60000 / bpm

        if urgency == "low":
            pulse_len = beat_ms * 0.50
        elif urgency == "medium":
            pulse_len = beat_ms * 0.35
        else:
            pulse_len = beat_ms * 0.25

        gap_ms = beat_ms * 0.15
        segments = []

        if urgency == "high":
            unit = []
            for index in range(3):
                unit.append(
                    self._generate_pulse(self.FREQS[melody_keys[index]], pulse_len, pitch)
                )
                unit.append(np.zeros(int(gap_ms * self.sample_rate / 1000)))

            unit.append(np.zeros(int(beat_ms * 0.5 * self.sample_rate / 1000)))

            for index in range(3, 5):
                unit.append(
                    self._generate_pulse(self.FREQS[melody_keys[index]], pulse_len, pitch)
                )
                unit.append(np.zeros(int(gap_ms * self.sample_rate / 1000)))

            segments.extend(unit)
            segments.append(np.zeros(int(beat_ms * 1.5 * self.sample_rate / 1000)))
            segments.extend(unit)
        elif urgency == "medium":
            for index in range(3):
                segments.append(
                    self._generate_pulse(self.FREQS[melody_keys[index]], pulse_len, pitch)
                )
                segments.append(np.zeros(int(gap_ms * self.sample_rate / 1000)))
        else:
            for _ in range(2):
                segments.append(
                    self._generate_pulse(self.FREQS[melody_keys[0]], pulse_len, pitch)
                )
                segments.append(np.zeros(int(gap_ms * 2 * self.sample_rate / 1000)))

        return np.concatenate(segments)

    def create_alarm(self, config):
        wave_data = self.generate_alarm(
            alarm_type=config.get("type", "General"),
            urgency=config.get("urgency", "high"),
            bpm=config.get("bpm", 120),
            pitch=config.get("pitch", 1.0),
        )
        self.export_audio(wave_data, config["name"])
        print(
            f"Exported: {config['name']} | "
            f"Type: {config.get('type', 'General')} | "
            f"Urgency: {config.get('urgency', 'high')}"
        )
        return wave_data

    def export_audio(self, wave_data, filename, peak=1.0):
        max_value = np.max(np.abs(wave_data))
        if max_value == 0:
            pcm_16bit = wave_data.astype(np.int16)
        else:
            pcm_16bit = (wave_data / max_value * peak * 32767).astype(np.int16)
        wavfile.write(filename, self.sample_rate, pcm_16bit)
