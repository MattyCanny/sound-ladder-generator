import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import logging
import subprocess
import sys

# Set up logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add FFmpeg to PATH at runtime
ffmpeg_path = r"C:\Program Files\ffmpeg\ffmpeg-2024-12-26-git-fe04b93afa-full_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        # Check FFmpeg
        logger.debug("Checking FFmpeg...")
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        
        # Check librosa
        logger.debug("Checking librosa...")
        import librosa
        import numpy as np
        from pydub import AudioSegment
        
        logger.debug("All dependencies found!")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"FFmpeg not found: {str(e)}")
        messagebox.showerror(
            "FFmpeg Not Found", 
            f"FFmpeg is required but not found on your system.\n\n"
            f"Please verify FFmpeg is in:\n{ffmpeg_path}\n\n"
            "If not, please install FFmpeg:\n"
            "1. Download from: https://github.com/BtbN/FFmpeg-Builds/releases\n"
            "2. Extract to correct location\n"
            "3. Restart this application"
        )
        return False
    except ImportError as e:
        logger.error(f"Missing Python dependency: {str(e)}")
        messagebox.showerror(
            "Missing Dependencies", 
            f"Required library not found: {str(e)}\n\n"
            "Please install missing dependencies using:\n"
            "1. Open terminal in your project directory\n"
            "2. Activate your virtual environment\n"
            "3. Run: pip install librosa numpy pydub\n"
            "4. Restart this application"
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error during dependency check: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
        return False

# Set up the Tkinter window first
root = tk.Tk()
root.title("Sound Bite Generator")
root.minsize(600, 300)  # Slightly larger minimum size
root.configure(bg='#ffffff')  # Windows 11 white background

# Check dependencies before importing them
if not check_dependencies():
    root.destroy()
    sys.exit(1)

# Only import these after checking dependencies
import librosa
import numpy as np
from pydub import AudioSegment

# Function to change the pitch of the sound
def change_pitch(sound, semitones):
    """Change pitch while preserving duration exactly."""
    try:
        # Convert pydub AudioSegment to numpy array
        samples = np.array(sound.get_array_of_samples())
        sample_rate = sound.frame_rate
        
        # Handle stereo by processing each channel separately
        if sound.channels == 2:
            samples = samples.reshape(-1, 2)
        
        # Convert to float32 for librosa
        samples = samples.astype(np.float32) / 32768.0
        
        # Process mono or each stereo channel
        if sound.channels == 1:
            shifted = librosa.effects.pitch_shift(
                y=samples,
                sr=sample_rate,
                n_steps=semitones,
                bins_per_octave=12,
                res_type='kaiser_best'  # Higher quality resampling
            )
        else:
            # Process each channel separately
            shifted_left = librosa.effects.pitch_shift(
                y=samples[:, 0],
                sr=sample_rate,
                n_steps=semitones,
                bins_per_octave=12,
                res_type='kaiser_best'
            )
            shifted_right = librosa.effects.pitch_shift(
                y=samples[:, 1],
                sr=sample_rate,
                n_steps=semitones,
                bins_per_octave=12,
                res_type='kaiser_best'
            )
            shifted = np.vstack((shifted_left, shifted_right)).T
        
        # Ensure exact same length as input
        if len(shifted) > len(samples):
            shifted = shifted[:len(samples)]
        elif len(shifted) < len(samples):
            # Pad with silence if needed
            if sound.channels == 2:
                padding = np.zeros((len(samples) - len(shifted), 2))
            else:
                padding = np.zeros(len(samples) - len(shifted))
            shifted = np.concatenate([shifted, padding])
        
        # Convert back to int16
        shifted = np.clip(shifted * 32768.0, -32768, 32767).astype(np.int16)
        
        # Create new AudioSegment
        new_sound = AudioSegment(
            shifted.tobytes(), 
            frame_rate=sample_rate,
            sample_width=2, 
            channels=sound.channels
        )
        
        # Final length check
        if len(new_sound) != len(sound):
            logger.warning(f"Length mismatch: original={len(sound)}ms, new={len(new_sound)}ms")
            new_sound = new_sound[:len(sound)]
        
        return new_sound
        
    except Exception as e:
        logger.error(f"Error in pitch shifting: {str(e)}", exc_info=True)
        raise

def detect_pitch(file_path):
    """Detect the fundamental frequency (pitch) of an audio file."""
    y, sr = librosa.load(file_path)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # Get the highest magnitude pitch for each time
    pit_mags = []
    for time_slice in range(pitches.shape[1]):
        index = magnitudes[:, time_slice].argmax()
        pit_mags.append(pitches[index, time_slice])
    
    # Get the most common pitch (excluding zeros)
    pit_mags = np.array(pit_mags)
    pit_mags = pit_mags[pit_mags > 0]
    return np.median(pit_mags)

def frequency_to_midi_note(frequency):
    """Convert frequency in Hz to MIDI note number."""
    return 69 + 12 * np.log2(frequency / 440.0)

def midi_note_to_frequency(midi_note):
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))

