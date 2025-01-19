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

# Color constants
DARK_BG = '#1e1e1e'
DARKER_BG = '#252526'
TEXT_COLOR = '#ffffff'
ACCENT_COLOR = '#0078d4'
FIELD_BG = '#3c3c3c'
FIELD_BORDER = '#555555'

# Status types dictionary
STATUS_TYPES = {
    'QUEUED': {'text': 'Queued...', 'color': '#666666'},
    'ANALYZING': {'text': 'Analyzing...', 'color': '#2b5797'},
    'CONVERTING': {'text': 'Converting...', 'color': '#0078d4'},
    'COMPLETED': {'text': 'Completed', 'color': '#107c10'},
    'ERROR': {'text': 'Error', 'color': '#c42b1c'},
    'CANCELLED': {'text': 'Cancelled', 'color': '#ca5010'}
}

# Style dictionaries
button_style = {
    'bg': ACCENT_COLOR,
    'fg': TEXT_COLOR,
    'relief': 'flat',
    'padx': 16,
    'pady': 6,
    'cursor': 'hand2',
    'borderwidth': 0,
    'highlightthickness': 0
}

# Create separate styles for regular and large buttons
regular_button_style = {
    **button_style,
    'font': ('Segoe UI', 10)
}

large_button_style = {
    **button_style,
    'font': ('Segoe UI', 11, 'bold'),
    'padx': 32,
    'pady': 8
}

entry_style = {
    'font': ('Segoe UI', 11),
    'bg': FIELD_BG,
    'fg': TEXT_COLOR,
    'relief': 'flat',
    'highlightthickness': 0,
    'insertbackground': TEXT_COLOR
}

label_style = {
    'font': ('Segoe UI', 11),
    'bg': DARK_BG,
    'fg': TEXT_COLOR,
    'anchor': 'w',
    'padx': 10
}

# Create the root window FIRST
root = tk.Tk()
root.title("Sound Bite Generator")
root.state('zoomed')
root.configure(bg=DARK_BG)

# THEN create Tkinter variables
output_dir_var = tk.StringVar()
num_files_var = tk.StringVar(value="100")
output_format_var = tk.StringVar(value="wav")
start_pitch_var = tk.StringVar(value="60")
pitch_increment_var = tk.StringVar(value="0.5")

# Other global variables
selected_files = []
files_treeview = None
status_label = None

# Variables for settings
output_dir_var = tk.StringVar()
num_files_var = tk.StringVar(value="100")  # Default value
output_format_var = tk.StringVar(value="wav")  # Default value
start_pitch_var = tk.StringVar(value="60")  # Default value
pitch_increment_var = tk.StringVar(value="0.5")  # Default value

def create_round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Create a rounded rectangle on a canvas."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]

    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedEntry(tk.Entry):
    """Custom Entry widget with rounded corners"""
    def __init__(self, master=None, **kwargs):
        self.frame = tk.Frame(master, bg=DARK_BG)
        self.frame.pack(fill='x', padx=2, pady=2)
        
        tk.Entry.__init__(self, self.frame, **kwargs)
        self.configure(
            bd=0,
            bg=FIELD_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            highlightthickness=0,
            font=('Segoe UI', 11)
        )
        self.pack(fill='x', ipady=6)

class RoundedSpinbox(tk.Spinbox):
    """Custom Spinbox widget with rounded corners"""
    def __init__(self, master=None, **kwargs):
        self.frame = tk.Frame(master, bg=DARK_BG)
        self.frame.pack(fill='x', padx=2, pady=2)
        
        tk.Spinbox.__init__(self, self.frame, **kwargs)
        self.configure(
            bd=0,
            bg=FIELD_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            highlightthickness=0,
            font=('Segoe UI', 11),
            buttonbackground=FIELD_BG,
            buttoncursor='hand2'
        )
        self.pack(fill='x', ipady=6)

