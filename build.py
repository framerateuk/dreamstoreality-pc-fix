#!/usr/bin/env python3
"""Build a ready-to-run Dreams to Reality (DOS, 3dfx) zip for RetroArch's DOSBox Pure core from your own CDs.

Usage:
  python3 build.py CD1.cue|CD1.ccd CD2.cue|CD2.ccd [--out DIR]

  CD1, CD2   your two Dreams to Reality CDs (Cryo, 1997, English) as .cue + .bin/.img or CloneCD .ccd + .img.
             The music is the CDs' audio tracks, so a plain .iso (data only) also works but plays without music.
  --out      where to create DreamsToReality/ (default: this folder)

Creates DreamsToReality/ with
  Dreams to Reality.zip   the game as the disc's 3dfx installer installs it (Full install) in C:\\CRYO\\DREAMS,
                          with the patched DREAMSFX.EXE, 3dfx's Glide driver from CD 1, the Sound Blaster set-up,
                          the pad map, a dosbox.conf and both CD images (about 1.4 GB, stored, not compressed)
  retroarch/              RetroArch's per-game settings for it (Dreams to Reality.cfg / .opt)

Needs Python 3.8+ only. Nothing from the game is in this repository: every game file comes from your discs.
"""
import argparse, hashlib, io, os, re, shutil, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import disc, padmap, patch_exe

NAME = "Dreams to Reality"                       # the zip's name: RetroArch finds the .cfg / .opt by it
OVL_MD5 = "341b8f5d82daa46fd1ce236300317c3c"   # Glide 2.42, Voodoo Graphics, DOS (3DFX\GRTVGR.EXE on CD 1)
OVL_IN_KIT = "Glide/Drivers/Voodoo/Dos/glide2x.ovl"


def md5(data): return hashlib.md5(data).hexdigest()


def ccd_to_cue(ccd, img_name):
    """A .cue for a CloneCD image: its track table, with each audio track's pregap (INDEX 0) as the .ccd has it."""
    def msf(lba): return f"{lba // 4500:02d}:{lba // 75 % 60:02d}:{lba % 75:02d}"
    sections, track = {}, None
    for line in open(ccd, encoding="utf-8", errors="replace"):
        t = line.strip()
        if t.startswith("[TRACK "): track = int(t[7:-1]); sections[track] = {}
        elif t.startswith("["): track = None
        elif track is not None and "=" in t:
            k, v = t.split("=", 1); sections[track][k.strip()] = v.strip()
    lines = [f'FILE "{img_name}" BINARY']
    for n in sorted(sections):
        s = sections[n]
        lines.append(f"  TRACK {n:02d} " + {"0": "AUDIO", "1": "MODE1/2352", "2": "MODE2/2352"}[s.get("MODE", "0")])
        for i in (0, 1):
            if f"INDEX {i}" in s: lines.append(f"    INDEX {i:02d} {msf(int(s[f'INDEX {i}']))}")
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def disc_members(path, n):
    """[(name in the zip, bytes or a file path)] for CD n: DREAMSn.CUE + DREAMSn.BIN (one .bin per track:
    DREAMSn_01.BIN ...), or DREAMSn.ISO. The .cue's FILE lines are rewritten to the new names."""
    low = path.lower()
    if low.endswith(".iso"): return [(f"DREAMS{n}.ISO", path)]
    if low.endswith(".ccd"):
        return [(f"DREAMS{n}.CUE", ccd_to_cue(path, f"DREAMS{n}.BIN")), (f"DREAMS{n}.BIN", os.path.splitext(path)[0] + ".img")]
    raw = open(path, "rb").read()
    files = re.findall(rb'(?m)^\s*FILE\s+"?(.*?)"?\s+\w+\s*$', raw)
    if not files: sys.exit(f"{path}: no FILE line")
    names = [f"DREAMS{n}.BIN"] if len(files) == 1 else [f"DREAMS{n}_{k:02d}.BIN" for k in range(1, len(files) + 1)]
    out, members, k = [], [], 0
    for line in raw.splitlines(keepends=True):
        m = re.match(rb'(\s*FILE\s+)"?(.*?)"?(\s+\w+\s*)$', line)
        if m:
            src = os.path.join(os.path.dirname(os.path.abspath(path)), m.group(2).decode("utf-8", "replace"))
            if not os.path.exists(src): sys.exit(f"{path} names {src}, which isn't there")
            line = m.group(1) + b'"' + names[k].encode() + b'"' + m.group(3)
            members.append((names[k], src)); k += 1
        out.append(line)
    return [(f"DREAMS{n}.CUE", b"".join(out))] + members


