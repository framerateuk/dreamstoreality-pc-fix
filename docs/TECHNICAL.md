# How it works

Notes on Dreams to Reality (Cryo Interactive, 1997; English, two CDs, exes dated 29 Oct 1997) and on what
`build.py` and `patch_exe.py` do.

## Which version

The CDs hold three versions, each with its own installer (the disc's `README.TXT`):

| Version | Exe | Installer | This kit |
|---|---|---|---|
| Windows 95, Direct3D / GDI | `WINDREAM.EXE`, `GDIDREAM.EXE` | `SETUP.EXE` (autorun) | no |
| DOS, software (SVGA through UniVBE) | `DREAMS.EXE` (1,176,454 bytes) | `INSTALL.BAT` -> `INST_SON.BAT` | fallback in `GO.BAT` |
| **DOS, 3dfx** | **`DREAMSFX.EXE`** (DOS/4GW, 1,025,154 bytes, MD5 `0a1da2aaf3c83db3ae941c46f8f74cd5`) | **`INSTALFX.BAT` -> `INST_SFX.BAT`** | **yes** |

`DREAMSFX.EXE` imports Glide 2 (130 functions) from `GLIDE2X.OVL` at run time. CD 1 brings 3dfx's own
runtime kit, `3DFX\GRTVGR.EXE` (Sep 1997, Glide 2.42, a self-extracting zip); its
`Glide\Drivers\Voodoo\Dos\glide2x.ovl` (348,791 bytes, MD5 `341b8f5d82daa46fd1ce236300317c3c`) exports all
130 and goes into the game folder. The other files in `3DFX\` are Windows drivers, not used.

The music is CD audio: CD 1 = data + 11 audio tracks, CD 2 = data + 13. The game tells the CDs apart by
`DATA\1CD.ID` / `DATA\2CD.ID`.

## The install

`INSTALFX.BAT` asks for the drive and calls `INST_SFX.BAT`, which only makes folders and `XCOPY`s files
(DOSBox and DOSBox Staging have no `XCOPY`, so the batch file can't run there; `build.py` does the same
copies): the disc root's files to `C:\CRYO\DREAMS`; `DATA\HD.ID`, `REPLAY.BIN`; `DATA\3DC\DIALOG.DRD`,
`*.3DC`, `*.3DM`; `DATA\SOUND\*`, `DATA\UNIVBE\*`; empty `DATA\GAME`, `DATA\ANIM`. Then it runs
`SETSOUND.EXE` and asks "Minimum install?": No = Full = `DATA\HD.ID` copied to `DATA\FULL.ID`.

- **Full install** doesn't copy more at install time: the game itself copies the current level set from
  the CD to `DATA\3DC` / `DATA\ANIM` when a game starts ("Please wait while loading", about 70 MB for CD 1's
  set, recorded in `DATA\LEVEL.ID`), and again for CD 2. The disc README: "improving disk access during the
  game ... also offers video-maps" (animated textures). So the folder grows to roughly 100-180 MB as you play.
- **`DATA\SOUND\DIG.INI`** (`config/DIG.INI`): what the game's `SETSOUND.EXE` (Miles Sound System 3.50B)
  writes after "Creative Labs Sound Blaster 16 or AWE32", "Attempt to configure automatically" ->
  "Device detected successfully": `SB16.DIG` at 220h, IRQ / DMA from the `BLASTER` variable. Digital audio
  only; the music is CD audio.
- **`GO.BAT`** sets `FX_GLIDE_NO_SPLASH=1` (no 3dfx logo) and runs `DREAMSFX.EXE`.
- Saved games: `DATA\GAME\GAME.DAT`, `GAMEn.DAT`, `GAMEn.ICO`.

`build.py`'s game folder is byte for byte the one we tested (69 files; only `GO.BAT`'s comments differ).

## The DOSBox Staging settings

`config/dosbox.conf`: S3 SVGA, Pentium, **200000 cycles** in protected mode, 32 MB (the installer asks for
20 MB), Sound Blaster 16 at 220 / 7 / 1 / 5, Voodoo 1 with 4 MB, bilinear filtering on (as a real Voodoo).
Cycles: the 3D frame rate about doubled from 77000 to 150000 cycles, and the 640x480 movies are decoded by
the CPU. Both CDs are mounted as D: (`imgmount`, which Staging 0.83 calls deprecated but still runs; it keeps
the file working in 0.82); Ctrl+F4 swaps them.

## The exe patches

`patch_exe.py` changes 3 places in `DREAMSFX.EXE` (21 bytes). Addresses are in the exe's code object
(loaded at 0x20000 by DOS/4GW); the file offsets are in `patch_exe.py`.

### Subtitles that flash

The dialogue text flickers or blinks. It isn't an emulator problem: on Vogons the same is reported in
DOSBox, DOSBox-X, dgVoodoo, PCem, 86Box, and on a real Voodoo 3 PC. The cause (found with an instrumented
emulator and the disassembly): the dialogue routine (0x5c73c, called every frame while someone talks)
works out a text clock, (time - start) / 14, and only on frames where that clock has moved on does it draw
the subtitle lines (straight into the Voodoo's back buffer); on every other frame it only checks for the
skip key and returns. A 1997 PC drew fewer frames than the clock ticked, so every frame had the text;
anything faster shows it on every second or third frame. Measured: the 2,685 text pixel writes came on
alternate buffer swaps only.

The patch changes two jumps:

- 0x5ce54 `je 0x5d010` (no clock tick: skip-key check, return) -> `je 0x5cf00`: draw the lines, then the
  line-advance / end-of-dialogue checks (which only compare the clock, so repeating them is harmless).
- 0x5cfd0 `ja 0x5d0b4` (return after drawing) -> `ja 0x5d010`: the skip-key check, then return, so the
  keys that skip a line still work on every frame.

The text now shows on every frame; the dialogue still advances and ends ("Again") as before.

### A black 3D world (DOSBox Pure)

In DOSBox Pure (RetroArch) the whole 3D world is black: only the HUD, the dialogue portraits and the movies
show. Found with an instrumented DOSBox Pure build (Voodoo register log): the game draws thousands of
triangles a frame, but its fog table is all 255 with a black fog colour.

For a level without fog the game still calls its fog routine (0x671d0) with density 0.0, which runs
`grFogMode(GR_FOG_WITH_TABLE)`, `grFogColorValue(0)`, `guFogGenerateExp(table, 0.0)`, `grFogTable(table)`.
Glide's `guFogGenerateExp` normalises by 1 / (1 - exp(0)) = 1 / 0, so every entry is NaN. On a real FPU the
NaN fails both clamp tests (f > 1, f < 0) and converts to 0: an all-zero table, no fog. DOSBox Pure's FPU
emulation (`src/fpu/fpu_instructions.h`, `FPU_FCOM` checks only the register tags, never for NaN) answers
"greater" for NaN > 1.0, so every entry becomes 255: full fog, in black.

The patch (at 0x29308) makes that "no fog" branch call `grFogMode(GR_FOG_DISABLE)` instead, which is what
the all-zero table meant:

```
xor eax,eax / push 0 / call 0x671d0          31 c0 6a 00 e8 bf de 03 00
push 0 / call grFogMode / nop nop            6a 00 e8 36 f7 08 00 90 90
```

(`grFogMode` is stdcall and pops its argument; the old callee popped its own float too.) Levels with real
fog (a non-zero density from the level, or the animated fog) still take the other branches. DOSBox Staging's
FPU handles the NaN as a real one does, so Staging doesn't need this patch; it changes nothing there or on
a real PC, and it lets the same exe run in DOSBox Pure.

## Changing CDs

When the game needs the other CD it shows **"Please change to CD no 2"** and keeps checking the drive (its
wait loop at 0x645be retries opening the ID file), so swapping the disc is enough: no key press needed.
