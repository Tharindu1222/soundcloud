ffmpeg for the Windows installer / portable folder
====================================================

1. Download a Windows "full" or "essentials" build (static ffmpeg.exe), for example:
   https://www.gyan.dev/ffmpeg/builds/
   (ffmpeg-release-essentials.zip)

2. From the zip, copy only:
      bin\ffmpeg.exe

3. Place it here as:
      vendor\ffmpeg.exe

4. Run build.ps1 from the project folder.

PyInstaller will copy ffmpeg.exe next to SCDownloader.exe so the app works after install without changing system PATH.
