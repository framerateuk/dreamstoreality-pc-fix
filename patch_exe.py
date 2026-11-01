#!/usr/bin/env python3
"""Patch DREAMSFX.EXE, the DOS 3dfx exe of Dreams to Reality (Cryo, 29 Oct 1997, 1,025,154 bytes,
MD5 0a1da2aaf3c83db3ae941c46f8f74cd5). build.py runs it; it also works on its own, on a game already
installed (DOSBox, or a real PC with a Voodoo card):

    python3 patch_exe.py DREAMSFX.EXE            patch in place, the original kept as DREAMSFX.ORG
    python3 patch_exe.py IN.EXE OUT.EXE          write the patched exe to OUT.EXE

nofog: the black world under DOSBox Pure's Voodoo.
  For a level without fog the game still calls its fog routine (0x671d0) with density 0.0, which runs
  grFogMode(GR_FOG_WITH_TABLE), grFogColorValue(0), guFogGenerateExp(table, 0.0), grFogTable(table).
  Glide's guFogGenerateExp normalises by 1 / (1 - exp(-density * w_max)) = 1 / 0 = inf, so every entry is
  0 * inf = NaN. On a real FPU the NaN fails both clamp tests (f > 1, f < 0) and its int conversion gives 0:
  an all-zero table, no fog. DOSBox Pure's C FPU (fpu_instructions.h FPU_FCOM: no NaN check, only the tags)
  answers "greater" for NaN > 1.0, so every entry becomes 255: full fog in black, the whole 3D world drawn
  black (only the HUD and dialogue show). Measured with an instrumented Pure core, 22 Oct 2026: fogTable
  register writes all 0xff00ff00, fogMode 1, fogColor 0; level struct fog fields 0.
  Patch (code object at 0x20000; this caller at 0x29308, file offset 0x3a508), the "no fog" branch:
      xor eax,eax / push 0 / call 0x671d0          (31 c0 6a 00 e8 bf de 03 00)
   -> push 0 / call grFogMode thunk 0xb8a45 / nop nop   (6a 00 e8 36 f7 08 00 90 90)
  i.e. grFogMode(GR_FOG_DISABLE) (stdcall, pops its argument; the old callee popped its own float too),
  which is what the all-zero table meant. The next instruction (mov [0x159f9c], ebx, with its fixup) is
  untouched. Levels with fog (non-zero density, or the animated sin() fog) still take the other branches.

subtitles: the dialogue text flashes (seen in DOSBox Pure on the Steam Deck, 22 Oct 2026; Vogons: the same in DOSBox, DOSBox-X,
  PCem, 86Box, and on a real Voodoo 3 PC). The dialogue routine (0x5c73c, called every frame while someone
  talks) works out the text clock, (time - start) / 14, and only on frames where that clock has moved on does it
  draw the subtitle lines (LFB writes into the back buffer, blitter 0x305ee); on every other frame it just checks
  for a skip key and returns. On a 1997 PC the game drew fewer frames than the clock ticked, so every frame had
  the text; on anything faster (any emulator at full speed) only every second or third frame has it = flashing.
  Measured with an instrumented Pure core: the 2,685 text pixel writes come on alternate swaps only.
  Patch, two jumps:
    0x5ce54  je 0x5d010 (no clock tick: skip-key check, return)  -> je 0x5cf00 (draw the lines, then the
             line-advance / end-of-dialogue checks, which only compare the clock, so repeating them is harmless)
             0f84b6010000 -> 0f84a6000000 (file offset 0x6e054)
    0x5cfd0  ja 0x5d0b4 (return after drawing) -> ja 0x5d010 (the skip-key check, then return), so the keys
             that skip a line still work on every frame
             0f87de000000 -> 0f873a000000 (file offset 0x6e1d0)
  The text now shows on every frame; the dialogue still advances and ends ("Again") as before.
"""
import hashlib, os, sys

MD5 = "0a1da2aaf3c83db3ae941c46f8f74cd5"
PATCHES = [  # (file offset, original bytes, new bytes, name)
    (0x3a508, "31c06a00e8bfde0300", "6a00e836f708009090", "nofog"),
    (0x6e054, "0f84b6010000", "0f84a6000000", "subtitles: draw without a clock tick"),
    (0x6e1d0, "0f87de000000", "0f873a000000", "subtitles: then check the skip key"),
]


def patch(data, verbose=True):
    """The patched exe's bytes; stops if `data` is not the expected DREAMSFX.EXE."""
    d = bytearray(data)
    if all(d[o:o + len(bytes.fromhex(n))] == bytes.fromhex(n) for o, _, n, _ in PATCHES) and len(d) == 1025154:
        sys.exit("this DREAMSFX.EXE is patched already")
    if hashlib.md5(d).hexdigest() != MD5:
        sys.exit(f"not the DREAMSFX.EXE the kit was made for (MD5 {hashlib.md5(d).hexdigest()}, expected {MD5})")
    for off, old, new, name in PATCHES:
        old, new = bytes.fromhex(old), bytes.fromhex(new)
        assert d[off:off + len(old)] == old, name
        d[off:off + len(new)] = new
        if verbose: print(f"  {name}: {off:#x} {old.hex()} -> {new.hex()}")
    return bytes(d)


def main(argv):
    if len(argv) not in (1, 2): sys.exit(__doc__)
    src = argv[0]
    out = patch(open(src, "rb").read())
    if len(argv) == 2:
        dst = argv[1]
    else:
        keep = os.path.join(os.path.dirname(src), "DREAMSFX.ORG")
        if os.path.exists(keep): sys.exit(f"{keep} exists already: move it away first")
        os.rename(src, keep); dst = src
        print(f"  original kept as {keep}")
    with open(dst, "wb") as f: f.write(out)
    print(f"patched: {dst}")


if __name__ == "__main__":
    main(sys.argv[1:])
