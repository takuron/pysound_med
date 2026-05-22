from basic.output import generate_examples as generate_basic_examples
from iec_60601.output import generate_examples as generate_iec_examples
from lifepak.output import generate_examples as generate_lifepak_examples
from philips_2021.output import generate_examples as generate_philips_examples


def generate_examples():
    generate_philips_examples()
    generate_iec_examples()
    generate_lifepak_examples()
    generate_basic_examples()


if __name__ == "__main__":
    generate_examples()