def open_disc(path):
    tr = disc.tracks(path)
    data = [t for t in tr if t.kind != "AUDIO"]
    if not data: sys.exit("no data track in " + path)
    dt = disc.DataTrack(data[0])
    files = {p.upper(): (l, s) for p, is_dir, l, s in dt.walk() if not is_dir}
    return dt, files, sum(t.kind == "AUDIO" for t in tr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cd1"); ap.add_argument("cd2"); ap.add_argument("--out", default=HERE)
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
    _, files2, audio2 = open_disc(a.cd2)
    if "DATA/2CD.ID" not in files2: sys.exit(f"{a.cd2} is not Dreams to Reality CD 2")
    if not (audio and audio2): print("  note: a CD without audio tracks (an .iso?): no music from it")

    pkg = os.path.join(os.path.abspath(a.out), "DreamsToReality")
    if os.path.exists(pkg): sys.exit(f"{pkg} already exists: move or delete it first")

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
    G = "CRYO/DREAMS/"
    game = {G + p: dt.read_file(l, s) for p, (l, s) in sorted(files.items()) if want(p)}
    game[G + "DATA/FULL.ID"] = get("DATA/HD.ID")

    print("2/4 DREAMSFX.EXE patched (steady subtitles, no black fog)")
    game[G + "DREAMSFX.EXE"] = patch_exe.patch(exe)

    print("3/4 3dfx's Glide 2.42 DOS driver from the disc's 3DFX\\GRTVGR.EXE")
    with zipfile.ZipFile(io.BytesIO(get("3DFX/GRTVGR.EXE"))) as z:   # a self-extracting zip
        ovl = z.read(OVL_IN_KIT)
    if md5(ovl) != OVL_MD5: sys.exit("unexpected glide2x.ovl in 3DFX\\GRTVGR.EXE")
    game[G + "GLIDE2X.OVL"] = ovl

    # the kit's own files over the top: AUTOBOOT.DBP, DOSBOX.CONF, GO.BAT, DIG.INI; the pad map
    cfg = os.path.join(HERE, "config", "zip")
    for d, _, fs in os.walk(cfg):
        for f in fs:
            if f.startswith("."): continue
            p = os.path.join(d, f)
            game[os.path.relpath(p, cfg).replace(os.sep, "/")] = open(p, "rb").read()
    game["PADMAP.DBP"] = padmap.build()

    print(f"4/4 {NAME}.zip (the CD images too, about 1.4 GB)")
    os.makedirs(os.path.join(pkg, "retroarch"))
    zpath = os.path.join(pkg, NAME + ".zip")
    dirs = sorted({k[:i + 1] for k in game for i, c in enumerate(k) if c == "/"} | {G + "DATA/GAME/", G + "DATA/ANIM/"})
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        # CD 1 first, so DOSBox Pure mounts it as D: at start; CD 2 is in its disc list for when the game asks
        for name, src in disc_members(a.cd1, 1) + disc_members(a.cd2, 2):
            if isinstance(src, bytes): z.writestr(name, src); continue
            zi = zipfile.ZipInfo.from_file(src, name); zi.compress_type = zipfile.ZIP_STORED
            with open(src, "rb") as f, z.open(zi, "w") as w: shutil.copyfileobj(f, w, 1 << 20)
        for d in dirs:
            zi = zipfile.ZipInfo(d); zi.external_attr = (0o40755 << 16) | 0x10; z.writestr(zi, b"")
        for name in sorted(game): z.writestr(name, game[name])
    with zipfile.ZipFile(zpath) as z:                 # read it all back: a bad write shows up here, not in the game
        bad = z.testzip()
    if bad: sys.exit(f"{zpath}: {bad} reads back wrong (a disk or network write problem): build again")
    for ext in (".cfg", ".opt"):
        shutil.copyfile(os.path.join(HERE, "config", "retroarch", NAME + ext), os.path.join(pkg, "retroarch", NAME + ext))
    print(f"\ndone: {pkg}  (see README.md)")


if __name__ == "__main__":
    main()
