@echo off
setlocal
TITLE Media Converter

REM --- SETTINGS ---
REM Specify the paths here for easy editing

set PYTHON_EXE="C:\Python\Python312\python.exe"
set SCRIPT_NAME="convert_folder.py"
set SOURCE_FOLDER="C:\Users\voothi\Downloads\20250715194603-convert-src"
set DEST_FOLDER="C:\Users\voothi\Downloads\20250715194651-convert-dst"
set FFMPEG_PATH="C:\Tools\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"

REM --- END OF SETTINGS ---


REM Change to the directory where this .cmd file is located
cd /d "%~dp0"

echo Starting the conversion process...
echo Source: %SOURCE_FOLDER%
echo Destination: %DEST_FOLDER%
echo.

REM Run the Python script using the variables
%PYTHON_EXE% %SCRIPT_NAME% %SOURCE_FOLDER% %DEST_FOLDER% %FFMPEG_PATH%

echo.
echo Script finished. Press any key to exit.
pause
endlocal