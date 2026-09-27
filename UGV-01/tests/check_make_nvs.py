"""Bring-up NVS helper (DD89): the CSV carries exactly the keys each firmware reads, with matching types; bad values
are refused; the files land outside the repo with owner-only permissions. Synthetic key, no real secrets."""
import csv
import io
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_nvs  # noqa: E402

KEY = "00112233445566778899aabbccddeeff" * 2
ENC = {"str": "string", "blob": "hex2bin", "u16": "u16", "u32": "u32", "i32": "i32"}


def reads(src):  # {key: nvs_get_* type} as the firmware reads it
    return {k: t for t, k in re.findall(r'nvs_get_(str|blob|u16|u32|i32)\(h, "(\w+)"', (ROOT / src).read_text())}


def table(text):
    rows = list(csv.reader(io.StringIO(text)))
    assert rows[:2] == [["key", "type", "encoding", "value"], ["ugv", "namespace", "", ""]], rows[:2]
    return {k: (t, e, v) for k, t, e, v in rows[2:]}


def refused(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except ValueError:
        return True
    return False


# Firmware <-> CSV: every key the firmware reads is written, with the encoding its nvs_get_* call needs.
s3 = table(make_nvs.render(make_nvs.rows_s3(KEY, "ugv, robot", "correct horse", motor_pol=(1, -1, 1, -1))))
fw = reads("firmware/lite/esp32/main/app_main.c")
assert set(s3) == set(fw) == {"link_key", "ssid", "pass", "port", "vbat_cal", "pca_osc_hz", "motor_pol"}, (s3, fw)
assert all(s3[k][:2] == ("data", ENC[t]) for k, t in fw.items()), s3
assert s3["link_key"][2] == KEY and s3["motor_pol"][2] == "01ff01ff" and s3["ssid"][2] == "ugv, robot"
assert s3["port"][2] == "4210" and s3["vbat_cal"][2] == "1000" and s3["pca_osc_hz"][2] == "25000000"
eye_fw = reads("firmware/lite/eye/main/eye_main.c")
eye = table(make_nvs.render(make_nvs.rows_eye("ugv", "correct horse", aec=300, agc=2, wb_mode=3)))
assert set(eye) == set(eye_fw) == {"ssid", "pass", "aec", "agc", "wb_mode"}, (eye, eye_fw)
assert all(eye[k][:2] == ("data", ENC[t]) for k, t in eye_fw.items()), eye
assert (eye["aec"][2], eye["agc"][2], eye["wb_mode"][2]) == ("300", "2", "3")
# Before the stereo calibration nothing is fixed: the eyes keep automatic exposure, gain and white balance.
assert set(table(make_nvs.render(make_nvs.rows_eye("ugv", "correct horse")))) == {"ssid", "pass"}

# Values the firmware would misuse are refused before anything is flashed.
assert refused(make_nvs.rows_s3, KEY[:-2], "ugv", "correct horse")               # 31-byte key
assert refused(make_nvs.rows_s3, "zz" * 32, "ugv", "correct horse")              # not hex
assert refused(make_nvs.rows_s3, KEY, "x" * 33, "correct horse")                 # SSID > 32 bytes
assert refused(make_nvs.rows_s3, KEY, "ugv", "short")                            # WPA2 needs 8..63
assert refused(make_nvs.rows_s3, KEY, "ugv", "correct horse", motor_pol=(1, 2, 1, 1))
assert refused(make_nvs.rows_s3, KEY, "ugv", "correct horse", motor_pol=(1, 1, 1))
assert refused(make_nvs.rows_s3, KEY, "ugv", "correct horse", vbat_cal=500)
assert refused(make_nvs.rows_s3, KEY, "ugv", "correct horse", pca_osc_hz=30_000_000)
assert refused(make_nvs.rows_s3, KEY, "ugv", "correct horse", port=0)
assert refused(make_nvs.rows_eye, "ugv", "correct horse", aec=1300)
assert refused(make_nvs.rows_eye, "ugv", "correct horse", wb_mode=5)
assert not refused(make_nvs.rows_s3, KEY, "open-net", "")                        # open network: no password

# The command reads the git-ignored env files and writes owner-only CSVs under ~/.config/ugv/nvs, never the repo.
with tempfile.TemporaryDirectory() as home:
    conf = Path(home) / ".config/ugv"
    conf.mkdir(parents=True)
    (conf / "link.env").write_text(f"UGV_LINK_KEY={KEY}\n")
    (conf / "wifi.env").write_text('# robot network\nexport UGV_WIFI_SSID="ugv robot"\nUGV_WIFI_PASS=correct horse\n')
    os.environ["HOME"] = home
    for board, args in (("s3", ["s3", "--motor-pol", "1,-1,1,-1"]), ("eye", ["eye", "--aec", "300"])):
        make_nvs.main(args)
        out = conf / "nvs" / f"{board}.csv"
        assert stat.S_IMODE(out.stat().st_mode) == 0o600 and stat.S_IMODE(out.parent.stat().st_mode) == 0o700
        got = table(out.read_text())
        assert got["ssid"][2] == "ugv robot" and got["pass"][2] == "correct horse", got
    assert table((conf / "nvs/s3.csv").read_text())["motor_pol"][2] == "01ff01ff"
    assert table((conf / "nvs/eye.csv").read_text())["aec"][2] == "300"
    (conf / "wifi.env").unlink()
    try:
        make_nvs.main(["eye"])
        raise AssertionError("missing wifi.env accepted")
    except SystemExit as e:
        assert "wifi.env" in str(e), e
assert not list(ROOT.rglob("s3.csv")) and not list(ROOT.rglob("eye.csv"))

print("PASS: NVS CSVs carry exactly the keys and types both firmwares read; bad key/Wi-Fi/calibration refused; "
      "written owner-only under ~/.config/ugv/nvs from the env files, never in the repo (DD89)")
