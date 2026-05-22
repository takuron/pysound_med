import os

from .defib import DefibrillatorSoundSynthesizer
from .monitor import IEC60601SoundSynthesizer


def generate_monitor_examples(output_dir=os.path.join("output", "iec", "monitor")):
    synth = IEC60601SoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    systems = [
        "General",
        "Cardiovascular",
        "Ventilation",
        "Oxygen",
        "Temperature",
        "DrugDelivery",
    ]
    urgencies = ["high", "medium", "low"]
    params = {
        "high": {"bpm": 120, "pitch": 2.0},
        "medium": {"bpm": 100, "pitch": 1.5},
        "low": {"bpm": 90, "pitch": 1.5},
    }

    for system in systems:
        for urgency in urgencies:
            filename = f"{system.lower()}_{urgency}.wav"
            path = os.path.join(output_dir, filename)
            wave_data = synth.generate_alarm(
                alarm_type=system,
                urgency=urgency,
                bpm=params[urgency]["bpm"],
                pitch=params[urgency]["pitch"],
            )
            synth.export_audio(wave_data, path)
            print(f"Exported: {path} | Type: {system} | Urgency: {urgency}")


def generate_defib_examples(output_dir=os.path.join("output", "iec", "defib")):
    synth = DefibrillatorSoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    tasks = {
        "defib_charge.wav": synth.generate_charging(duration_sec=4.0, end_freq=1200),
        "defib_charge_complete.wav": synth.generate_charge_complete(
            duration_sec=1.5, freq=1200
        ),
        "defib_stand_clear.wav": synth.generate_stand_clear(repeats=8, freq=1046.5),
    }

    for filename, wave_data in tasks.items():
        synth.export_audio(wave_data, os.path.join(output_dir, filename))


def generate_examples():
    generate_monitor_examples()
    generate_defib_examples()


if __name__ == "__main__":
    generate_examples()
