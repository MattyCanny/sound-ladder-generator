# Sound Ladder Generator

A Python application that generates a series of pitch-shifted audio files, useful for vocal training, sound design, and music production.

## Features

- Generate 100 pitch-shifted variations of an input audio file
- Support for WAV, MP3, and OGG input formats
- Simple graphical user interface
- Each output file increases by one semitone

## Installation

1. Clone the repository:   ```bash
   git clone https://github.com/yourusername/sound-ladder-generator.git
   cd sound-ladder-generator   ```

2. Create a virtual environment (recommended):   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate   ```

3. Install dependencies:   ```bash
   pip install -r requirements.txt   ```

## Usage

1. Run the application:   ```bash
   python soundladder.py   ```

2. Using the interface:
   - Click "Browse" to select your input audio file
   - Choose an output directory
   - Click "Generate Sound Bites"
   - Wait for the success message

## Requirements

- Python 3.6 or higher
- pydub library
- FFmpeg (required by pydub for MP3 and OGG support)

## Installing FFmpeg

#### Windows
1. Download FFmpeg from [here](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the downloaded file
3. Move the contents of the `bin` folder to `C:\Program Files\ffmpeg`
4. Add to System PATH:
   - Open "System Properties" (Windows key + X → System)
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", select "Path"
   - Click "Edit" → "New"
   - Add `C:\Program Files\ffmpeg`
   - Click "OK" on all windows

#### macOS
Run in terminal:
`brew install ffmpeg`

#### Linux
Run in terminal:
`sudo apt-get install ffmpeg`

### Running the Program
1. Download the latest release
2. Run the application:
   `python soundladder.py`
3. Using the interface:
   - Click "Browse" to select your input audio file
   - Choose an output directory
   - Click "Generate Sound Bites"
   - Wait for the success message

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.