# Add this helper class for rounded buttons
class RoundedButton(tk.Button):
    """Custom Button widget with rounded corners"""
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.configure(
            bd=0,
            relief='flat',
            bg=ACCENT_COLOR,
            fg=TEXT_COLOR,
            activebackground='#1a85d6',  # Lighter accent color
            activeforeground=TEXT_COLOR,
            cursor='hand2',
            padx=16,
            pady=8,
            font=('Segoe UI', 10)
        )

        # Bind hover events
        self.bind('<Enter>', lambda e: self.configure(bg='#1a85d6'))
        self.bind('<Leave>', lambda e: self.configure(bg=ACCENT_COLOR))

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
def generate_sounds(input_file, output_dir, item_id):
    """Generate pitch-shifted sounds with user-defined settings."""
    try:
        # Get all values first
        try:
            start_pitch = float(start_pitch_var.get())
            pitch_increment = float(pitch_increment_var.get())
            num_files = int(num_files_var.get())  # Get num_files from the variable
            output_format = output_format_var.get()
            
            if num_files < 1:
                raise ValueError("Number of files must be at least 1")
                
        except ValueError as e:
            logger.error(f"Invalid values: {str(e)}")
            messagebox.showerror("Error", f"Please enter valid numbers: {str(e)}")
            return
            
        # Update status to analyzing
        update_file_status(item_id, 'ANALYZING')
        
        # Get original filename without extension
        original_filename = os.path.splitext(os.path.basename(input_file))[0]
        
        # Load and process sound
        sound = AudioSegment.from_file(input_file)
        input_freq = detect_pitch(input_file)
        input_note = frequency_to_midi_note(input_freq)
        semitone_adjustment = start_pitch - input_note
        
        logger.debug(f"Input frequency: {input_freq:.2f} Hz")
        logger.debug(f"Input MIDI note: {input_note:.1f}")
        logger.debug(f"Adjustment needed: {semitone_adjustment:.1f} semitones")
        logger.debug(f"Pitch increment: {pitch_increment} semitones")
        logger.debug(f"Number of files: {num_files}")
        logger.debug(f"Output format: {output_format}")
        
        os.makedirs(output_dir, exist_ok=True)

        # Generate sound bites
        for i in range(num_files):
            if PROCESSING_CANCELLED:
                update_file_status(item_id, 'CANCELLED')
                return
                
            progress = int((i + 1) / num_files * 100)
            update_file_status(item_id, 'CONVERTING', progress)
            
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
            
        update_file_status(item_id, 'COMPLETED', 100)
        return output_dir
    except Exception as e:
        logger.error(f"Error in generate_sounds: {str(e)}", exc_info=True)
        update_file_status(item_id, 'ERROR')
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
    global PROCESSING_CANCELLED
    PROCESSING_CANCELLED = False
    
    if not selected_files:
        logger.error("No files selected")
        messagebox.showerror("Error", "Please select at least one input file.")
        return

    output_dir = output_dir_var.get()
    if not output_dir:
        logger.error("No output directory specified")
        messagebox.showerror("Error", "Please select an output directory.")
        return

    # Enable cancel button
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button) and widget['text'] == "Cancel Processing":
            widget.configure(state='normal')

    try:
        total_files = 0
        for i, (input_file, _) in enumerate(selected_files, 1):
            if PROCESSING_CANCELLED:
                messagebox.showinfo("Cancelled", "Processing has been cancelled.")
                break

            item_id = files_treeview.get_children()[i-1]
            
            try:
                generate_sounds(input_file, output_dir, item_id)
            except Exception as e:
                logger.error(f"Error processing {input_file}: {str(e)}")
                update_file_status(item_id, 'ERROR')
                messagebox.showerror("Error", f"Error processing {os.path.basename(input_file)}:\n{str(e)}")
                
        if total_files > 0 and not PROCESSING_CANCELLED:
            messagebox.showinfo("Success", f"Generated {total_files} sound files in:\n{output_dir}")
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    finally:
        # Disable cancel button
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == "Cancel Processing":
                widget.configure(state='disabled')
        PROCESSING_CANCELLED = False

# Callback for the "Select Output Directory" button
def select_output_dir():
    dir_path = filedialog.askdirectory(title="Select Output Directory")
    if dir_path:
        output_dir_var.set(dir_path)

