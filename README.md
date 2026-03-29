# Logitech Yeti GX — Linux Control

Full hardware control for the Logitech Yeti GX microphone on Linux, without G Hub.
Reverse-engineered from G Hub USB traffic captures.

---

## Requirements

- Python 3
- udev rule to allow access without sudo (see below)

---

## Setup

Copy the udev rule so any user can access the device:

```
sudo cp udev/99-yeti-gx.rules /etc/udev/rules.d/
sudo udevadm control --reload && sudo udevadm trigger
```

Replug the microphone. After that, no `sudo` is needed.

---

## Usage

```
python3 yeti-ctl.py get
python3 yeti-ctl.py set <0-100>
python3 yeti-ctl.py mute
python3 yeti-ctl.py unmute
python3 yeti-ctl.py smartlock on|off
```

### Examples

```
python3 yeti-ctl.py set 75       # set hardware gain to 75%
python3 yeti-ctl.py get          # read current gain
python3 yeti-ctl.py mute         # mute mic, LED turns red
python3 yeti-ctl.py unmute       # unmute mic, LED turns white
python3 yeti-ctl.py smartlock on # enable Smart Audio Lock
python3 yeti-ctl.py smartlock off
```

---

## Features

### Hardware Gain (`set` / `get`)

Controls the actual hardware preamp gain (0–100). This is the same slider as in G Hub.
ALSA only exposes a software gain (0–12) which is separate and less useful.

### Mute / Unmute

Mutes or unmutes the microphone in hardware. The LED reflects the state:
- White = active
- Red = muted

This is equivalent to pressing the physical mute button on the device.

### Smart Audio Lock

A Logitech feature that automatically limits the gain when loud sounds are detected,
preventing clipping. Toggle it on or off from the command line.

---

## Protocol

The Yeti GX uses **Logitech HID++ 2.0** over USB HID.

- USB IDs: `046d:0afc`
- hidraw node: `/dev/hidraw7` (may vary — check `/dev/hidraw*` if it changes)
- HID Usage Page: `0xFF43` (Logitech vendor-defined)
- All mic controls live on **feature `0x8370`** (index 13), function 3

### Packet format

```
Byte 0    Report ID    0x10 = SHORT (7 bytes), 0x11 = LONG (20 bytes)
Byte 1    Device index 0xFF (wired)
Byte 2    Feature idx  0x0D (13 = feature 0x8370)
Byte 3    Func + SW_ID (func << 4) | SW_ID — func 3, SW_ID 12 = 0x3C
Bytes 4+  Parameters
```

### Raw commands

| Action | Packet |
|--------|--------|
| Set gain to N | `10 ff 0d 3c 00 01 <N>` |
| Get gain | `10 ff 0d 2c 00 01 00` → gain in byte 7 of response |
| Mute | `10 ff 0d 3c 00 00 00` |
| Unmute | `10 ff 0d 3c 00 00 01` |
| Smart Lock on | `11 ff 0d 3c 00 05 07 00 ca 00 00 02 00 00 00 00 00 00 00 00` |
| Smart Lock off | `11 ff 0d 3c 00 05 06 00 ca 00 00 02 00 00 00 00 00 00 00 00` |

### Physical button events (device → host, read-only)

The mute button on the device sends notifications you can listen to:

```
Button press:   11 ff 0d 20 00 00 00 00 ...
Button release: 11 ff 0d 20 00 00 01 00 ...
```

These are input reports from the device, not commands.