# Function to generate sound files
def generate_sounds(input_file, output_dir):
    """Generate pitch-shifted sounds with user-defined settings."""
    try:
        # Get all values
        try:
            start_pitch = float(start_pitch_var.get())
            pitch_increment = float(pitch_increment_var.get())
            num_files = int(num_files_var.get())
            output_format = output_format_var.get()
            if num_files < 1:
                raise ValueError("Number of files must be at least 1")
        except ValueError as e:
            logger.error(f"Invalid values: {str(e)}")
            messagebox.showerror("Error", f"Please enter valid numbers: {str(e)}")
            return
            
        # Get original filename without extension
        original_filename = os.path.splitext(os.path.basename(input_file))[0]
        
        # Detect input pitch
        input_freq = detect_pitch(input_file)
        input_note = frequency_to_midi_note(input_freq)
        semitone_adjustment = start_pitch - input_note
        
        logger.debug(f"Input frequency: {input_freq:.2f} Hz")
        logger.debug(f"Input MIDI note: {input_note:.1f}")
        logger.debug(f"Adjustment needed: {semitone_adjustment:.1f} semitones")
        logger.debug(f"Pitch increment: {pitch_increment} semitones")
        logger.debug(f"Number of files: {num_files}")
        logger.debug(f"Output format: {output_format}")
        logger.debug(f"Original filename: {original_filename}")
        
        sound = AudioSegment.from_file(input_file)
        os.makedirs(output_dir, exist_ok=True)

        # Generate sound bites
        for i in range(num_files):
            semitone_increase = (i * pitch_increment) + semitone_adjustment
            new_sound = change_pitch(sound, semitone_increase)
            output_file = os.path.join(output_dir, f"{original_filename}_sound_{i+1:03d}.{output_format}")
            
            # Export with format-specific settings
            if output_format == "mp3":
                new_sound.export(
                    output_file, 
                    format="mp3",
                    bitrate="192k",
                    tags={
                        'title': f'{original_filename} Sound {i+1}',
                        'artist': 'Sound Ladder Generator',
                        'pitch_shift': f'{semitone_increase:.1f} semitones'
                    }
                )
            else:  # WAV
                new_sound.export(output_file, format="wav")
            
            # Update progress
            if status_label:
                update_status(f"Generating file {i+1} of {num_files}...")
            
        return output_dir
    except Exception as e:
        logger.error(f"Error in generate_sounds: {str(e)}", exc_info=True)
        raise

# Callback for the "Select File" button
def select_file():
    file_path = filedialog.askopenfilename(
        title="Select Sound File",
        filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")]
    )
    if file_path:
        input_file_var.set(file_path)

# Callback for the "Generate" button
def generate():
    input_file = input_file_var.get()
    output_dir = output_dir_var.get()

    logger.debug(f"Input file path: {input_file}")
    logger.debug(f"Output directory: {output_dir}")

    if not input_file:
        logger.error("No input file selected")
        messagebox.showerror("Error", "Please select an input sound file.")
        return

    if not os.path.exists(input_file):
        logger.error(f"Input file does not exist: {input_file}")
        messagebox.showerror("Error", f"Input file not found:\n{input_file}")
        return

    if not output_dir:
        logger.error("No output directory specified")
        messagebox.showerror("Error", "Please select an output directory.")
        return

    try:
        num_files = int(num_files_var.get())  # Get the actual number of files
        logger.debug("Attempting to read input file...")
        generate_sounds(input_file, output_dir)
        messagebox.showinfo("Success", f"{num_files} sound files generated in:\n{output_dir}")
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

# Callback for the "Select Output Directory" button
def select_output_dir():
    dir_path = filedialog.askdirectory(title="Select Output Directory")
    if dir_path:
        output_dir_var.set(dir_path)