# Update the UI setup code
def create_ui():
    # Create main container frame with padding
    main_container = tk.Frame(root, bg=DARK_BG)
    main_container.pack(fill='both', expand=True, padx=20, pady=20)

    # Input Files section
    files_section = tk.LabelFrame(main_container, text="Input Files", bg=DARK_BG, fg=TEXT_COLOR, font=('Segoe UI', 11))
    files_section.pack(fill='x', padx=10, pady=(0, 20))

    # Treeview for files
    tree_frame = tk.Frame(files_section, bg=DARK_BG)
    tree_frame.pack(fill='x', padx=10, pady=10)

    # Style the treeview
    style = ttk.Style()
    style.configure(
        "Custom.Treeview",
        background=FIELD_BG,
        foreground=TEXT_COLOR,
        fieldbackground=FIELD_BG,
        borderwidth=0
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=DARKER_BG,  # Dark background for headers
        foreground=TEXT_COLOR,  # White text
        relief="flat",
        borderwidth=0
    )
    style.map(
        "Custom.Treeview.Heading",
        background=[('active', ACCENT_COLOR)],  # Blue highlight on hover
        foreground=[('active', TEXT_COLOR)]
    )

    # Create Treeview with scrollbar
    global files_treeview
    files_treeview = ttk.Treeview(
        tree_frame,
        columns=("file", "status", "progress"),
        show="headings",
        style="Custom.Treeview",
        height=8
    )
    
    files_treeview.heading("file", text="File")
    files_treeview.heading("status", text="Status")
    files_treeview.heading("progress", text="Progress")
    
    files_treeview.column("file", width=400)
    files_treeview.column("status", width=100)
    files_treeview.column("progress", width=100)
    
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=files_treeview.yview)
    files_treeview.configure(yscrollcommand=scrollbar.set)
    
    files_treeview.pack(side='left', fill='x', expand=True)
    scrollbar.pack(side='right', fill='y')

    # File buttons
    button_frame = tk.Frame(files_section, bg=DARK_BG)
    button_frame.pack(fill='x', padx=10, pady=10)
    
    # Container for centered buttons
    center_frame = tk.Frame(button_frame, bg=DARK_BG)
    center_frame.pack(expand=True)
    
    RoundedButton(center_frame, text="Add Files", command=add_files, **regular_button_style).pack(side='left', padx=5)
    RoundedButton(center_frame, text="Remove Selected", command=remove_selected, **regular_button_style).pack(side='left', padx=5)
    RoundedButton(center_frame, text="Clear All", command=clear_files, **regular_button_style).pack(side='left', padx=5)

    # Settings section - standardize all input rows
    settings_section = tk.LabelFrame(main_container, text="Settings", bg=DARK_BG, fg=TEXT_COLOR, font=('Segoe UI', 11))
    settings_section.pack(fill='x', padx=10, pady=(0, 20))

    # Function to create consistent input rows with visible labels
    def create_input_row(parent, label_text, widget_creator):
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            frame,
            text=label_text,
            bg=DARK_BG,
            fg=TEXT_COLOR,
            font=('Segoe UI', 11),
            width=25,
            anchor='w'
        ).pack(side='left')
        
        return frame  # Return the frame instead of a container

    # Output Directory - special case for browse button
    dir_frame = create_input_row(settings_section, "Output Directory:", None)
    
    # Entry that fills remaining space
    RoundedEntry(
        dir_frame,
        textvariable=output_dir_var
    ).pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    # Browse button at the end
    RoundedButton(
        dir_frame,
        text="Browse",
        command=select_output_dir,
        **regular_button_style
    ).pack(side='right')

    # Regular input rows
    num_frame = create_input_row(settings_section, "Number of Files:", None)
    RoundedSpinbox(
        num_frame,
        from_=1,
        to=999,
        textvariable=num_files_var,
        width=10
    ).pack(side='left')

    format_frame = create_input_row(settings_section, "Output Format:", None)
    ttk.Combobox(
        format_frame,
        textvariable=output_format_var,
        values=["wav", "mp3"],
        state="readonly",
        width=8
    ).pack(side='left')

    pitch_frame = create_input_row(settings_section, "Starting Pitch (MIDI note):", None)
    RoundedSpinbox(
        pitch_frame,
        from_=0,
        to=127,
        textvariable=start_pitch_var,
        width=10
    ).pack(side='left')

    increment_frame = create_input_row(settings_section, "Pitch Increment (semitones):", None)
    RoundedSpinbox(
        increment_frame,
        from_=0.1,
        to=12,
        increment=0.1,
        textvariable=pitch_increment_var,
        width=10
    ).pack(side='left')

    # Preview section
    preview_frame = tk.Frame(main_container, bg=DARK_BG)
    preview_frame.pack(fill='x', pady=10)
    
    preview_center = tk.Frame(preview_frame, bg=DARK_BG)
    preview_center.pack(expand=True)
    
    RoundedButton(preview_center, text="Preview Lowest", command=lambda: preview_pitch("lowest"), **regular_button_style).pack(side='left', padx=5)
    RoundedButton(preview_center, text="Preview Highest", command=lambda: preview_pitch("highest"), **regular_button_style).pack(side='left', padx=5)

    # Center the generate button
    generate_frame = tk.Frame(main_container, bg=DARK_BG)
    generate_frame.pack(fill='x', pady=20)
    
    generate_center = tk.Frame(generate_frame, bg=DARK_BG)
    generate_center.pack(expand=True)
    
    RoundedButton(
        generate_center,
        text="Generate Sound Bites",
        command=generate,
        **large_button_style
    ).pack()

    # Status label
    global status_label
    status_label = tk.Label(main_container, text="", bg=DARK_BG, fg=TEXT_COLOR, font=('Segoe UI', 11))
    status_label.pack(pady=10)

