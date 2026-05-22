import os

from .monitor import HeartbeatSoundSynthesizer
from .ui import BasicUISoundSynthesizer


def generate_ui_examples(output_dir=os.path.join("output", "basic", "ui")):
    synth = BasicUISoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    tasks = {
        "ui_basic_startup.wav": synth.generate_startup(),
        "ui_basic_click_normal.wav": synth.generate_click_normal(),
        "ui_basic_click_success.wav": synth.generate_click_success(),
        "ui_basic_click_error.wav": synth.generate_click_error(),
        "ui_basic_notification.wav": synth.generate_system_notification(),
    }

    for filename, wave_data in tasks.items():
        synth.export_audio(wave_data, os.path.join(output_dir, filename))


def generate_monitor_examples(output_dir=os.path.join("output", "basic", "monitor")):
    synth = HeartbeatSoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    wave_data = synth.generate_deteriorating_spo2_hr_sequence()
    synth.export_audio(wave_data, os.path.join(output_dir, "spo2_hr_dynamic_10beats.wav"))


def generate_examples():
    generate_ui_examples()
    generate_monitor_examples()


if __name__ == "__main__":
    generate_examples()
