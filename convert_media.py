import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

# ============================================================================
# CONFIGURATION (edit here first)
# ============================================================================
SHORTCUT_DISPLAY_NAME = "FFmpeg Convert Media"
SHORTCUT_DESCRIPTION = "Convert media files to MP4 (black canvas video + audio)."
SENDTO_DIRECTORY = r"%APPDATA%\Microsoft\Windows\SendTo"

ZID_SCRIPT_PATH = r"U:\voothi\20241116203211-zid\zid.py"

SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.mp4', '.m4a', '.aac', '.flac', '.ogg', '.wma')
DEFAULT_OUTPUT_MODE = 'same-dir'  # same-dir | converted-subdir
DEFAULT_DUPLICATE_MODE = 'zid-dir'  # zid-dir | skip | overwrite
DEFAULT_CONVERTED_SUBDIR_NAME = 'converted'
DEFAULT_DUPLICATE_INDEX_START = 2

DEFAULT_VIDEO_FILTER = 'color=c=black:s=256x144'
DEFAULT_VIDEO_CODEC = 'libx264'
DEFAULT_VIDEO_PRESET = 'veryslow'
DEFAULT_VIDEO_CRF = '36'
DEFAULT_VIDEO_TUNE = 'stillimage'
DEFAULT_VIDEO_X264_PARAMS = 'keyint=300:min-keyint=300:scenecut=0'
DEFAULT_VIDEO_FPS = '15'
DEFAULT_PIXEL_FORMAT = 'yuv420p'
DEFAULT_AUDIO_CODEC = 'aac'
DEFAULT_AUDIO_BITRATE = '128k'
DEFAULT_MOVFLAGS = '+faststart'
# ============================================================================


def build_ffmpeg_command(input_file, output_file, ffmpeg_path):
    return [
        ffmpeg_path,
        '-i', input_file,
        '-f', 'lavfi',
        '-i', DEFAULT_VIDEO_FILTER,
        '-shortest',
        '-c:v', DEFAULT_VIDEO_CODEC,
        '-preset', DEFAULT_VIDEO_PRESET,
        '-crf', DEFAULT_VIDEO_CRF,
        '-tune', DEFAULT_VIDEO_TUNE,
        '-x264-params', DEFAULT_VIDEO_X264_PARAMS,
        '-r', DEFAULT_VIDEO_FPS,
        '-pix_fmt', DEFAULT_PIXEL_FORMAT,
        '-c:a', DEFAULT_AUDIO_CODEC,
        '-b:a', DEFAULT_AUDIO_BITRATE,
        '-movflags', DEFAULT_MOVFLAGS,
        '-y',
        output_file,
    ]


def run_ffmpeg(input_file, output_file, ffmpeg_path):
    command = build_ffmpeg_command(input_file, output_file, ffmpeg_path)
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
        'ffmpeg was not found. Install ffmpeg or pass --ffmpeg-path with a full path to ffmpeg.exe.'
    )


def get_zid():
    try:
        result = subprocess.run(
            [sys.executable, ZID_SCRIPT_PATH, '--no-clipboard'],
            capture_output=True,
            text=True,
            check=True,
        )
        zid = result.stdout.strip()
        if zid and zid.isdigit() and len(zid) == 14:
            return zid
    except Exception:
        pass

    return datetime.now().strftime('%Y%m%d%H%M%S')


