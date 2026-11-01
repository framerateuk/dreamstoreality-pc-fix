# Dreams to Reality (DOS, 3dfx, 1997): subtitles that stay on screen

## Why this exists

One of the original 3DFX demo games. I had a demo of this with my Orchid Righteous 3D. The flying is
still quite impressive now, even if the game has dated quite a bit!

The aim here is to fix a bug with flashing subtitles that happens on real hardware and on DOSBox/PCEm.

## What this does

The fixes are three small changes to the game's DOS 3dfx exe, `DREAMSFX.EXE`:

- **Subtitles that stay on screen.** The game draws the dialogue text only on frames where its text clock has
  ticked, so on anything faster than a 1997 PC the text flashes or blinks: on real hardware, in DOSBox and
  its forks, PCem and 86Box. Patched to draw it every frame; the dialogue still advances and skips as before.
- **No black 3D world in DOSBox Pure**: a fog table built from density 0 comes out as solid black fog under
  DOSBox Pure's FPU emulation. Patched to switch the fog off instead, which is what the game meant. It
  changes nothing on a real PC or in other emulators.

Two ways to use it:

- **You have the game installed already** (a real PC with a Voodoo card, PCem / 86Box, DOSBox): patch the
  exe with `patch_exe.py` ([below](#just-the-fix)).
- **You'd like it ready to play in RetroArch's DOSBox Pure core** (the Steam Deck, or RetroArch on a PC):
  `build.py` turns your own two CDs into one zip with the game installed as the disc's 3dfx installer does
  it (Full install; the installer itself can't run in DOSBox, which has no `XCOPY`), the patched exe,
  **3dfx's Glide 2.42 DOS driver** from the disc's own 3dfx runtime kit, the Sound Blaster 16 set up, a pad
  layout, and both CDs (the music is CD audio).

**No game files are in this repository**, only the scripts and the patches. Everything from the game comes
from your CDs or your install.

## Just the fix

```
python3 patch_exe.py C:\CRYO\DREAMS\DREAMSFX.EXE
```

patches it in place and keeps the original as `DREAMSFX.ORG`. It checks the exe first (the English 3dfx
exe dated 29 Oct 1997, 1,025,154 bytes) and stops on any other. Python 3.8 or newer; on a real DOS PC,
patch the exe on another computer and copy it over.

## The DOSBox Pure zip

### What you need

| | |
|---|---|
| The game | **Both Dreams to Reality CDs** (English, exes dated 29 Oct 1997) as `.cue` + `.bin` / `.img`, or CloneCD `.ccd` + `.img`. `build.py` checks the 3dfx exe and stops on another version. A plain `.iso` works but has no music (it's on the CDs' audio tracks). |
| Python | 3.8 or newer (python.org on Windows; already on macOS/Linux). Nothing else to install. |
| RetroArch | with the **DOSBox Pure** core (Online Updater > Core Downloader > DOS (DOSBox-Pure)). |

### Build

```
python3 build.py DreamsToReality1.cue DreamsToReality2.cue
```

creates `DreamsToReality/` with `Dreams to Reality.zip` (about 1.4 GB: the CD images are in it, stored) and
`retroarch/` (`Dreams to Reality.cfg` and `.opt`, RetroArch's settings for this game), in a few seconds to a
minute. `--out DIR` puts it somewhere else. The zip is read back once at the end, so a bad copy on a full or
flaky disk shows up there rather than in the game.

### Install

1. Copy `Dreams to Reality.zip` to your DOS games folder, for example on the Steam Deck with EmuDeck
   `Emulation/roms/dos/`. Keep its name: RetroArch finds the game's settings by it.
2. With RetroArch closed, copy the two files in `retroarch/` to RetroArch's `config/DOSBox-pure/` folder:
   on the Steam Deck (Flatpak RetroArch) `~/.var/app/org.libretro.RetroArch/config/retroarch/config/DOSBox-pure/`,
   on Windows `RetroArch\config\DOSBox-pure\`. They set OpenGL (`glcore`, needed for Pure's Voodoo), a
   4:3 picture and Pure's machine settings. (RetroArch rewrites the `.opt` when the game closes, so copy
   it while RetroArch isn't running.)
3. Load the zip with the DOSBox Pure core. The game starts by itself (the intro: Select / Esc skips it).

Saved games and the level data the game copies as you play go to RetroArch's `saves/Dreams to Reality.pure.zip`
(it grows to roughly 70-150 MB), so rebuilding the zip keeps them.

### Controls

| Pad (Xbox / Deck labels) | Sends | In the game |
|---|---|---|
| Left stick, D-pad | arrows | run, back up, turn; menus |
| A | Alt | punch, sword, bow; with Up take off; hold with the arrows to fly / swim; walk |
| X | Ctrl | jump; kick in combat mode; with Down fast backwards |
| B | Space | combat mode on / off |
| LB / Y / RB | 1 / 2 / 3 | select magic 1 / 2 / 3 |
| RT / LT | Alt + 6 / Alt + 7 | other cameras |
| R3 | Alt + 5 | back to the default camera |
| Start | Enter | confirm (menus, New Game) |
| Select | Esc | the interface (menu) / back; skips the intro |
| L3 | Pure's on-screen keyboard | F10 help, F1-F6 resolution, Alt + 8 / 9 / 0 cameras; LB from there = Pure's Start Menu (disc swap) |

The keyboard works too: the game's keys are in the disc's `README.TXT` (section 6).

### Changing to CD 2

When the game says **"Please change to CD no 2"** it keeps checking the drive, so just swap the disc:

1. Press **L3** (Pure's on-screen keyboard), then **LB** to switch to Pure's **Start Menu** tab.
2. Move to `DREAMS2.CUE` (INSERT) with the D-pad and press **A**: it replaces CD 1 in D:.
3. Press **L3** to close the menu. The game carries on.

The same works backwards if it asks for CD 1. Or RetroArch's own: Quick Menu > Disc Control > Current Disc
Index 2, then Insert Disc.

### Settings

Edit the files in `config/zip/` and build again:

- **Speed**: `cycles=200000` in `DOSBOX.CONF`. If the 3D or the movies stutter, try `cycles=max`.
- **Software version** (no 3dfx): in `CRYO/DREAMS/GO.BAT` put `REM` in front of `DREAMSFX.EXE` and remove it
  from `REM DREAMS.EXE`. Same data and saved games; its first start asks to analyse the video modes (press a
  key), and the 3D is software, lower resolution.
- **Pad**: the table in `padmap.py`.

Tested on the Steam Deck (RetroArch, DOSBox Pure).

## What's in this repository

| File | What |
|---|---|
| `patch_exe.py` | The exe patches, each explained; runs on its own (above) and from `build.py`. |
| `build.py` | Builds the DOSBox Pure zip: copies the game from CD 1 as the 3dfx installer does, patches the exe, adds the Glide driver, the kit's settings, the pad map and both CD images. Python standard library only. |
| `disc.py` | Reads the CD images: `.cue`/`.bin`, `.ccd`/`.img` or `.iso`, ISO 9660. |
| `padmap.py` | DOSBox Pure's pad map (`PADMAP.DBP` in the zip). |
| `config/zip/` | What goes into the zip besides the game: `AUTOBOOT.DBP` (start `GO.BAT`), `DOSBOX.CONF` (the machine), `CRYO/DREAMS/GO.BAT`, `CRYO/DREAMS/DATA/SOUND/DIG.INI` (the game's sound set-up, Sound Blaster 16). |
| `config/retroarch/` | RetroArch's per-game `.cfg` and `.opt`. |
| `docs/TECHNICAL.md` | The versions on the CDs, the install, the settings, and how each patch was found. |

## Credits

- **Cryo Interactive** made Dreams to Reality. Please own the game: this kit needs your CDs.
- **3dfx Interactive**: Glide, from the runtime kit on the game's own CD 1.
- **Bernhard "schellingb" Schelling** for DOSBox Pure and its Voodoo emulation, and the DOSBox team.

## License

The scripts and docs in this repository: MIT (see `LICENSE`). The license covers only this repository's own
files, not the game.

Not affiliated with or endorsed by the game's rights holders.
