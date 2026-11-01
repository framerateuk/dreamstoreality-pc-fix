#!/usr/bin/env python3
"""Build a ready-to-run Dreams to Reality (DOS, 3dfx) folder for DOSBox Staging from your own CDs.

Usage:
  python3 build.py CD1.cue|CD1.ccd [CD2.cue|CD2.ccd] [--out DIR]

  CD1, CD2   your two Dreams to Reality CDs (Cryo, 1997, English) as .cue + .bin/.img or CloneCD .ccd + .img.
             The music is the CDs' audio tracks, so a plain .iso (data only) plays without music. For a .ccd
             without a .cue, a .cue of the same name is written next to it (DOSBox Staging reads .cue files).
             CD 2 is optional: without it the game stops where it asks for CD 2, until you add it.
  --out      where to create DreamsToReality/ (default: this folder)

Creates DreamsToReality/ with drive_c/CRYO/DREAMS (the game as the disc's 3dfx installer installs it, Full
install, with the patched DREAMSFX.EXE and 3dfx's Glide driver from the disc) and dosbox.conf.

Needs Python 3.8+ only. Nothing from the game is in this repository: every game file comes from your discs.
"""
import argparse, hashlib, io, os, shutil, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import disc, patch_exe

OVL_MD5 = "341b8f5d82daa46fd1ce236300317c3c"   # Glide 2.42, Voodoo Graphics, DOS (3DFX\GRTVGR.EXE on CD 1)
OVL_IN_KIT = "Glide/Drivers/Voodoo/Dos/glide2x.ovl"


def md5(data): return hashlib.md5(data).hexdigest()


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f: f.write(data)


def cue_for(path):
    """The .cue to mount in DOSBox Staging. A .ccd gets one written next to it (unless it has one already)."""
    if not path.lower().endswith(".ccd"): return os.path.abspath(path)
    cue = os.path.splitext(path)[0] + ".cue"
    if os.path.exists(cue): return os.path.abspath(cue)
    # the CloneCD track table, with each audio track's pregap (INDEX 0) as the .ccd records it
    lines = [f'FILE "{os.path.basename(os.path.splitext(path)[0])}.img" BINARY']
    track, idx = None, {}
    def msf(lba): return f"{lba // 4500:02d}:{lba // 75 % 60:02d}:{lba % 75:02d}"
    sections = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        t = line.strip()
        if t.startswith("[TRACK "): track = int(t[7:-1]); sections[track] = {}
        elif t.startswith("[") : track = None
        elif track is not None and "=" in t:
            k, v = t.split("=", 1); sections[track][k.strip()] = v.strip()
    for n in sorted(sections):
        s = sections[n]
        lines.append(f"  TRACK {n:02d} " + {"0": "AUDIO", "1": "MODE1/2352", "2": "MODE2/2352"}[s.get("MODE", "0")])
        for i in (0, 1):
            if f"INDEX {i}" in s: lines.append(f"    INDEX {i:02d} {msf(int(s[f'INDEX {i}']))}")
    with open(cue, "w", newline="\r\n") as f: f.write("\n".join(lines) + "\n")
    print(f"  wrote {cue}")
    return os.path.abspath(cue)


