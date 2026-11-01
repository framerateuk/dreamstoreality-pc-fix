@echo off
rem Dreams to Reality, 3dfx version (DREAMSFX.EXE, patched by patch_exe.py), Full install in C:\CRYO\DREAMS.
rem FX_GLIDE_NO_SPLASH skips the 3dfx logo. For the software version instead (no 3dfx), put REM in front of
rem DREAMSFX.EXE and remove it from DREAMS.EXE: same data and saved games; its first start asks to analyse
rem the video modes (press a key).
c:
cd \CRYO\DREAMS
set FX_GLIDE_NO_SPLASH=1
DREAMSFX.EXE
rem DREAMS.EXE