# Update the UI setup code
def create_ui():
    # Configure root window grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Main frame with Windows 11 style background
    main_frame = tk.Frame(root, padx=24, pady=24, bg='#ffffff')  # Windows 11 uses more whitespace
    main_frame.grid(row=0, column=0, sticky='nsew')
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(3, weight=1)

    # Windows 11 style button configuration
    button_style = {
        'bg': '#0067c0',  # Windows 11 blue
        'fg': 'white',
        'font': ('Segoe UI', 10),  # Windows 11 system font
        'padx': 16,
        'pady': 8,
        'relief': 'flat',  # Flat design
        'cursor': 'hand2',
        'borderwidth': 0  # No border
    }

    # Input file selection row
    input_frame = tk.Frame(main_frame, bg='#ffffff')
    input_frame.grid(row=0, column=0, sticky='ew', pady=(0, 16))
    input_frame.grid_columnconfigure(1, weight=1)

    tk.Label(
        input_frame, 
        text="Select Sound File:", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'  # Dark gray text
    ).grid(row=0, column=0, sticky='w', padx=(0, 12))
    
    entry_style = {
        'font': ('Segoe UI', 11),
        'relief': 'flat',
        'bg': '#f5f5f5',  # Light gray background
        'highlightthickness': 1,
        'highlightbackground': '#e0e0e0',  # Border color
        'highlightcolor': '#0067c0'  # Focus border color
    }
    
    tk.Entry(
        input_frame, 
        textvariable=input_file_var,
        **entry_style
    ).grid(row=0, column=1, sticky='ew', padx=5, ipady=8)  # Added internal padding
    
    tk.Button(
        input_frame, 
        text="Browse", 
        command=select_file, 
        **button_style
    ).grid(row=0, column=2, padx=(5, 0))

    # Output directory row
    output_frame = tk.Frame(main_frame, bg='#ffffff')
    output_frame.grid(row=1, column=0, sticky='ew', pady=(0, 24))
    output_frame.grid_columnconfigure(1, weight=1)

    tk.Label(
        output_frame, 
        text="Output Directory:", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'
    ).grid(row=0, column=0, sticky='w', padx=(0, 12))
    
    tk.Entry(
        output_frame, 
        textvariable=output_dir_var,
        **entry_style
    ).grid(row=0, column=1, sticky='ew', padx=5, ipady=8)
    
    tk.Button(
        output_frame, 
        text="Browse", 
        command=select_output_dir, 
        **button_style
    ).grid(row=0, column=2, padx=(5, 0))

    # Add number of files control
    num_files_frame = tk.Frame(main_frame, bg='#ffffff')
    num_files_frame.grid(row=2, column=0, sticky='ew', pady=(0, 16))
    num_files_frame.grid_columnconfigure(1, weight=1)

    tk.Label(
        num_files_frame, 
        text="Number of Files:", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'
    ).grid(row=0, column=0, sticky='w', padx=(0, 12))
    
    num_files_spinbox = tk.Spinbox(
        num_files_frame,
        from_=1,
        to=1000,
        increment=1,
        textvariable=num_files_var,
        font=('Segoe UI', 11),
        relief='flat',
        bg='#f5f5f5',
        highlightthickness=1,
        highlightbackground='#e0e0e0',
        highlightcolor='#0067c0',
        width=10
    )
    num_files_spinbox.grid(row=0, column=1, sticky='w', padx=5, ipady=8)

    # Add format selection
    format_frame = tk.Frame(main_frame, bg='#ffffff')
    format_frame.grid(row=3, column=0, sticky='ew', pady=(0, 16))
    format_frame.grid_columnconfigure(1, weight=1)

    tk.Label(
        format_frame, 
        text="Output Format:", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'
    ).grid(row=0, column=0, sticky='w', padx=(0, 12))
    
    # Combobox for format selection
    format_combo = ttk.Combobox(
        format_frame,
        textvariable=output_format_var,
        values=["wav", "mp3"],
        state="readonly",
        font=('Segoe UI', 11),
        width=9
    )
    format_combo.grid(row=0, column=1, sticky='w', padx=5, ipady=8)

    # Style the combobox to match Windows 11
    style = ttk.Style()
    style.configure('TCombobox', 
        background='#f5f5f5',
        fieldbackground='#f5f5f5',
        selectbackground='#0067c0',
        selectforeground='white'
    )

    # Starting pitch control (moved to row 4)
    start_pitch_frame = tk.Frame(main_frame, bg='#ffffff')
    start_pitch_frame.grid(row=4, column=0, sticky='ew', pady=(0, 16))
    start_pitch_frame.grid_columnconfigure(1, weight=1)

    tk.Label(
        start_pitch_frame, 
        text="Starting Pitch (MIDI note):", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'
    ).grid(row=0, column=0, sticky='w', padx=(0, 12))
    
    start_pitch_spinbox = tk.Spinbox(
        start_pitch_frame,
        from_=24,  # Low C
        to=96,     # High C
        increment=1,
        textvariable=start_pitch_var,
        font=('Segoe UI', 11),
        relief='flat',
        bg='#f5f5f5',
        highlightthickness=1,
        highlightbackground='#e0e0e0',
        highlightcolor='#0067c0',
        width=10
    )
    start_pitch_spinbox.grid(row=0, column=1, sticky='w', padx=5, ipady=8)

    # Pitch increment control (moved to row 5)
    pitch_frame = tk.Frame(main_frame, bg='#ffffff')
    pitch_frame.grid(row=5, column=0, sticky='ew', pady=(0, 16))
    pitch_frame.grid_columnconfigure(1, weight=1)

    tk.Label(
        pitch_frame, 
        text="Pitch Increment (semitones):", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'
    ).grid(row=0, column=0, sticky='w', padx=(0, 12))
    
    pitch_spinbox = tk.Spinbox(
        pitch_frame,
        from_=0.1,
        to=2.0,
        increment=0.1,
        textvariable=pitch_increment_var,
        font=('Segoe UI', 11),
        relief='flat',
        bg='#f5f5f5',
        highlightthickness=1,
        highlightbackground='#e0e0e0',
        highlightcolor='#0067c0',
        width=10
    )
    pitch_spinbox.grid(row=0, column=1, sticky='w', padx=5, ipady=8)

    # Preview buttons frame (moved to row 6)
    preview_frame = tk.Frame(main_frame, bg='#ffffff')
    preview_frame.grid(row=6, column=0, pady=(0, 16))

    preview_button_style = button_style.copy()
    preview_button_style['bg'] = '#0078d4'  # Slightly lighter blue

    tk.Button(
        preview_frame,
        text="Preview Lowest",
        command=lambda: preview_pitch("lowest"),
        **preview_button_style
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        preview_frame,
        text="Preview Highest",
        command=lambda: preview_pitch("highest"),
        **preview_button_style
    ).grid(row=0, column=1, padx=5)

    # Generate button (moved to row 7)
    generate_button = tk.Button(
        main_frame,
        text="Generate Sound Bites",
        command=generate,
        bg='#0067c0',
        fg='white',
        font=('Segoe UI', 11, 'bold'),
        padx=32,
        pady=12,
        relief='flat',
        cursor='hand2',
        borderwidth=0
    )
    generate_button.grid(row=7, column=0, pady=(0, 16))

    # Status label (moved to row 8)
    global status_label
    status_label = tk.Label(
        main_frame, 
        text="", 
        font=('Segoe UI', 11),
        bg='#ffffff',
        fg='#202020'
    )
    status_label.grid(row=8, column=0)

    # Add hover effects for buttons
    def on_enter(e):
        e.widget['bg'] = '#0078d4'  # Lighter blue on hover

    def on_leave(e):
        e.widget['bg'] = '#0067c0'  # Return to original blue

    # Bind hover events to all buttons
    for widget in main_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        for child in widget.winfo_children():
            if isinstance(child, tk.Button):
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)

