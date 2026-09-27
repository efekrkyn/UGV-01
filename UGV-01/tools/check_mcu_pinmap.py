"""Check UGV-MCU-01 GPIO choices against KiCad's STM32G474 LQFP100 symbol."""
import argparse
import json
import re
from pathlib import Path


def _block(source, start):
    depth = 0
    quoted = escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ValueError("Unclosed KiCad s-expression")


def read_kicad_pins(library, base_symbol):
    source = Path(library).read_text()
    needle = f'(symbol "{base_symbol}"'
    if needle not in source:
        raise ValueError(f"Symbol missing: {base_symbol}")
    symbol = _block(source, source.index(needle))
    pins = {}
    for match in re.finditer(r"\(pin (?:input|output|bidirectional|passive|power_in|power_out)", symbol):
        entry = _block(symbol, match.start())
        name = re.search(r'\(name "([^"]+)"', entry)
        number = re.search(r'\(number "([^"]+)"', entry)
        if name and number:
            pins[name.group(1)] = {
                "number": int(number.group(1)),
                "functions": set(re.findall(r'\(alternate "([^"]+)"', entry)),
            }
    return pins


SERVOS = ("SERVO_PAN", "SERVO_TILT", "SERVO_SHOULDER", "SERVO_GRIPPER")
FORBIDDEN = {"PB8": "BOOT0"}


def validate(manifest, pins):
    errors, seen, signals = [], {}, set()
    required = {
        *(f"ENC_{wheel}_{phase}" for wheel in ("FL", "FR", "RL", "RR") for phase in ("A", "B")),
        *(f"PWM_{wheel}_{side}" for wheel in ("FL", "FR", "RL", "RR") for side in ("IN1", "IN2")),
        "CAN_RX", "CAN_TX", "SWDIO", "SWCLK", "SAFETY_BKIN_TIM1", "SAFETY_BKIN_TIM8",
        "MCU_RUN_REQ", "MCU_WDI", "PWR_ACT_EN_FB", "PWR_K1_FB", "PWR_K2_FB",
        "ESTOP_A_CLOSED", "ESTOP_B_CLOSED", "PWR_WD_OK",
        *SERVOS, "LIGHT_DATA", "SERVO_I_SENSE", "SERVO_PWR_REQ",
    }
    for assignment in manifest["assignments"]:
        signal, gpio = assignment["signal"], assignment["gpio"]
        if signal in signals:
            errors.append(f"duplicate signal {signal}")
        signals.add(signal)
        if gpio in seen:
            errors.append(f"duplicate GPIO {gpio}: {seen[gpio]} and {signal}")
        seen[gpio] = signal
        if gpio not in pins:
            errors.append(f"{signal}: {gpio} missing from package")
            continue
        pin = pins[gpio]
        if pin["number"] != assignment["package_pin"]:
            errors.append(f"{signal}: {gpio} package pin {pin['number']} != {assignment['package_pin']}")
        function = assignment["function"]
        if function != "GPIO" and function not in pin["functions"]:
            errors.append(f"{signal}: {gpio} has no {function} alternate function")
        if gpio in FORBIDDEN:
            errors.append(f"{signal}: {gpio} is reserved for {FORBIDDEN[gpio]}")
    # One timer = one PWM frequency; servo timers run at 50 Hz and are not shared.
    timer = lambda a: a["function"].split("_")[0] if a["function"].startswith("TIM") else None
    servo_timers = {timer(a) for a in manifest["assignments"] if a["signal"] in SERVOS}
    for a in manifest["assignments"]:
        if a["signal"] not in SERVOS and timer(a) in servo_timers:
            errors.append(f"{a['signal']}: {timer(a)} is a 50 Hz servo timer")
    for signal in sorted(required - signals):
        errors.append(f"missing required signal {signal}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("config/mcu_pinmap.json"))
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    errors = validate(manifest, read_kicad_pins(args.library, manifest["kicad_base_symbol"]))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(manifest['assignments'])} assignments match {manifest['mcu']}")
