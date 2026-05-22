import os

from .ventilator import HamiltonVentilatorSoundSynthesizer


def generate_examples(output_dir=os.path.join("output", "hamilton", "ventilator")):
    synth = HamiltonVentilatorSoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    tasks = {
        "hamilton_alarm_high.wav": synth.generate_high_priority_alarm(repeats=4),
        "hamilton_alarm_medium.wav": synth.generate_medium_priority_alarm(repeats=3),
        "hamilton_alarm_low.wav": synth.generate_low_priority_alarm(),
        "hamilton_alarm_high_loop_once.wav": synth.generate_alarm_loop_once("high"),
        "hamilton_alarm_medium_loop_once.wav": synth.generate_alarm_loop_once("medium"),
        "hamilton_alarm_low_once.wav": synth.generate_alarm_loop_once("low"),
        "hamilton_technical_fault.wav": synth.generate_technical_fault(duration_sec=8.0),
        "hamilton_continuous_buzzer.wav": synth.generate_continuous_buzzer(
            duration_sec=8.0
        ),
        "hamilton_touch_key.wav": synth.generate_touch_key(),
        "hamilton_screen_locked_beep.wav": synth.generate_screen_locked_beep(),
        "hamilton_prompt_confirm.wav": synth.generate_prompt_confirm(),
        "hamilton_prompt_warning.wav": synth.generate_prompt_warning(),
    }

    for filename, wave_data in tasks.items():
        synth.export_audio(wave_data, os.path.join(output_dir, filename))

    print(f"All Hamilton ventilator examples generated in directory: {output_dir}")


if __name__ == "__main__":
    generate_examples()
