@echo off
rem Started by AUTOBOOT.DBP. Dreams to Reality, 3dfx version (DREAMSFX.EXE, patched by patch_exe.py), Full
rem install in C:\CRYO\DREAMS, on DOSBox Pure's emulated Voodoo 1 through GLIDE2X.OVL (3dfx's Glide 2.42 DOS
rem driver from CD 1). FX_GLIDE_NO_SPLASH skips the 3dfx logo.
rem For the software version instead (no 3dfx): put REM in front of DREAMSFX.EXE and remove it from DREAMS.EXE
rem (same data and saved games; its first start asks to analyse the video modes: press a key).
c:
cd \CRYO\DREAMS
set FX_GLIDE_NO_SPLASH=1
DREAMSFX.EXE
rem DREAMS.EXE
