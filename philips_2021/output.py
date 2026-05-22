import os

from .monitor import Philips2021SoundSynthesizer


def generate_examples(output_dir=os.path.join("output", "philips", "monitor")):
    synth = Philips2021SoundSynthesizer()
    os.makedirs(output_dir, exist_ok=True)

    tasks = {
        "philips_2021_alarm_high.wav": synth.generate_alarm("high"),
        "philips_2021_alarm_medium.wav": synth.generate_alarm("medium"),
        "philips_2021_alarm_low.wav": synth.generate_alarm("low"),
        "philips_2021_alarm_high_loop_once.wav": synth.generate_alarm_loop_once(
            "high"
        ),
        "philips_2021_alarm_medium_loop_once.wav": synth.generate_alarm_loop_once(
            "medium"
        ),
        "philips_2021_alarm_low_loop_once.wav": synth.generate_alarm_loop_once("low"),
        "philips_2021_spo2_98_hr72.wav": synth.generate_spo2_pulse(
            spo2=98, heart_rate=72, beats=12
        ),
        "philips_2021_spo2_90_hr110.wav": synth.generate_spo2_pulse(
            spo2=90, heart_rate=110, beats=16
        ),
        "philips_2021_qrs_hr75.wav": synth.generate_qrs_beep(heart_rate=75, beats=10),
        "philips_2021_prompt_ok.wav": synth.generate_prompt_ok(),
        "philips_2021_prompt_error.wav": synth.generate_prompt_error(),
        "philips_2021_key.wav": synth.generate_prompt_key(),
    }

    for filename, wave_data in tasks.items():
        synth.export_audio(wave_data, os.path.join(output_dir, filename))

    print(f"All Philips 2021 monitor examples generated in directory: {output_dir}")


if __name__ == "__main__":
    generate_examples()
