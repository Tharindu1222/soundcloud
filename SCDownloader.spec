# PyInstaller spec — run from project root: py -m PyInstaller SCDownloader.spec
import os

from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas, binaries, hiddenimports = collect_all("yt_dlp")

vendor_ffmpeg = os.path.join("vendor", "ffmpeg.exe")
if os.path.isfile(vendor_ffmpeg):
    binaries = list(binaries) + [(vendor_ffmpeg, ".")]

a = Analysis(
    ["soundcloud_downloader.py"],
    pathex=[os.path.abspath(".")],
    binaries=binaries,
    datas=datas,
    hiddenimports=list(hiddenimports),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SCDownloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SCDownloader",
)
