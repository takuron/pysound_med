import os

from .defib import LifePakSeriesDefibrillatorSoundSynthesizer


def generate_examples(output_dir=os.path.join("output", "lifepak", "defib")):
    synth = LifePakSeriesDefibrillatorSoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    tasks = {
        "lifepak_priority1_alarm.wav": synth.generate_priority1_alarm(),
        "lifepak_priority1_alarm_loop_once.wav": synth.generate_priority1_alarm_loop_once(),
        "lifepak_priority1_alarm_loop_repeat.wav": synth.generate_priority1_alarm_loop(
            repeats=3
        ),
        "lifepak_priority2_alarm.wav": synth.generate_priority2_alarm(),
        "lifepak_priority3_alarm.wav": synth.generate_priority3_alarm(),
        "lifepak_priority4_qrs.wav": synth.generate_priority4_qrs(),
        "lifepak_key_click.wav": synth.generate_key_click(),
        "lifepak_alert_tone.wav": synth.generate_alert_tone(),
        "lifepak_charge_tone.wav": synth.generate_charge_tone(),
        "lifepak_charge_complete.wav": synth.generate_charge_complete(),
    }

    for filename, wave_data in tasks.items():
        synth.export_audio(wave_data, os.path.join(output_dir, filename))

    print(f"All LIFEPAK defibrillator examples generated in directory: {output_dir}")


if __name__ == "__main__":
    generate_examples()
