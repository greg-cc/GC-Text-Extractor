"""
GC Text Extractor v1.5.4

Overall Description:
A desktop application built with Tkinter for extracting and filtering text from
various document types. It provides a unified graphical user interface with
extensive, configurable filters to clean and refine extracted text content.
Settings are persistent across sessions, saved to a JSON file.

Key Features:
--------------------------------------------------------------------------------
1.  File Handling:
    - Extracts text from .txt, .docx (Microsoft Word), and .pdf files.
    - Supports user-defined custom file extensions (comma-separated, e.g., .log, .md)
      to be processed as plain text.
    - Drag-and-drop interface for easy file processing.
    - Customizable output file suffix (e.g., "_processed"), with output always as .txt.

2.  User Interface (Single Window):
    - All controls and functional areas are visible simultaneously.
    - Scrollable "Filter Settings" section for detailed configuration.
    - Resizable "Filter Test Pad" with:
        - Input text area for pasting sample text.
        - "Process Pasted Text" button to apply current filters.
        - Output text area to display filtered results immediately.
    - Status bar for operational feedback, error messages, and version information.

3.  Filter Settings & Persistence:
    - All filter settings are automatically saved to `text_extractor_settings.json`
      on application close and loaded on startup.
    - Basic Filters:
        - Min Words (General Sequence): Configurable minimum word count for general text lines.
        - Min Words (Punctuated Sentences): Configurable minimum word count for lines ending
          with sentence punctuation.
        - Alphanumeric Filter:
            - Toggle (ON/OFF) to enable/disable.
            - Threshold (slider & entry): Sets the minimum required ratio (0.0-1.0)
              of alphanumeric characters for a text segment to be kept.
    - Advanced Word/Block Filters (each with its own enable/disable toggle):
        - Attempt to remove code-like blocks:
            - Identifies and removes segments resembling computer code.
            - Sensitivity Controls: Min keywords, min code symbols, min words in segment
              to check, and symbol density threshold.
        - Concatenated Word Filter:
            - Targets long tokens that appear to be multiple words joined without spaces
              (e.g., CamelCaseOrPascalCaseStrings).
            - Behavior Toggle: Option to remove these tokens entirely or abbreviate them
              (e.g., "First...Last").
            - Sensitivity Controls: Min token length to check, min internal sub-words
              to trigger the action.
        - Symbol-Enclosed Word Filter:
            - Removes words surrounded by non-alphanumeric symbols (e.g., *word*, _text_).
            - Sensitivity Control: Max number of symbols to consider on each side of the word.
        - Custom Regex Filter:
            - Allows users to input a custom regular expression.
            - Modes: "Remove segments matching regex" or "Keep only segments matching regex".
            - Toggle for case-sensitive matching.
            - Invalid regex patterns are flagged in the status bar.

4.  Core Processing Logic:
    - Text is extracted from files.
    - Enabled filters are applied sequentially to text segments based on the
      configured settings and their sensitivities.
    - Processed text is saved to a new output file.
    - Debug messages can be viewed in the console.
--------------------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk 
from tkinter import (Label, Frame, IntVar, BooleanVar, DoubleVar, Scale, Entry, Checkbutton, Spinbox, Button, Text, Scrollbar, PanedWindow, Radiobutton,
                     SUNKEN, W, X, Y, BOTTOM, LEFT, TOP, BOTH, HORIZONTAL, RIGHT, NW, DISABLED, NORMAL, END, RAISED, VERTICAL, StringVar)
import os
import re
import json
import traceback
from docx import Document
import PyPDF2

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    print("INFO: tkinterdnd2 imported successfully.")
    DND_AVAILABLE = True
except ImportError:
    print("WARNING: tkinterdnd2 library not found. Drag and drop will be disabled.")
    DND_AVAILABLE = False
    class TkinterDnD:
        @staticmethod
        def Tk(): return tk.Tk()
    DND_FILES = None

APP_VERSION = "1.5.4" # Custom output suffix, removed old suffix

# --- Default values ---
DEFAULT_MIN_WORDS_GENERAL = 11; DEFAULT_MIN_WORDS_SENTENCE = 5; DEFAULT_ALPHANUM_ENABLED = 1; DEFAULT_ALPHANUM_THRESHOLD = 0.75
DEFAULT_REMOVE_CODE_BLOCKS = 1; DEFAULT_MIN_CODE_KEYWORDS = 1; DEFAULT_MIN_CODE_SYMBOLS = 2; DEFAULT_MIN_WORDS_CODE_CHECK = 2; DEFAULT_CODE_SYMBOL_DENSITY = 0.20
DEFAULT_REMOVE_CONCAT_ENTIRELY = 1; DEFAULT_MIN_LEN_CONCAT_CHECK = 18; DEFAULT_MIN_SUB_WORDS_REPLACE = 3
DEFAULT_REMOVE_SYMBOL_ENCLOSED = 1; DEFAULT_MAX_SYMBOLS_AROUND = 3
DEFAULT_CUSTOM_REGEX_ENABLED = 0; DEFAULT_CUSTOM_REGEX_PATTERN = ""; DEFAULT_CUSTOM_REGEX_MODE = "remove_matches"; DEFAULT_CUSTOM_REGEX_CASE_SENSITIVE = 0
DEFAULT_CUSTOM_FILE_EXTENSIONS = ""
DEFAULT_OUTPUT_FILE_SUFFIX = "_processed" # New default for output suffix

CODE_KEYWORDS_LIST = {
    'var', 'let', 'const', 'function', 'return', 'this', 'class', 'constructor', 'new', 'Error', 'throw', 'if', 'else', 'for', 'while', 'switch', 'case', 'break', 'continue', 'try', 'catch', 'finally', 'import', 'export', 'super', 'extends', 'async', 'await', 'yield', 'true', 'false', 'null', 'undefined', 'typeof', 'instanceof', 'void', 'delete', 'prototype', 'static', 'get', 'set', 'document', 'window', 'JSON', 'Map', 'Promise', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Symbol', '=>', '...','require','module','exports','googletag','pubads','slot', 'addEventListener','removeEventListener','querySelector','getElementById','getElementsByClassName', 'createElement','appendChild','innerHTML','outerHTML','style','console','log','warn','info', 'ajax','fetch','XMLHttpRequest','jQuery','angular','react','vue', 'webpack', 'chunk', 'props', 'state'
}
CODE_SYMBOLS_SET = {
    '{', '}', '(', ')', '[', ']', ';', '=', '<', '>', '%', ':', '-', '+', '!', '#', '$', '&', '*', '|', '~', '`', '/', '\\', '@', '^', '_'
}

# --- Global Tkinter Variables ---
min_words_general_var, min_words_sentence_var, alphanum_filter_enabled_var, alphanum_threshold_var = (None,) * 4
remove_concat_entirely_var, remove_symbol_enclosed_var, remove_code_blocks_var = (None,) * 3
min_len_concat_check_var, min_sub_words_replace_var = (None,) * 2
max_symbols_around_var = None
min_code_keywords_var, min_code_symbols_var, min_words_code_check_var, code_symbol_density_var = (None,) * 4
custom_regex_enabled_var, custom_regex_pattern_var, custom_regex_mode_var, custom_regex_case_sensitive_var, \
custom_file_extensions_var, custom_output_suffix_var = (None,) * 6 # Added custom_output_suffix_var


SETTINGS_FILENAME = "text_extractor_settings.json"
SETTINGS_CONFIG = {
    'min_words_general_var': (tk.IntVar, DEFAULT_MIN_WORDS_GENERAL), 'min_words_sentence_var': (tk.IntVar, DEFAULT_MIN_WORDS_SENTENCE),
    'alphanum_filter_enabled_var': (tk.IntVar, DEFAULT_ALPHANUM_ENABLED), 'alphanum_threshold_var': (tk.DoubleVar, DEFAULT_ALPHANUM_THRESHOLD),
    'custom_file_extensions_var': (tk.StringVar, DEFAULT_CUSTOM_FILE_EXTENSIONS), # Moved up
    'custom_output_suffix_var': (tk.StringVar, DEFAULT_OUTPUT_FILE_SUFFIX),   # New setting
    'remove_code_blocks_var': (tk.IntVar, DEFAULT_REMOVE_CODE_BLOCKS), 'min_code_keywords_var': (tk.IntVar, DEFAULT_MIN_CODE_KEYWORDS),
    'min_code_symbols_var': (tk.IntVar, DEFAULT_MIN_CODE_SYMBOLS), 'min_words_code_check_var': (tk.IntVar, DEFAULT_MIN_WORDS_CODE_CHECK),
    'code_symbol_density_var': (tk.DoubleVar, DEFAULT_CODE_SYMBOL_DENSITY), 'remove_concat_entirely_var': (tk.IntVar, DEFAULT_REMOVE_CONCAT_ENTIRELY),
    'min_len_concat_check_var': (tk.IntVar, DEFAULT_MIN_LEN_CONCAT_CHECK), 'min_sub_words_replace_var': (tk.IntVar, DEFAULT_MIN_SUB_WORDS_REPLACE),
    'remove_symbol_enclosed_var': (tk.IntVar, DEFAULT_REMOVE_SYMBOL_ENCLOSED), 'max_symbols_around_var': (tk.IntVar, DEFAULT_MAX_SYMBOLS_AROUND),
    'custom_regex_enabled_var': (tk.IntVar, DEFAULT_CUSTOM_REGEX_ENABLED),
    'custom_regex_pattern_var': (tk.StringVar, DEFAULT_CUSTOM_REGEX_PATTERN),
    'custom_regex_mode_var': (tk.StringVar, DEFAULT_CUSTOM_REGEX_MODE),
    'custom_regex_case_sensitive_var': (tk.IntVar, DEFAULT_CUSTOM_REGEX_CASE_SENSITIVE),
}
g_test_pad_input_text = None; g_test_pad_output_text = None

def setup_variables(): # Unchanged
    for var_name, (var_type, default_value) in SETTINGS_CONFIG.items():
        if globals().get(var_name) is None or not isinstance(globals().get(var_name), var_type):
            globals()[var_name] = var_type(value=default_value)
def load_app_settings(): # Unchanged
    try:
        if os.path.exists(SETTINGS_FILENAME):
            with open(SETTINGS_FILENAME, 'r') as f: loaded_settings = json.load(f)
            for var_name, value in loaded_settings.items():
                var_object = globals().get(var_name)
                if var_name in SETTINGS_CONFIG and var_object: # Check if var_name is a known setting
                    try: var_object.set(value)
                    except Exception: print(f"WARN: Could not set {var_name} from settings file value '{value}'. Using its default.")
            print(f"INFO: Settings loaded from {SETTINGS_FILENAME}")
        else: print(f"INFO: No settings file ({SETTINGS_FILENAME}). Using compile-time defaults.")
    except Exception as e: print(f"ERROR: Failed to load settings: {e}. Using compile-time defaults.")
def save_app_settings(): # Unchanged
    settings_to_save = {}
    for var_name in SETTINGS_CONFIG.keys():
        var_object = globals().get(var_name)
        if var_object: settings_to_save[var_name] = var_object.get()
    if not settings_to_save: print("WARN: No settings found to save."); return
    try:
        with open(SETTINGS_FILENAME, 'w') as f: json.dump(settings_to_save, f, indent=4)
        print(f"INFO: Settings saved to {SETTINGS_FILENAME}")
    except Exception as e: print(f"ERROR: Failed to save settings: {e}")

# --- UI Element Creation Helpers (create_entry_setting updated slightly) ---
def create_entry_setting(parent, label_text, var, label_width=26, entry_width=30, indent=0, side_to_pack_label=LEFT, side_to_pack_entry=LEFT):
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=2)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=side_to_pack_label, padx=(indent,5))
    entry = Entry(frame, textvariable=var, width=entry_width)
    entry.pack(side=side_to_pack_entry, fill=X, expand=True, padx=5)
    return entry
def create_synchronized_setting(parent, label_text, var, from_, to, resolution=None, is_int=True, label_width=26, control_length=180): # Unchanged
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=2)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=LEFT)
    entry_var = tk.StringVar()
    entry = Entry(frame, textvariable=entry_var, width=7); entry.pack(side=RIGHT, padx=(0,5))
    scale = Scale(frame, variable=var, from_=from_, to=to, resolution=resolution if resolution else -1, orient=HORIZONTAL, length=control_length)
    scale.pack(side=RIGHT, fill=X, expand=True, padx=(5,5))
    def _update_entry_from_scale(*args):
        try: val = var.get(); entry_var.set(str(int(val)) if is_int else f"{val:.2f}")
        except tk.TclError: pass
    def _update_scale_from_entry(*args):
        try:
            val_str = entry_var.get();
            if not val_str: return
            new_val = int(val_str) if is_int else float(val_str)
            new_val = max(from_, min(to, new_val))
            if var.get() != new_val: var.set(new_val)
            current_var_val_for_entry = var.get()
            entry_var.set(str(int(current_var_val_for_entry)) if is_int else f"{current_var_val_for_entry:.2f}")
        except ValueError: _update_entry_from_scale()
        except tk.TclError: pass
    var.trace_add("write", _update_entry_from_scale); entry_var.trace_add("write", _update_scale_from_entry)
    _update_entry_from_scale()
    return frame
def create_spinbox_setting(parent, label_text, var, from_, to, label_width=24, spinbox_width=5, indent=15): # Unchanged
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=1)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=LEFT, padx=(indent, 5))
    spinbox = Spinbox(frame, from_=from_, to=to, textvariable=var, width=spinbox_width)
    spinbox.pack(side=LEFT, padx=5)
    return spinbox
def create_scale_setting(parent, label_text, var, from_, to, resolution, label_width=24, scale_length=150, indent=15): # Unchanged
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=1)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=LEFT, padx=(indent, 5))
    scale = Scale(frame, variable=var, from_=from_, to=to, resolution=resolution, orient=HORIZONTAL, length=scale_length)
    scale.pack(side=LEFT, fill=X, expand=True, padx=5)
    return scale
def toggle_controls_state(toggle_var, controls_list_of_widgets): # Unchanged
    new_state = NORMAL if toggle_var.get() == 1 else DISABLED
    for control_widget in controls_list_of_widgets:
        if control_widget and hasattr(control_widget, 'configure'):
            try: control_widget.configure(state=new_state)
            except tk.TclError as e: print(f"ERROR: TclError configuring widget {control_widget}: {e}")

def populate_settings_content(parent_scrollable_frame):
    setup_variables(); load_app_settings()
    column_container = ttk.Frame(parent_scrollable_frame); column_container.pack(fill=BOTH, expand=True)
    left_column = ttk.Frame(column_container, padding=(0,0,10,0)); left_column.pack(side=LEFT, fill=Y, expand=False, anchor=NW)
    right_column = ttk.Frame(column_container); right_column.pack(side=LEFT, fill=BOTH, expand=True, anchor=NW)

    # --- Left Column: Basic Filters & Custom Extensions & Output Suffix ---
    Label(left_column, text="Basic & File Settings:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    create_synchronized_setting(left_column, "Min Words (General Seq):", min_words_general_var, 1, 100, is_int=True)
    create_synchronized_setting(left_column, "Min Words (Punctuated Sent.):", min_words_sentence_var, 1, 50, is_int=True)
    filter_toggle_frame_left = Frame(left_column); filter_toggle_frame_left.pack(side=TOP, fill=X, padx=5, pady=2)
    Label(filter_toggle_frame_left, text="Alphanumeric Filter:", width=26, anchor=W).pack(side=LEFT)
    filter_status_label_var = tk.StringVar(value="ON" if alphanum_filter_enabled_var.get() == 1 else "OFF") 
    def update_alphanum_status_label(*args): filter_status_label_var.set("ON" if alphanum_filter_enabled_var.get() == 1 else "OFF")
    alphanum_filter_enabled_var.trace_add("write", update_alphanum_status_label)
    Scale(filter_toggle_frame_left, variable=alphanum_filter_enabled_var, from_=0, to=1, resolution=1, orient=HORIZONTAL, length=80, showvalue=0).pack(side=LEFT, padx=5)
    Label(filter_toggle_frame_left, textvariable=filter_status_label_var, width=5).pack(side=LEFT)
    update_alphanum_status_label()
    create_synchronized_setting(left_column, "Alphanumeric Threshold (if ON):", alphanum_threshold_var, 0.0, 1.0, resolution=0.01, is_int=False)
    
    create_entry_setting(left_column, "Custom Input Exts (,.ext):", custom_file_extensions_var, entry_width=35)
    # Label(left_column, text=" (Comma-sep, e.g., .log,.md. Processed as plain text)", font=('Helvetica', 8, 'italic')).pack(side=TOP, anchor=W, padx=10, pady=(0,5))
    create_entry_setting(left_column, "Output File Suffix:", custom_output_suffix_var, entry_width=35)
    Label(left_column, text=" (e.g., _cleaned. Will be 'filename<suffix>.txt')", font=('Helvetica', 8, 'italic')).pack(side=TOP, anchor=W, padx=10, pady=(0,5))


    # --- Right Column: Advanced Filters ---
    Label(right_column, text="Advanced Word/Block Filters:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    
    # Code Block Filter
    code_filter_frame_right = Frame(right_column); code_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=2)
    cb_remove_code = Checkbutton(code_filter_frame_right, text="Attempt to remove code-like blocks", variable=remove_code_blocks_var)
    cb_remove_code.pack(side=TOP, anchor=W); temp_code_controls = []
    temp_code_controls.append(create_spinbox_setting(code_filter_frame_right, "Min Keywords:", min_code_keywords_var, 0, 20))
    temp_code_controls.append(create_spinbox_setting(code_filter_frame_right, "Min Code Symbols:", min_code_symbols_var, 0, 30))
    temp_code_controls.append(create_spinbox_setting(code_filter_frame_right, "Min Words in Segment:", min_words_code_check_var, 1, 20))
    temp_code_controls.append(create_scale_setting(code_filter_frame_right, "Symbol Density >", code_symbol_density_var, 0.01, 0.5, 0.01, scale_length=120))
    remove_code_blocks_var.trace_add("write", lambda *args: toggle_controls_state(remove_code_blocks_var, temp_code_controls))
    toggle_controls_state(remove_code_blocks_var, temp_code_controls)

    # Concatenated Word Filter
    concat_filter_frame_right = Frame(right_column); concat_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=2)
    cb_remove_concat = Checkbutton(concat_filter_frame_right, text="Remove long concatenated words entirely", variable=remove_concat_entirely_var)
    cb_remove_concat.pack(side=TOP, anchor=W)
    create_spinbox_setting(concat_filter_frame_right, "Min Length to Check:", min_len_concat_check_var, 10, 50)
    create_spinbox_setting(concat_filter_frame_right, "Min Sub-Words to Act:", min_sub_words_replace_var, 2, 10)

    # Symbol-Enclosed Word Filter
    symbol_filter_frame_right = Frame(right_column); symbol_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=2)
    cb_remove_symbol = Checkbutton(symbol_filter_frame_right, text="Remove words enclosed by symbols", variable=remove_symbol_enclosed_var)
    cb_remove_symbol.pack(side=TOP, anchor=W); temp_symbol_controls = []
    temp_symbol_controls.append(create_spinbox_setting(symbol_filter_frame_right, "Max Symbols Around:", max_symbols_around_var, 1, 5))
    remove_symbol_enclosed_var.trace_add("write", lambda *args: toggle_controls_state(remove_symbol_enclosed_var, temp_symbol_controls))
    toggle_controls_state(remove_symbol_enclosed_var, temp_symbol_controls)

    # Custom Regex Filter
    regex_filter_frame_right = Frame(right_column, bd=1, relief=SUNKEN); regex_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=(10,2))
    Label(regex_filter_frame_right, text="Custom Regex Filter:", font=('Helvetica', 10, 'bold')).pack(side=TOP, anchor=NW, padx=5, pady=(0,2))
    cb_custom_regex = Checkbutton(regex_filter_frame_right, text="Enable Custom Regex Filter", variable=custom_regex_enabled_var)
    cb_custom_regex.pack(side=TOP, anchor=W, padx=5)
    
    temp_regex_controls = [] # List to hold controls to be enabled/disabled by cb_custom_regex
    temp_regex_controls.append(create_entry_setting(regex_filter_frame_right, "Regex Pattern:", custom_regex_pattern_var, entry_width=40, indent=15))
    
    regex_mode_frame = Frame(regex_filter_frame_right); regex_mode_frame.pack(side=TOP, fill=X, padx=(20,5))
    Label(regex_mode_frame, text="Mode:").pack(side=LEFT)
    rb_remove = Radiobutton(regex_mode_frame, text="Remove Matches", variable=custom_regex_mode_var, value="remove_matches")
    rb_remove.pack(side=LEFT, padx=2)
    rb_keep = Radiobutton(regex_mode_frame, text="Keep Matches Only", variable=custom_regex_mode_var, value="keep_matches")
    rb_keep.pack(side=LEFT, padx=2)
    temp_regex_controls.extend([regex_mode_frame]) # Add frame containing radio buttons for state control
                                                    # Or individually: temp_regex_controls.extend([rb_remove, rb_keep])

    cb_case_sensitive = Checkbutton(regex_filter_frame_right, text="Case Sensitive", variable=custom_regex_case_sensitive_var)
    cb_case_sensitive.pack(side=TOP, anchor=W, padx=20)
    temp_regex_controls.append(cb_case_sensitive)

    custom_regex_enabled_var.trace_add("write", lambda *args: toggle_controls_state(custom_regex_enabled_var, temp_regex_controls))
    toggle_controls_state(custom_regex_enabled_var, temp_regex_controls)


# --- Text Extraction and Processing Logic ---
def extract_text_from_txt(filepath): # ... (as in v1.5.2)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
    except Exception as e: print(f"Error reading .txt {filepath}: {e}"); status_label.config(text=f"Error reading .txt: {os.path.basename(filepath)}"); return ""
def extract_text_from_docx(filepath): # ... (as in v1.5.2)
    try:
        doc = Document(filepath); return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e: print(f"Error reading .docx {filepath}: {e}"); status_label.config(text=f"Error reading .docx: {os.path.basename(filepath)}"); return ""
def extract_text_from_pdf(filepath): # ... (as in v1.5.2)
    text = "";
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if reader.is_encrypted:
                try: reader.decrypt('')
                except: print(f"PDF Decryption failed for {filepath}"); status_label.config(text=f"PDF Decryption Failed: {os.path.basename(filepath)}"); return ""
            for page in reader.pages: page_text = page.extract_text(); text += (page_text + "\n") if page_text else ""
    except Exception as e: print(f"Error reading .pdf {filepath}: {e}"); status_label.config(text=f"Error reading .pdf: {os.path.basename(filepath)}"); return ""
    return text
def get_alphanumeric_ratio(text_segment): # ... (as in v1.5.2)
    if not text_segment: return 0.0
    alphanumeric_chars = sum(1 for char in text_segment if char.isalnum())
    return alphanumeric_chars / len(text_segment) if len(text_segment) > 0 else 0.0
def is_sentence_or_long_sequence(text_segment, min_words_general_sequence=6, min_words_punctuated_sentence=2): # ... (as in v1.5.2)
    stripped_segment = text_segment.strip();
    if not stripped_segment: return False
    words = stripped_segment.split(); word_count = len(words)
    if stripped_segment.endswith(('.', '!', '?')) and word_count >= min_words_punctuated_sentence: return True
    if word_count >= min_words_general_sequence: return True
    return False
def split_concatenated_token(token): # ... (as in v1.5.2)
    if not token: return []
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", token)
    s2 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s1)
    s3 = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", s2)
    s4 = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", s3)
    return [word for word in s4.split(' ') if word]
def is_code_like_segment(segment_text, words_in_segment, 
                         min_keywords, min_symbols, min_words_check, symbol_density_thresh): # ... (as in v1.5.2)
    if len(words_in_segment) < min_words_check: return False 
    keyword_hits = sum(1 for word in words_in_segment if word in CODE_KEYWORDS_LIST or word.lower() in CODE_KEYWORDS_LIST)
    segment_len = len(segment_text)
    if segment_len == 0: return False
    symbol_hits = sum(1 for char in segment_text if char in CODE_SYMBOLS_SET)
    current_symbol_density = symbol_hits / segment_len if segment_len > 0 else 0
    cond1 = (keyword_hits >= min_keywords and symbol_hits >= min_symbols)
    cond2 = (current_symbol_density > symbol_density_thresh)
    cond3 = (symbol_hits > (min_symbols * 2.5) and keyword_hits >= max(0, min_keywords // 2) )
    if cond1 or cond2 or cond3: return True
    return False

def process_text(full_text, min_words_general, min_words_sentence, 
                 apply_alphanumeric_filter, alphanumeric_threshold,
                 do_remove_concat_entirely, concat_min_len_check, concat_min_sub_words,
                 do_remove_symbol_enclosed, symbol_max_around,
                 do_remove_code_blocks, code_min_kw, code_min_sym, code_min_words_seg, code_sym_dens,
                 custom_regex_on, custom_regex_pat, custom_regex_mode_val, custom_regex_cs): # Updated signature
    extracted_content = []
    if not full_text or not full_text.strip(): return ""
    
    segments = re.split(r'\n\s*\n+|(?<=[.!?])\s+(?=(?:[A-Z0-9"]|$))', full_text)
    if not segments or (len(segments) == 1 and not segments[0].strip()): segments = full_text.splitlines()

    compiled_regex = None
    if custom_regex_on and custom_regex_pat: # Check if pattern is not empty
        try:
            flags = 0 if custom_regex_cs == 1 else re.IGNORECASE
            compiled_regex = re.compile(custom_regex_pat, flags)
        except re.error as e:
            print(f"ERROR: Invalid custom regex: '{custom_regex_pat}' - {e}")
            status_label.config(text=f"Error: Invalid custom regex!") # Update status bar
            # compiled_regex remains None, so this filter won't run

    final_segments_before_regex = [] # Segments after all other filters, before custom regex

    for segment_idx, segment in enumerate(segments):
        current_segment_to_check = segment.strip()
        if not current_segment_to_check: continue
        
        words_in_segment_original = current_segment_to_check.split(' ')

        if do_remove_code_blocks:
            if is_code_like_segment(current_segment_to_check, words_in_segment_original,
                                    code_min_kw, code_min_sym, code_min_words_seg, code_sym_dens):
                continue
        if apply_alphanumeric_filter:
            if get_alphanumeric_ratio(current_segment_to_check) < alphanumeric_threshold: continue
        if not is_sentence_or_long_sequence(current_segment_to_check, min_words_general, min_words_sentence):
            continue
            
        processed_words_for_segment = []
        for word_token in words_in_segment_original:
            token_processed_by_concat = False
            if len(word_token) >= concat_min_len_check:
                sub_words = split_concatenated_token(word_token)
                if len(sub_words) >= concat_min_sub_words:
                    if do_remove_concat_entirely: token_processed_by_concat = True 
                    else: processed_words_for_segment.append(f"{sub_words[0]}...{sub_words[-1]}"); token_processed_by_concat = True
            if not token_processed_by_concat: processed_words_for_segment.append(word_token)
        
        modified_segment = ' '.join(processed_words_for_segment)

        if do_remove_symbol_enclosed:
            max_sym = max(1, symbol_max_around)
            symbol_pattern = r'(?<!\w)\W{1,' + str(max_sym) + r'}\w+\W{1,' + str(max_sym) + r'}(?!\w)'
            modified_segment = re.sub(symbol_pattern, '', modified_segment)
            modified_segment = ' '.join(modified_segment.split())

        if modified_segment.strip():
            final_segments_before_regex.append(modified_segment)

    # Apply Custom Regex filter to the list of already filtered segments
    if custom_regex_on and compiled_regex: # Check compiled_regex is not None
        output_after_regex = []
        for segment in final_segments_before_regex:
            match_found = compiled_regex.search(segment)
            if custom_regex_mode_val == "remove_matches":
                if not match_found:
                    output_after_regex.append(segment)
            elif custom_regex_mode_val == "keep_matches":
                if match_found:
                    output_after_regex.append(segment)
        # print(f"DEBUG: Regex filter applied. Before: {len(final_segments_before_regex)}, After: {len(output_after_regex)}")
        extracted_content = output_after_regex
    else:
        extracted_content = final_segments_before_regex # No regex filter applied or pattern was bad
    
    return "\n\n".join(extracted_content)


# --- File Processing Orchestration (Updated to handle new settings) ---
def process_file(filepath):
    global status_label
    if not os.path.exists(filepath): status_label.config(text=f"Error: File not found {filepath}"); return
    
    filename_base, extension_raw = os.path.splitext(filepath)
    extension = extension_raw.lower()
    
    raw_custom_ext_str = custom_file_extensions_var.get()
    parsed_custom_extensions = []
    if raw_custom_ext_str:
        parsed_custom_extensions = [ext.strip().lower() for ext in raw_custom_ext_str.split(',') if ext.strip().startswith('.')]
    
    full_text = ""
    status_label.config(text=f"Processing: {os.path.basename(filepath)}..."); root.update_idletasks()
    
    if extension == '.txt' or extension in parsed_custom_extensions:
        full_text = extract_text_from_txt(filepath)
    elif extension == '.docx':
        full_text = extract_text_from_docx(filepath)
    elif extension == '.pdf':
        full_text = extract_text_from_pdf(filepath)
    else:
        status_label.config(text=f"Unsupported or unlisted file type: {extension} for {os.path.basename(filepath)}")
        return
        
    if not full_text or not full_text.strip(): status_label.config(text=f"No text extracted from {os.path.basename(filepath)}."); return
    
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    # print(f"DEBUG PARAMS from process_file: {params}")

    extracted_data = process_text(full_text, 
                                  params['min_words_general_var'], params['min_words_sentence_var'],
                                  True if params['alphanum_filter_enabled_var'] == 1 else False, params['alphanum_threshold_var'],
                                  True if params['remove_concat_entirely_var'] == 1 else False, 
                                  params['min_len_concat_check_var'], params['min_sub_words_replace_var'],
                                  True if params['remove_symbol_enclosed_var'] == 1 else False, 
                                  params['max_symbols_around_var'],
                                  True if params['remove_code_blocks_var'] == 1 else False, 
                                  params['min_code_keywords_var'], params['min_code_symbols_var'],
                                  params['min_words_code_check_var'], params['code_symbol_density_var'],
                                  True if params['custom_regex_enabled_var'] == 1 else False, # Custom Regex params
                                  params['custom_regex_pattern_var'],
                                  params['custom_regex_mode_var'],
                                  True if params['custom_regex_case_sensitive_var'] == 1 else False)
                                  
    if not extracted_data or not extracted_data.strip(): status_label.config(text=f"No content passed filters for {os.path.basename(filepath)}."); return
    
    # New output filename logic
    user_suffix = custom_output_suffix_var.get().strip()
    # Ensure there's always a suffix if user clears the field, to avoid potential overwrites of original .txt files
    actual_suffix = user_suffix if user_suffix else DEFAULT_OUTPUT_FILE_SUFFIX 
    
    output_filepath = filename_base + actual_suffix + ".txt" # Always output as .txt

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f_out: f_out.write(extracted_data)
        status_label.config(text=f"Successfully processed: {os.path.basename(filepath)}\nSaved to: {os.path.basename(output_filepath)}")
    except Exception as e: print(f"Error writing output {output_filepath}: {e}"); status_label.config(text=f"Error writing output for {os.path.basename(filepath)}: {e}")

# --- Filter Test Pad Functions (Updated to pass new params) ---
def process_pasted_text():
    global g_test_pad_input_text, g_test_pad_output_text
    if g_test_pad_input_text is None or g_test_pad_output_text is None: print("ERROR: Test pad text widgets not initialized."); return
    if 'min_words_general_var' not in globals() or globals()['min_words_general_var'] is None: setup_variables(); load_app_settings() 
    input_text = g_test_pad_input_text.get("1.0", tk.END).strip()
    if not input_text:
        g_test_pad_output_text.config(state=tk.NORMAL); g_test_pad_output_text.delete("1.0", tk.END)
        g_test_pad_output_text.insert(tk.END, "Input text is empty."); g_test_pad_output_text.config(state=tk.DISABLED)
        return
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    processed_output = process_text(input_text, 
                                  params['min_words_general_var'], params['min_words_sentence_var'],
                                  True if params['alphanum_filter_enabled_var'] == 1 else False, params['alphanum_threshold_var'],
                                  True if params['remove_concat_entirely_var'] == 1 else False, 
                                  params['min_len_concat_check_var'], params['min_sub_words_replace_var'],
                                  True if params['remove_symbol_enclosed_var'] == 1 else False, 
                                  params['max_symbols_around_var'],
                                  True if params['remove_code_blocks_var'] == 1 else False, 
                                  params['min_code_keywords_var'], params['min_code_symbols_var'],
                                  params['min_words_code_check_var'], params['code_symbol_density_var'],
                                  True if params['custom_regex_enabled_var'] == 1 else False, # Custom Regex params
                                  params['custom_regex_pattern_var'],
                                  params['custom_regex_mode_var'],
                                  True if params['custom_regex_case_sensitive_var'] == 1 else False)
    g_test_pad_output_text.config(state=tk.NORMAL); g_test_pad_output_text.delete("1.0", tk.END)
    g_test_pad_output_text.insert(tk.END, processed_output if processed_output else "<No content passed filters>")
    g_test_pad_output_text.config(state=tk.DISABLED)
def populate_test_pad_ui(parent_frame): # Unchanged from v1.5.2
    global g_test_pad_input_text, g_test_pad_output_text
    pw = PanedWindow(parent_frame, orient=HORIZONTAL, sashrelief=RAISED, sashwidth=6)
    pw.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)
    input_pane = Frame(pw, relief=SUNKEN, borderwidth=1);
    Label(input_pane, text="Paste Text to Test Here:", font=('Helvetica', 10, 'bold')).pack(side=TOP, anchor=W, padx=2, pady=2)
    input_text_sb = Scrollbar(input_pane, orient=VERTICAL)
    g_test_pad_input_text = Text(input_pane, wrap=tk.WORD, height=10, yscrollcommand=input_text_sb.set, undo=True)
    input_text_sb.config(command=g_test_pad_input_text.yview); input_text_sb.pack(side=RIGHT, fill=Y)
    g_test_pad_input_text.pack(side=LEFT, fill=BOTH, expand=True); pw.add(input_pane, stretch="always", width=350)
    output_pane = Frame(pw, relief=SUNKEN, borderwidth=1);
    Label(output_pane, text="Filtered Output:", font=('Helvetica', 10, 'bold')).pack(side=TOP, anchor=W, padx=2, pady=2)
    output_text_sb = Scrollbar(output_pane, orient=VERTICAL)
    g_test_pad_output_text = Text(output_pane, wrap=tk.WORD, height=10, state=tk.DISABLED, yscrollcommand=output_text_sb.set)
    output_text_sb.config(command=g_test_pad_output_text.yview); output_text_sb.pack(side=RIGHT, fill=Y)
    g_test_pad_output_text.pack(side=LEFT, fill=BOTH, expand=True); pw.add(output_pane, stretch="always", width=350)
    process_button = Button(parent_frame, text="Process Pasted Text (using current settings)", command=process_pasted_text)
    process_button.pack(side=TOP, pady=(0,5))

# --- Drop Handler (no changes) ---
def drop_handler(event): # ... (as in v1.5.2)
    filepaths_str = event.data;
    if not filepaths_str: return
    paths = []
    if filepaths_str.startswith('{') and filepaths_str.endswith('}'):
        path_segments = re.findall(r'\{[^{}]*\}|\S+', filepaths_str)
        for segment in path_segments: paths.append(segment[1:-1] if segment.startswith('{') and segment.endswith('}') else segment)
    elif '\n' in filepaths_str: paths = filepaths_str.splitlines()
    elif ' ' in filepaths_str and not os.path.exists(filepaths_str): paths = filepaths_str.split(' ')
    else: paths = [filepaths_str]
    actual_files = [p.strip() for p in paths if os.path.isfile(p.strip())]
    if not actual_files: status_label.config(text="Could not identify valid file(s) from drop."); return
    for filepath in actual_files: process_file(filepath)

# --- Main Application Setup (Mostly unchanged, ensures setup_variables and load_app_settings are called) ---
if DND_AVAILABLE: root = TkinterDnD.Tk()
else: root = tk.Tk()
root.title(f"File Text Extractor v{APP_VERSION}"); root.geometry("800x750") 
setup_variables() 
load_app_settings() 
def on_main_window_close(): save_app_settings(); root.destroy()
root.protocol("WM_DELETE_WINDOW", on_main_window_close)
print(f"--- Main GUI (v{APP_VERSION}) ---")
settings_container_frame = Frame(root, relief=SUNKEN, borderwidth=1); settings_container_frame.pack(side=TOP, fill=X, padx=7, pady=(7,0))
Label(settings_container_frame, text="Filter Settings", font=('Helvetica', 12, 'bold')).pack(anchor=W, padx=5, pady=(5,2))
settings_scroll_canvas_frame = Frame(settings_container_frame); settings_scroll_canvas_frame.pack(fill=X, expand=False)
settings_canvas = tk.Canvas(settings_scroll_canvas_frame, borderwidth=0, height=300)
settings_scrollbar = ttk.Scrollbar(settings_scroll_canvas_frame, orient="vertical", command=settings_canvas.yview)
scrollable_settings_content_frame = ttk.Frame(settings_canvas) 
scrollable_settings_content_frame.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
settings_canvas_window = settings_canvas.create_window((0, 0), window=scrollable_settings_content_frame, anchor="nw", tags="settings_content_window")
def _configure_settings_content_width(event): settings_canvas.itemconfig("settings_content_window", width=event.width)
settings_canvas.bind("<Configure>", _configure_settings_content_width, add='+') # Ensure it's added, not replacing other binds
settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
settings_canvas.pack(side=LEFT, fill=X, expand=True); settings_scrollbar.pack(side=RIGHT, fill=Y)
populate_settings_content(scrollable_settings_content_frame)
test_pad_container_frame = Frame(root, relief=SUNKEN, borderwidth=1); test_pad_container_frame.pack(side=TOP, fill=BOTH, expand=True, padx=7, pady=7)
populate_test_pad_ui(test_pad_container_frame)
file_processing_container_frame = Frame(root, relief=SUNKEN, borderwidth=1); file_processing_container_frame.pack(side=TOP, fill=X, padx=7, pady=(0,7))
Label(file_processing_container_frame, text="Process Files", font=('Helvetica', 12, 'bold')).pack(anchor=W, padx=5, pady=(5,2))
drop_target_label = Label(file_processing_container_frame,text="Drag and drop files here\n(Supports .txt, .docx, .pdf)",bg="lightgrey",relief=SUNKEN,height=5)
drop_target_label.pack(padx=10, pady=(0,10), fill=X, expand=False)
if DND_AVAILABLE and DND_FILES is not None:
    try:
        drop_target_label.drop_target_register(DND_FILES)
        drop_target_label.dnd_bind('<<Drop>>', drop_handler)
    except Exception as e: print(f"ERROR: Failed to register DND: {e}")
initial_status_text = f"Settings loaded. Ready. (v{APP_VERSION})"
if not DND_AVAILABLE: initial_status_text += " (DND Disabled)"
status_label = Label(root, text=initial_status_text, relief=SUNKEN, anchor=W)
status_label.pack(side=BOTTOM, fill=X)
root.mainloop()
