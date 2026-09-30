"""Deterministic host re-arm race; signed frames only, no hardware or paid API.

Usage: python3 repro_rearm_telemetry_race.py /path/to/UGV-01
"""
import struct
import sys
import threading
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "software"))
from ugv_lite import frames
from ugv_lite.vehicle import LiteVehicle


class Clock:
    t = 0

    def monotonic(self):
        return self.t


class Link:
    def __init__(self):
        self.inbox = []

    def recv(self):
        result, self.inbox = self.inbox, []
        return result

    def send(self, data):
        pass


clock, link, key = Clock(), Link(), bytes(range(32))
vehicle = LiteVehicle(link, key, clock, session=0x12345678)
vehicle.lease_ext, vehicle.leases = 70001, [(70000, 0)]
old_session = vehicle.session
old_status = struct.pack("<BBHI", 2, 0, 10, 1000)
link.inbox = [frames.pack(frames.TLM, 0x190, old_status, key, frames.bind(old_session, 70000))]
verified, resume = threading.Event(), threading.Event()
verify = vehicle._verify


def paused_verify(data):
    result = verify(data)
    verified.set()
    assert resume.wait(2)
    return result


vehicle._verify = paused_verify
pump = threading.Thread(target=vehicle.pump)
pump.start()
assert verified.wait(2)
vehicle.request_arm()  # Gateway.task worker, concurrently with main's pump worker
resume.set()
pump.join(2)
assert not pump.is_alive()
vehicle._verify = verify
assert vehicle.session != old_session
assert vehicle.last_ext[0x190] == 70000 and vehicle.armed()
print("old DRIVING status accepted after session reset: armed=True, last_ext=70000")

clock.t = 0.02
vehicle.leases = [(1, clock.t)]
idle = struct.pack("<BBHI", 0, 0, 11, 1020)
new_status = frames.pack(frames.TLM, 0x190, idle, key, frames.bind(vehicle.session, 1))
assert verify(new_status) is not None  # authentic current-session packet
link.inbox = [new_status]
vehicle.pump()
assert vehicle.status["state"] == "DRIVING" and vehicle.last_ext[0x190] == 70000
clock.t = 0.3
assert not vehicle.armed()
print("valid new-session IDLE ext1 rejected; old status subsequently stale: armed=False")
print("Host freshness/recovery defect confirmed; unsafe physical motion not tested or claimed.")
