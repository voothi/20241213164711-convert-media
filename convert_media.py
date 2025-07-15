import subprocess
import argparse
import os

def convert_wav_to_mp4(input_file, output_file, ffmpeg_path):
    """
    Converts a single WAV file to MP4 with a black screen using ffmpeg.
    """
    # Creating the ffmpeg command
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
        output_file
    ]

    # Executing the command and hiding ffmpeg's output
    print(f"Converting: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully converted: '{output_file}'")
    except subprocess.CalledProcessError as e:
        print(f"Error converting file {input_file}:")
        print(e.stderr.decode('utf-8', errors='ignore'))
    except FileNotFoundError:
        print(f"Error: Could not find ffmpeg at path '{ffmpeg_path}'. Please check the path.")
        exit(1) # Exit the script if ffmpeg is not found


def main():
    # Setting up the argument parser
    parser = argparse.ArgumentParser(description='Converts all new WAV files from a source folder to MP4 in a destination folder.')
    parser.add_argument('source_folder', metavar='source', type=str, 
                        help='Source folder with WAV files')
    parser.add_argument('destination_folder', metavar='destination', type=str, 
                        help='Destination folder to save MP4 files')
    parser.add_argument('ffmpeg_path', metavar='ffmpeg', type=str, 
                        help='Path to the ffmpeg executable (ffmpeg.exe)')

    args = parser.parse_args()

    # --- Path validation ---
    # Check if the source folder exists
    if not os.path.isdir(args.source_folder):
        print(f"Error: Source folder '{args.source_folder}' does not exist.")
        return

    # Check if ffmpeg exists
    if not os.path.isfile(args.ffmpeg_path):
        print(f"Error: ffmpeg not found at path '{args.ffmpeg_path}'.")
        return

    # Create the destination folder if it doesn't exist
    os.makedirs(args.destination_folder, exist_ok=True)

    # --- File comparison and processing logic ---
    # Get a list of WAV files in the source folder
    try:
        source_files = [f for f in os.listdir(args.source_folder) if f.lower().endswith('.wav')]
    except FileNotFoundError:
        print(f"Error: Could not access folder '{args.source_folder}'.")
        return

    # Get a list of MP4 files in the destination folder
    try:
        dest_files = [f for f in os.listdir(args.destination_folder) if f.lower().endswith('.mp4')]
    except FileNotFoundError:
        # This error shouldn't happen since we create the folder above, but just in case
        print(f"Error: Could not access folder '{args.destination_folder}'.")
        return
        
    # Create a set of destination filenames without the extension for fast lookup
    dest_filenames_without_ext = {os.path.splitext(f)[0] for f in dest_files}

    files_to_process_count = 0
    
    # Iterate over the source files
    for wav_file in source_files:
        # Get the base name of the file (without extension)
        base_name = os.path.splitext(wav_file)[0]

        # Check if the processed file already exists
        if base_name in dest_filenames_without_ext:
            print(f"Skipping: File '{wav_file}' is already processed. ({base_name}.mp4 exists)")
            continue
        
        # If the file doesn't exist, start processing
        files_to_process_count += 1
        input_path = os.path.join(args.source_folder, wav_file)
        output_path = os.path.join(args.destination_folder, base_name + '.mp4')
        
        # Perform the conversion
        convert_wav_to_mp4(input_path, output_path, args.ffmpeg_path)

    if files_to_process_count == 0:
        print("\nAll files are already processed. No new files to convert.")
    else:
        print(f"\nProcessing complete! Converted new files: {files_to_process_count}.")


if __name__ == '__main__':
    main()