def resolve_base_output_directory(source_dir, output_mode, converted_subdir_name):
    if output_mode == 'same-dir':
        return source_dir
    if output_mode == 'converted-subdir':
        output_dir = os.path.join(source_dir, converted_subdir_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    raise ValueError(f'Unsupported output mode: {output_mode}')


def build_output_path(input_file, zid_cache, output_mode, duplicate_mode, converted_subdir_name):
    source_dir = os.path.dirname(os.path.abspath(input_file))
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    base_output_dir = resolve_base_output_directory(source_dir, output_mode, converted_subdir_name)
    primary_output = os.path.join(base_output_dir, f'{base_name}.mp4')

    if not os.path.exists(primary_output):
        return primary_output, 'new'

    if duplicate_mode == 'overwrite':
        return primary_output, 'overwrite'

    if duplicate_mode == 'skip':
        return primary_output, 'skip'

    if duplicate_mode != 'zid-dir':
        raise ValueError(f'Unsupported duplicate mode: {duplicate_mode}')

    if not zid_cache.get('value'):
        zid_cache['value'] = get_zid()

    duplicate_dir = os.path.join(base_output_dir, zid_cache['value'])
    os.makedirs(duplicate_dir, exist_ok=True)

    duplicate_output = os.path.join(duplicate_dir, f'{base_name}.mp4')
    if not os.path.exists(duplicate_output):
        return duplicate_output, 'duplicate-zid-dir'

    index = DEFAULT_DUPLICATE_INDEX_START
    while True:
        candidate = os.path.join(duplicate_dir, f'{base_name}-{index}.mp4')
        if not os.path.exists(candidate):
            return candidate, 'duplicate-zid-dir-indexed'
        index += 1


def convert_selected_files(input_files, ffmpeg_path, output_mode, duplicate_mode, converted_subdir_name):
    zid_cache = {'value': None}
    success_count = 0

    for input_file in input_files:
        if not os.path.isfile(input_file):
            print(f'Skipping missing file: {input_file}')
            continue

        if not input_file.lower().endswith(SUPPORTED_EXTENSIONS):
            print(f'Skipping unsupported extension: {input_file}')
            continue

        output_file, policy = build_output_path(
            input_file,
            zid_cache,
            output_mode,
            duplicate_mode,
            converted_subdir_name,
        )

        if policy == 'skip':
            print(f"Skipping duplicate (exists): {output_file}")
            continue

        print(f'Converting: {input_file} -> {output_file}')

        try:
            run_ffmpeg(input_file, output_file, ffmpeg_path)
            success_count += 1
            print(f'Done: {output_file}')
        except subprocess.CalledProcessError as error:
            print(f"Conversion failed for '{input_file}': {error}")

    print(f'Completed. Converted files: {success_count}')


def install_sendto_shortcut(ffmpeg_path, output_mode, duplicate_mode, converted_subdir_name):
    script_path = os.path.abspath(__file__)
    pythonw_path = sys.executable.lower().replace('python.exe', 'pythonw.exe')
    if not os.path.exists(pythonw_path):
        pythonw_path = sys.executable

    sendto_dir = os.path.expandvars(SENDTO_DIRECTORY)
    os.makedirs(sendto_dir, exist_ok=True)
    shortcut_path = os.path.join(sendto_dir, f'{SHORTCUT_DISPLAY_NAME}.lnk')

    arguments = (
        f'"{script_path}" --sendto --ffmpeg-path "{ffmpeg_path}" '
        f'--output-mode {output_mode} --duplicate-mode {duplicate_mode} '
        f'--converted-subdir-name "{converted_subdir_name}"'
    )

    print('Installing SendTo shortcut...')
    print(f'Script path: {script_path}')
    print(f'Pythonw path: {pythonw_path}')
    print(f'SendTo dir: {sendto_dir}')
    print(f'Shortcut path: {shortcut_path}')
    print(f'ffmpeg path: {ffmpeg_path}')
    print(
        'Shortcut options: '
        f'output_mode={output_mode}, duplicate_mode={duplicate_mode}, '
        f'converted_subdir_name={converted_subdir_name}'
    )

    # Set IconLocation to pythonw to make icon behavior deterministic in Explorer.
    ps_script = (
        "$WshShell = New-Object -ComObject WScript.Shell; "
        f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); "
        f"$Shortcut.TargetPath = '{pythonw_path}'; "
        f"$Shortcut.Arguments = '{arguments}'; "
        f"$Shortcut.Description = '{SHORTCUT_DESCRIPTION}'; "
        f"$Shortcut.IconLocation = '{pythonw_path},0'; "
        "$Shortcut.WindowStyle = 7; "
        "$Shortcut.Save()"
    )

    subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], check=True)
    print(f'SendTo shortcut created: {shortcut_path}')
    print(f'Output mode: {output_mode}, duplicate mode: {duplicate_mode}')
    print('Usage: Select files in Explorer -> Right click -> Send to -> FFmpeg Convert Media')
    print('SUCCESS: SendTo installation completed.')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert media files to MP4 with a black screen overlay and Windows SendTo support.'
    )

    parser.add_argument('--ffmpeg-path', dest='ffmpeg_path', default=None, help='Path to ffmpeg.exe')
    parser.add_argument('--install-sendto', action='store_true', help='Install Windows SendTo shortcut for this script')
    parser.add_argument('--sendto', action='store_true', help='Treat positional args as selected files from Windows SendTo')

    parser.add_argument(
        '--output-mode',
        choices=['same-dir', 'converted-subdir'],
        default=DEFAULT_OUTPUT_MODE,
        help='Where to save converted files.',
    )
    parser.add_argument(
        '--duplicate-mode',
        choices=['zid-dir', 'skip', 'overwrite'],
        default=DEFAULT_DUPLICATE_MODE,
        help='How to handle output filename duplicates.',
    )
    parser.add_argument(
        '--converted-subdir-name',
        default=DEFAULT_CONVERTED_SUBDIR_NAME,
        help='Subdirectory name used when --output-mode converted-subdir.',
    )

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
        install_sendto_shortcut(
            ffmpeg_path,
            args.output_mode,
            args.duplicate_mode,
            args.converted_subdir_name,
        )
        return

    if args.sendto:
        if not args.paths:
            print('No files were passed from SendTo.')
            return
        convert_selected_files(
            args.paths,
            ffmpeg_path,
            args.output_mode,
            args.duplicate_mode,
            args.converted_subdir_name,
        )
        return

    if len(args.paths) in (2, 3):
        input_file = args.paths[0]
        output_file = args.paths[1]

        if len(args.paths) == 3:
            if os.path.isfile(args.paths[2]):
                ffmpeg_path = args.paths[2]
            else:
                print(f'Invalid ffmpeg path: {args.paths[2]}')
                return

        if not os.path.isfile(input_file):
            print(f'Input file does not exist: {input_file}')
            return

        run_ffmpeg(input_file, output_file, ffmpeg_path)
        print(f"Conversion complete! Output file: '{output_file}'")
        return

    print('Usage examples:')
    print('  python convert_media.py --install-sendto --ffmpeg-path "C:\\ffmpeg\\bin\\ffmpeg.exe"')
    print('  python convert_media.py --install-sendto --output-mode same-dir --duplicate-mode zid-dir')
    print('  python convert_media.py --sendto --ffmpeg-path "C:\\ffmpeg\\bin\\ffmpeg.exe" "C:\\path\\a.wav" "C:\\path\\b.mp3"')
    print('  python convert_media.py "input.wav" "output.mp4" "C:\\ffmpeg\\bin\\ffmpeg.exe"')


if __name__ == '__main__':
    main()
