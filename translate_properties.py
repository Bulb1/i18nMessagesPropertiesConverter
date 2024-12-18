import tkinter as tk
from tkinter import filedialog, messagebox
from googletrans import Translator
import os
from datetime import datetime
import json

# Function to load custom dictionary from a JSON file
def load_custom_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            custom_dict = json.load(file)
        return custom_dict
    except Exception as e:
        messagebox.showerror("Error", f"Could not load custom dictionary: {e}")
        return {}

def translate_values(input_data, src_lang, dest_lang, custom_dict=None, is_file_input=True):
    translator = Translator()
    try:
        if is_file_input:
            with open(input_data, 'r', encoding='utf-8') as infile:
                lines = infile.readlines()
        else:
            lines = input_data.splitlines()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"{src_lang}_{dest_lang}_{current_date}.txt"
        output_file = os.path.join(output_dir, output_filename)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    if src_lang == 'en' and value.strip() in custom_dict:
                        translated_value = custom_dict[value.strip()]
                    elif src_lang == 'pl' and key.strip() in custom_dict:
                        translated_value = custom_dict[key.strip()]
                    else:
                        translated_value = translator.translate(value.strip(), src=src_lang, dest=dest_lang).text
                    outfile.write(f"{key}={translated_value}\n")
                else:
                    outfile.write(line)

        messagebox.showinfo("Success", f"Translation saved to {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def select_input_file():
    # Get the 'input' directory in the same location as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script's directory
    input_dir = os.path.join(script_dir, 'input')  # Path to 'input' directory

    # Check if the 'input' directory exists, otherwise show an error
    if not os.path.exists(input_dir):
        messagebox.showerror("Error", "The 'input' directory does not exist. Please create it in the script's directory.")
        return

    # Open a file dialog starting at the 'input' directory
    input_file = filedialog.askopenfilename(
        initialdir=input_dir,
        title="Select Input File",
        filetypes=[("Text Files", "*.txt")]
    )

    # If a file is selected, insert its path into the input entry field
    if input_file:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, input_file)

def toggle_input_mode():
    if file_input_var.get():
        input_text.grid_forget()
        file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        file_frame.grid_columnconfigure(1, weight=1)  # Allow file entry to expand
    else:
        file_frame.grid_forget()
        input_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

def run_translation():
    if file_input_var.get():
        input_file = input_entry.get()
        if not input_file:
            messagebox.showwarning("Input Error", "Please select an input file.")
            return
        input_data = input_file
        is_file_input = True
    else:
        input_data = input_text.get("1.0", "end-1c")
        if not input_data.strip():
            messagebox.showwarning("Input Error", "Please enter some text.")
            return
        is_file_input = False

    custom_dict = load_custom_dict("custom_dict.json")
    src_lang = src_lang_var.get()
    dest_lang = dest_lang_var.get()
    translate_values(input_data, src_lang, dest_lang, custom_dict, is_file_input)

# Main application
root = tk.Tk()
root.title("Translation Tool")

# Window size
window_width = 600
window_height = 400

# Update tasks and get screen dimensions
root.update_idletasks()  # Ensure correct dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the center position
x_coordinate = (screen_width // 2) - (window_width // 2)
y_coordinate = (screen_height // 2) - (window_height // 2)

# Set the dimensions and position of the window
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Configure grid layout
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

# Toggle input mode
file_input_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Use File Input", variable=file_input_var, command=toggle_input_mode).grid(
    row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5
)

# File input frame
file_frame = tk.Frame(root)
tk.Label(file_frame, text="Select Input File:").grid(row=0, column=0, padx=5, pady=5)
input_entry = tk.Entry(file_frame)
input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
file_frame.grid_columnconfigure(1, weight=1)
tk.Button(file_frame, text="Browse", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

# Text input area
input_text = tk.Text(root, wrap="word")
input_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

# Language selection
lang_frame = tk.Frame(root)
lang_frame.grid(row=2, column=0, columnspan=2, pady=5)
tk.Label(lang_frame, text="From:").grid(row=0, column=0, padx=5)
src_lang_var = tk.StringVar(value="pl")
tk.OptionMenu(lang_frame, src_lang_var, "pl", "en").grid(row=0, column=1, padx=5)
tk.Label(lang_frame, text="To:").grid(row=0, column=2, padx=5)
dest_lang_var = tk.StringVar(value="en")
tk.OptionMenu(lang_frame, dest_lang_var, "en", "pl").grid(row=0, column=3, padx=5)

# Translate button
tk.Button(root, text="Translate", command=run_translation).grid(row=3, column=0, columnspan=2, pady=10)

# Initial layout setup
toggle_input_mode()
root.mainloop()
