"""Bring-up helper (DD89): writes the NVS CSV each board reads at boot (namespace "ugv") from the git-ignored
~/.config/ugv/link.env and wifi.env, into ~/.config/ugv/nvs/ (owner-only), never into the repo.

    python3 tools/make_nvs.py s3 [--motor-pol 1,-1,1,1] [--vbat-cal 1000] [--pca-osc-hz 25000000] [--port 4210]
    python3 tools/make_nvs.py eye [--aec 300 --agc 2 --wb-mode 3]   # after the stereo calibration

wifi.env holds UGV_WIFI_SSID= and UGV_WIFI_PASS= lines. The printed commands turn the CSV into a partition image and
flash it (docs/lite_software_A3.md, "NVS ayarları")."""
import argparse
import csv
import io
import os
from pathlib import Path
import re
import sys


def check(ok, msg):
    if not ok:
        raise ValueError(msg)


def _in(v, lo, hi, name):
    check(lo <= v <= hi, f"{name} {v} outside {lo}..{hi}")
    return str(v)


def _wifi(ssid, pw):
    check(1 <= len(ssid.encode()) <= 32, "SSID must be 1..32 bytes")
    check(pw == "" or re.fullmatch(r"[ -~]{8,63}|[0-9a-fA-F]{64}", pw), "Wi-Fi password: 8..63 ASCII (or empty)")
    return [("ssid", "data", "string", ssid), ("pass", "data", "string", pw)]


def rows_s3(key_hex, ssid, pw, port=4210, vbat_cal=1000, pca_osc_hz=25_000_000, motor_pol=(1, 1, 1, 1)):
    """The keys app_main.c reads (settings_load)."""
    check(re.fullmatch(r"[0-9a-fA-F]{64}", key_hex or ""), "link key must be 64 hex characters (32 bytes)")
    check(len(motor_pol) == 4 and all(p in (1, -1) for p in motor_pol), "motor_pol: four of +1/-1 (FL, FR, RL, RR)")
    return [("link_key", "data", "hex2bin", key_hex.lower()), *_wifi(ssid, pw),
            ("port", "data", "u16", _in(port, 1, 65535, "port")),
            ("vbat_cal", "data", "u16", _in(vbat_cal, 800, 1200, "vbat_cal (per mille)")),
            ("pca_osc_hz", "data", "u32", _in(pca_osc_hz, 23_000_000, 27_000_000, "pca_osc_hz")),
            ("motor_pol", "data", "hex2bin", bytes(p & 0xFF for p in motor_pol).hex())]


def rows_eye(ssid, pw, aec=None, agc=None, wb_mode=None):
    """The keys eye_main.c reads; left out = automatic until the stereo calibration fixes them."""
    rows = _wifi(ssid, pw)
    for name, v, hi in (("aec", aec, 1200), ("agc", agc, 30), ("wb_mode", wb_mode, 4)):
        if v is not None:
            rows.append((name, "data", "i32", _in(v, 0, hi, name)))
    return rows


def render(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerows([("key", "type", "encoding", "value"), ("ugv", "namespace", "", ""), *rows])
    return buf.getvalue()


def read_env(path):
    if not path.exists():
        sys.exit(f"{path} missing (see docs/lite_software_A3.md)")
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, _, v = line.removeprefix("export ").partition("=")
            env[k.strip()] = v.strip().strip("'\"")
    return env


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="board", required=True)
    s3 = sub.add_parser("s3")
    s3.add_argument("--port", type=int, default=4210)
    s3.add_argument("--vbat-cal", type=int, default=1000)
    s3.add_argument("--pca-osc-hz", type=int, default=25_000_000)
    s3.add_argument("--motor-pol", default="1,1,1,1")
    eye = sub.add_parser("eye")
    for opt in ("--aec", "--agc", "--wb-mode"):
        eye.add_argument(opt, type=int)
    a = ap.parse_args(argv)
    conf = Path.home() / ".config/ugv"
    wifi = read_env(conf / "wifi.env")
    ssid, pw = wifi.get("UGV_WIFI_SSID", ""), wifi.get("UGV_WIFI_PASS", "")
    try:
        if a.board == "s3":
            key = read_env(conf / "link.env").get("UGV_LINK_KEY", "")
            pol = tuple(int(p) for p in a.motor_pol.split(","))
            rows, chip = rows_s3(key, ssid, pw, a.port, a.vbat_cal, a.pca_osc_hz, pol), "esp32s3"
        else:
            rows, chip = rows_eye(ssid, pw, a.aec, a.agc, a.wb_mode), "esp32"
    except ValueError as e:
        sys.exit(f"refused: {e}")
    out_dir = conf / "nvs"
    out_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    out_dir.chmod(0o700)
    out = out_dir / f"{a.board}.csv"
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(render(rows))
    gen = "/opt/esp/idf/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py"
    print(f"wrote {out} (secrets: never commit or paste it). Next:\n"
          f"  docker run --rm -v {out_dir}:/nvs espressif/idf:v5.3.2 python {gen} generate "
          f"/nvs/{a.board}.csv /nvs/{a.board}.bin 0x6000\n"
          f"  python3 -m esptool --chip {chip} write_flash 0x9000 {out_dir}/{a.board}.bin")


if __name__ == "__main__":
    main()
