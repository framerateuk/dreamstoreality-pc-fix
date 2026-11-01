#!/usr/bin/env python3
"""PADMAP.DBP, DOSBox Pure's gamepad map for Dreams to Reality (3dfx DOS version); build.py puts it in the zip.

    python3 padmap.py          prints the map's bytes

Keys only, no emulated joystick (the game has its own joypad mode, J / K switch joypad / keyboard, but the
keyboard is its default, and a keys-only map keeps Pure's joystick and any calibration away).
The game's keys (README.TXT section 6 on the disc): Up run, Down backwards, Left / Right turn; Ctrl jump (kick in
combat mode; Ctrl + Down fast backwards, Ctrl + Up long jump); Alt walk, punch, swing the sword / shoot the bow
(Alt + Up take off; hold Alt + arrows to fly or swim); Space combat mode; 1 / 2 / 3 select a magic; Alt + 5..0
cameras (Alt + 5 the default one); F1..F6 resolution; Esc the interface (menu); F10 controls help.
Layout (Xbox / Steam Deck labels): A attack (Alt), X jump (Ctrl), B combat mode, Y and the shoulders the magic
keys, Start Enter, Select Esc, L3 Pure's on-screen keyboard; left stick and D-pad both send the arrows (the game
is digital).
File format: a version byte (0), then per port the number of mappings and, for each, the RetroPad button id
(top two bits: number of keys - 1) followed by the key codes (analog ids: a negative, positive pair each).
Key codes are DOSBox Pure's KBD_KEYS enum (include/keyboard.h).
"""
import os
# RetroPad ids. RetroPad names follow the SNES layout, so on the Deck (Xbox labels):
# RetroPad B = Deck A (bottom), RetroPad A = Deck B (right), RetroPad Y = Deck X (left), RetroPad X = Deck Y (top).
B, Y, SELECT, START, UP, DOWN, LEFT, RIGHT, A, X, L, R, L2, R2, L3, R3, LSTICK_X, LSTICK_Y = range(18)
# keyboard (Pure's KBD_KEYS enum, include/keyboard.h)
KBD_1, KBD_2, KBD_3, KBD_5, KBD_6, KBD_7 = 1, 2, 3, 5, 6, 7
KBD_f10 = 46
KBD_esc, KBD_enter, KBD_space, KBD_leftalt, KBD_leftctrl = 49, 52, 53, 54, 56
KBD_left, KBD_up, KBD_down, KBD_right = 83, 84, 85, 86
OSD = 225                     # Pure's on-screen keyboard (DBP_SpecialMappings)

MAP = [  # (button id, [codes]) -- analog ids take (negative, positive) pairs
    (LSTICK_X, [(KBD_left, KBD_right)]),   # turn
    (LSTICK_Y, [(KBD_up, KBD_down)]),      # run / backwards
    (LEFT, [KBD_left]), (RIGHT, [KBD_right]), (UP, [KBD_up]), (DOWN, [KBD_down]),
    (B, [KBD_leftalt]),       # Deck A: Alt = punch, sword, bow; with Up take off; hold to fly / swim; walk
    (Y, [KBD_leftctrl]),      # Deck X: Ctrl = jump; kick in combat mode
    (A, [KBD_space]),         # Deck B: Space = combat mode on / off
    (X, [KBD_2]),             # Deck Y: magic 2
    (L, [KBD_1]),             # LB: magic 1
    (R, [KBD_3]),             # RB: magic 3
    (R2, [KBD_leftalt, KBD_6]),   # RT: Alt + 6 = second camera
    (L2, [KBD_leftalt, KBD_7]),   # LT: Alt + 7 = third camera
    (R3, [KBD_leftalt, KBD_5]),   # R3: Alt + 5 = back to the default camera
    (START, [KBD_enter]),     # Enter
    (SELECT, [KBD_esc]),      # Escape: the interface (menu) / back
    (L3, [OSD]),              # Pure's on-screen keyboard (F10 help, F1-F6 resolution, other cameras, J / K)
]

def build():
    out = bytearray([0])              # version
    port = bytearray([len(MAP)])
    for btn, keys in sorted(MAP):
        port.append(btn | ((len(keys) - 1) << 6))
        for k in keys:
            port.extend(k if isinstance(k, tuple) else (k,))
    out += port
    return bytes(out)

if __name__ == "__main__":
    data = build()
    print(len(data), "bytes:", data.hex(" "))
