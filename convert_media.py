import subprocess
import argparse
import os

def convert_wav_to_mp4(input_file, output_file, ffmpeg_path):
    # Creating a command for ffmpeg
    command = [
        ffmpeg_path,
        '-i', input_file,
        '-f', 'lavfi',
        '-i', 'color=c=black:s=176x144',
        '-shortest',
        '-c:v', 'libx264',
        '-preset', 'veryslow',
        '-b:v', '0',
        '-x264opts', 'bitrate=1',
        '-r', '15',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_file
    ]

    # Executing command
    subprocess.run(command)

def main():
    # Setting up argument parser
    parser = argparse.ArgumentParser(description='Convert WAV to MP4 with black screen.')
    parser.add_argument('input_file', metavar='input', type=str, 
                        help='Input WAV file to convert')
    parser.add_argument('output_file', metavar='output', type=str, 
                        help='Output MP4 file name')
    parser.add_argument('ffmpeg_path', metavar='ffmpeg', type=str, 
                        help='Path to ffmpeg.exe')

    args = parser.parse_args()

    # Check the existence of the input file
    if not os.path.isfile(args.input_file):
        print(f"Input file '{args.input_file}' does not exist.")
        return

    # Performing conversion
    convert_wav_to_mp4(args.input_file, args.output_file, args.ffmpeg_path)
    print(f"Conversion complete! Output file: '{args.output_file}'")

if __name__ == '__main__':
    main()