# Initialize variables
input_file_var = tk.StringVar()
output_dir_var = tk.StringVar()
status_label = None
pitch_increment_var = tk.StringVar(value="0.5")  # Default increment
start_pitch_var = tk.StringVar(value="60")  # Default to middle C (MIDI note 60)
num_files_var = tk.StringVar(value="100")  # Default to 100 files
output_format_var = tk.StringVar(value="wav")  # Default to WAV
start_file_var = tk.StringVar(value="1")  # Default start file number
end_file_var = tk.StringVar(value="100")  # Default end file number
selected_files = []  # List to store file paths

def add_files():
    """Callback for Add Files button"""
    files = filedialog.askopenfilenames(
        title="Select Sound Files",
        filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")]
    )
    if files:
        for file in files:
            if file not in [f[0] for f in selected_files]:
                selected_files.append((file, "Queued..."))
                files_treeview.insert('', 'end', values=(os.path.basename(file), "Queued...", ""))

def remove_selected():
    """Callback for Remove Selected button"""
    selected = files_treeview.selection()
    for item in selected:
        item_values = files_treeview.item(item)['values']
        selected_files[:] = [f for f in selected_files if os.path.basename(f[0]) != item_values[0]]
        files_treeview.delete(item)

def clear_files():
    """Callback for Clear All button"""
    selected_files.clear()
    for item in files_treeview.get_children():
        files_treeview.delete(item)

def cancel_processing():
    """Cancel the file processing."""
    global PROCESSING_CANCELLED
    PROCESSING_CANCELLED = True
    if status_label:
        update_status("Cancelling processing...")

def preview_pitch(position):
    """Preview the pitch-shifted sound"""
    if not selected_files:
        messagebox.showwarning("Warning", "Please select at least one input file.")
        return
        
    try:
        input_file = selected_files[0][0]  # Use first file for preview
        sound = AudioSegment.from_file(input_file)
        
        if position == "lowest":
            semitones = float(start_pitch_var.get()) - frequency_to_midi_note(detect_pitch(input_file))
        else:  # highest
            num_files = int(num_files_var.get())
            pitch_increment = float(pitch_increment_var.get())
            semitones = (float(start_pitch_var.get()) - frequency_to_midi_note(detect_pitch(input_file)) + 
                        (num_files - 1) * pitch_increment)
        
        preview = change_pitch(sound, semitones)
        preview.export("preview.wav", format="wav")
        
        # Play the preview
        if sys.platform == "win32":
            os.startfile("preview.wav")
        else:
            subprocess.run(["xdg-open", "preview.wav"])
            
    except Exception as e:
        logger.error(f"Error in preview: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"Error previewing sound:\n{str(e)}")

def update_file_status(item_id, status, progress=None):
    """Update the status and progress of a file in the treeview"""
    current_values = files_treeview.item(item_id)['values']
    new_values = [
        current_values[0],
        STATUS_TYPES[status]['text'],
        f"{progress}%" if progress is not None else ""
    ]
    files_treeview.item(item_id, values=new_values)
    files_treeview.update()

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

root.mainloop()
