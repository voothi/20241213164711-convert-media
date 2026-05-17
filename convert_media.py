import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

# GLOBAL CONFIGURATION
SHORTCUT_DISPLAY_NAME = "FFmpeg Convert Media"
SENDTO_DIRECTORY = r"%APPDATA%\Microsoft\Windows\SendTo"
SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.mp4', '.m4a', '.aac', '.flac', '.ogg', '.wma')


def run_ffmpeg(input_file, output_file, ffmpeg_path):
    command = [
        ffmpeg_path,
        '-i', input_file,
        '-f', 'lavfi',
        '-i', 'color=c=black:s=256x144',
        '-shortest',
        '-c:v', 'libx264',
        '-preset', 'veryslow',
        '-b:v', '0',
        '-x264opts', 'bitrate=1',
        '-r', '15',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_file,
    ]

    subprocess.run(command, check=True)


def resolve_ffmpeg_path(explicit_ffmpeg_path):
    if explicit_ffmpeg_path:
        if os.path.isfile(explicit_ffmpeg_path):
            return explicit_ffmpeg_path
        raise FileNotFoundError(f"ffmpeg not found at: {explicit_ffmpeg_path}")

    discovered = shutil.which('ffmpeg')
    if discovered:
        return discovered

    raise FileNotFoundError(
        "ffmpeg was not found. Install ffmpeg or pass --ffmpeg-path with a full path to ffmpeg.exe."
    )


def get_zid():
    zid_script = r"U:\voothi\20241116203211-zid\zid.py"
    try:
        result = subprocess.run(
            [sys.executable, zid_script, '--no-clipboard'],
            capture_output=True,
            text=True,
            check=True,
        )
        zid = result.stdout.strip()
        if zid and zid.isdigit() and len(zid) == 14:
            return zid
    except Exception:
        pass

    # Safe fallback when zid utility is unavailable.
    return datetime.now().strftime('%Y%m%d%H%M%S')


def build_output_path(input_file, zid_cache):
    source_dir = os.path.dirname(os.path.abspath(input_file))
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    converted_dir = os.path.join(source_dir, 'converted')
    os.makedirs(converted_dir, exist_ok=True)

    primary_output = os.path.join(converted_dir, f"{base_name}.mp4")
    if not os.path.exists(primary_output):
        return primary_output

    # Duplicate policy: write to a per-run ZID folder.
    if not zid_cache.get('value'):
        zid_cache['value'] = get_zid()

    duplicate_dir = os.path.join(converted_dir, zid_cache['value'])
    os.makedirs(duplicate_dir, exist_ok=True)

    duplicate_output = os.path.join(duplicate_dir, f"{base_name}.mp4")
    if not os.path.exists(duplicate_output):
        return duplicate_output

    # If the same name already exists in the ZID folder, keep incrementing.
    index = 2
    while True:
        candidate = os.path.join(duplicate_dir, f"{base_name}-{index}.mp4")
        if not os.path.exists(candidate):
            return candidate
        index += 1


def convert_selected_files(input_files, ffmpeg_path):
    zid_cache = {'value': None}
    success_count = 0

    for input_file in input_files:
        if not os.path.isfile(input_file):
            print(f"Skipping missing file: {input_file}")
            continue

        if not input_file.lower().endswith(SUPPORTED_EXTENSIONS):
            print(f"Skipping unsupported extension: {input_file}")
            continue

        output_file = build_output_path(input_file, zid_cache)
        print(f"Converting: {input_file} -> {output_file}")

        try:
            run_ffmpeg(input_file, output_file, ffmpeg_path)
            success_count += 1
            print(f"Done: {output_file}")
        except subprocess.CalledProcessError as error:
            print(f"Conversion failed for '{input_file}': {error}")

    print(f"Completed. Converted files: {success_count}")


def install_sendto_shortcut(ffmpeg_path):
    script_path = os.path.abspath(__file__)
    pythonw_path = sys.executable.lower().replace('python.exe', 'pythonw.exe')
    if not os.path.exists(pythonw_path):
        pythonw_path = sys.executable

    sendto_dir = os.path.expandvars(SENDTO_DIRECTORY)
    os.makedirs(sendto_dir, exist_ok=True)
    shortcut_path = os.path.join(sendto_dir, f"{SHORTCUT_DISPLAY_NAME}.lnk")

    arguments = f'"{script_path}" --sendto --ffmpeg-path "{ffmpeg_path}"'

    ps_script = (
        "$WshShell = New-Object -ComObject WScript.Shell; "
        f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); "
        f"$Shortcut.TargetPath = '{pythonw_path}'; "
        f"$Shortcut.Arguments = '{arguments}'; "
        "$Shortcut.WindowStyle = 7; "
        "$Shortcut.Save()"
    )

    subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], check=True)
    print(f"SendTo shortcut created: {shortcut_path}")
    print("Usage: Select media files in Explorer -> Right click -> Send to -> FFmpeg Convert Media")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert media files to MP4 with a black screen overlay and support Windows SendTo flow.'
    )

    parser.add_argument('--ffmpeg-path', dest='ffmpeg_path', default=None, help='Path to ffmpeg.exe')
    parser.add_argument('--install-sendto', action='store_true', help='Install Windows SendTo shortcut for this script')
    parser.add_argument('--sendto', action='store_true', help='Treat positional args as selected files from Windows SendTo')

    # Backward-compatible legacy mode: input output [ffmpeg]
    parser.add_argument('paths', nargs='*', help='Input files for SendTo mode, or input/output[/ffmpeg] in legacy mode')

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        ffmpeg_path = resolve_ffmpeg_path(args.ffmpeg_path)
    except FileNotFoundError as error:
        print(str(error))
        return

    if args.install_sendto:
        install_sendto_shortcut(ffmpeg_path)
        return

    if args.sendto:
        if not args.paths:
            print('No files were passed from SendTo.')
            return
        convert_selected_files(args.paths, ffmpeg_path)
        return

    # Legacy compatibility:
    # python convert_media.py <input_file> <output_file> [ffmpeg_path]
    if len(args.paths) in (2, 3):
        input_file = args.paths[0]
        output_file = args.paths[1]
        if len(args.paths) == 3:
            if os.path.isfile(args.paths[2]):
                ffmpeg_path = args.paths[2]
            else:
                print(f"Invalid ffmpeg path: {args.paths[2]}")
                return

        if not os.path.isfile(input_file):
            print(f"Input file does not exist: {input_file}")
            return

        run_ffmpeg(input_file, output_file, ffmpeg_path)
        print(f"Conversion complete! Output file: '{output_file}'")
        return

    print('Usage examples:')
    print('  python convert_media.py --install-sendto --ffmpeg-path "C:\\ffmpeg\\bin\\ffmpeg.exe"')
    print('  python convert_media.py --sendto --ffmpeg-path "C:\\ffmpeg\\bin\\ffmpeg.exe" "C:\\path\\a.wav" "C:\\path\\b.mp3"')
    print('  python convert_media.py "input.wav" "output.mp4" "C:\\ffmpeg\\bin\\ffmpeg.exe"')


if __name__ == '__main__':
    main()
