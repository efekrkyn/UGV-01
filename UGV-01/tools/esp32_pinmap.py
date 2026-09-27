"""Check the A3 Lite ESP32-S3-DevKitC-1 pin map (config/esp32_pinmap.json)."""
import json
from pathlib import Path

MOTORS = ("FL", "FR", "RL", "RR")
REQUIRED = {
    *(f"M_{m}_IN{i}" for m in MOTORS for i in (1, 2)),
    *(f"ENC_{m}_A" for m in MOTORS),  # one channel per motor, rear included (R4)
    "SERVO_OE", "LIGHT_DATA",  # M3: servo PWM comes from the PCA9685 on I2C0; /OE stays on the ESP32
    "I2C_SDA", "I2C_SCL", "TOF_XSHUT", "VBAT_SENSE", "ACT_EN", "ESTOP_SENSE",
}
# ESP32-S3: 2 MCPWM units x 6 outputs, 8 LEDC channels, 4 RMT TX channels, 2 I2C buses, 4 PCNT units.
CAPACITY = {"MCPWM": 12, "LEDC": 8, "RMT": 4, "I2C": 4}
PCNT_UNITS = 4
ADC1_GPIOS = range(1, 11)  # ADC2 is shared with Wi-Fi and unusable while it runs


def header_pin(m, gpio):
    """'J1-4' style DevKitC header position of a GPIO, or None."""
    for header, names in m["headers"].items():
        if str(gpio) in names:
            return f"{header}-{names.index(str(gpio)) + 1}"
    return None


def validate(m):
    errors, gpios, signals, counts, pcnt = [], {}, set(), {}, set()
    for a in m["assignments"]:
        name, gpio, peripheral = a["signal"], a["gpio"], a["peripheral"]
        if name in signals:
            errors.append(f"duplicate signal {name}")
        signals.add(name)
        if gpio in gpios:
            errors.append(f"duplicate GPIO{gpio} : {gpios[gpio]} and {name}")
        gpios[gpio] = name
        if header_pin(m, gpio) is None:
            errors.append(f"GPIO{gpio} {name}: not on the DevKitC headers")
        if str(gpio) in m["unavailable"]:
            errors.append(f"GPIO{gpio} {name}: reserved ({m['unavailable'][str(gpio)]})")
        if peripheral == "ADC1" and gpio not in ADC1_GPIOS:
            errors.append(f"GPIO{gpio} {name}: analog input must be on ADC1 (GPIO1-10)")
        if peripheral == "PCNT":
            pcnt.add(name.rsplit("_", 1)[0])  # one unit per encoder
        counts[peripheral] = counts.get(peripheral, 0) + 1
    for peripheral, cap in CAPACITY.items():
        if counts.get(peripheral, 0) > cap:
            errors.append(f"{peripheral}: {counts[peripheral]} > {cap}")
    if len(pcnt) > PCNT_UNITS:
        errors.append(f"PCNT: {len(pcnt)} units > {PCNT_UNITS}")
    errors += [f"missing required signal {s}" for s in sorted(REQUIRED - signals)]
    return errors


if __name__ == "__main__":
    manifest = json.loads((Path(__file__).resolve().parents[1] / "config/esp32_pinmap.json").read_text())
    problems = validate(manifest)
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"PASS: {len(manifest['assignments'])} assignments")
