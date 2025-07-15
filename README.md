```bash
python convert_folder.py "C:\Users\MyUser\Music\WAV_Source" "C:\Users\MyUser\Videos\MP4_Output" "C:\ffmpeg\bin\ffmpeg.exe"
```
```bash
PS C:\Tools\convert_media> python convert_folder.py "C:\Users\voothi\Downloads\20250715194603-convert-src" "C:\Users\voothi\Downloads\20250715194651-convert-dst" "C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
Processing: 20250715131709-praesens.mp4 -> 20250715131709-praesens.mp4
Successfully processed: 'C:\Users\voothi\Downloads\20250715194651-convert-dst\20250715131709-praesens.mp4'
Processing: 20250715134759-perfekt.mp4 -> 20250715134759-perfekt.mp4
Successfully processed: 'C:\Users\voothi\Downloads\20250715194651-convert-dst\20250715134759-perfekt.mp4'

Processing complete! Processed new files: 2.
PS C:\Tools\convert_media> python convert_folder.py "C:\Users\voothi\Downloads\20250715194603-convert-src" "C:\Users\voothi\Downloads\20250715194651-convert-dst" "C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
Skipping: A file for '20250715131709-praesens.mp4' already exists in the destination folder.
Skipping: A file for '20250715134759-perfekt.mp4' already exists in the destination folder.

All applicable files have been processed. No new files to convert.
PS C:\Tools\convert_media> python convert_folder.py "C:\Users\voothi\Downloads\20250715194603-convert-src" "C:\Users\voothi\Downloads\20250715194651-convert-dst" "C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
```