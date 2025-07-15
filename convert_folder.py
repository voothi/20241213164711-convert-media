import subprocess
import argparse
import os

def process_media_file(input_file, output_file, ffmpeg_path):
    """
    Converts a media file (audio or video) to a standard MP4 with a black screen.
    It takes the audio track from the source file and replaces the video stream.
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
        '-b:v', '20k',
        '-g', '12',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_file
    ]

    # Executing the command
    print(f"Processing: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
    try:
        # check=True will raise an exception if ffmpeg returns an error
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully processed: '{output_file}'")
    except subprocess.CalledProcessError as e:
        print(f"Error processing file {input_file}:")
        # Print the error from stderr to understand what went wrong with ffmpeg
        print(e.stderr.decode('utf-8', errors='ignore'))
    except FileNotFoundError:
        print(f"Error: Could not find ffmpeg at path '{ffmpeg_path}'. Please check the path.")
        exit(1) # Exit the script if ffmpeg is not found


def main():
    # Setting up the argument parser
    parser = argparse.ArgumentParser(description='Converts new audio/video files from a source folder to a standard MP4 format.')
    parser.add_argument('source_folder', metavar='source', type=str, 
                        help='Source folder with media files (wav, mp3, mp4)')
    parser.add_argument('destination_folder', metavar='destination', type=str, 
                        help='Destination folder to save the resulting MP4 files')
    parser.add_argument('ffmpeg_path', metavar='ffmpeg', type=str, 
                        help='Path to the ffmpeg executable (ffmpeg.exe)')

    args = parser.parse_args()

    # --- Path validation ---
    if not os.path.isdir(args.source_folder):
        print(f"Error: Source folder '{args.source_folder}' does not exist.")
        return

    if not os.path.isfile(args.ffmpeg_path):
        print(f"Error: ffmpeg not found at path '{args.ffmpeg_path}'.")
        return

    os.makedirs(args.destination_folder, exist_ok=True)

    # --- File comparison and processing logic ---
    
    # Define a tuple of supported extensions
    SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.mp4')

    # Get a list of supported files in the source folder
    try:
        source_files = [f for f in os.listdir(args.source_folder) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    except FileNotFoundError:
        print(f"Error: Could not access folder '{args.source_folder}'.")
        return

    # Get a list of MP4 files in the destination folder
    try:
        dest_files = [f for f in os.listdir(args.destination_folder) if f.lower().endswith('.mp4')]
    except FileNotFoundError:
        print(f"Error: Could not access folder '{args.destination_folder}'.")
        return
        
    # Create a set of destination filenames without the extension for fast lookup
    dest_filenames_without_ext = {os.path.splitext(f)[0] for f in dest_files}

    files_to_process_count = 0
    
    # Iterate over the source files
    for source_filename in source_files:
        # Get the base name of the file (without extension)
        base_name = os.path.splitext(source_filename)[0]

        # Check if a processed file with the same base name already exists
        if base_name in dest_filenames_without_ext:
            print(f"Skipping: A file for '{source_filename}' already exists in the destination folder.")
            continue
        
        # If the file doesn't exist, start processing
        files_to_process_count += 1
        input_path = os.path.join(args.source_folder, source_filename)
        output_path = os.path.join(args.destination_folder, base_name + '.mp4')
        
        # Perform the conversion
        process_media_file(input_path, output_path, args.ffmpeg_path)

    if files_to_process_count == 0:
        print("\nAll applicable files have been processed. No new files to convert.")
    else:
        print(f"\nProcessing complete! Processed new files: {files_to_process_count}.")


if __name__ == '__main__':
    main()