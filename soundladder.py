from pydub import AudioSegment
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to change the pitch of the sound
def change_pitch(sound, semitone_change):
    """Change the pitch of a sound by a given number of semitones."""
    octaves = semitone_change / 12.0
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    return sound._spawn(sound.raw_data, overrides={"frame_rate": new_sample_rate}).set_frame_rate(sound.frame_rate)

# Function to generate sound files
def generate_sounds(input_file, output_dir, num_files=100):
    sound = AudioSegment.from_file(input_file)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate sound bites
    for i in range(num_files):
        semitone_increase = i  # Each file increases pitch by 1 semitone
        new_sound = change_pitch(sound, semitone_increase)
        output_file = os.path.join(output_dir, f"sound_{i+1:03d}.wav")
        new_sound.export(output_file, format="wav")

    return output_dir

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

    if not input_file or not os.path.exists(input_file):
        messagebox.showerror("Error", "Please select a valid sound file.")
        return

    if not output_dir:
        messagebox.showerror("Error", "Please specify an output directory.")
        return

    try:
        generate_sounds(input_file, output_dir)
        messagebox.showinfo("Success", f"100 sound files generated in:\n{output_dir}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

# Callback for the "Select Output Directory" button
def select_output_dir():
    dir_path = filedialog.askdirectory(title="Select Output Directory")
    if dir_path:
        output_dir_var.set(dir_path)

# Set up the Tkinter window
root = tk.Tk()
root.title("Sound Bite Generator")

# Input file selection
input_file_var = tk.StringVar()
output_dir_var = tk.StringVar()

tk.Label(root, text="Select Sound File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
tk.Entry(root, textvariable=input_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=5, pady=5)

# Output directory selection
tk.Label(root, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
tk.Entry(root, textvariable=output_dir_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_dir).grid(row=1, column=2, padx=5, pady=5)

# Generate button
tk.Button(root, text="Generate Sound Bites", command=generate, bg="green", fg="white").grid(
    row=2, column=0, columnspan=3, pady=10
)

root.mainloop()
