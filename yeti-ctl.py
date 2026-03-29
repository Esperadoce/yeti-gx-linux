#!/usr/bin/env python3
"""
Logitech Yeti GX control via HID++ 2.0
Feature 0x8370 (index 13), func 3

Reverse-engineered from G Hub USB capture.

Usage:
  python3 yeti-ctl.py get
  python3 yeti-ctl.py set <0-100>
  python3 yeti-ctl.py mute
  python3 yeti-ctl.py unmute
  python3 yeti-ctl.py smartlock on|off
"""
import sys, time, os, glob

VENDOR_ID = "046D"
PRODUCT_ID = "0AFC"

def find_hidraw():
    for uevent_path in glob.glob("/sys/bus/hid/devices/*/uevent"):
        with open(uevent_path) as f:
            content = f.read()
        if f"HID_ID=0003:0000{VENDOR_ID}:0000{PRODUCT_ID}" in content:
            dev_dir = os.path.dirname(uevent_path)
            nodes = glob.glob(os.path.join(dev_dir, "hidraw/hidraw*"))
            if nodes:
                return "/dev/" + os.path.basename(nodes[0])
    return None

HIDRAW = find_hidraw()
if HIDRAW is None:
    print("Yeti GX not found. Is it plugged in?", file=sys.stderr)
    sys.exit(1)

DEV_IDX  = 0xFF
FEAT_IDX = 13    # 0x8370
FUNC     = 3
SW_ID    = 12    # G Hub uses SW_ID=12
FUNC_SW  = (FUNC << 4) | SW_ID   # 0x3C

class HidrawDevice:
    def __init__(self, path):
        self.f = open(path, "r+b", buffering=0)
        os.set_blocking(self.f.fileno(), False)
    def __enter__(self): return self.f
    def __exit__(self, *_): self.f.close()

def open_dev():
    return HidrawDevice(HIDRAW)

def send_recv(f, data, timeout=0.5):
    f.write(bytes(data))
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = f.read(64)
            if r:
                return r
        except BlockingIOError:
            time.sleep(0.01)
    return None

def set_gain(f, gain):
    pkt = bytes([0x10, DEV_IDX, FEAT_IDX, FUNC_SW, 0x00, 0x01, gain])
    return send_recv(f, pkt)

def get_gain(f):
    r = send_recv(f, bytes([0x10, DEV_IDX, FEAT_IDX, (2 << 4) | SW_ID, 0x00, 0x01, 0x00]))
    if r and len(r) >= 8:
        return r[7]
    return None

def set_mute(f, muted):
    # muted=True  → 10 ff 0d 3c 00 00 00
    # muted=False → 10 ff 0d 3c 00 00 01
    pkt = bytes([0x10, DEV_IDX, FEAT_IDX, FUNC_SW, 0x00, 0x00, 0x00 if muted else 0x01])
    return send_recv(f, pkt)

def set_smartlock(f, enabled):
    # on  → 11 ff 0d 3c 00 05 07 00 ca 00 00 02 00 00 00 00 00 00 00 00
    # off → 11 ff 0d 3c 00 05 06 00 ca 00 00 02 00 00 00 00 00 00 00 00
    pkt = bytes([0x11, DEV_IDX, FEAT_IDX, FUNC_SW, 0x00, 0x05, 0x07 if enabled else 0x06,
                 0x00, 0xca, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    return send_recv(f, pkt)

cmd = sys.argv[1] if len(sys.argv) > 1 else "get"

with open_dev() as f:
    if cmd == "get":
        g = get_gain(f)
        print(f"Gain: {g} / 100")

    elif cmd == "set":
        if len(sys.argv) < 3:
            print("Usage: yeti-ctl.py set <0-100>")
            sys.exit(1)
        gain = int(sys.argv[2])
        if not 0 <= gain <= 100:
            print("Gain must be 0–100")
            sys.exit(1)
        set_gain(f, gain)
        print(f"Gain: {gain} / 100")

    elif cmd == "mute":
        set_mute(f, True)
        print("Muted")

    elif cmd == "unmute":
        set_mute(f, False)
        print("Unmuted")

    elif cmd == "smartlock":
        if len(sys.argv) < 3 or sys.argv[2] not in ("on", "off"):
            print("Usage: yeti-ctl.py smartlock on|off")
            sys.exit(1)
        set_smartlock(f, sys.argv[2] == "on")
        print(f"Smart Lock: {sys.argv[2]}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
