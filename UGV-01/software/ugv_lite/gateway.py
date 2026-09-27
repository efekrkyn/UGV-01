"""MacBook panel gateway for A3 Lite: panel WebSocket messages -> AI-mode permit, local stop, AI task.

The panel (software/web_ui/panel.html) is served on 127.0.0.1 only and talks JSON over ws://<host>/ai:
in  {"type": "lease", "ai": true} every 50 ms while allowed, {"type": "stop", "source": ...},
    {"type": "instruction", "text": ...}, {"type": "arm_parked"} (operator parked the arm at stow by hand);
    out {"type": "say"|"ask"|"status", ...}.
`websockets`, the Anthropic SDK and sockets are imported only by `main()`; the logic is host-testable.
"""
import json
import os
from pathlib import Path
import queue
import re
import threading

STOP_WORDS = {"dur", "durdur", "stop", "kes"}  # same list as software/web_ui/panel_logic.mjs


def is_stop(text):
    return any(word in STOP_WORDS for word in re.split(r"[^\w]+", str(text).lower()))


class Gateway:
    def __init__(self, permit, executor, vehicle, run_task, send):
        self.permit, self.executor, self.vehicle = permit, executor, vehicle
        self.run_task, self.send = run_task, send
        self.busy = False
        self.answers = None  # a queue while ask() waits for the operator

    def stop(self, source):
        self.executor.request_stop(source)
        self.vehicle.send_stop()
        self.send({"type": "status", "text": f"Durduruldu ({source})."})

    def handle(self, message):
        kind = message.get("type") if isinstance(message, dict) else None
        if kind == "lease":
            if message.get("ai"):
                self.permit.set(ai_switch=True, visible_focused=True)
                self.permit.renew()
            else:
                self.permit.set(ai_switch=False, visible_focused=False)
        elif kind == "stop":
            self.stop(str(message.get("source", "panel")))
        elif kind == "arm_parked":
            if self.busy:
                self.send({"type": "status", "text": "Görev sürerken kol park onayı verilemez; önce durdurun."})
            else:
                self.vehicle.confirm_arm_parked()
                self.send({"type": "status", "text": "Kol park onayı gönderildi (yalnız araç kurulu değilken geçer)."})
        elif kind == "instruction":
            text = str(message.get("text", "")).strip()
            if is_stop(text):
                self.stop("instruction")  # defence in depth: the panel already stops locally
            elif self.answers is not None:
                self.answers.put(text)
            elif self.busy:
                self.send({"type": "status", "text": "Bir görev sürüyor; önce bitmesini bekleyin ya da durdurun."})
            elif text:
                self.run_task(text)
        else:
            self.send({"type": "status", "text": f"unknown message type {kind!r}"})

    def ask(self, question, timeout=60.0):
        """Executor `operator` callback: ask on the panel and wait for the next typed answer."""
        self.answers = queue.Queue()
        self.send({"type": "ask", "question": question})
        try:
            return self.answers.get(timeout=timeout)
        except queue.Empty:
            return None
        finally:
            self.answers = None

    def task(self, bridge, text, arm_timeout_s=2.0):
        """One AI task: arm through the IDLE handshake, run the bridge, report; the vehicle ends stopped."""
        self.busy = True
        try:
            self.vehicle.request_arm()
            clock, start = self.executor.clock, self.executor.clock.monotonic()
            while not self.vehicle.armed() and clock.monotonic() - start < arm_timeout_s:
                clock.sleep(0.05)
            if not self.vehicle.armed():
                self.send({"type": "status", "text": "Araç kurulamadı (bağlantı, E-stop veya arıza)."})
                return
            result = bridge.run(text)
            self.send({"type": "status", "text": f"{result.status}: {result.text} ({result.steps} adım, ${result.usd:.3f})"})
        finally:
            self.vehicle.stop()
            self.vehicle.disarm()
            self.busy = False


def serve(gateway, host="127.0.0.1", port=8765):
    """Serve the panel page and the /ai WebSocket on one localhost port (blocking)."""
    import asyncio
    from websockets.asyncio.server import serve as ws_serve
    from websockets.datastructures import Headers
    from websockets.http11 import Response

    web = Path(__file__).resolve().parents[1] / "web_ui"
    files = {"/": ("panel.html", "text/html"), "/panel_logic.mjs": ("panel_logic.mjs", "text/javascript")}

    def page(connection, request):
        if request.path == "/ai":
            return None
        name, mime = files.get(request.path, (None, None))
        if name is None:
            return connection.respond(404, "not found\n")
        body = (web / name).read_bytes()
        return Response(200, "OK", Headers([("Content-Type", f"{mime}; charset=utf-8"),
                                            ("Content-Length", str(len(body)))]), body)

    async def main():
        loop = asyncio.get_running_loop()

        async def client(ws):
            gateway.send = lambda msg: loop.call_soon_threadsafe(asyncio.ensure_future, ws.send(json.dumps(msg)))
            async for raw in ws:
                try:
                    gateway.handle(json.loads(raw))
                except (ValueError, TypeError):
                    gateway.send({"type": "status", "text": "unknown message type: not JSON"})
        async with ws_serve(client, host, port, process_request=page):
            await asyncio.Future()

    asyncio.run(main())


def main():
    """MacBook entry point. Needs UGV_LINK_KEY (64 hex chars, from the git-ignored ~/.config/ugv/link.env),
    UGV_ESP32_ADDR (host:port), optional UGV_EYE_URLS (comma-separated ESP32-CAM /capture URLs) and the
    model API key the bridge reads. Not run against hardware yet (L4)."""
    import socket
    import sys
    import time
    import urllib.request

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from ugv_ai.bridge import AiBridge
    from ugv_ai.executor import Permit, SkillExecutor
    from ugv_lite.vehicle import LiteVehicle

    class Clock:
        monotonic, sleep = staticmethod(time.monotonic), staticmethod(time.sleep)

    class UdpLink:
        def __init__(self, address):
            self.address, self.sock = address, socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setblocking(False)

        def send(self, data):
            self.sock.sendto(data, self.address)

        def recv(self):
            got = []
            while True:
                try:
                    data, source = self.sock.recvfrom(64)
                except BlockingIOError:
                    return got
                if source[0] == self.address[0]:
                    got.append(data)

    key = bytes.fromhex(os.environ["UGV_LINK_KEY"])
    host, port = os.environ["UGV_ESP32_ADDR"].rsplit(":", 1)
    eyes = [u for u in os.environ.get("UGV_EYE_URLS", "").split(",") if u]
    clock = Clock()
    permit = Permit(clock)
    vehicle = LiteVehicle(UdpLink((host, int(port))), key, clock, permit_ok=permit.ok,
                          cameras=[lambda u=u: urllib.request.urlopen(u, timeout=2).read() for u in eyes])

    def pump():
        while True:
            vehicle.pump()
            time.sleep(0.02)
    threading.Thread(target=pump, daemon=True).start()
    gateway = Gateway(permit, None, vehicle, run_task=None, send=lambda msg: None)
    gateway.executor = SkillExecutor(vehicle, permit, clock, panel=lambda t: gateway.send({"type": "say", "text": t}),
                                     operator=gateway.ask)
    bridge = AiBridge(gateway.executor, vehicle, log_dir=Path.home() / ".local/share/ugv/logs")
    gateway.run_task = lambda text: threading.Thread(target=gateway.task, args=(bridge, text), daemon=True).start()
    serve(gateway)


if __name__ == "__main__":
    main()
