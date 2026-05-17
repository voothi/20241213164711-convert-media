# Convert Media Utility

[![Version](https://img.shields.io/badge/version-v1.0.2-blue)](https://github.com/voothi/20241213164711-convert-media)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Windows utility that converts selected media files into MP4 videos with a black canvas and original audio, including Explorer SendTo integration and ZID-based duplicate handling.

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Duplicate Handling](#duplicate-handling)
- [Kardenwort](#kardenwort)
- [License](#license)

---

## Description
`convert-media` is designed for fast, repeatable media conversion on Windows. You can select one or multiple files in Explorer and run conversion through the `Send to` menu, or call the script directly from PowerShell.

The output video is an MP4 with a black video track and AAC audio, making it convenient for workflows where audio-only sources need a video container.

[Return to Top](#convert-media-utility)

## Features
- **Windows SendTo Integration**: Right-click one or more files in Explorer and convert them directly.
- **ZID-Based Duplicate Handling**: On duplicate output names, files can be routed into a ZID folder.
- **Configurable Output Location**: Save output in the source directory or in a configurable subdirectory.
- **Batch Processing**: Handles multiple selected files in one pass.
- **Legacy Compatibility**: Keeps classic single-file input/output CLI mode.

[Return to Top](#convert-media-utility)

## Installation

### Requirements
1. Windows 11 (or Windows with SendTo support)
2. Python 3.12+
3. `ffmpeg.exe` available in `PATH` or passed explicitly

### Install SendTo Shortcut
Run from this project directory:

```powershell
python .\convert_media.py --install-sendto --ffmpeg-path "C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
```

After installation:
1. Select media files in Explorer.
2. Right click -> `Send to` -> `FFmpeg Convert Media`.

[Return to Top](#convert-media-utility)

## Configuration

All core settings are grouped at the top of [convert_media.py](/u:/voothi/20241213164711-convert-media/convert_media.py).

### Main Defaults
- `DEFAULT_OUTPUT_MODE = 'same-dir'`
- `DEFAULT_DUPLICATE_MODE = 'zid-dir'`
- `DEFAULT_CONVERTED_SUBDIR_NAME = 'converted'`
- `SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.mp4', '.m4a', '.aac', '.flac', '.ogg', '.wma')`

### Runtime Options
- `--output-mode same-dir|converted-subdir`
- `--duplicate-mode zid-dir|skip|overwrite`
- `--converted-subdir-name <name>`
- `--ffmpeg-path <full path to ffmpeg.exe>`

[Return to Top](#convert-media-utility)

## Usage

### SendTo Mode (normally used by the shortcut)

```powershell
python .\convert_media.py --sendto --ffmpeg-path "C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe" "C:\path\a.wav" "C:\path\b.mp3"
```

### Reinstall Shortcut With Custom Behavior

```powershell
python .\convert_media.py --install-sendto --output-mode converted-subdir --duplicate-mode skip --converted-subdir-name converted
```

### Legacy Single-File Mode

```powershell
python .\convert_media.py "C:\path\input.wav" "C:\path\output.mp4" "C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
```

[Return to Top](#convert-media-utility)

## Duplicate Handling

When output already exists:
- `zid-dir`: write to `<output_base>\<ZID>\file.mp4`, then `file-2.mp4`, `file-3.mp4`, etc.
- `skip`: skip conversion for that file.
- `overwrite`: overwrite existing output.

Default behavior is `zid-dir` for traceability and safe non-destructive operation.

[Return to Top](#convert-media-utility)

## Kardenwort Ecosystem

This project is part of the **[Kardenwort](https://github.com/kardenwort)** environment and follows ZID-based traceability practices.

[Return to Top](#table-of-contents)

## License
MIT License. See LICENSE file for details.

[Return to Top](#convert-media-utility)
