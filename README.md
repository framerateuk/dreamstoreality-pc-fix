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
- **You'd like it ready to play in [DOSBox Staging](https://www.dosbox-staging.org/)**: `build.py` turns
  your own two CDs into a folder with the game installed as the disc's 3dfx installer does it (Full install;
  the installer itself can't run in DOSBox, which has no `XCOPY`), the patched exe, **3dfx's Glide 2.42 DOS
  driver** from the disc's own 3dfx runtime kit, the Sound Blaster 16 set up, and a `dosbox.conf` with both
  CDs mounted (the music is CD audio), a fast Pentium and the Voodoo on.

**No game files are in this repository.** Everything from the game comes from your CDs or your install.

## Just the fix

```
python3 patch_exe.py C:\CRYO\DREAMS\DREAMSFX.EXE
```

patches it in place and keeps the original as `DREAMSFX.ORG`. It checks the exe first (the English 3dfx
exe dated 29 Oct 1997, 1,025,154 bytes) and stops on any other. Python 3.8 or newer; on a real DOS PC,
patch the exe on another computer and copy it over.

## What you need

| | |
|---|---|
| The game | **Both Dreams to Reality CDs** (English, exes dated 29 Oct 1997) as `.cue` + `.bin` / `.img`, or CloneCD `.ccd` + `.img`. `build.py` checks the 3dfx exe and stops on another version. A plain `.iso` works but has no music (it's on the CDs' audio tracks). |
| Python | 3.8 or newer (python.org on Windows; already on macOS/Linux). Nothing else to install. |
| DOSBox Staging | for `build.py`'s folder: 0.82 or newer, [dosbox-staging.org](https://www.dosbox-staging.org/). |

## Build

```
python3 build.py DreamsToReality1.cue DreamsToReality2.cue
```

creates `DreamsToReality/` with `drive_c/` (the game in `C:\CRYO\DREAMS`) and `dosbox.conf`, in a few
seconds. `--out DIR` puts it somewhere else. CD 2 can be left off and added later (edit the `imgmount` line
in `dosbox.conf`). The CD images stay where they are: `dosbox.conf` names them by their full path, so if
you move them, edit that line. For a `.ccd` without a `.cue`, `build.py` writes a `.cue` next to it (DOSBox
Staging reads `.cue` files).

## Play

Start DOSBox Staging in the folder:

```
dosbox --working-dir "C:\Games\DreamsToReality"                   (Windows: dosbox.exe in Staging's folder)
dosbox-staging --working-dir ~/Games/DreamsToReality               (macOS with Homebrew)
```

It loads the folder's `dosbox.conf` and starts the game. **Alt+Enter** toggles full screen. When the game
says **"Please change to CD no 2"**, press **Ctrl+F4** (swap disc) and it carries on by itself. Quitting the
game closes DOSBox.

Your saved games and the level data the game copies as you play are in `drive_c/CRYO/DREAMS/DATA/`, so
keep the folder when you rebuild.

## Controls

The game's keys (disc `README.TXT`):

| Key | Does |
|---|---|
| Up / Down, Left / Right | run, back up; turn |
| Ctrl | jump; kick in combat mode; Ctrl + Down fast backwards; Ctrl + Up long jump |
| Alt | walk; punch, sword, bow; Alt + Up take off; hold with the arrows to fly or swim |
| Space | combat mode on / off |
| 1 / 2 / 3 | select a magic |
| Alt + 5 ... 0 | cameras (Alt + 5 = the default) |
| F1-F6 | resolution (F3 default) |
| Esc | the interface (menu); skips the intro |
| F10 | controls help |
| J / K | joypad / keyboard |

## Settings

- **Speed**: `cpu_cycles_protected = 200000` in `dosbox.conf`. If the 3D or the movies stutter on your PC,
  try `max`.
- **Software version** (no 3dfx): in `drive_c/CRYO/DREAMS/GO.BAT` put `REM` in front of `DREAMSFX.EXE` and
  remove it from `REM DREAMS.EXE`. Same data and saved games; its first start asks to analyse the video modes
  (press a key), and the 3D is software, lower resolution.

## What's in this repository

| File | What |
|---|---|
| `build.py` | Builds the folder: copies the game from CD 1 as the 3dfx installer does, patches the exe, adds the Glide driver, the sound settings and `dosbox.conf`. Python standard library only. |
| `patch_exe.py` | The exe patches, each explained; also runs on its own. |
| `disc.py` | Reads the CD images: `.cue`/`.bin`, `.ccd`/`.img` or `.iso`, ISO 9660. |
| `config/` | `dosbox.conf` (with the CD paths filled in by `build.py`), `GO.BAT`, `DIG.INI` (the game's sound set-up, Sound Blaster 16). |
| `docs/TECHNICAL.md` | The versions on the CDs, the install, and how each patch was found. |

## Credits

- **Cryo Interactive** made Dreams to Reality. Please own the game: this kit needs your CDs.
- **3dfx Interactive**: Glide, from the runtime kit on the game's own CD 1.
- **The DOSBox Staging team** for DOSBox Staging and its Voodoo emulation.

## License

The scripts and docs in this repository: MIT (see `LICENSE`). The license covers only this repository's own
files, not the game.

Not affiliated with or endorsed by the game's rights holders.