def open_disc(path):
    tr = disc.tracks(path)
    data = [t for t in tr if t.kind != "AUDIO"]
    if not data: sys.exit("no data track in " + path)
    dt = disc.DataTrack(data[0])
    files = {p.upper(): (l, s) for p, is_dir, l, s in dt.walk() if not is_dir}
    return dt, files, sum(t.kind == "AUDIO" for t in tr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cd1"); ap.add_argument("cd2", nargs="?"); ap.add_argument("--out", default=HERE)
    a = ap.parse_args()

    dt, files, audio = open_disc(a.cd1)
    def get(name):
        if name not in files: sys.exit(f"no {name} on {a.cd1}: it isn't Dreams to Reality CD 1")
        return dt.read_file(*files[name])
    if "DATA/1CD.ID" not in files:
        sys.exit(f"{a.cd1} is not Dreams to Reality CD 1" + (" (it's CD 2)" if "DATA/2CD.ID" in files else ""))
    exe = get("DREAMSFX.EXE")
    if md5(exe) != patch_exe.MD5:
        sys.exit(f"this CD's DREAMSFX.EXE is not the 29 Oct 1997 one the kit was made for (MD5 {md5(exe)})")
    if audio == 0: print("  note: CD 1 has no audio tracks (an .iso?): the game will play without music")
    if a.cd2:
        _, files2, _ = open_disc(a.cd2)
        if "DATA/2CD.ID" not in files2: sys.exit(f"{a.cd2} is not Dreams to Reality CD 2")

    pkg = os.path.join(os.path.abspath(a.out), "DreamsToReality")
    if os.path.exists(pkg): sys.exit(f"{pkg} already exists: move or delete it first (your saves are in drive_c)")
    game = os.path.join(pkg, "drive_c", "CRYO", "DREAMS")

    # What the 3dfx installer (INSTALFX.BAT -> INST_SFX.BAT) copies with XCOPY, no subfolders: the disc root's files;
    # DATA\HD.ID, REPLAY.BIN; DATA\3DC\DIALOG.DRD, *.3DC, *.3DM; DATA\SOUND\*, DATA\UNIVBE\*; empty DATA\GAME, ANIM.
    # Then its "Minimum install? No" = Full: HD.ID copied to FULL.ID (the game copies each CD's level set to the
    # hard disk when a game starts and plays the animated textures).
    print("1/4 the game files from CD 1, as the 3dfx installer copies them (Full install)")
    def want(p):
        d, _, f = p.rpartition("/")
        if d == "": return True
        if d == "DATA": return f in ("HD.ID", "REPLAY.BIN")
        if d == "DATA/3DC": return f == "DIALOG.DRD" or f.endswith((".3DC", ".3DM"))
        return d in ("DATA/SOUND", "DATA/UNIVBE")
    n = 0
    for p, (l, s) in sorted(files.items()):
        if want(p) and p != "DREAMSFX.EXE":
            dt.copy_file(l, s, os.path.join(game, *p.split("/"))); n += 1
    for d in ("GAME", "ANIM"): os.makedirs(os.path.join(game, "DATA", d), exist_ok=True)
    write(os.path.join(game, "DATA", "FULL.ID"), get("DATA/HD.ID"))
    print(f"  {n + 1} files")

    print("2/4 DREAMSFX.EXE patched (no black fog, steady subtitles)")
    write(os.path.join(game, "DREAMSFX.EXE"), patch_exe.patch(exe))

    print("3/4 3dfx's Glide 2.42 DOS driver from the disc's 3DFX\\GRTVGR.EXE")
    with zipfile.ZipFile(io.BytesIO(get("3DFX/GRTVGR.EXE"))) as z:   # a self-extracting zip
        ovl = z.read(OVL_IN_KIT)
    if md5(ovl) != OVL_MD5: sys.exit("unexpected glide2x.ovl in 3DFX\\GRTVGR.EXE")
    write(os.path.join(game, "GLIDE2X.OVL"), ovl)

    print("4/4 sound settings, start-up batch file, dosbox.conf")
    shutil.copyfile(os.path.join(HERE, "config", "DIG.INI"), os.path.join(game, "DATA", "SOUND", "DIG.INI"))
    shutil.copyfile(os.path.join(HERE, "config", "GO.BAT"), os.path.join(game, "GO.BAT"))
    cds = " ".join(f'"{cue_for(c)}"' for c in [a.cd1] + ([a.cd2] if a.cd2 else []))
    conf = open(os.path.join(HERE, "config", "dosbox.conf"), encoding="utf-8").read().replace("@CDS@", cds)
    with open(os.path.join(pkg, "dosbox.conf"), "w", encoding="utf-8") as f: f.write(conf)
    print(f"\ndone: {pkg}  (see README.md)")


if __name__ == "__main__":
    main()