# Initialize variables
input_file_var = tk.StringVar()
output_dir_var = tk.StringVar()
status_label = None
pitch_increment_var = tk.StringVar(value="0.5")  # Default increment
start_pitch_var = tk.StringVar(value="60")  # Default to middle C (MIDI note 60)
num_files_var = tk.StringVar(value="100")  # Default number of files
output_format_var = tk.StringVar(value="wav")  # Default to WAV

# Create the UI
create_ui()

# Update status function with Windows 11 colors
def update_status(message, is_error=False):
    if status_label:
        status_label.config(
            text=message,
            fg='#c42b1c' if is_error else '#0067c0'  # Windows 11 red for errors, blue for success
        )
    root.update()

# Update generate function to show progress
def generate():
    if not input_file_var.get():
        update_status("Please select an input file", True)
        return
    if not output_dir_var.get():
        update_status("Please select an output directory", True)
        return
    
    try:
        update_status("Generating sound bites...")
        # Your existing generate code here
        update_status("Successfully generated 100 sound files!")
    except Exception as e:
        update_status(f"Error: {str(e)}", True)

def preview_pitch(semitones):
    """Preview the pitch-shifted sound."""
    try:
        input_file = input_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select an input file first")
            return
            
        # Get all values
        try:
            start_pitch = float(start_pitch_var.get())
            pitch_increment = float(pitch_increment_var.get())
            num_files = int(num_files_var.get())
            if num_files < 1:
                raise ValueError("Number of files must be at least 1")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid values: {str(e)}")
            return
            
        # Load and process sound
        sound = AudioSegment.from_file(input_file)
        input_freq = detect_pitch(input_file)
        input_note = frequency_to_midi_note(input_freq)
        semitone_adjustment = start_pitch - input_note
        
        # Calculate final adjustment
        if semitones == "highest":
            semitone_increase = ((num_files - 1) * pitch_increment) + semitone_adjustment
        else:  # lowest
            semitone_increase = semitone_adjustment
            
        # Generate preview
        new_sound = change_pitch(sound, semitone_increase)
        
        # Play the preview (first 2 seconds)
        preview_length = min(len(new_sound), 2000)
        preview = new_sound[:preview_length]
        preview.export("temp_preview.wav", format="wav")
        
        if sys.platform == "win32":
            os.startfile("temp_preview.wav")
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, "temp_preview.wav"])
            
    except Exception as e:
        logger.error(f"Error in preview: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"Preview failed: {str(e)}")

root.mainloop()
