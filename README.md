===============================
    SOUND LADDER GENERATOR
===============================

A Python application that generates a series of pitch-shifted audio files, useful for 
vocal training, sound design, and music production.

------------------
    FEATURES
------------------
* Generate customizable number of pitch-shifted variations of audio files
* Support for WAV and MP3 input/output formats
* Modern dark-themed graphical user interface
* Customizable pitch increment and starting pitch
* Preview lowest and highest pitch before generating
* Batch processing support for multiple files
* Progress tracking for each file

------------------
   REQUIREMENTS
------------------
* Python 3.8 or higher
* FFmpeg (required for audio processing)
* Required Python packages (installed automatically):
  - librosa
  - numpy
  - pydub
  - resampy

-------------------------
   QUICK START (Windows)
-------------------------
1. Download the latest release
2. Install FFmpeg:
   - Download from FFmpeg Builds: https://github.com/BtbN/FFmpeg-Builds/releases
   - Extract to C:\Program Files\ffmpeg
3. Double-click launch_soundladder.bat

------------------------
   MANUAL INSTALLATION
------------------------
1. Clone the repository:
   git clone https://github.com/yourusername/sound-ladder-generator.git
   cd sound-ladder-generator

2. Create a virtual environment:
   python -m venv venv
   
   Windows:
   venv\Scripts\activate
   
   macOS/Linux:
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

----------------------
   INSTALLING FFMPEG
----------------------
Windows:
1. Download FFmpeg from FFmpeg Builds (link above)
2. Extract to C:\Program Files\ffmpeg
3. The program will automatically find FFmpeg in this location

macOS:
brew install ffmpeg

Linux:
sudo apt-get install ffmpeg

--------------
    USAGE
--------------
1. Launch the application using the provided shortcut or:
   python soundladder.py

2. Using the interface:
   * Click "Add Files" to select input audio files
   * Choose an output directory
   * Adjust settings:
     - Number of files to generate
     - Output format (WAV/MP3)
     - Starting pitch (MIDI note)
     - Pitch increment (semitones)
   * Preview lowest/highest pitch (optional)
   * Click "Generate Sound Bites"
   * Monitor progress in the files list

--------------
   LICENSE
--------------
This project is licensed under the MIT License - see the LICENSE file for details.

===============================