import tkinter as tk
from tkinter import filedialog, messagebox
from googletrans import Translator
import os
from datetime import datetime
import json
import logging
from time import sleep
import random


# Function to load custom dictionary from a JSON file
def load_custom_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            custom_dict = json.load(file)
        logging.info(f"Loaded dictionary from {file_path}")
        return custom_dict
    except Exception as e:
        messagebox.showerror("Error", f"Could not load custom dictionary: {e}")
        return {}


def safe_translate(translator, value, src_lang, dest_lang, retries=3):
    """Safe translation function with retries."""
    for attempt in range(retries):
        try:
            return translator.translate(value, src=src_lang, dest=dest_lang).text
        except Exception as e:
            if attempt < retries - 1:
                sleep(1)  # Wait before retrying
            else:
                logging.error(f"Translation failed for '{value}': {e}")
                return value  # Fallback to original text


def translate_values(input_data, src_lang, dest_lang, custom_dict, is_file_input=True):
    translator = Translator()
    try:
        # Load the input data
        if is_file_input:
            with open(input_data, 'r', encoding='utf-8') as infile:
                lines = infile.readlines()  # Keep all lines, including newlines
        else:
            lines = input_data.splitlines(True)  # Keep all newlines

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"{src_lang}_{dest_lang}_{current_date}_{random.randint(1000, 9999)}.txt"
        output_file = os.path.join(output_dir, output_filename)

        seen_keys = set()
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line_number, line in enumerate(lines, start=1):
                if line.strip():  # Skip completely empty lines (lines with just whitespace are kept)
                    try:
                        key, value = line.split('=', 1)
                        if not value.strip():
                            raise ValueError(f"Empty value for key '{key.strip()}' on line {line_number}.")
                    except ValueError:
                        raise ValueError(
                            f"Error on line {line_number}: Invalid format '{line.strip()}'. Ensure it has 'key=value'.")

                    # Detect duplicate keys
                    if key.strip() in seen_keys:
                        raise ValueError(f"Duplicate key '{key.strip()}' found on line {line_number}.")
                    seen_keys.add(key.strip())

                    logging.info(f"Translating: {value.strip()}")

                    translated_value = None

                    # Perform dictionary lookup based on source language
                    if src_lang == 'pl':  # PL → EN
                        if value.strip() in custom_dict:
                            translated_value = custom_dict[value.strip()]
                            logging.info(f"Custom Dictionary Match (PL to EN): {translated_value}")
                        else:
                            # Case-insensitive match
                            for dict_key, dict_value in custom_dict.items():
                                if value.strip().lower() == dict_key.lower():
                                    translated_value = dict_value
                                    logging.info(f"Case-Insensitive Match (PL to EN): {translated_value}")
                                    break
                    elif src_lang == 'en':  # EN → PL
                        # Find the key in the dictionary that matches the value being translated
                        for dict_key, dict_value in custom_dict.items():
                            if value.strip() == dict_key:  # Exact match
                                translated_value = dict_value
                                logging.info(f"Custom Dictionary Match (EN to PL): {translated_value}")
                                break
                            elif value.strip().lower() == dict_key.lower():  # Case-insensitive
                                translated_value = dict_value
                                logging.info(f"Case-Insensitive Match (EN to PL): {translated_value}")
                                break

                    # If no match found in the dictionary, fall back to Google Translate
                    if translated_value is None:
                        logging.info(f"Google Translate for: {value.strip()}")
                        translated_value = safe_translate(translator, value.strip(), src_lang, dest_lang)

                    outfile.write(f"{key.strip()}={translated_value}\n")
                    logging.info(f"Translation written: {key.strip()}={translated_value}")
                else:
                    # Preserve newlines for empty lines (no action needed)
                    outfile.write('\n')

        messagebox.showinfo("Success", f"Translation saved to {output_file}")
    except ValueError as ve:
        messagebox.showerror("Input Error", f"An error occurred: {ve}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def select_input_file():
    # Allow user to paste the file path manually, no restrictions to the input directory
    input_file = filedialog.askopenfilename(
        title="Select Input File",
        filetypes=[("Text Files", "*.txt"), ("Properties Files", "*.properties"), ("All Files", "*.*")]
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
        if not input_file or not os.path.isfile(input_file):  # Validate the file path
            messagebox.showwarning("Input Error", "Please select a valid input file or paste a valid path.")
            return
        input_data = input_file
        is_file_input = True
    else:
        input_data = input_text.get("1.0", "end-1c")
        if not input_data.strip():
            messagebox.showwarning("Input Error", "Please enter some text.")
            return
        is_file_input = False

    src_lang = src_lang_var.get()
    dest_lang = dest_lang_var.get()

    # Load the correct dictionary based on the source language and direction
    if src_lang == 'pl' and dest_lang == 'en':
        custom_dict = load_custom_dict("custom_dict_en.json")  # Polish to English
    elif src_lang == 'en' and dest_lang == 'pl':
        custom_dict = load_custom_dict("custom_dict_pl.json")  # English to Polish
    else:
        custom_dict = {}

    translate_values(input_data, src_lang, dest_lang, custom_dict, is_file_input)


# Function to automatically switch the destination language based on the source language
def update_dest_lang(*args):
    src_lang = src_lang_var.get()
    if src_lang == 'pl':
        dest_lang_var.set('en')
    elif src_lang == 'en':
        dest_lang_var.set('pl')


def update_src_lang(*args):
    dest_lang = dest_lang_var.get()
    if dest_lang == 'pl':
        src_lang_var.set('en')
    elif dest_lang == 'en':
        src_lang_var.set('pl')


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
tk.Label(file_frame, text="Select Input File or Paste Path:").grid(row=0, column=0, padx=5, pady=5)
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
src_lang_var.trace("w", update_dest_lang)  # Watch the source language variable for changes
tk.OptionMenu(lang_frame, src_lang_var, "pl", "en").grid(row=0, column=1, padx=5)
tk.Label(lang_frame, text="To:").grid(row=0, column=2, padx=5)
dest_lang_var = tk.StringVar(value="en")
dest_lang_var.trace("w", update_src_lang)  # Watch the destination language variable for changes
tk.OptionMenu(lang_frame, dest_lang_var, "en", "pl").grid(row=0, column=3, padx=5)

# Translate button
tk.Button(root, text="Translate", command=run_translation).grid(row=3, column=0, columnspan=2, pady=10)

# Initial layout setup
toggle_input_mode()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

root.mainloop()
