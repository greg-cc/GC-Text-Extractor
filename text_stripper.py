"""
Ver.1.7.4
GC Text Extractor v1.7.0 AI created explanation:

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
    - New: Can consolidate all processed output into a single file.
    - New: A configurable timeout for each file processing operation to prevent
      the application from hanging on large or corrupted files.

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
    1. Determines file type (.txt, .docx, .pdf, or custom user extension).
    2. Extracts raw full text content from the file.
    3. If "Extract URLs" setting is ON: Calls `extract_and_format_urls` on the
      `raw_full_text` to get a comprehensive list of all original URLs.
    4. Retrieves all current filter settings from the GUI.
    5. Calls `process_text(raw_full_text, all_current_settings...)` to get the
      cleaned `processed_text_content`.
    6. Appends the (optionally) extracted list of URLs from the raw text to the
      `processed_text_content`.
    7. If consolidation is OFF, constructs the output filename using the user-defined suffix
      and saves the combined data as a new .txt file.
    8. If consolidation is ON, appends the processed content to the single consolidated file.
    9. Updates the status bar with the result.

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
import tkinter.filedialog as filedialog
import os
import re
import json
import traceback
from docx import Document
import PyPDF2
# NEW IMPORTS FOR TIMEOUT FEATURE
import multiprocessing
import queue

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

APP_VERSION = "1.7.4" # Fixed multiprocessing NameError

# NEW DEFAULT VALUE
DEFAULT_FILE_PROCESSING_TIMEOUT = 60 # New: Default timeout for file processing in seconds

# --- Default values ---
DEFAULT_MIN_WORDS_GENERAL = 11; DEFAULT_MIN_WORDS_SENTENCE = 5
DEFAULT_ALPHANUM_ENABLED = 1; DEFAULT_ALPHANUM_THRESHOLD = 0.75
DEFAULT_ALPHANUM_MIN_LEN_FOR_RATIO = 5; DEFAULT_ALPHANUM_ABS_COUNT_FALLBACK = 15
DEFAULT_MAX_SEGMENT_LEN_BEFORE_NEWLINE_SPLIT = 350
DEFAULT_PARA_FILTER_ENABLED = 0; DEFAULT_PARA_MIN_SENTENCES = 2; DEFAULT_PARA_MIN_WORDS = 20; DEFAULT_PARA_MIN_AVG_LEN = 5; DEFAULT_PARA_MAX_AVG_LEN = 40
DEFAULT_REMOVE_CODE_BLOCKS = 1; DEFAULT_MIN_CODE_KEYWORDS = 1; DEFAULT_MIN_CODE_SYMBOLS = 2; DEFAULT_MIN_WORDS_CODE_CHECK = 2; DEFAULT_CODE_SYMBOL_DENSITY = 0.20
DEFAULT_REMOVE_CONCAT_ENTIRELY = 1; DEFAULT_MIN_LEN_CONCAT_CHECK = 18; DEFAULT_MIN_SUB_WORDS_REPLACE = 3
DEFAULT_REMOVE_SYMBOL_ENCLOSED = 1; DEFAULT_MAX_SYMBOLS_AROUND = 3
DEFAULT_CUSTOM_REGEX_ENABLED = 0; DEFAULT_CUSTOM_REGEX_PATTERN = ""; DEFAULT_CUSTOM_REGEX_MODE = "remove_matches"; DEFAULT_CUSTOM_REGEX_CASE_SENSITIVE = 0
DEFAULT_CUSTOM_FILE_EXTENSIONS = ""
DEFAULT_OUTPUT_FILE_SUFFIX = "_processed"
DEFAULT_EXTRACT_URLS_ENABLED = 0
DEFAULT_FILE_PROCESSING_MODE = "specified"
DEFAULT_INCLUDE_EXTENSIONS = ""
DEFAULT_IGNORE_EXTENSIONS = ".zip, .rar, .7z, .exe, .dll, .msi, .pkg, .dmg, .iso, .img, .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp, .mp3, .wav, .aac, .ogg, .mp4, .mov, .avi, .mkv, .webm"
DEFAULT_REMOVE_NUMBER_HEAVY = 0; DEFAULT_NUMBER_RATIO_THRESHOLD = 0.5; DEFAULT_MIN_DIGITS_FOR_RATIO_CHECK = 5; DEFAULT_MAX_CONSECUTIVE_DIGITS = 8; DEFAULT_MIN_WORDS_TO_EXEMPT_DIGITS = 10
DEFAULT_CODE_SYMBOL_MODE = "all"; DEFAULT_CODE_CUSTOM_SYMBOLS = ""
DEFAULT_HTML_STRIPPING_MODE = "strip_tags"
DEFAULT_CONSOLIDATE_OUTPUT = 0
DEFAULT_CONSOLIDATED_OUTPUT_FILENAME = "consolidated_output.txt"
DEFAULT_PAGES_TO_PROCESS = 0

CODE_KEYWORDS_LIST = {
    'var', 'let', 'const', 'function', 'return', 'this', 'class', 'constructor', 'new', 'Error', 'throw', 'if', 'else', 'for', 'while', 'switch', 'case',
'break', 'continue', 'try', 'catch', 'finally', 'import', 'export', 'super', 'extends', 'async', 'await', 'yield', 'true', 'false', 'null', 'undefined',
'typeof', 'instanceof', 'void', 'delete', 'prototype', 'static', 'get', 'set', 'document', 'window', 'JSON', 'Map', 'Promise', 'Object', 'Array',
'String', 'Number', 'Boolean', 'Symbol', '=>', '...','require','module','exports','googletag','pubads','slot',
'addEventListener','removeEventListener','querySelector','getElementById','getElementsByClassName',
'createElement','appendChild','innerHTML','outerHTML','style','console','log','warn','info',
'ajax','fetch','XMLHttpRequest','jQuery','angular','react','vue', 'webpack', 'chunk', 'props', 'state',
    'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'href', 'src', 'alt', 'class', 'id', 'rel',
'target', 'type', 'value', 'placeholder', 'html', 'head', 'body', 'title', 'meta', 'link', 'script'
}
CODE_SYMBOLS_SET = {
    '{', '}', '(', ')', '[', ']', ';', '=', '<', '>', '%', ':', '-', '+', '!', '#', '$', '&', '*', '|', '~', '`', '/', '\\', '@', '^', '_'
}

# --- Global Tkinter Variables ---
min_words_general_var, min_words_sentence_var = (None,) * 2
alphanum_filter_enabled_var, alphanum_threshold_var, \
    alnum_min_len_for_ratio_var, alnum_abs_count_fallback_var = (None,) * 4
max_segment_len_var = None
remove_concat_entirely_var, remove_symbol_enclosed_var, remove_code_blocks_var = (None,) * 3
min_len_concat_check_var, min_sub_words_replace_var = (None,) * 2
max_symbols_around_var = None
min_code_keywords_var, min_code_symbols_var, min_words_code_check_var, code_symbol_density_var = (None,) * 4
custom_regex_enabled_var, custom_regex_pattern_var, custom_regex_mode_var, custom_regex_case_sensitive_var, \
custom_file_extensions_var, custom_output_suffix_var, extract_urls_enabled_var, \
file_processing_mode_var, include_extensions_var, ignore_extensions_var = (None,) * 10
remove_number_heavy_var, number_ratio_threshold_var, min_digits_for_ratio_check_var, \
max_consecutive_digits_var, min_words_to_exempt_digits_var = (None,) * 5
code_symbol_mode_var, code_custom_symbols_var = (None,) * 2
para_filter_enabled_var, para_min_sentences_var, para_min_words_var, \
para_min_avg_len_var, para_max_avg_len_var = (None,) * 5
html_stripping_mode_var = None
consolidate_output_enabled_var = None
consolidated_output_filename_var = None
pages_to_process_var = None
# NEW GLOBAL VARIABLE
file_processing_timeout_var = None

SETTINGS_FILENAME = "text_extractor_settings.json"
SETTINGS_CONFIG = {
    'html_stripping_mode_var': (tk.StringVar, DEFAULT_HTML_STRIPPING_MODE),
    'min_words_general_var': (tk.IntVar, DEFAULT_MIN_WORDS_GENERAL),
    'min_words_sentence_var': (tk.IntVar, DEFAULT_MIN_WORDS_SENTENCE),
    'alphanum_filter_enabled_var': (tk.IntVar, DEFAULT_ALPHANUM_ENABLED),
    'alphanum_threshold_var': (tk.DoubleVar, DEFAULT_ALPHANUM_THRESHOLD),
    'alnum_min_len_for_ratio_var': (tk.IntVar, DEFAULT_ALPHANUM_MIN_LEN_FOR_RATIO),
    'alnum_abs_count_fallback_var': (tk.IntVar, DEFAULT_ALPHANUM_ABS_COUNT_FALLBACK),
    'max_segment_len_var': (tk.IntVar, DEFAULT_MAX_SEGMENT_LEN_BEFORE_NEWLINE_SPLIT),
    'para_filter_enabled_var': (tk.IntVar, DEFAULT_PARA_FILTER_ENABLED),
    'para_min_sentences_var': (tk.IntVar, DEFAULT_PARA_MIN_SENTENCES),
    'para_min_words_var': (tk.IntVar, DEFAULT_PARA_MIN_WORDS),
    'para_min_avg_len_var': (tk.IntVar, DEFAULT_PARA_MIN_AVG_LEN),
    'para_max_avg_len_var': (tk.IntVar, DEFAULT_PARA_MAX_AVG_LEN),
    'file_processing_mode_var': (tk.StringVar, DEFAULT_FILE_PROCESSING_MODE),
    'custom_file_extensions_var': (tk.StringVar, DEFAULT_CUSTOM_FILE_EXTENSIONS),
    'include_extensions_var': (tk.StringVar, DEFAULT_INCLUDE_EXTENSIONS),
    'ignore_extensions_var': (tk.StringVar, DEFAULT_IGNORE_EXTENSIONS),
    'custom_output_suffix_var': (tk.StringVar, DEFAULT_OUTPUT_FILE_SUFFIX),
    'extract_urls_enabled_var': (tk.IntVar, DEFAULT_EXTRACT_URLS_ENABLED),
    'remove_number_heavy_var': (tk.IntVar, DEFAULT_REMOVE_NUMBER_HEAVY),
    'number_ratio_threshold_var': (tk.DoubleVar, DEFAULT_NUMBER_RATIO_THRESHOLD),
    'min_digits_for_ratio_check_var': (tk.IntVar, DEFAULT_MIN_DIGITS_FOR_RATIO_CHECK),
    'max_consecutive_digits_var': (tk.IntVar, DEFAULT_MAX_CONSECUTIVE_DIGITS),
    'min_words_to_exempt_digits_var': (tk.IntVar, DEFAULT_MIN_WORDS_TO_EXEMPT_DIGITS),
    'remove_code_blocks_var': (tk.IntVar, DEFAULT_REMOVE_CODE_BLOCKS),
    'min_code_keywords_var': (tk.IntVar, DEFAULT_MIN_CODE_KEYWORDS),
    'min_code_symbols_var': (tk.IntVar, DEFAULT_MIN_CODE_SYMBOLS),
    'min_words_code_check_var': (tk.IntVar, DEFAULT_MIN_WORDS_CODE_CHECK),
    'code_symbol_density_var': (tk.DoubleVar, DEFAULT_CODE_SYMBOL_DENSITY),
    'code_symbol_mode_var': (tk.StringVar, DEFAULT_CODE_SYMBOL_MODE),
    'code_custom_symbols_var': (tk.StringVar, DEFAULT_CODE_CUSTOM_SYMBOLS),
    'remove_concat_entirely_var': (tk.IntVar, DEFAULT_REMOVE_CONCAT_ENTIRELY),
    'min_len_concat_check_var': (tk.IntVar, DEFAULT_MIN_LEN_CONCAT_CHECK),
    'min_sub_words_replace_var': (tk.IntVar, DEFAULT_MIN_SUB_WORDS_REPLACE),
    'remove_symbol_enclosed_var': (tk.IntVar, DEFAULT_REMOVE_SYMBOL_ENCLOSED),
    'max_symbols_around_var': (tk.IntVar, DEFAULT_MAX_SYMBOLS_AROUND),
    'custom_regex_enabled_var': (tk.IntVar, DEFAULT_CUSTOM_REGEX_ENABLED),
    'custom_regex_pattern_var': (tk.StringVar, DEFAULT_CUSTOM_REGEX_PATTERN),
    'custom_regex_mode_var': (tk.StringVar, DEFAULT_CUSTOM_REGEX_MODE),
    'custom_regex_case_sensitive_var': (tk.IntVar, DEFAULT_CUSTOM_REGEX_CASE_SENSITIVE),
    'consolidate_output_enabled_var': (tk.IntVar, DEFAULT_CONSOLIDATE_OUTPUT),
    'consolidated_output_filename_var': (tk.StringVar, DEFAULT_CONSOLIDATED_OUTPUT_FILENAME),
    'pages_to_process_var': (tk.IntVar, DEFAULT_PAGES_TO_PROCESS),
    # NEW SETTINGS ENTRY
    'file_processing_timeout_var': (tk.IntVar, DEFAULT_FILE_PROCESSING_TIMEOUT),
}
g_test_pad_input_text = None; g_test_pad_output_text = None
g_processed_files_list = [] # Global list to track files processed for consolidation

def setup_variables():
    for var_name, (var_type, default_value) in SETTINGS_CONFIG.items():
        if globals().get(var_name) is None or not isinstance(globals().get(var_name), var_type):
            globals()[var_name] = var_type(value=default_value)
def load_app_settings():
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
def save_app_settings():
    settings_to_save = {}
    for var_name in SETTINGS_CONFIG.keys():
        var_object = globals().get(var_name)
        if var_object: settings_to_save[var_name] = var_object.get()
    if not settings_to_save: print("WARN: No settings found to save."); return
    try:
        with open(SETTINGS_FILENAME, 'w') as f: json.dump(settings_to_save, f, indent=4)
        print(f"INFO: Settings saved to {SETTINGS_FILENAME}")
    except Exception as e: print(f"ERROR: Failed to save settings: {e}")

def create_entry_setting(parent, label_text, var, label_width=28, entry_width=30, indent=0, side_to_pack_label=LEFT, side_to_pack_entry=LEFT):
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=1)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=side_to_pack_label, padx=(indent,2))
    entry = Entry(frame, textvariable=var, width=entry_width)
    entry.pack(side=side_to_pack_entry, fill=X, expand=True, padx=2)
    return entry
def create_synchronized_setting(parent, label_text, var, from_, to, resolution=None, is_int=True, label_width=28, control_length=130, indent=0):
    frame = Frame(parent); frame.pack(side=TOP, fill=X, padx=5, pady=1)
    Label(frame, text=label_text, width=label_width, anchor=W).pack(side=LEFT, padx=(indent,2))
    entry_var = tk.StringVar()
    entry = Entry(frame, textvariable=entry_var, width=6); entry.pack(side=RIGHT, padx=(0,2))
    scale = Scale(frame, variable=var, from_=from_, to=to, resolution=resolution if resolution else -1, orient=HORIZONTAL, length=control_length)
    scale.pack(side=RIGHT, fill=X, expand=True, padx=(2,2))
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
    return [entry, scale]
def toggle_controls_state(toggle_var, controls_list_of_widgets):
    new_state = NORMAL if toggle_var.get() == 1 else DISABLED
    for control_widget in controls_list_of_widgets:
        if not (control_widget and hasattr(control_widget, 'configure')): continue
        if isinstance(control_widget, tk.Label): continue
        try:
            control_widget.configure(state=new_state)
        except tk.TclError as e:
            if isinstance(control_widget, (tk.Frame, ttk.Frame)) and \
               ("unknown option \"-state\"" in str(e).lower() or "invalid command name" in str(e).lower()):
                for child in control_widget.winfo_children():
                    if hasattr(child, 'configure') and not isinstance(child, tk.Label):
                        try: child.configure(state=new_state)
                        except tk.TclError: pass
            else:
                print(f"ERROR: TclError configuring widget {control_widget}: {e}")

def populate_settings_content(parent_scrollable_frame):
    col_padding = (0,0,5,0); col_padx = (0,2)
    column_container = ttk.Frame(parent_scrollable_frame); column_container.pack(fill=BOTH, expand=True)
    col1_frame = ttk.Frame(column_container, padding=col_padding); col1_frame.pack(side=LEFT, fill=Y, expand=True, anchor=NW, padx=col_padx)
    col2_frame = ttk.Frame(column_container, padding=col_padding); col2_frame.pack(side=LEFT, fill=Y, expand=True, anchor=NW, padx=col_padx)
    col3_frame = ttk.Frame(column_container, padding=col_padding); col3_frame.pack(side=LEFT, fill=Y, expand=True, anchor=NW, padx=col_padx)
    col4_frame = ttk.Frame(column_container, padding=col_padding); col4_frame.pack(side=LEFT, fill=Y, expand=True, anchor=NW, padx=col_padx)
    col5_frame = ttk.Frame(column_container); col5_frame.pack(side=LEFT, fill=Y, expand=True, anchor=NW, padx=col_padx)

    # --- Column 1: Pre-Filter & Basic Segmentation ---
    Label(col1_frame, text="Pre-Filter & Basic Segmentation:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)

    # New HTML Stripper
    html_frame = Frame(col1_frame); html_frame.pack(side=TOP, fill=X, padx=5)
    Label(html_frame, text="HTML Stripping Mode:", font=('Helvetica', 9, 'bold')).pack(side=TOP, anchor=W)
    Radiobutton(html_frame, text="Off", variable=html_stripping_mode_var, value="off").pack(side=TOP, anchor=W, padx=10)
    Radiobutton(html_frame, text="Strip Tags & Keep Content", variable=html_stripping_mode_var, value="strip_tags").pack(side=TOP, anchor=W, padx=10)
    Radiobutton(html_frame, text="Discard Segments w/ Tags", variable=html_stripping_mode_var, value="discard_segments").pack(side=TOP, anchor=W, padx=10)

    create_synchronized_setting(col1_frame, "Min Words (General Seq):", min_words_general_var, 1, 100, is_int=True, label_width=24, control_length=90)
    create_synchronized_setting(col1_frame, "Min Words (Punctuated Sent.):", min_words_sentence_var, 1, 50, is_int=True, label_width=24, control_length=90)
    create_synchronized_setting(col1_frame, "Max Chars Seg (for NL split):", max_segment_len_var, 50, 2000, resolution=50, is_int=True, label_width=24, control_length=90)

    # --- Column 2: Alphanum, Number & Paragraph Filters ---
    Label(col2_frame, text="Content Structure Filters:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    Label(col2_frame, text="Alphanumeric Filter:", font=('Helvetica', 9, 'bold')).pack(side=TOP, pady=(5,0), anchor=NW, padx=5)
    alphanum_main_frame = Frame(col2_frame); alphanum_main_frame.pack(side=TOP, fill=X, padx=5, pady=(0,0))
    alnum_sensitivity_controls = []
    def update_alphanum_status_and_toggle(*args): toggle_controls_state(alphanum_filter_enabled_var, alnum_sensitivity_controls)
    alphanum_filter_enabled_var.trace_add("write", update_alphanum_status_and_toggle)
    Checkbutton(alphanum_main_frame, text="Enable", variable=alphanum_filter_enabled_var).pack(side=LEFT, anchor=W)
    ratio_widgets = create_synchronized_setting(col2_frame, "Ratio Threshold:", alphanum_threshold_var, 0.0, 1.0, resolution=0.01, is_int=False, label_width=22, indent=10, control_length=90)
    alnum_sensitivity_controls.extend(ratio_widgets)
    alnum_sensitivity_controls.extend(create_synchronized_setting(col2_frame, "Min Seg Len for Ratio Test:", alnum_min_len_for_ratio_var, 1, 50, is_int=True, label_width=22, indent=10, control_length=90))
    alnum_sensitivity_controls.extend(create_synchronized_setting(col2_frame, "Abs Alnum Fallback Count:", alnum_abs_count_fallback_var, 0, 100, is_int=True, label_width=22, indent=10, control_length=90))
    update_alphanum_status_and_toggle()

    Label(col2_frame, text="Number-Heavy Filter:", font=('Helvetica', 9, 'bold')).pack(side=TOP, pady=(10,0), anchor=NW, padx=5)
    cb_remove_number_heavy = Checkbutton(col2_frame, text="Enable", variable=remove_number_heavy_var)
    cb_remove_number_heavy.pack(side=TOP, anchor=W, padx=15)
    temp_number_controls = []
    temp_number_controls.extend(create_synchronized_setting(col2_frame, "Digit Ratio Threshold >", number_ratio_threshold_var, 0.01, 1.0, resolution=0.01, is_int=False, label_width=22, indent=10, control_length=90))
    temp_number_controls.extend(create_synchronized_setting(col2_frame, "Min Digits for Ratio Chk:", min_digits_for_ratio_check_var, 1, 50, is_int=True, label_width=22, indent=10, control_length=90))
    temp_number_controls.extend(create_synchronized_setting(col2_frame, "Max Consecutive Digits:", max_consecutive_digits_var, 3, 50, is_int=True, label_width=22, indent=10, control_length=90))
    temp_number_controls.extend(create_synchronized_setting(col2_frame, "Min Words to Exempt:", min_words_to_exempt_digits_var, 0, 50, is_int=True, label_width=22, indent=10, control_length=90))
    remove_number_heavy_var.trace_add("write", lambda *args: toggle_controls_state(remove_number_heavy_var, temp_number_controls))
    toggle_controls_state(remove_number_heavy_var, temp_number_controls)

    Label(col2_frame, text="Paragraph Structure Filter:", font=('Helvetica', 9, 'bold')).pack(side=TOP, pady=(10,0), anchor=NW, padx=5)
    cb_para_filter = Checkbutton(col2_frame, text="Enable", variable=para_filter_enabled_var)
    cb_para_filter.pack(side=TOP, anchor=W, padx=15)
    para_sensitivity_controls = []
    para_sensitivity_controls.extend(create_synchronized_setting(col2_frame, "Min Sentences / Para:", para_min_sentences_var, 1, 20, is_int=True, label_width=22, indent=10, control_length=90))
    para_sensitivity_controls.extend(create_synchronized_setting(col2_frame, "Min Words / Para:", para_min_words_var, 1, 200, resolution=5, is_int=True, label_width=22, indent=10, control_length=90))
    para_sensitivity_controls.extend(create_synchronized_setting(col2_frame, "Min Avg Sent. Len:", para_min_avg_len_var, 1, 50, is_int=True, label_width=22, indent=10, control_length=90))
    para_sensitivity_controls.extend(create_synchronized_setting(col2_frame, "Max Avg Sent. Len:", para_max_avg_len_var, 5, 100, is_int=True, label_width=22, indent=10, control_length=90))
    para_filter_enabled_var.trace_add("write", lambda *args: toggle_controls_state(para_filter_enabled_var, para_sensitivity_controls))
    toggle_controls_state(para_filter_enabled_var, para_sensitivity_controls)


    # --- Column 3: File Handling & Output ---
    Label(col3_frame, text="File & Output Options:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    file_mode_frame = Frame(col3_frame); file_mode_frame.pack(side=TOP, fill=X, padx=5, pady=(5,0))
    Label(file_mode_frame, text="File Processing Mode:").pack(side=TOP, anchor=W)
    Radiobutton(file_mode_frame, text="Specified Exts Only", variable=file_processing_mode_var, value="specified").pack(side=TOP, anchor=W, padx=10)
    Radiobutton(file_mode_frame, text="Attempt All Dropped Files", variable=file_processing_mode_var, value="all_files").pack(side=TOP, anchor=W, padx=10)
    create_entry_setting(col3_frame, "Process ONLY these (,.ext):", include_extensions_var, entry_width=20, label_width=22)
    create_entry_setting(col3_frame, "Always IGNORE these (,.ext):", ignore_extensions_var, entry_width=20, label_width=22)
    create_entry_setting(col3_frame, "Additional Text Exts:", custom_file_extensions_var, entry_width=20, label_width=22)
    create_entry_setting(col3_frame, "Output File Suffix:", custom_output_suffix_var, entry_width=20, label_width=22)

    # New Pages to Process
    create_synchronized_setting(col3_frame, "Pages to Process (0=all):", pages_to_process_var, 0, 500, is_int=True, label_width=22, control_length=80)
    
    # NEW UI ELEMENT FOR TIMEOUT
    create_synchronized_setting(col3_frame, "File Processing Timeout (secs):", file_processing_timeout_var, 1, 300, is_int=True, label_width=22, control_length=80)


    # Updated URL extraction label
    url_frame = Frame(col3_frame); url_frame.pack(side=TOP, fill=X, padx=5, pady=(5,2))
    Checkbutton(url_frame, text="Extract and list URLs", variable=extract_urls_enabled_var).pack(side=LEFT, anchor=W)
    Label(url_frame, text="(Appends to output)", font=('Helvetica', 8, 'italic')).pack(side=LEFT, anchor=W, padx=(2,0))


    # New Consolidation Options
    Label(col3_frame, text="Consolidate Output:", font=('Helvetica', 9, 'bold')).pack(side=TOP, pady=(10,0), anchor=NW, padx=5)
    consolidation_controls = []
    cb_consolidate = Checkbutton(col3_frame, text="Enable Consolidation", variable=consolidate_output_enabled_var)
    cb_consolidate.pack(side=TOP, anchor=W, padx=15)
    consolidation_controls.append(create_entry_setting(col3_frame, "Consolidated Filename:", consolidated_output_filename_var, entry_width=20, label_width=22, indent=10))

    def update_consolidation_controls(*args):
        toggle_controls_state(consolidate_output_enabled_var, consolidation_controls)
    consolidate_output_enabled_var.trace_add("write", update_consolidation_controls)
    update_consolidation_controls()

    # --- Column 4: Advanced Filter Toggles & Basic Sensitivities ---
    Label(col4_frame, text="Advanced Toggles & Params:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    cb_remove_code = Checkbutton(col4_frame, text="Enable Code Block Filter", variable=remove_code_blocks_var)
    cb_remove_code.pack(side=TOP, anchor=W, padx=5)
    cb_remove_concat = Checkbutton(col4_frame, text="Concatenated: Remove Entirely", variable=remove_concat_entirely_var)
    cb_remove_concat.pack(side=TOP, anchor=W, padx=5)
    cb_remove_symbol = Checkbutton(col4_frame, text="Enable Symbol-Enclosed Filter", variable=remove_symbol_enclosed_var)
    cb_remove_symbol.pack(side=TOP, anchor=W, padx=5)
    cb_custom_regex = Checkbutton(col4_frame, text="Enable Custom Regex Filter", variable=custom_regex_enabled_var)
    cb_custom_regex.pack(side=TOP, anchor=W, padx=5, pady=(0,10))
    concat_sensitivity_label = Label(col4_frame, text="Concatenated Word Def.:", font=('Helvetica', 9, 'italic'))
    concat_sensitivity_label.pack(side=TOP, pady=(5,0), anchor=NW, padx=5)
    create_synchronized_setting(col4_frame, "Min Length to Check:", min_len_concat_check_var, 10, 50, is_int=True, label_width=20, control_length=80, indent=10)
    create_synchronized_setting(col4_frame, "Min Sub-Words to Act:", min_sub_words_replace_var, 2, 10, is_int=True, label_width=20, control_length=80, indent=10)
    symbol_sensitivity_label = Label(col4_frame, text="Symbol-Enclosed Sens.:", font=('Helvetica', 9, 'italic'))
    symbol_sensitivity_label.pack(side=TOP, pady=(5,0), anchor=NW, padx=5); temp_symbol_controls = []
    temp_symbol_controls.extend(create_synchronized_setting(col4_frame, "Max Symbols Around:", max_symbols_around_var, 1, 5, is_int=True, label_width=20, control_length=80, indent=10))
    remove_symbol_enclosed_var.trace_add("write", lambda *args: toggle_controls_state(remove_symbol_enclosed_var, temp_symbol_controls + [symbol_sensitivity_label]))
    toggle_controls_state(remove_symbol_enclosed_var, temp_symbol_controls + [symbol_sensitivity_label])

    # --- Column 5: Code Filter & Custom Regex Details ---
    Label(col5_frame, text="Code & Regex Details:", font=('Helvetica', 10, 'bold')).pack(side=TOP, pady=(5,2), anchor=NW, padx=5)
    code_sensitivity_label = Label(col5_frame, text="Code Filter Sensitivity:", font=('Helvetica', 9, 'italic'))
    code_sensitivity_label.pack(side=TOP, pady=(5,0), anchor=NW, padx=5); temp_code_controls = []
    temp_code_controls.extend(create_synchronized_setting(col5_frame, "Min Keywords:", min_code_keywords_var, 0, 20, is_int=True, label_width=20, control_length=80, indent=10))
    temp_code_controls.extend(create_synchronized_setting(col5_frame, "Min Code Symbols:", min_code_symbols_var, 0, 30, is_int=True, label_width=20, control_length=80, indent=10))
    temp_code_controls.extend(create_synchronized_setting(col5_frame, "Min Words in Seg:", min_words_code_check_var, 1, 20, is_int=True, label_width=20, control_length=80, indent=10))
    temp_code_controls.extend(create_synchronized_setting(col5_frame, "Symbol Density >", code_symbol_density_var, 0.01, 0.5, resolution=0.01, is_int=False, label_width=20, control_length=80, indent=10))
    code_symbol_mode_frame = Frame(col5_frame); code_symbol_mode_frame.pack(side=TOP, fill=X, padx=(15, 5))
    Label(code_symbol_mode_frame, text="Symbol Mode:").pack(side=TOP, anchor=W)
    Radiobutton(code_symbol_mode_frame, text="All Pre-def", variable=code_symbol_mode_var, value="all").pack(side=LEFT, padx=1)
    Radiobutton(code_symbol_mode_frame, text="Only These", variable=code_symbol_mode_var, value="only").pack(side=LEFT, padx=1)
    Radiobutton(code_symbol_mode_frame, text="All Except", variable=code_symbol_mode_var, value="except").pack(side=LEFT, padx=1)
    custom_symbol_entry = create_entry_setting(col5_frame, "Custom Symbols:", code_custom_symbols_var, entry_width=20, indent=15, label_width=20)
    temp_code_controls.extend([code_sensitivity_label, code_symbol_mode_frame, custom_symbol_entry])
    remove_code_blocks_var.trace_add("write", lambda *args: toggle_controls_state(remove_code_blocks_var, temp_code_controls))
    toggle_controls_state(remove_code_blocks_var, temp_code_controls)
    regex_sensitivity_label = Label(col5_frame, text="Custom Regex Details:", font=('Helvetica', 9, 'italic'))
    regex_sensitivity_label.pack(side=TOP, pady=(10,0), anchor=NW, padx=5); temp_regex_controls = []
    regex_entry_widget = create_entry_setting(col5_frame, "Regex Pattern:", custom_regex_pattern_var, entry_width=25, indent=15, label_width=20)
    temp_regex_controls.append(regex_entry_widget)
    regex_mode_frame_col5 = Frame(col5_frame); regex_mode_frame_col5.pack(side=TOP, fill=X, padx=(20,5))
    Label(regex_mode_frame_col5, text="Mode:").pack(side=LEFT)
    rb_remove = Radiobutton(regex_mode_frame_col5, text="Remove", variable=custom_regex_mode_var, value="remove_matches")
    rb_remove.pack(side=LEFT, padx=1); temp_regex_controls.append(rb_remove)
    rb_keep = Radiobutton(regex_mode_frame_col5, text="Keep Only", variable=custom_regex_mode_var, value="keep_matches")
    rb_keep.pack(side=LEFT, padx=1); temp_regex_controls.append(rb_keep)
    cb_case_sensitive = Checkbutton(regex_mode_frame_col5, text="Case Sens.", variable=custom_regex_case_sensitive_var)
    cb_case_sensitive.pack(side=LEFT, padx=2); temp_regex_controls.append(cb_case_sensitive)
    custom_regex_enabled_var.trace_add("write", lambda *args: toggle_controls_state(custom_regex_enabled_var, temp_regex_controls + [regex_sensitivity_label]))
    toggle_controls_state(custom_regex_enabled_var, temp_regex_controls + [regex_sensitivity_label])

# --- New function to consolidate files ---
def reset_consolidated_file():
    """Wipes the consolidated file, preparing for a new batch."""
    if consolidate_output_enabled_var.get() == 1:
        consolidated_filename = consolidated_output_filename_var.get().strip()
        if not consolidated_filename:
            status_label.config(text="Error: Consolidated filename cannot be empty.")
            return
        
        consolidated_output_path = os.path.join(os.getcwd(), consolidated_filename)
        
        try:
            with open(consolidated_output_path, 'w', encoding='utf-8') as outfile:
                outfile.write("") # Overwrite with empty content
        except Exception as e:
            status_label.config(text=f"Error resetting consolidated file: {e}")

def append_to_consolidated(filename, content):
    """Appends processed content from a single file to the consolidated output file."""
    if consolidate_output_enabled_var.get() == 1:
        consolidated_filename = consolidated_output_filename_var.get().strip()
        if not consolidated_filename:
            print("WARNING: Consolidated filename is empty. Skipping append.")
            return
            
        consolidated_output_path = os.path.join(os.getcwd(), consolidated_filename)
        
        try:
            with open(consolidated_output_path, 'a', encoding='utf-8') as outfile:
                outfile.write(f"--- Start of file: {os.path.basename(filename)} ---\n\n")
                outfile.write(content)
                outfile.write(f"\n\n--- End of file: {os.path.basename(filename)} ---\n\n")
        except Exception as e:
            print(f"ERROR: Failed to append to consolidated file: {e}")
            
# MOVE FUNCTIONS INSIDE HERE
def _process_file_in_process(filepath, params, result_queue):
    """
    A separate function to run file processing in a dedicated process.
    It puts a tuple of (status, data) into a queue for the main process.
    """
    # --- TROUBLESHOOTING START POINT 1: ENTRY AND FILE TYPE
    print(f"DEBUG: Starting worker process for: {filepath}")
    
    # Moved helper functions inside this function to ensure they are available to the new process
    def extract_text_from_txt(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
        except Exception as e:
            # print(f"Error reading .txt {filepath}: {e}")
            # status_label.config(text=f"Error reading .txt: {os.path.basename(filepath)}")
            return ""
    def extract_text_from_docx(filepath):
        try:
            doc = Document(filepath); return '\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            # print(f"Error reading .docx {filepath}: {e}")
            # status_label.config(text=f"Error reading .docx: {os.path.basename(filepath)}")
            return ""
    def extract_text_from_pdf(filepath, pages_to_process):
        text = ""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if reader.is_encrypted:
                    try: reader.decrypt('')
                    except:
                        # print(f"PDF Decryption failed for {filepath}")
                        # status_label.config(text=f"PDF Decryption Failed: {os.path.basename(filepath)}")
                        return ""
                    
                num_pages = len(reader.pages)
                
                # --- TROUBLESHOOTING START POINT 2: PAGE COUNT
                print(f"DEBUG: {os.path.basename(filepath)} has {num_pages} pages. Processing up to {pages_to_process if pages_to_process > 0 and pages_to_process < num_pages else num_pages} pages.")
                
                if pages_to_process > 0 and pages_to_process < num_pages:
                    page_limit = pages_to_process
                    # print(f"INFO: Processing first {page_limit} pages of {os.path.basename(filepath)}.")
                else:
                    page_limit = num_pages
                    # print(f"INFO: Processing all {num_pages} pages of {os.path.basename(filepath)}.")
                    
                for i in range(page_limit):
                    # --- TROUBLESHOOTING START POINT 3: PAGE-BY-PAGE PROGRESS
                    print(f"DEBUG: Attempting to extract page {i+1}...")
                    page_text = reader.pages[i].extract_text()
                    text += (page_text + "\n") if page_text else ""
        except Exception as e:
            # print(f"Error reading .pdf {filepath}: {e}")
            # status_label.config(text=f"Error reading .pdf: {os.path.basename(filepath)}")
            print(f"ERROR: Exception in extract_text_from_pdf: {e}")
            return ""
        return text
    def get_alphanumeric_ratio(text_segment):
        if not text_segment: return 0.0
        alphanumeric_chars = sum(1 for char in text_segment if char.isalnum())
        return alphanumeric_chars / len(text_segment) if len(text_segment) > 0 else 0.0
    def is_sentence_or_long_sequence(text_segment, min_words_general_sequence=6, min_words_punctuated_sentence=2):
        stripped_segment = text_segment.strip();
        if not stripped_segment: return False
        words = stripped_segment.split(); word_count = len(words)
        if stripped_segment.endswith(('.', '!', '?')) and word_count >= min_words_punctuated_sentence: return True
        if word_count >= min_words_general_sequence: return True
        return False
    def split_concatenated_token(token):
        if not token: return []
        s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", token)
        s2 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s1)
        s3 = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", s2)
        s4 = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", s3)
        return [word for word in s4.split(' ') if word]
    def is_code_like_segment(segment_text, words_in_segment,
                             min_keywords, min_symbols, min_words_check, symbol_density_thresh,
                             symbol_mode, custom_symbols):
        if len(words_in_segment) < min_words_check: return False
        
        active_symbol_set = CODE_SYMBOLS_SET
        if symbol_mode == "only":
            active_symbol_set = set(custom_symbols)
        elif symbol_mode == "except":
            active_symbol_set = CODE_SYMBOLS_SET - set(custom_symbols)
        
        keyword_hits = sum(1 for word in words_in_segment if word in CODE_KEYWORDS_LIST or word.lower() in CODE_KEYWORDS_LIST)
        segment_len = len(segment_text)
        if segment_len == 0: return False
        symbol_hits = sum(1 for char in segment_text if char in active_symbol_set)
        current_symbol_density = symbol_hits / segment_len if segment_len > 0 else 0
        cond1 = (keyword_hits >= min_keywords and symbol_hits >= min_symbols)
        cond2 = (current_symbol_density > symbol_density_thresh)
        cond3 = (symbol_hits > (min_symbols * 2.5) and keyword_hits >= max(0, min_keywords // 2) )
        if cond1 or cond2 or cond3: return True
        return False
    def is_number_heavy_segment(segment_text, words_in_segment,
                                ratio_thresh, min_digits_for_ratio,
                                max_consecutive, min_words_exempt):
        if min_words_exempt > 0 and len(words_in_segment) >= min_words_exempt:
            return False
        segment_len = len(segment_text)
        if segment_len == 0: return False
        if max_consecutive > 0:
            if re.search(r'\d{' + str(max_consecutive) + r',}', segment_text):
                return True
        if ratio_thresh > 0:
            digit_count = sum(1 for char in segment_text if char.isdigit())
            if digit_count >= min_digits_for_ratio:
                digit_ratio = digit_count / segment_len
                if digit_ratio > ratio_thresh:
                    return True
        return False
    def is_valid_paragraph(para_text, min_sentences, min_words, min_avg_len, max_avg_len):
        """
        New helper to check if a paragraph meets structural criteria.
        """
        # A simple way to count sentences is by splitting by standard terminators
        sentences = re.split(r'[.!?]+', para_text)
        sentences = [s.strip() for s in sentences if s.strip()] # Filter out empty strings
        num_sentences = len(sentences)
        if num_sentences < min_sentences:
            return False
        words_in_para = para_text.split()
        num_words = len(words_in_para)
        if num_words < min_words:
            return False
        if num_sentences > 0:
            avg_sentence_len = num_words / num_sentences
            if avg_sentence_len < min_avg_len or avg_sentence_len > max_avg_len:
                return False
        return True
    def process_text(full_text, params):
        extracted_content = []
        if not full_text or not full_text.strip(): return ""
        
        # --- STAGE 0: HTML Stripping (if enabled) ---
        html_mode = params['html_stripping_mode_var']
        if html_mode == "strip_tags":
            # Surgically remove tags, keep content
            processed_full_text = re.sub(r'<[^>]+>', ' ', full_text) # Replace tag with space
            processed_full_text = re.sub(r'\s+', ' ', processed_full_text).strip() # Normalize spaces
        elif html_mode == "discard_segments":
            # Pre-split by newline, then filter
            lines = full_text.splitlines()
            processed_full_text = "\n".join([line for line in lines if not re.search(r'<[^>]+>', line)])
        else: # Mode is "off"
            processed_full_text = full_text
        
        # --- STAGE 1: Paragraph Segmentation ---
        paragraphs = re.split(r'\n\s*\n+', processed_full_text.strip())
        
        segments_for_filtering = []
        for para_text in paragraphs:
            para_text_stripped = para_text.strip()
            if not para_text_stripped: continue
            if params['para_filter_enabled_var']:
                if not is_valid_paragraph(para_text_stripped,
                                         params['para_min_sentences_var'], params['para_min_words_var'],
                                         params['para_min_avg_len_var'], params['para_max_avg_len_var']):
                    continue # Discard this entire paragraph
            sentence_candidates = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'\(\[\d“‘\u2022\u2023\u25E6\u2043\u2219*+-])|(?<=[.!?])\s*$', para_text_stripped)
            for s_candidate in sentence_candidates:
                s_candidate_stripped = s_candidate.strip()
                if not s_candidate_stripped: continue
                split_by_newline_further = False
                if len(sentence_candidates) == 1 and "\n" in s_candidate_stripped:
                    split_by_newline_further = True
                elif len(s_candidate_stripped) > params['max_segment_len_var'] and "\n" in s_candidate_stripped:
                    split_by_newline_further = True
                if split_by_newline_further:
                    for line in s_candidate_stripped.splitlines():
                        if line.strip(): segments_for_filtering.append(line.strip())
                else:
                    segments_for_filtering.append(s_candidate_stripped)
        
        if not segments_for_filtering and processed_full_text.strip():
            segments_for_filtering = [line.strip() for line in processed_full_text.splitlines() if line.strip()]
        compiled_regex = None
        if params['custom_regex_enabled_var'] and params['custom_regex_pattern_var']:
            try:
                flags = 0 if params['custom_regex_case_sensitive_var'] else re.IGNORECASE
                compiled_regex = re.compile(params['custom_regex_pattern_var'], flags)
            except re.error as e:
                # print(f"ERROR: Invalid custom regex: '{params['custom_regex_pattern_var']}' - {e}")
                # status_label.config(text=f"Error: Invalid custom regex pattern!")
                pass
    
        final_segments_before_regex = []
        for segment_text in segments_for_filtering:
            current_segment_to_check = segment_text
            words_in_segment_original = current_segment_to_check.split(' ')
            if params['remove_code_blocks_var']:
                if is_code_like_segment(current_segment_to_check, words_in_segment_original,
                                         params['min_code_keywords_var'], params['min_code_symbols_var'],
                                         params['min_words_code_check_var'], params['code_symbol_density_var'],
                                         params['code_symbol_mode_var'], params['code_custom_symbols_var']):
                    continue
            if params['remove_number_heavy_var']:
                if is_number_heavy_segment(current_segment_to_check, words_in_segment_original,
                                           params['number_ratio_threshold_var'], params['min_digits_for_ratio_check_var'],
                                           params['max_consecutive_digits_var'], params['min_words_to_exempt_digits_var']):
                    continue
            if params['alphanum_filter_enabled_var']:
                passes_alnum_filter = True
                segment_len = len(current_segment_to_check)
                if segment_len == 0: passes_alnum_filter = False
                elif segment_len < params['alnum_min_len_for_ratio_var']:
                    num_alnum_chars_short_seg = sum(1 for char in current_segment_to_check if char.isalnum())
                    if num_alnum_chars_short_seg == 0: passes_alnum_filter = False
                else:
                    num_alnum_chars_long_seg = sum(1 for char in current_segment_to_check if char.isalnum())
                    ratio = num_alnum_chars_long_seg / segment_len if segment_len > 0 else 0.0
                    if ratio < params['alphanum_threshold_var']:
                        if num_alnum_chars_long_seg < params['alnum_abs_count_fallback_var']: passes_alnum_filter = False
                if not passes_alnum_filter: continue
            if not is_sentence_or_long_sequence(current_segment_to_check, params['min_words_general_var'], params['min_words_sentence_var']):
                continue
            processed_words_for_segment = []
            for word_token in words_in_segment_original:
                token_processed_by_concat = False
                if len(word_token) >= params['min_len_concat_check_var']:
                    sub_words = split_concatenated_token(word_token)
                    if len(sub_words) >= params['min_sub_words_replace_var']:
                        if params['remove_concat_entirely_var']: token_processed_by_concat = True
                        else: processed_words_for_segment.append(f"{sub_words[0]}...{sub_words[-1]}"); token_processed_by_concat = True
                if not token_processed_by_concat: processed_words_for_segment.append(word_token)
            modified_segment = ' '.join(processed_words_for_segment)
            if params['remove_symbol_enclosed_var']:
                max_sym = max(1, params['max_symbols_around_var'])
                symbol_pattern = r'(?<!\w)\W{1,' + str(max_sym) + r'}\w+\W{1,' + str(max_sym) + r'}(?!\w)'
                modified_segment = re.sub(symbol_pattern, '', modified_segment)
                modified_segment = ' '.join(modified_segment.split())
            if modified_segment.strip(): final_segments_before_regex.append(modified_segment)
    
        if params['custom_regex_enabled_var'] and compiled_regex:
            output_after_regex = []
            for segment in final_segments_before_regex:
                if params['custom_regex_mode_var'] == "remove_matches":
                    processed_segment = compiled_regex.sub('', segment).strip()
                    if processed_segment: output_after_regex.append(processed_segment)
                elif params['custom_regex_mode_var'] == "keep_matches":
                    if compiled_regex.search(segment): output_after_regex.append(segment)
            extracted_content = output_after_regex
        else:
            extracted_content = final_segments_before_regex
        return "\n\n".join(extracted_content)

    def extract_and_format_urls(text_content):
        if not text_content: return "", []
        # This pattern now better handles trailing punctuation and includes common TLDs
        url_pattern = re.compile(r'(?:(?:https?|ftp):\/\/|www\.)(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,12}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:[/?#][^\s"<>()\[\]]*|\b)', re.IGNORECASE)
        found_urls_raw = []
        for match in url_pattern.finditer(text_content):
            url = match.group(0)
            # Remove trailing punctuation that might be part of the sentence, not the URL
            cleaned_url = re.sub(r'[.,;!?"\')\]>]$', '', url)
            # Handle cases like 'word(url)'
            cleaned_url = re.sub(r'\(.*?\)', '', cleaned_url)
            # Deduplicate with normalization
            found_urls_raw.append(cleaned_url)

        if not found_urls_raw: return "", []
        
        normalized_for_dedupe = {}
        for url in found_urls_raw:
            u_stripped = url.strip().rstrip('/')
            u_lower_key = u_stripped.lower()
            if u_lower_key.startswith('www.') and not (u_lower_key.startswith('http://') or u_lower_key.startswith('https://')):
                u_display = 'http://' + u_stripped
                u_norm_key = 'http://' + u_lower_key
            else:
                u_display = u_stripped
                u_norm_key = u_lower_key
            if u_norm_key not in normalized_for_dedupe:
                normalized_for_dedupe[u_norm_key] = u_display
                
        unique_display_urls = sorted(list(normalized_for_dedupe.values()), key=lambda x: (x.lower(), x))
        
        if unique_display_urls:
            url_list_string = "\n\n--- Detected URLs ---\n" + "\n".join(unique_display_urls)
            return url_list_string, unique_display_urls
        return "", []

    try:
        filename_base, extension_raw = os.path.splitext(filepath)
        extension = extension_raw.lower()
        
        # --- TROUBLESHOOTING START POINT 4: CONFIRMING EXTENSION
        print(f"DEBUG: Identified file extension as '{extension}'")
        
        raw_full_text = ""
        
        pages_to_process = params['pages_to_process_var']
        
        # Determine which extractor to use
        if extension == '.docx':
            raw_full_text = extract_text_from_docx(filepath)
        elif extension == '.pdf':
            raw_full_text = extract_text_from_pdf(filepath, pages_to_process)
        elif extension == '.txt' or extension in {ext.strip().lower() for ext in params['custom_file_extensions_var'].split(',') if ext.strip().startswith('.')}:
            raw_full_text = extract_text_from_txt(filepath)
        elif {ext.strip().lower() for ext in params['include_extensions_var'].split(',')} and extension in {ext.strip().lower() for ext in params['include_extensions_var'].split(',')}:
            raw_full_text = extract_text_from_txt(filepath)
        elif params['file_processing_mode_var'] == "all_files":
            raw_full_text = extract_text_from_txt(filepath)
        else:
            result_queue.put(('skipped_unknown', f"Skipped (unknown extension '{extension}'): {os.path.basename(filepath)}."))
            return

        if not raw_full_text and os.path.getsize(filepath) > 0:
            result_queue.put(('error', f"No text could be extracted from {os.path.basename(filepath)}. Check file integrity or type."))
            return
        
        formatted_urls_from_raw = ""
        if params['extract_urls_enabled_var'] == 1 and raw_full_text is not None :
            formatted_urls_from_raw, _ = extract_and_format_urls(raw_full_text)
        
        processed_text_content = process_text(raw_full_text if raw_full_text is not None else "", params)
                                             
        final_output_data = processed_text_content
        if not final_output_data.strip() and formatted_urls_from_raw:
            final_output_data = "<No main content passed filters>" + formatted_urls_from_raw
        elif final_output_data.strip() and formatted_urls_from_raw:
            final_output_data += formatted_urls_from_raw
        
        if not final_output_data.strip():
            result_queue.put(('skipped_empty', f"No content passed filters or URLs found for {os.path.basename(filepath)}."))
            return
            
        result_queue.put(('success', final_output_data))
    
    except Exception as e:
        result_queue.put(('error', f"An unexpected error occurred during processing: {e}"))
        print(f"ERROR: Exception in worker process for {filepath}: {traceback.format_exc()}")
        
# MODIFIED PROCESS_FILE FUNCTION
def process_file(filepath):
    global status_label
    if not os.path.exists(filepath):
        status_label.config(text=f"Error: File not found {filepath}"); return
    
    filename_base, extension_raw = os.path.splitext(filepath)
    extension = extension_raw.lower()
    raw_ignore_ext_str = ignore_extensions_var.get()
    parsed_ignore_extensions = {ext.strip().lower() for ext in raw_ignore_ext_str.split(',') if ext.strip().startswith('.')}
    if extension in parsed_ignore_extensions:
        status_label.config(text=f"Skipped (ignored ext): {os.path.basename(filepath)}"); return
    
    status_label.config(text=f"Processing: {os.path.basename(filepath)}..."); root.update_idletasks()
    
    # Pass all settings to the worker process
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    
    result_queue = multiprocessing.Queue()
    worker_process = multiprocessing.Process(target=_process_file_in_process, args=(filepath, params, result_queue))
    worker_process.start()
    worker_process.join(timeout=file_processing_timeout_var.get())
    
    if worker_process.is_alive():
        worker_process.terminate()
        status_label.config(text=f"Error: Processing timed out for {os.path.basename(filepath)}.")
        return
        
    try:
        status, result = result_queue.get_nowait()
    except queue.Empty:
        status_label.config(text=f"Error: Worker process for {os.path.basename(filepath)} finished but returned no result.")
        return

    if status == 'error':
        status_label.config(text=f"Error processing {os.path.basename(filepath)}: {result}")
        return
    elif status == 'skipped_unknown' or status == 'skipped_empty':
        status_label.config(text=result)
        return

    # At this point, status must be 'success'
    final_output_data = result

    user_suffix = custom_output_suffix_var.get().strip()
    actual_suffix = user_suffix if user_suffix else DEFAULT_OUTPUT_FILE_SUFFIX
    output_filepath = filename_base + actual_suffix + ".txt"

    try:
        if consolidate_output_enabled_var.get() == 0:
            with open(output_filepath, 'w', encoding='utf-8') as f_out: f_out.write(final_output_data)
            status_label.config(text=f"Successfully processed: {os.path.basename(filepath)}\nSaved to: {os.path.basename(output_filepath)}")
        else:
            append_to_consolidated(filepath, final_output_data)
            status_label.config(text=f"Appended output from: {os.path.basename(filepath)} to consolidated file.")
    except Exception as e:
        print(f"Error writing output {output_filepath}: {e}")
        status_label.config(text=f"Error writing output for {os.path.basename(filepath)}: {e}")

# --- Filter Test Pad UI Population & Logic ---
def populate_test_pad_ui(parent_frame):
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
def process_pasted_text():
    global g_test_pad_input_text, g_test_pad_output_text
    if g_test_pad_input_text is None or g_test_pad_output_text is None: print("ERROR: Test pad text widgets not initialized."); return
    if 'min_words_general_var' not in globals() or globals()['min_words_general_var'] is None: setup_variables(); load_app_settings()
    raw_input_text = g_test_pad_input_text.get("1.0", tk.END).strip()
    if not raw_input_text:
        g_test_pad_output_text.config(state=tk.NORMAL); g_test_pad_output_text.delete("1.0", tk.END)
        g_test_pad_output_text.insert(tk.END, "Input text is empty."); g_test_pad_output_text.config(state=tk.DISABLED)
        return
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    processed_text_content = process_text(raw_input_text, params)
    
    final_display_output = processed_text_content if processed_text_content.strip() else "<No main content passed filters>"
    if extract_urls_enabled_var.get() == 1 and raw_input_text.strip() :
        formatted_urls_output, _ = extract_and_format_urls(raw_input_text)
        if formatted_urls_output: final_display_output += formatted_urls_output
    g_test_pad_output_text.config(state=tk.NORMAL); g_test_pad_output_text.delete("1.0", tk.END)
    g_test_pad_output_text.insert(tk.END, final_display_output)
    g_test_pad_output_text.config(state=tk.DISABLED)

# --- Drop Handler (unchanged) ---
def drop_handler(event):
    filepaths_str = event.data
    if not filepaths_str: return
    
    reset_consolidated_file()
    
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

# --- New Function to Process a File List ---
def process_file_list():
    global status_label
    file_path = filedialog.askopenfilename(
        title="Select a file list (.txt)",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_path:
        status_label.config(text="File selection canceled.")
        return
        
    reset_consolidated_file()

    status_label.config(text=f"Reading file list from {os.path.basename(file_path)}...")
    root.update_idletasks()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        status_label.config(text=f"Error reading list file: {e}")
        return
    if not file_paths:
        status_label.config(text="File list is empty or invalid.")
        return
    status_label.config(text=f"Processing {len(file_paths)} files from list...")
    root.update_idletasks()
    for path in file_paths:
        process_file(path)
    
    status_label.config(text=f"Finished processing all files from list.")

# --- Main Application Setup ---
if __name__ == "__main__":
    if DND_AVAILABLE: multiprocessing.freeze_support(); root = TkinterDnD.Tk()
    else: root = tk.Tk()
    root.title(f"File Text Extractor v{APP_VERSION}"); root.geometry("950x800")
    setup_variables(); load_app_settings()
    def on_main_window_close(): save_app_settings(); root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_main_window_close)
    settings_container_frame = Frame(root, relief=SUNKEN, borderwidth=1); settings_container_frame.pack(side=TOP, fill=X, padx=7, pady=(7,0))
    Label(settings_container_frame, text="Filter Settings", font=('Helvetica', 12, 'bold')).pack(anchor=W, padx=5, pady=(5,2))
    settings_scroll_canvas_frame = Frame(settings_container_frame); settings_scroll_canvas_frame.pack(fill=X, expand=False)
    settings_canvas = tk.Canvas(settings_scroll_canvas_frame, borderwidth=0, height=350)
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
    drop_target_label = Label(file_processing_container_frame,text="Supports any file - Drop here to process",bg="lightgrey",relief=SUNKEN,height=4)
    drop_target_label.pack(padx=10, pady=(0,10), fill=X, expand=False)
    if DND_AVAILABLE and DND_FILES is not None:
        try:
            drop_target_label.drop_target_register(DND_FILES)
            drop_target_label.dnd_bind('<<Drop>>', drop_handler)
        except Exception as e: print(f"ERROR: Failed to register DND: {e}")
    # New button for processing a file list
    process_list_button = Button(file_processing_container_frame, text="Process Files from List", command=process_file_list)
    process_list_button.pack(padx=10, pady=(0, 10), fill=X, expand=False)
    initial_status_text = f"Settings loaded. Ready. (v{APP_VERSION})"
    if not DND_AVAILABLE: initial_status_text += " (DND Disabled)"
    status_label = Label(root, text=initial_status_text, relief=SUNKEN, anchor=W)
    status_label.pack(side=BOTTOM, fill=X)
    root.mainloop()
