import os

from .infusion_pump import Medfusion4000PumpSoundSynthesizer


def generate_examples(output_dir=os.path.join("output", "medfusion_4000", "pump")):
    synth = Medfusion4000PumpSoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    tasks = {
        "medfusion_4000_alarm_high.wav": synth.generate_high_priority_alarm(repeats=5),
        "medfusion_4000_alarm_medium.wav": synth.generate_medium_priority_alarm(
            repeats=4
        ),
        "medfusion_4000_alarm_low.wav": synth.generate_low_priority_alarm(),
        "medfusion_4000_alarm_high_loop_once.wav": synth.generate_alarm_loop_once(
            "high"
        ),
        "medfusion_4000_alarm_medium_loop_once.wav": synth.generate_alarm_loop_once(
            "medium"
        ),
        "medfusion_4000_alarm_low_once.wav": synth.generate_alarm_loop_once("low"),
        "medfusion_4000_limit_alert.wav": synth.generate_limit_alert(
            key_click_level=4
        ),
        "medfusion_4000_key_click_level2.wav": synth.generate_key_click(level=2),
        "medfusion_4000_key_click_level5.wav": synth.generate_key_click(level=5),
        "medfusion_4000_user_callback.wav": synth.generate_user_callback_alarm(),
        "medfusion_4000_syringe_near_empty_medium.wav": synth.generate_syringe_near_empty_alarm(
            "medium"
        ),
        "medfusion_4000_syringe_near_empty_low.wav": synth.generate_syringe_near_empty_alarm(
            "low"
        ),
        "medfusion_4000_syringe_volume_near_empty.wav": synth.generate_syringe_volume_near_empty_alarm(),
        "medfusion_4000_syringe_empty.wav": synth.generate_syringe_empty_alarm(),
        "medfusion_4000_kvo_in_progress.wav": synth.generate_kvo_in_progress_alarm(),
        "medfusion_4000_system_advisory.wav": synth.generate_system_advisory_alarm(),
        "medfusion_4000_system_fault.wav": synth.generate_system_fault_alarm(
            duration_sec=8.0
        ),
        "medfusion_4000_motor_fault_two_tone.wav": synth.generate_motor_fault_alarm(
            duration_sec=8.0
        ),
    }

    for filename, wave_data in tasks.items():
        synth.export_audio(wave_data, os.path.join(output_dir, filename))

    print(f"All Medfusion 4000 pump examples generated in directory: {output_dir}")


if __name__ == "__main__":
    generate_examples()
