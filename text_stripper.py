"""
GC Text Extractor v1.6.3

Overall Description:
A desktop application built with Tkinter for extracting and filtering text from
various document types (.txt, .docx, .pdf, and user-defined). It provides a
unified, single-window graphical user interface with extensive, configurable
filters to clean and refine extracted text content. All settings are persistent
across sessions, saved to a local JSON file. The tool includes a test pad for
quick filter tuning and supports drag-and-drop file processing.

Key Features:
--------------------------------------------------------------------------------
1.  File Handling:
    - Extracts text from .txt, .docx (Microsoft Word), and .pdf files.
    - Supports user-defined custom file extensions (comma-separated, e.g., .log, .md)
      to be processed as plain text.
    - Drag-and-drop interface for easy file processing.
    - Customizable output file suffix (e.g., "_cleaned"), with output always as .txt.
    - Optional extraction, deduplication, and sorted listing of all URLs found in
      the original raw text, appended to the processed output.

2.  User Interface (Single Window, All Controls Visible):
    - Main sections for "Filter Settings," "Filter Test Pad," and "Process Files."
    - Scrollable "Filter Settings" area with a three-column layout for better visibility
      and reduced vertical scrolling.
    - Resizable "Filter Test Pad" with:
        - Input text area for pasting sample text.
        - "Process Pasted Text" button to apply current filters.
        - Output text area to display filtered results immediately, including any
          extracted URLs if the option is enabled.
    - Status bar for operational feedback, error messages, and version information.

3.  Filter Settings & Persistence:
    - All filter settings are automatically saved to `text_extractor_settings.json`
      on application close and loaded on startup.
    - Basic & Segmentation Filters:
        - Min Words (General Sequence): Slider & entry for minimum word count.
        - Min Words (Punctuated Sentences): Slider & entry for minimum word count.
        - Max Chars for Segment (before newline split): Spinbox to tune initial
          segmentation granularity for long lines with internal newlines.
        - Alphanumeric Filter:
            - Main Toggle (ON/OFF).
            - Sensitivity Controls (when ON):
                - Ratio Threshold: Slider & entry for the required alphanumeric ratio.
                - Min Segment Length for Ratio Test: Spinbox; segments shorter than this
                  bypass the ratio test (checked for at least one alphanumeric char).
                - Absolute Alphanum Fallback Count: Spinbox; rescues segments failing
                  the ratio test if they still have this many alphanumeric characters.
    - Advanced Word/Block Filters (each with enable/disable toggle and sensitivity controls):
        - Attempt to remove code-like blocks:
            - Identifies and removes segments resembling computer code/markup.
            - Sensitivity: Min keywords, min code symbols, min words in segment
              to check, and symbol density threshold.
        - Concatenated Word Filter:
            - Targets long tokens appearing as multiple words joined without spaces.
            - Behavior Toggle: Option to remove these tokens entirely or abbreviate
              (e.g., "First...Last").
            - Sensitivity: Min token length, min internal sub-words to trigger.
        - Symbol-Enclosed Word Filter:
            - Removes words surrounded by non-alphanumeric symbols (e.g., *word*).
            - Sensitivity: Max number of symbols around the word to consider.
        - Custom Regex Filter:
            - Allows user-defined regular expressions for advanced text manipulation.
            - Modes: "Remove segments matching regex" (surgically removes only matched
              parts) or "Keep only segments matching regex" (keeps whole segment if match found).
            - Toggle for case-sensitive matching.
            - Invalid regex patterns are flagged.

Core Processing Logic (Chronological Flow):
--------------------------------------------------------------------------------
A. File Processing (`process_file` function):
   1. Determines file type (.txt, .docx, .pdf, or custom extension).
   2. Extracts raw full text content from the file.
   3. If "Extract URLs" setting is ON: Calls `extract_and_format_urls` on the
      `raw_full_text` to get a comprehensive list of all original URLs.
   4. Retrieves all current filter settings from the GUI.
   5. Calls `process_text(raw_full_text, all_current_settings...)` to get the
      cleaned `processed_text_content`.
   6. Appends the (optionally) extracted list of URLs from the raw text to the
      `processed_text_content`.
   7. Constructs the output filename using the user-defined suffix (or a default)
      and saves the combined data as a new .txt file.
   8. Updates the status bar with the result.

B. Text Segmentation and Filtering (`process_text` function):
   0. Pre-segmentation (HTML/Tag Isolation):
      - Inserts newlines around detected HTML-like tags (`<...>`).
      - Normalizes multiple newlines to single newlines. This prepares the text for
        more effective subsequent segmentation, aiming to isolate tags from content.
   1. Initial Segmentation into `segments_for_filtering`:
      - Splits the pre-processed text by paragraph breaks (multiple newlines).
      - Within each paragraph, attempts to split by sentence-ending punctuation.
      - If a resulting "sentence" is very long (exceeds "Max Chars for Seg" setting) AND
        contains internal newlines, OR if a paragraph wasn't sentence-split but has
        internal newlines, it's further broken down by those newlines.
      - An ultimate fallback splits by all newlines if no segments were otherwise produced.
   2. Per-Segment Filtering Loop (for each segment from step 1):
      a. The segment is split into words for some checks.
      b. Code-like Block Filter: If enabled, `is_code_like_segment` is called. If True,
         the entire segment is discarded.
      c. Alphanumeric Filter: If enabled, the refined logic (using ratio threshold,
         min segment length for ratio test, and absolute alphanumeric fallback count)
         is applied. If the segment fails, it's discarded.
      d. Sentence/Length Filter: `is_sentence_or_long_sequence` checks if the segment
         meets the minimum word counts for general sequences or punctuated sentences.
         If it fails, it's discarded.
      e. Word-level Processing (on segments that passed above filters):
         i.  Concatenated Word Filter: Each word in the segment is checked. If it's
             a long concatenated token (based on length and internal sub-word count
             settings), it's either removed entirely or abbreviated, based on the toggle.
         ii. The segment is reconstructed from these (potentially modified) words.
      f. Symbol-Enclosed Word Filter: If enabled, applies a regex to the (potentially modified)
         segment to remove words enclosed by a specified number of symbols. Spaces are
         normalized after removal.
      g. If the segment still has content after these steps, it's collected.
   3. Final Custom Regex Filter Application:
      - If the Custom Regex Filter is enabled and the pattern is valid:
         - If mode is "Remove Matches": The regex pattern is used with `re.sub('', segment)`
           to surgically remove matching parts from each collected segment.
         - If mode is "Keep Matches Only": Only segments where the regex finds at least
           one match are kept.
      - Segments that are empty after regex processing (for "remove" mode) are discarded.
   4. The final list of processed segments is joined together with double newlines.

Key Function Details:
--------------------------------------------------------------------------------
- `setup_variables()`: Initializes all Tkinter variables for settings with default values.
- `load_app_settings()`: Loads settings from `SETTINGS_FILENAME` at startup, overriding defaults.
- `save_app_settings()`: Saves current settings to `SETTINGS_FILENAME` when the application closes.
- `populate_settings_content(parent_frame)`: Creates and lays out all the filter controls
  and their sensitivity adjusters in the scrollable settings area using a 3-column layout.
- `populate_test_pad_ui(parent_frame)`: Creates the input/output text areas and "Process"
  button for the Filter Test Pad.
- `process_pasted_text()`: Handles the logic for the Test Pad, using current settings.
- `extract_text_from_txt/docx/pdf(filepath)`: Perform raw text extraction from the respective file types.
- `get_alphanumeric_ratio(segment)`: Calculates the ratio of alphanumeric characters in a text segment.
- `is_sentence_or_long_sequence(segment, min_gen, min_punc)`: Checks if a segment meets
  minimum word count criteria for general or punctuated text.
- `split_concatenated_token(token)`: Attempts to break a single long token into conceptual
  sub-words based on camel/pascal casing and digit transitions.
- `is_code_like_segment(segment, words, params...)`: Uses heuristics (keywords, symbols, density)
  to determine if a segment is likely computer code or markup.
- `extract_and_format_urls(text_content)`: Finds all URLs in the given text,
  deduplicates them, sorts them, and returns a formatted list string.
- `process_text(full_text, all_settings...)`: The main engine that applies the entire
  segmentation and filtering pipeline described above.
- `process_file(filepath)`: Orchestrates file reading, URL extraction (from raw), calling
  `process_text`, and writing the final output (processed text + URL list) to a file.
- `drop_handler(event)`: Manages files dropped onto the GUI, passing them to `process_file`.
- `create_..._setting()` helpers: Utility functions to build common UI patterns for settings.
- `toggle_controls_state()`: Enables/disables sensitivity controls based on master filter toggles.
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
from urllib.parse import urlparse, urlunparse # For URL normalization (optional, can be simpler)

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    print("INFO: tkinterdnd2 imported successfully.")
    DND_AVAILABLE = True
except ImportError:
    print("WARNING: tkinterdnd2 library not found. Drag and drop will be disabled.")
    DND_AVAILABLE = False
    class TkinterDnD: # Mock class
        @staticmethod
        def Tk(): return tk.Tk()
    DND_FILES = None

APP_VERSION = "1.6.0" # Added URL extraction, deduplication, and sorting

# --- Default values (no change from 1.5.9) ---
DEFAULT_MIN_WORDS_GENERAL = 11; DEFAULT_MIN_WORDS_SENTENCE = 5
DEFAULT_ALPHANUM_ENABLED = 1; DEFAULT_ALPHANUM_THRESHOLD = 0.75 
DEFAULT_ALPHANUM_MIN_LEN_FOR_RATIO = 5; DEFAULT_ALPHANUM_ABS_COUNT_FALLBACK = 15
DEFAULT_MAX_SEGMENT_LEN_BEFORE_NEWLINE_SPLIT = 350 
DEFAULT_REMOVE_CODE_BLOCKS = 1; DEFAULT_MIN_CODE_KEYWORDS = 1; DEFAULT_MIN_CODE_SYMBOLS = 2; DEFAULT_MIN_WORDS_CODE_CHECK = 2; DEFAULT_CODE_SYMBOL_DENSITY = 0.20
DEFAULT_REMOVE_CONCAT_ENTIRELY = 1; DEFAULT_MIN_LEN_CONCAT_CHECK = 18; DEFAULT_MIN_SUB_WORDS_REPLACE = 3
DEFAULT_REMOVE_SYMBOL_ENCLOSED = 1; DEFAULT_MAX_SYMBOLS_AROUND = 3
DEFAULT_CUSTOM_REGEX_ENABLED = 0; DEFAULT_CUSTOM_REGEX_PATTERN = ""; DEFAULT_CUSTOM_REGEX_MODE = "remove_matches"; DEFAULT_CUSTOM_REGEX_CASE_SENSITIVE = 0
DEFAULT_CUSTOM_FILE_EXTENSIONS = ""
DEFAULT_OUTPUT_FILE_SUFFIX = "_processed"

CODE_KEYWORDS_LIST = { 
    'var', 'let', 'const', 'function', 'return', 'this', 'class', 'constructor', 'new', 'Error', 'throw', 'if', 'else', 'for', 'while', 'switch', 'case', 'break', 'continue', 'try', 'catch', 'finally', 'import', 'export', 'super', 'extends', 'async', 'await', 'yield', 'true', 'false', 'null', 'undefined', 'typeof', 'instanceof', 'void', 'delete', 'prototype', 'static', 'get', 'set', 'document', 'window', 'JSON', 'Map', 'Promise', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Symbol', '=>', '...','require','module','exports','googletag','pubads','slot', 'addEventListener','removeEventListener','querySelector','getElementById','getElementsByClassName', 'createElement','appendChild','innerHTML','outerHTML','style','console','log','warn','info', 'ajax','fetch','XMLHttpRequest','jQuery','angular','react','vue', 'webpack', 'chunk', 'props', 'state',
    'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'href', 'src', 'alt', 'class', 'id', 'rel', 'target', 'type', 'value', 'placeholder', 'html', 'head', 'body', 'title', 'meta', 'link', 'script'
}
CODE_SYMBOLS_SET = {
    '{', '}', '(', ')', '[', ']', ';', '=', '<', '>', '%', ':', '-', '+', '!', '#', '$', '&', '*', '|', '~', '`', '/', '\\', '@', '^', '_'
}

# --- Global Tkinter Variables (declarations unchanged) ---
min_words_general_var, min_words_sentence_var = (None,) * 2
alphanum_filter_enabled_var, alphanum_threshold_var, \
    alnum_min_len_for_ratio_var, alnum_abs_count_fallback_var = (None,) * 4
max_segment_len_var = None 
remove_concat_entirely_var, remove_symbol_enclosed_var, remove_code_blocks_var = (None,) * 3
min_len_concat_check_var, min_sub_words_replace_var = (None,) * 2
max_symbols_around_var = None
min_code_keywords_var, min_code_symbols_var, min_words_code_check_var, code_symbol_density_var = (None,) * 4
custom_regex_enabled_var, custom_regex_pattern_var, custom_regex_mode_var, custom_regex_case_sensitive_var, \
custom_file_extensions_var, custom_output_suffix_var = (None,) * 6

SETTINGS_FILENAME = "text_extractor_settings.json"
SETTINGS_CONFIG = {
    'min_words_general_var': (tk.IntVar, DEFAULT_MIN_WORDS_GENERAL), 
    'min_words_sentence_var': (tk.IntVar, DEFAULT_MIN_WORDS_SENTENCE),
    'alphanum_filter_enabled_var': (tk.IntVar, DEFAULT_ALPHANUM_ENABLED), 
    'alphanum_threshold_var': (tk.DoubleVar, DEFAULT_ALPHANUM_THRESHOLD),
    'alnum_min_len_for_ratio_var': (tk.IntVar, DEFAULT_ALPHANUM_MIN_LEN_FOR_RATIO), 
    'alnum_abs_count_fallback_var': (tk.IntVar, DEFAULT_ALPHANUM_ABS_COUNT_FALLBACK), 
    'max_segment_len_var': (tk.IntVar, DEFAULT_MAX_SEGMENT_LEN_BEFORE_NEWLINE_SPLIT),
    'custom_file_extensions_var': (tk.StringVar, DEFAULT_CUSTOM_FILE_EXTENSIONS),
    'custom_output_suffix_var': (tk.StringVar, DEFAULT_OUTPUT_FILE_SUFFIX),   
    'remove_code_blocks_var': (tk.IntVar, DEFAULT_REMOVE_CODE_BLOCKS), 
    'min_code_keywords_var': (tk.IntVar, DEFAULT_MIN_CODE_KEYWORDS),
    'min_code_symbols_var': (tk.IntVar, DEFAULT_MIN_CODE_SYMBOLS), 
    'min_words_code_check_var': (tk.IntVar, DEFAULT_MIN_WORDS_CODE_CHECK),
    'code_symbol_density_var': (tk.DoubleVar, DEFAULT_CODE_SYMBOL_DENSITY), 
    'remove_concat_entirely_var': (tk.IntVar, DEFAULT_REMOVE_CONCAT_ENTIRELY),
    'min_len_concat_check_var': (tk.IntVar, DEFAULT_MIN_LEN_CONCAT_CHECK), 
    'min_sub_words_replace_var': (tk.IntVar, DEFAULT_MIN_SUB_WORDS_REPLACE),
    'remove_symbol_enclosed_var': (tk.IntVar, DEFAULT_REMOVE_SYMBOL_ENCLOSED), 
    'max_symbols_around_var': (tk.IntVar, DEFAULT_MAX_SYMBOLS_AROUND),
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
                if var_name in SETTINGS_CONFIG and var_object: 
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

# --- UI Element Creation Helpers (unchanged) ---
def create_entry_setting(parent, label_text, var, label_width=28, entry_width=30, indent=0, side_to_pack_label=LEFT, side_to_pack_entry=LEFT):
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=2)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=side_to_pack_label, padx=(indent,5))
    entry = Entry(frame, textvariable=var, width=entry_width)
    entry.pack(side=side_to_pack_entry, fill=X, expand=True, padx=5)
    return entry
def create_synchronized_setting(parent, label_text, var, from_, to, resolution=None, is_int=True, label_width=28, control_length=180):
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
    return [frame.winfo_children()[0], entry, scale]
def create_spinbox_setting(parent, label_text, var, from_, to, label_width=26, spinbox_width=5, indent=15, increment=1):
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=1)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=LEFT, padx=(indent, 5))
    spinbox = Spinbox(frame, from_=from_, to=to, textvariable=var, width=spinbox_width, increment=increment)
    spinbox.pack(side=LEFT, padx=5)
    return spinbox
def create_scale_setting(parent, label_text, var, from_, to, resolution, label_width=26, scale_length=150, indent=15):
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=1)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=LEFT, padx=(indent, 5))
    scale = Scale(frame, variable=var, from_=from_, to=to, resolution=resolution, orient=HORIZONTAL, length=scale_length)
    scale.pack(side=LEFT, fill=X, expand=True, padx=5)
    return scale
def toggle_controls_state(toggle_var, controls_list_of_widgets):
    new_state = NORMAL if toggle_var.get() == 1 else DISABLED
    for control_widget in controls_list_of_widgets:
        if control_widget and hasattr(control_widget, 'configure'):
            try: control_widget.configure(state=new_state)
            except tk.TclError as e: print(f"ERROR: TclError configuring widget {control_widget}: {e}")

def populate_settings_content(parent_scrollable_frame): # Unchanged
    column_container = ttk.Frame(parent_scrollable_frame); column_container.pack(fill=BOTH, expand=True)
    left_column = ttk.Frame(column_container, padding=(0,0,10,0)); left_column.pack(side=LEFT, fill=Y, expand=False, anchor=NW)
    right_column = ttk.Frame(column_container); right_column.pack(side=LEFT, fill=BOTH, expand=True, anchor=NW)
    Label(left_column, text="Basic, Segmentation & File Settings:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    create_synchronized_setting(left_column, "Min Words (General Seq):", min_words_general_var, 1, 100, is_int=True)
    create_synchronized_setting(left_column, "Min Words (Punctuated Sent.):", min_words_sentence_var, 1, 50, is_int=True)
    create_spinbox_setting(left_column, "Max Chars for Seg (b4 newline split):", max_segment_len_var, 50, 2000, increment=50, label_width=28, indent=0) 
    alphanum_main_frame = Frame(left_column); alphanum_main_frame.pack(side=TOP, fill=X, padx=5, pady=(5,2)) 
    Label(alphanum_main_frame, text="Alphanumeric Filter:", width=28, anchor=W).pack(side=LEFT)
    filter_status_label_var = tk.StringVar(value="ON" if alphanum_filter_enabled_var.get() == 1 else "OFF")
    alnum_sensitivity_controls = [] 
    def update_alphanum_status_and_toggle(*args):
        filter_status_label_var.set("ON" if alphanum_filter_enabled_var.get() == 1 else "OFF")
        toggle_controls_state(alphanum_filter_enabled_var, alnum_sensitivity_controls)
    alphanum_filter_enabled_var.trace_add("write", update_alphanum_status_and_toggle)
    Scale(alphanum_main_frame, variable=alphanum_filter_enabled_var, from_=0, to=1, resolution=1, orient=HORIZONTAL, length=80, showvalue=0).pack(side=LEFT, padx=5)
    Label(alphanum_main_frame, textvariable=filter_status_label_var, width=5).pack(side=LEFT)
    ratio_frame_parent = Frame(left_column); ratio_frame_parent.pack(fill=X, padx=(20,0)) 
    # create_synchronized_setting returns a list of [Label, Entry, Scale]
    ratio_widgets = create_synchronized_setting(ratio_frame_parent, "Ratio Threshold:", alphanum_threshold_var, 0.0, 1.0, resolution=0.01, is_int=False, label_width=26)
    alnum_sensitivity_controls.extend(ratio_widgets) # Add all created widgets to the list
    alnum_sensitivity_controls.append(create_spinbox_setting(left_column, "Min Seg Len for Ratio Test:", alnum_min_len_for_ratio_var, 1, 50, label_width=26, indent=20))
    alnum_sensitivity_controls.append(create_spinbox_setting(left_column, "Abs Alnum Fallback Count:", alnum_abs_count_fallback_var, 0, 100, label_width=26, indent=20))
    update_alphanum_status_and_toggle() 
    create_entry_setting(left_column, "Custom Input Exts (,.ext):", custom_file_extensions_var, entry_width=35, label_width=28)
    create_entry_setting(left_column, "Output File Suffix:", custom_output_suffix_var, entry_width=35, label_width=28)
    Label(left_column, text=" (e.g., _cleaned. Appended before final .txt ext)", font=('Helvetica', 8, 'italic')).pack(side=TOP, anchor=W, padx=10, pady=(0,5))
    Label(right_column, text="Advanced Word/Block Filters:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    code_filter_frame_right = Frame(right_column); code_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=2)
    cb_remove_code = Checkbutton(code_filter_frame_right, text="Attempt to remove code-like blocks", variable=remove_code_blocks_var)
    cb_remove_code.pack(side=TOP, anchor=W); temp_code_controls = []
    temp_code_controls.append(create_spinbox_setting(code_filter_frame_right, "Min Keywords:", min_code_keywords_var, 0, 20))
    temp_code_controls.append(create_spinbox_setting(code_filter_frame_right, "Min Code Symbols:", min_code_symbols_var, 0, 30))
    temp_code_controls.append(create_spinbox_setting(code_filter_frame_right, "Min Words in Segment:", min_words_code_check_var, 1, 20))
    temp_code_controls.append(create_scale_setting(code_filter_frame_right, "Symbol Density >", code_symbol_density_var, 0.01, 0.5, 0.01, scale_length=120))
    remove_code_blocks_var.trace_add("write", lambda *args: toggle_controls_state(remove_code_blocks_var, temp_code_controls))
    toggle_controls_state(remove_code_blocks_var, temp_code_controls)
    concat_filter_frame_right = Frame(right_column); concat_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=2)
    cb_remove_concat = Checkbutton(concat_filter_frame_right, text="Remove long concatenated words entirely", variable=remove_concat_entirely_var)
    cb_remove_concat.pack(side=TOP, anchor=W)
    create_spinbox_setting(concat_filter_frame_right, "Min Length to Check:", min_len_concat_check_var, 10, 50)
    create_spinbox_setting(concat_filter_frame_right, "Min Sub-Words to Act:", min_sub_words_replace_var, 2, 10)
    symbol_filter_frame_right = Frame(right_column); symbol_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=2)
    cb_remove_symbol = Checkbutton(symbol_filter_frame_right, text="Remove words enclosed by symbols", variable=remove_symbol_enclosed_var)
    cb_remove_symbol.pack(side=TOP, anchor=W); temp_symbol_controls = []
    temp_symbol_controls.append(create_spinbox_setting(symbol_filter_frame_right, "Max Symbols Around:", max_symbols_around_var, 1, 5))
    remove_symbol_enclosed_var.trace_add("write", lambda *args: toggle_controls_state(remove_symbol_enclosed_var, temp_symbol_controls))
    toggle_controls_state(remove_symbol_enclosed_var, temp_symbol_controls)
    regex_filter_frame_right = Frame(right_column, bd=1, relief=SUNKEN); regex_filter_frame_right.pack(side=TOP, fill=X, padx=5, pady=(10,2))
    Label(regex_filter_frame_right, text="Custom Regex Filter:", font=('Helvetica', 10, 'bold')).pack(side=TOP, anchor=NW, padx=5, pady=(0,2))
    cb_custom_regex = Checkbutton(regex_filter_frame_right, text="Enable Custom Regex Filter", variable=custom_regex_enabled_var)
    cb_custom_regex.pack(side=TOP, anchor=W, padx=5); temp_regex_controls = []
    regex_entry_widget = create_entry_setting(regex_filter_frame_right, "Regex Pattern:", custom_regex_pattern_var, entry_width=40, indent=15)
    temp_regex_controls.append(regex_entry_widget)
    regex_mode_frame = Frame(regex_filter_frame_right); regex_mode_frame.pack(side=TOP, fill=X, padx=(20,5))
    Label(regex_mode_frame, text="Mode:").pack(side=LEFT)
    rb_remove = Radiobutton(regex_mode_frame, text="Remove Matches", variable=custom_regex_mode_var, value="remove_matches")
    rb_remove.pack(side=LEFT, padx=2); temp_regex_controls.append(rb_remove)
    rb_keep = Radiobutton(regex_mode_frame, text="Keep Matches Only", variable=custom_regex_mode_var, value="keep_matches")
    rb_keep.pack(side=LEFT, padx=2); temp_regex_controls.append(rb_keep)
    cb_case_sensitive = Checkbutton(regex_filter_frame_right, text="Case Sensitive", variable=custom_regex_case_sensitive_var)
    cb_case_sensitive.pack(side=TOP, anchor=W, padx=20); temp_regex_controls.append(cb_case_sensitive)
    custom_regex_enabled_var.trace_add("write", lambda *args: toggle_controls_state(custom_regex_enabled_var, temp_regex_controls))
    toggle_controls_state(custom_regex_enabled_var, temp_regex_controls)


# --- Text Extraction and Processing Logic ---
def extract_text_from_txt(filepath): # Unchanged
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
    except Exception as e: print(f"Error reading .txt {filepath}: {e}"); status_label.config(text=f"Error reading .txt: {os.path.basename(filepath)}"); return ""
def extract_text_from_docx(filepath): # Unchanged
    try:
        doc = Document(filepath); return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e: print(f"Error reading .docx {filepath}: {e}"); status_label.config(text=f"Error reading .docx: {os.path.basename(filepath)}"); return ""
def extract_text_from_pdf(filepath): # Unchanged
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
def get_alphanumeric_ratio(text_segment): # Unchanged
    if not text_segment: return 0.0
    alphanumeric_chars = sum(1 for char in text_segment if char.isalnum())
    return alphanumeric_chars / len(text_segment) if len(text_segment) > 0 else 0.0
def is_sentence_or_long_sequence(text_segment, min_words_general_sequence=6, min_words_punctuated_sentence=2): # Unchanged
    stripped_segment = text_segment.strip();
    if not stripped_segment: return False
    words = stripped_segment.split(); word_count = len(words)
    if stripped_segment.endswith(('.', '!', '?')) and word_count >= min_words_punctuated_sentence: return True
    if word_count >= min_words_general_sequence: return True
    return False
def split_concatenated_token(token): # Unchanged
    if not token: return []
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", token)
    s2 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s1)
    s3 = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", s2)
    s4 = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", s3)
    return [word for word in s4.split(' ') if word]
def is_code_like_segment(segment_text, words_in_segment, 
                         min_keywords, min_symbols, min_words_check, symbol_density_thresh): # Unchanged
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
                 alnum_min_len_ratio_check, alnum_abs_fallback, 
                 do_remove_concat_entirely, concat_min_len_check, concat_min_sub_words,
                 do_remove_symbol_enclosed, symbol_max_around,
                 do_remove_code_blocks, code_min_kw, code_min_sym, code_min_words_seg, code_sym_dens,
                 custom_regex_on, custom_regex_pat, custom_regex_mode_val, custom_regex_cs,
                 max_segment_len_for_nl_split): # Unchanged (uses new params)
    
    extracted_content = []
    if not full_text or not full_text.strip(): return ""
    processed_full_text = re.sub(r'(<[^>]+>)', r'\n\1\n', full_text) 
    processed_full_text = re.sub(r'\s*\n\s*', '\n', processed_full_text).strip()
    paragraphs = re.split(r'\n{2,}', processed_full_text)
    segments_for_filtering = []
    for para_text in paragraphs:
        if not para_text.strip(): continue
        sentence_candidates = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'\(\[\d“‘\u2022\u2023\u25E6\u2043\u2219*+-])|(?<=[.!?])\s*$', para_text)
        for s_candidate in sentence_candidates:
            s_candidate_stripped = s_candidate.strip()
            if not s_candidate_stripped: continue
            split_by_newline_further = False
            if len(sentence_candidates) == 1 and s_candidate_stripped == para_text.strip() and "\n" in s_candidate_stripped:
                split_by_newline_further = True
            elif len(s_candidate_stripped) > max_segment_len_for_nl_split: # Use new setting
                if "\n" in s_candidate_stripped: # Only split if newlines are present
                    split_by_newline_further = True
            if split_by_newline_further:
                for line in s_candidate_stripped.splitlines():
                    if line.strip(): segments_for_filtering.append(line.strip())
            else:
                segments_for_filtering.append(s_candidate_stripped)
    if not segments_for_filtering and processed_full_text.strip():
        segments_for_filtering = [line.strip() for line in processed_full_text.splitlines() if line.strip()]

    compiled_regex = None
    if custom_regex_on and custom_regex_pat:
        try:
            flags = 0 if custom_regex_cs else re.IGNORECASE
            compiled_regex = re.compile(custom_regex_pat, flags)
        except re.error as e:
            print(f"ERROR: Invalid custom regex: '{custom_regex_pat}' - {e}")
            status_label.config(text=f"Error: Invalid custom regex pattern!")

    final_segments_before_regex = []
    for segment_text in segments_for_filtering: 
        current_segment_to_check = segment_text
        words_in_segment_original = current_segment_to_check.split(' ')
        if do_remove_code_blocks:
            if is_code_like_segment(current_segment_to_check, words_in_segment_original,
                                    code_min_kw, code_min_sym, code_min_words_seg, code_sym_dens):
                continue
        if apply_alphanumeric_filter: 
            passes_alnum_filter = True 
            segment_len = len(current_segment_to_check)
            if segment_len == 0: passes_alnum_filter = False
            elif segment_len < alnum_min_len_ratio_check: 
                num_alnum_chars_short_seg = sum(1 for char in current_segment_to_check if char.isalnum())
                if num_alnum_chars_short_seg == 0: passes_alnum_filter = False
            else: 
                num_alnum_chars_long_seg = sum(1 for char in current_segment_to_check if char.isalnum())
                ratio = num_alnum_chars_long_seg / segment_len if segment_len > 0 else 0.0
                if ratio < alphanumeric_threshold:
                    if num_alnum_chars_long_seg < alnum_abs_fallback: passes_alnum_filter = False
            if not passes_alnum_filter: continue
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
        if modified_segment.strip(): final_segments_before_regex.append(modified_segment)

    if custom_regex_on and compiled_regex:
        output_after_regex = []
        for segment in final_segments_before_regex:
            if custom_regex_mode_val == "remove_matches":
                processed_segment = compiled_regex.sub('', segment).strip() 
                if processed_segment: output_after_regex.append(processed_segment)
            elif custom_regex_mode_val == "keep_matches":
                if compiled_regex.search(segment): output_after_regex.append(segment)
        extracted_content = output_after_regex
    else:
        extracted_content = final_segments_before_regex
    return "\n\n".join(extracted_content)

# --- New Function: extract_and_format_urls ---
def extract_and_format_urls(text_content):
    """Extracts, deduplicates, sorts, and formats URLs from text."""
    # A fairly comprehensive regex for URLs
    url_pattern = re.compile(
        r'(?:(?:https?|ftp):\/\/|www\.)'  # Scheme or www
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)', re.IGNORECASE)
    
    found_urls = url_pattern.findall(text_content)
    
    if not found_urls:
        return "", []

    # Normalize for deduplication and sorting: lowercase, add http to www, strip trailing /
    normalized_for_dedupe = {} # Store original casing keyed by normalized version
    for url in found_urls:
        u_stripped = url.strip().rstrip('/')
        u_lower = u_stripped.lower()
        if u_lower.startswith('www.') and not u_lower.startswith('http'):
            u_norm_key = 'http://' + u_lower
            u_display = 'http://' + u_stripped
        else:
            u_norm_key = u_lower
            u_display = u_stripped
        
        if u_norm_key not in normalized_for_dedupe:
            normalized_for_dedupe[u_norm_key] = u_display # Keep first encountered casing

    unique_display_urls = sorted(list(normalized_for_dedupe.values()), key=lambda x: (x.lower(), x))

    if unique_display_urls:
        url_list_string = "\n\n--- Detected URLs ---\n" + "\n".join(unique_display_urls)
        return url_list_string, unique_display_urls
    return "", []

# --- File Processing Orchestration (MODIFIED to include URL extraction) ---
def process_file(filepath):
    global status_label
    if not os.path.exists(filepath): status_label.config(text=f"Error: File not found {filepath}"); return
    
    filename_base, extension_raw = os.path.splitext(filepath); extension = extension_raw.lower()
    raw_custom_ext_str = custom_file_extensions_var.get()
    parsed_custom_extensions = []
    if raw_custom_ext_str:
        parsed_custom_extensions = [ext.strip().lower() for ext in raw_custom_ext_str.split(',') if ext.strip().startswith('.')]
    full_text = ""; status_label.config(text=f"Processing: {os.path.basename(filepath)}..."); root.update_idletasks()
    
    if extension == '.txt' or extension in parsed_custom_extensions: full_text = extract_text_from_txt(filepath)
    elif extension == '.docx': full_text = extract_text_from_docx(filepath)
    elif extension == '.pdf': full_text = extract_text_from_pdf(filepath)
    else: status_label.config(text=f"Unsupported or unlisted file type: {extension}"); return
    if not full_text or not full_text.strip(): status_label.config(text=f"No text extracted from {os.path.basename(filepath)}."); return
    
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    
    processed_text_content = process_text(full_text, 
                                  params['min_words_general_var'], params['min_words_sentence_var'],
                                  True if params['alphanum_filter_enabled_var'] == 1 else False, 
                                  params['alphanum_threshold_var'],
                                  params['alnum_min_len_for_ratio_var'], 
                                  params['alnum_abs_count_fallback_var'], 
                                  True if params['remove_concat_entirely_var'] == 1 else False, 
                                  params['min_len_concat_check_var'], params['min_sub_words_replace_var'],
                                  True if params['remove_symbol_enclosed_var'] == 1 else False, 
                                  params['max_symbols_around_var'],
                                  True if params['remove_code_blocks_var'] == 1 else False, 
                                  params['min_code_keywords_var'], params['min_code_symbols_var'],
                                  params['min_words_code_check_var'], params['code_symbol_density_var'],
                                  True if params['custom_regex_enabled_var'] == 1 else False,
                                  params['custom_regex_pattern_var'],
                                  params['custom_regex_mode_var'],
                                  True if params['custom_regex_case_sensitive_var'] == 1 else False,
                                  params['max_segment_len_var'])
                                  
    if not processed_text_content or not processed_text_content.strip(): 
        status_label.config(text=f"No content passed filters for {os.path.basename(filepath)}."); return
    
    # Extract and append URLs
    formatted_urls, _ = extract_and_format_urls(processed_text_content) # Use the content that passed all filters
    final_output_data = processed_text_content + formatted_urls
    
    user_suffix = custom_output_suffix_var.get().strip()
    actual_suffix = user_suffix if user_suffix else DEFAULT_OUTPUT_FILE_SUFFIX 
    output_filepath = filename_base + actual_suffix + ".txt"
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f_out: f_out.write(final_output_data)
        status_label.config(text=f"Successfully processed: {os.path.basename(filepath)}\nSaved to: {os.path.basename(output_filepath)}")
        if formatted_urls:
            print(f"INFO: URLs extracted and appended to {os.path.basename(output_filepath)}")
    except Exception as e: print(f"Error writing output {output_filepath}: {e}"); status_label.config(text=f"Error writing output for {os.path.basename(filepath)}: {e}")

# --- Filter Test Pad Functions (MODIFIED to include URL extraction in display) ---
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
    
    processed_text_content = process_text(input_text, 
                                  params['min_words_general_var'], params['min_words_sentence_var'],
                                  True if params['alphanum_filter_enabled_var'] == 1 else False, 
                                  params['alphanum_threshold_var'],
                                  params['alnum_min_len_for_ratio_var'], 
                                  params['alnum_abs_count_fallback_var'], 
                                  True if params['remove_concat_entirely_var'] == 1 else False, 
                                  params['min_len_concat_check_var'], params['min_sub_words_replace_var'],
                                  True if params['remove_symbol_enclosed_var'] == 1 else False, 
                                  params['max_symbols_around_var'],
                                  True if params['remove_code_blocks_var'] == 1 else False, 
                                  params['min_code_keywords_var'], params['min_code_symbols_var'],
                                  params['min_words_code_check_var'], params['code_symbol_density_var'],
                                  True if params['custom_regex_enabled_var'] == 1 else False,
                                  params['custom_regex_pattern_var'],
                                  params['custom_regex_mode_var'],
                                  True if params['custom_regex_case_sensitive_var'] == 1 else False,
                                  params['max_segment_len_var'])
    
    final_display_output = processed_text_content if processed_text_content.strip() else "<No content passed filters>"
    if processed_text_content.strip(): # Only extract URLs if there's processed text
        formatted_urls, _ = extract_and_format_urls(processed_text_content)
        final_display_output += formatted_urls # Append URLs to the display

    g_test_pad_output_text.config(state=tk.NORMAL); g_test_pad_output_text.delete("1.0", tk.END)
    g_test_pad_output_text.insert(tk.END, final_display_output)
    g_test_pad_output_text.config(state=tk.DISABLED)

def populate_test_pad_ui(parent_frame): # Unchanged
    global g_test_pad_input_text, g_test_pad_output_text # ... (as in v1.5.5)
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

# --- Drop Handler (unchanged) ---
def drop_handler(event): # ... (as in v1.5.5)
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

# --- Main Application Setup (unchanged) ---
if DND_AVAILABLE: root = TkinterDnD.Tk()
else: root = tk.Tk()
root.title(f"File Text Extractor v{APP_VERSION}"); root.geometry("800x750") 
setup_variables(); load_app_settings() 
def on_main_window_close(): save_app_settings(); root.destroy()
root.protocol("WM_DELETE_WINDOW", on_main_window_close)
settings_container_frame = Frame(root, relief=SUNKEN, borderwidth=1); settings_container_frame.pack(side=TOP, fill=X, padx=7, pady=(7,0))
Label(settings_container_frame, text="Filter Settings", font=('Helvetica', 12, 'bold')).pack(anchor=W, padx=5, pady=(5,2))
settings_scroll_canvas_frame = Frame(settings_container_frame); settings_scroll_canvas_frame.pack(fill=X, expand=False) 
settings_canvas = tk.Canvas(settings_scroll_canvas_frame, borderwidth=0, height=300) 
settings_scrollbar = ttk.Scrollbar(settings_scroll_canvas_frame, orient="vertical", command=settings_canvas.yview)
scrollable_settings_content_frame = ttk.Frame(settings_canvas) 
scrollable_settings_content_frame.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))
settings_canvas_window = settings_canvas.create_window((0, 0), window=scrollable_settings_content_frame, anchor="nw", tags="settings_content_window")
def _configure_settings_content_width(event): settings_canvas.itemconfig("settings_content_window", width=event.width)
settings_canvas.bind("<Configure>", _configure_settings_content_width, add='+')
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
