import tkinter as tk
import customtkinter as ctk
from tkinter import (PanedWindow, SUNKEN, RAISED, VERTICAL, BOTH, X, Y, RIGHT, LEFT, TOP, BOTTOM, W, NW, END, DISABLED, NORMAL)
import tkinter.filedialog as filedialog
import os
import re
import json
import traceback
from docx import Document
import PyPDF2
import multiprocessing
import queue
import threading
from queue import Queue

# The tkinterdnd2 library is compatible with customtkinter
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
    # Define a custom CTk class that inherits from the DND root
    class CTkinterDnD(ctk.CTk, TkinterDnD.Tk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
except ImportError:
    print("WARNING: tkinterdnd2 library not found. Drag and drop will be disabled.")
    DND_AVAILABLE = False
    class CTkinterDnD(ctk.CTk): pass # Fallback class
    DND_FILES = None


APP_VERSION = "1.8.0" # Added Stop Button

# --- Default values ---
DEFAULT_PRE_FILTER_ENABLED = 1
DEFAULT_FILE_PROCESSING_TIMEOUT = 60
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
pre_filter_enabled_var = None
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
file_processing_timeout_var = None

SETTINGS_FILENAME = "text_extractor_settings.json"
SETTINGS_CONFIG = {
    'pre_filter_enabled_var': (tk.IntVar, DEFAULT_PRE_FILTER_ENABLED),
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
    'file_processing_timeout_var': (tk.IntVar, DEFAULT_FILE_PROCESSING_TIMEOUT),
}
g_test_pad_input_text = None; g_test_pad_output_text = None
g_processed_files_list = []
g_message_queue = Queue()
g_stop_event = threading.Event() # <<< CHANGE 1: The global stop flag
g_stop_button = None
status_log = None
root = None


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

def create_entry_setting(parent, label_text, var, label_width=28, entry_width=30, indent=0):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(side=TOP, fill=X, padx=5, pady=1)
    label = ctk.CTkLabel(frame, text=label_text, width=label_width*6, anchor=W, text_color="black")
    label.pack(side=LEFT, padx=(indent, 2))
    entry = ctk.CTkEntry(frame, textvariable=var, fg_color="white", text_color="black", border_color="black")
    entry.pack(side=LEFT, fill=X, expand=True, padx=2)
    return entry

def create_synchronized_setting(parent, label_text, var, from_, to, resolution=None, is_int=True, label_width=28, indent=0):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(side=TOP, fill=X, padx=5, pady=1)
    ctk.CTkLabel(frame, text=label_text, width=label_width*6, anchor=W, text_color="black").pack(side=LEFT, padx=(indent, 2))
    
    entry_var = tk.StringVar()
    entry = ctk.CTkEntry(frame, textvariable=entry_var, width=50, fg_color="white", text_color="black", border_color="black")
    entry.pack(side=RIGHT, padx=(0, 2))
    
    slider = ctk.CTkSlider(frame, variable=var, from_=from_, to=to,
                           fg_color="white", progress_color="black", button_color="black",
                           button_hover_color="black")
    if is_int:
        slider.configure(number_of_steps=to - from_)
    slider.pack(side=RIGHT, fill=X, expand=True, padx=(2, 2))

    def _update_entry_from_scale(*args):
        try:
            val = var.get()
            entry_var.set(str(int(val)) if is_int else f"{val:.2f}")
        except (tk.TclError, ValueError): pass

    def _update_scale_from_entry(*args):
        try:
            val_str = entry_var.get()
            if not val_str: return
            new_val = int(val_str) if is_int else float(val_str)
            new_val = max(from_, min(to, new_val))
            if var.get() != new_val: var.set(new_val)
            current_var_val_for_entry = var.get()
            entry_var.set(str(int(current_var_val_for_entry)) if is_int else f"{current_var_val_for_entry:.2f}")
        except (ValueError, tk.TclError): _update_entry_from_scale()
        
    var.trace_add("write", _update_entry_from_scale)
    entry_var.trace_add("write", _update_scale_from_entry)
    _update_entry_from_scale()
    return [entry, slider]

def log_message(message, level='status'):
    global status_log, root
    if status_log is None or not status_log.winfo_exists():
        print(f"LOG ({level}): {message}")
        return

    status_log.configure(state=NORMAL)
    if level == 'error':
        status_log.insert(END, f"ERROR: {message}\n", "error")
    else:
        status_log.insert(END, f"{message}\n")
    
    status_log.see(END)
    status_log.configure(state=DISABLED)
    if root:
        root.update_idletasks()

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
    sentences = re.split(r'[.!?]+', para_text)
    sentences = [s.strip() for s in sentences if s.strip()]
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
    if params.get('pre_filter_enabled_var', 1) == 0:
        return full_text
    if not full_text or not full_text.strip(): return ""
    html_mode = params['html_stripping_mode_var']
    if html_mode == "strip_tags":
        processed_full_text = re.sub(r'<.*?>', ' ', full_text)
        processed_full_text = re.sub(r'\s+', ' ', processed_full_text).strip()
    elif html_mode == "discard_segments":
        lines = full_text.splitlines()
        processed_full_text = "\n".join([line for line in lines if not re.search(r'<[^>]+>', line)])
    else:
        processed_full_text = full_text
    paragraphs = re.split(r'\n\s*\n+', processed_full_text.strip())
    segments_for_filtering = []
    for para_text in paragraphs:
        para_text_stripped = para_text.strip()
        if not para_text_stripped: continue
        if params['para_filter_enabled_var']:
            if not is_valid_paragraph(para_text_stripped,
                                      params['para_min_sentences_var'], params['para_min_words_var'],
                                      params['para_min_avg_len_var'], params['para_max_avg_len_var']):
                continue
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
        except re.error: pass
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


def reset_consolidated_file():
    if consolidate_output_enabled_var.get() == 1:
        consolidated_filename = consolidated_output_filename_var.get().strip()
        if not consolidated_filename:
            g_message_queue.put(('error', "Consolidated filename cannot be empty."))
            return
        consolidated_output_path = os.path.join(os.getcwd(), consolidated_filename)
        try:
            with open(consolidated_output_path, 'w', encoding='utf-8') as outfile:
                outfile.write("")
        except Exception as e:
            g_message_queue.put(('error', f"Error resetting consolidated file: {e}"))
def append_to_consolidated(filename, content):
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
def _process_file_in_process(filepath, params, result_queue):
    def extract_text_from_txt(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
        except Exception: return ""
    def extract_text_from_docx(filepath):
        try:
            doc = Document(filepath); return '\n'.join([para.text for para in doc.paragraphs])
        except Exception: return ""
    def extract_text_from_pdf(filepath, pages_to_process):
        text = ""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if reader.is_encrypted:
                    try: reader.decrypt('')
                    except: return ""
                num_pages = len(reader.pages)
                page_limit = pages_to_process if pages_to_process > 0 and pages_to_process < num_pages else num_pages
                for i in range(page_limit):
                    page_text = reader.pages[i].extract_text()
                    text += (page_text + "\n") if page_text else ""
        except Exception as e:
            print(f"ERROR: Exception in extract_text_from_pdf: {e}")
            return ""
        return text
    def extract_and_format_urls(text_content):
        if not text_content: return "", []
        url_pattern = re.compile(r'(?:(?:https?|ftp):\/\/|www\.)(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,12}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:[/?#][^\s"<>()\[\]]*|\b)', re.IGNORECASE)
        found_urls_raw = []
        for match in url_pattern.finditer(text_content):
            url = match.group(0)
            cleaned_url = re.sub(r'[.,;!?"\')\]>]$', '', url)
            cleaned_url = re.sub(r'\(.*?\)', '', cleaned_url)
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
        _, extension_raw = os.path.splitext(filepath)
        extension = extension_raw.lower()
        raw_full_text = ""
        pages_to_process = params['pages_to_process_var']
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
def _process_file_inner(filepath):
    if not os.path.exists(filepath):
        g_message_queue.put(('error', f"Error: File not found {filepath}"))
        return
    filename_base, extension_raw = os.path.splitext(filepath)
    extension = extension_raw.lower()
    raw_ignore_ext_str = ignore_extensions_var.get()
    parsed_ignore_extensions = {ext.strip().lower() for ext in raw_ignore_ext_str.split(',') if ext.strip().startswith('.')}
    if extension in parsed_ignore_extensions:
        g_message_queue.put(('status', f"Skipped (ignored ext): {os.path.basename(filepath)}"))
        return
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    result_queue = multiprocessing.Queue()
    worker_process = multiprocessing.Process(target=_process_file_in_process, args=(filepath, params, result_queue))
    worker_process.start()
    timeout_val = file_processing_timeout_var.get()
    status, result = None, None
    try:
        status, result = result_queue.get(timeout=timeout_val)
    except queue.Empty:
        g_message_queue.put(('error', f"Processing timed out for {os.path.basename(filepath)} (worker unresponsive)."))
        if worker_process.is_alive():
            worker_process.terminate()
    finally:
        worker_process.join()
    if status is None:
        return
    if status == 'error':
        g_message_queue.put(('error', f"Error processing {os.path.basename(filepath)}: {result}"))
        return
    elif status == 'skipped_unknown' or status == 'skipped_empty':
        g_message_queue.put(('status', result))
        return
    final_output_data = result
    user_suffix = custom_output_suffix_var.get().strip()
    actual_suffix = user_suffix if user_suffix else DEFAULT_OUTPUT_FILE_SUFFIX
    output_filepath = filename_base + actual_suffix + ".txt"
    try:
        if consolidate_output_enabled_var.get() == 0:
            with open(output_filepath, 'w', encoding='utf-8') as f_out: f_out.write(final_output_data)
            g_message_queue.put(('status', f"Successfully processed: {os.path.basename(filepath)}\nSaved to: {os.path.basename(output_filepath)}"))
        else:
            append_to_consolidated(filepath, final_output_data)
            g_message_queue.put(('status', f"Appended output from: {os.path.basename(filepath)} to consolidated file."))
    except Exception as e:
        g_message_queue.put(('error', f"Error writing output for {os.path.basename(filepath)}: {e}"))
def process_files_in_thread(filepaths):
    global g_stop_event
    total_files = len(filepaths)
    for i, filepath in enumerate(filepaths):
        # <<< CHANGE 4a: Check the stop flag before processing each file
        if g_stop_event.is_set():
            break
        
        file_number = i + 1
        g_message_queue.put(('status', f"Processing file {file_number} of {total_files}: {os.path.basename(filepath)}..."))
        try:
            _process_file_inner(filepath)
        except Exception as e:
            g_message_queue.put(('error', f"Critical error processing {os.path.basename(filepath)}: {e}"))

    # <<< CHANGE 4b: Add a final message indicating if the process was stopped or finished
    if g_stop_event.is_set():
        g_message_queue.put(('status', "Processing stopped by user."))
    else:
        g_message_queue.put(('status', f"Finished processing all {total_files} files."))

def check_for_updates():
    global g_stop_button
    while not g_message_queue.empty():
        try:
            msg_type, msg = g_message_queue.get_nowait()
            log_message(msg, level=msg_type)
            g_message_queue.task_done()
        except queue.Empty:
            break
            
    # <<< CHANGE 3b: Manage the button state after processing
    if 'processing_thread' in globals() and globals()['processing_thread'].is_alive():
        root.after(100, check_for_updates)
    else:
        # Once the thread is finished, disable the stop button
        if g_stop_button:
            g_stop_button.configure(state=DISABLED)

def process_file(filepaths):
    global g_processed_files_list, g_stop_button, g_stop_event
    if 'processing_thread' in globals() and globals()['processing_thread'].is_alive():
        log_message("A processing task is already running.", level='error')
        return
    
    # <<< CHANGE 3a: Reset the flag and enable the button before starting
    g_stop_event.clear()
    if g_stop_button:
        g_stop_button.configure(state=NORMAL)
        
    g_processed_files_list = filepaths
    reset_consolidated_file()
    globals()['processing_thread'] = threading.Thread(target=process_files_in_thread, args=(g_processed_files_list,))
    globals()['processing_thread'].daemon = True
    globals()['processing_thread'].start()
    root.after(100, check_for_updates)

def stop_processing():
    # <<< CHANGE 2: Function to be called by the stop button
    global g_stop_event, g_stop_button
    log_message("Stop request received. Finishing current file...")
    g_stop_event.set()
    if g_stop_button:
        g_stop_button.configure(state=DISABLED) # Prevent multiple clicks

def drop_handler(event):
    filepaths_str = event.data
    if not filepaths_str: return
    paths = []
    if filepaths_str.startswith('{') and filepaths_str.endswith('}'):
        path_segments = re.findall(r'\{[^{}]*\}|\S+', filepaths_str)
        for segment in path_segments: paths.append(segment[1:-1] if segment.startswith('{') and segment.endswith('}') else segment)
    elif '\n' in filepaths_str: paths = filepaths_str.splitlines()
    elif ' ' in filepaths_str and not os.path.exists(filepaths_str): paths = filepaths_str.split(' ')
    else: paths = [filepaths_str]
    actual_files = [p.strip() for p in paths if os.path.isfile(p.strip())]
    if not actual_files: log_message("Could not identify valid file(s) from drop.", level='error'); return
    process_file(actual_files)
def process_file_list():
    file_path = filedialog.askopenfilename(
        title="Select a file list (.txt)",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_path:
        log_message("File selection canceled.")
        return
    reset_consolidated_file()
    log_message(f"Reading file list from {os.path.basename(file_path)}...")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    except Exception as e:
        log_message(f"Error reading list file: {e}", level='error')
        return
    if not file_paths:
        log_message("File list is empty or invalid.", level='error')
        return
    log_message(f"Processing {len(file_paths)} files from list...")
    process_file(file_paths)


def populate_settings_content(parent_container):
    canvas = ctk.CTkCanvas(parent_container, highlightthickness=0, bg="white")
    v_scrollbar = ctk.CTkScrollbar(parent_container, orientation="vertical", command=canvas.yview,
                                   fg_color="white", button_color="black", button_hover_color="black")
    h_scrollbar = ctk.CTkScrollbar(parent_container, orientation="horizontal", command=canvas.xview,
                                   fg_color="white", button_color="black", button_hover_color="black")
    
    content_frame = ctk.CTkFrame(canvas, width=1150, fg_color="white")

    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def on_canvas_configure(event):
        if content_frame.winfo_width() < event.width:
             canvas.itemconfig(canvas_window, width=event.width)

    content_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)
    
    parent_container.grid_rowconfigure(0, weight=1)
    parent_container.grid_columnconfigure(0, weight=1)
    
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    content_frame.grid_columnconfigure((0, 1), weight=2)
    content_frame.grid_columnconfigure((2, 3, 4), weight=3)

    col_padx = (5, 5)
    col1_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    col2_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    col3_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    col4_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    col5_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

    col1_frame.grid(row=0, column=0, sticky="nsew", padx=col_padx, pady=5)
    col2_frame.grid(row=0, column=1, sticky="nsew", padx=col_padx, pady=5)
    col3_frame.grid(row=0, column=2, sticky="nsew", padx=col_padx, pady=5)
    col4_frame.grid(row=0, column=3, sticky="nsew", padx=col_padx, pady=5)
    col5_frame.grid(row=0, column=4, sticky="nsew", padx=col_padx, pady=5)

    def create_header(parent, text):
        ctk.CTkLabel(parent, text=text, font=("", 14, "bold"), text_color="black").pack(side=TOP, pady=(5, 5), anchor=NW, padx=5)

    create_header(col1_frame, "Pre-Filter & Basic Segmentation:")
    ctk.CTkCheckBox(col1_frame, text="Enable Pre-Filter / Segmentation", variable=pre_filter_enabled_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5, pady=(0, 5))
    ctk.CTkLabel(col1_frame, text="HTML Stripping Mode:", font=("", 12, "bold"), text_color="black").pack(side=TOP, anchor=W, padx=5, pady=(5,2))
    ctk.CTkRadioButton(col1_frame, text="Off", variable=html_stripping_mode_var, value="off", text_color="black", fg_color="black", border_color="black").pack(side=TOP, anchor=W, padx=15, pady=1)
    ctk.CTkRadioButton(col1_frame, text="Strip Tags & Keep Content", variable=html_stripping_mode_var, value="strip_tags", text_color="black", fg_color="black", border_color="black").pack(side=TOP, anchor=W, padx=15, pady=1)
    ctk.CTkRadioButton(col1_frame, text="Discard Segments w/ Tags", variable=html_stripping_mode_var, value="discard_segments", text_color="black", fg_color="black", border_color="black").pack(side=TOP, anchor=W, padx=15, pady=1)
    create_synchronized_setting(col1_frame, "Min Words (General Seq):", min_words_general_var, 1, 100, is_int=True, label_width=24)
    create_synchronized_setting(col1_frame, "Min Words (Punctuated Sent.):", min_words_sentence_var, 1, 50, is_int=True, label_width=24)
    create_synchronized_setting(col1_frame, "Max Chars Seg (for NL split):", max_segment_len_var, 50, 2000, is_int=True, label_width=24)

    create_header(col2_frame, "Content Structure Filters:")
    ctk.CTkLabel(col2_frame, text="Alphanumeric Filter:", font=("", 12, "bold"), text_color="black").pack(side=TOP, pady=(5,0), anchor=NW, padx=5)
    ctk.CTkCheckBox(col2_frame, text="Enable", variable=alphanum_filter_enabled_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=15, pady=(2,5))
    create_synchronized_setting(col2_frame, "Ratio Threshold:", alphanum_threshold_var, 0.0, 1.0, is_int=False, label_width=22, indent=10)
    create_synchronized_setting(col2_frame, "Min Seg Len for Ratio Test:", alnum_min_len_for_ratio_var, 1, 50, is_int=True, label_width=22, indent=10)
    create_synchronized_setting(col2_frame, "Abs Alnum Fallback Count:", alnum_abs_count_fallback_var, 0, 100, is_int=True, label_width=22, indent=10)
    ctk.CTkLabel(col2_frame, text="Number-Heavy Filter:", font=("", 12, "bold"), text_color="black").pack(side=TOP, pady=(10,0), anchor=NW, padx=5)
    ctk.CTkCheckBox(col2_frame, text="Enable", variable=remove_number_heavy_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=15, pady=(2,5))
    create_synchronized_setting(col2_frame, "Digit Ratio Threshold >", number_ratio_threshold_var, 0.01, 1.0, is_int=False, label_width=22, indent=10)
    create_synchronized_setting(col2_frame, "Min Digits for Ratio Chk:", min_digits_for_ratio_check_var, 1, 50, is_int=True, label_width=22, indent=10)
    
    create_header(col3_frame, "File & Output Options:")
    ctk.CTkLabel(col3_frame, text="File Processing Mode:", text_color="black").pack(side=TOP, anchor=W, padx=5)
    ctk.CTkRadioButton(col3_frame, text="Specified Exts Only", variable=file_processing_mode_var, value="specified", text_color="black", fg_color="black", border_color="black").pack(side=TOP, anchor=W, padx=15, pady=1)
    ctk.CTkRadioButton(col3_frame, text="Attempt All Dropped Files", variable=file_processing_mode_var, value="all_files", text_color="black", fg_color="black", border_color="black").pack(side=TOP, anchor=W, padx=15, pady=1)
    create_entry_setting(col3_frame, "Process ONLY these (,.ext):", include_extensions_var, label_width=22)
    create_entry_setting(col3_frame, "Always IGNORE these (,.ext):", ignore_extensions_var, label_width=22)
    create_entry_setting(col3_frame, "Additional Text Exts:", custom_file_extensions_var, label_width=22)
    create_entry_setting(col3_frame, "Output File Suffix:", custom_output_suffix_var, label_width=22)
    create_synchronized_setting(col3_frame, "Pages to Process (0=all):", pages_to_process_var, 0, 500, is_int=True, label_width=22)
    create_synchronized_setting(col3_frame, "File Processing Timeout (secs):", file_processing_timeout_var, 1, 300, is_int=True, label_width=22)
    ctk.CTkCheckBox(col3_frame, text="Extract and list URLs (Appends to output)", variable=extract_urls_enabled_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5, pady=(5,2))
    ctk.CTkCheckBox(col3_frame, text="Enable Consolidation", variable=consolidate_output_enabled_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5, pady=(10,0))
    create_entry_setting(col3_frame, "Consolidated Filename:", consolidated_output_filename_var, label_width=22, indent=10)

    create_header(col4_frame, "Advanced Toggles & Params:")
    ctk.CTkCheckBox(col4_frame, text="Enable Code Block Filter", variable=remove_code_blocks_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5)
    ctk.CTkCheckBox(col4_frame, text="Concatenated: Remove Entirely", variable=remove_concat_entirely_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5)
    ctk.CTkCheckBox(col4_frame, text="Enable Symbol-Enclosed Filter", variable=remove_symbol_enclosed_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5)
    ctk.CTkCheckBox(col4_frame, text="Enable Custom Regex Filter", variable=custom_regex_enabled_var, text_color="black", border_color="black", checkmark_color="black").pack(side=TOP, anchor=W, padx=5, pady=(0,10))
    ctk.CTkLabel(col4_frame, text="Concatenated Word Def.:", font=("", 12, "italic"), text_color="black").pack(side=TOP, pady=(5,0), anchor=NW, padx=5)
    create_synchronized_setting(col4_frame, "Min Length to Check:", min_len_concat_check_var, 10, 50, is_int=True, label_width=20, indent=10)
    create_synchronized_setting(col4_frame, "Min Sub-Words to Act:", min_sub_words_replace_var, 2, 10, is_int=True, label_width=20, indent=10)
    ctk.CTkLabel(col4_frame, text="Symbol-Enclosed Sens.:", font=("", 12, "italic"), text_color="black").pack(side=TOP, pady=(5,0), anchor=NW, padx=5)
    create_synchronized_setting(col4_frame, "Max Symbols Around:", max_symbols_around_var, 1, 5, is_int=True, label_width=20, indent=10)
    
    create_header(col5_frame, "Code & Regex Details:")
    ctk.CTkLabel(col5_frame, text="Code Filter Sensitivity:", font=("", 12, "italic"), text_color="black").pack(side=TOP, pady=(5,0), anchor=NW, padx=5)
    create_synchronized_setting(col5_frame, "Min Keywords:", min_code_keywords_var, 0, 20, is_int=True, label_width=20, indent=10)
    create_synchronized_setting(col5_frame, "Min Code Symbols:", min_code_symbols_var, 0, 30, is_int=True, label_width=20, indent=10)
    create_synchronized_setting(col5_frame, "Min Words in Seg:", min_words_code_check_var, 1, 20, is_int=True, label_width=20, indent=10)
    create_synchronized_setting(col5_frame, "Symbol Density >", code_symbol_density_var, 0.01, 0.5, is_int=False, label_width=20, indent=10)
    ctk.CTkLabel(col5_frame, text="Symbol Mode:", text_color="black").pack(side=TOP, anchor=W, padx=15, pady=(5,0))
    radio_frame = ctk.CTkFrame(col5_frame, fg_color="transparent"); radio_frame.pack(fill=X, padx=15)
    ctk.CTkRadioButton(radio_frame, text="All Pre-def", variable=code_symbol_mode_var, value="all", text_color="black", fg_color="black", border_color="black").pack(side=LEFT, padx=1)
    ctk.CTkRadioButton(radio_frame, text="Only These", variable=code_symbol_mode_var, value="only", text_color="black", fg_color="black", border_color="black").pack(side=LEFT, padx=1)
    ctk.CTkRadioButton(radio_frame, text="All Except", variable=code_symbol_mode_var, value="except", text_color="black", fg_color="black", border_color="black").pack(side=LEFT, padx=1)
    create_entry_setting(col5_frame, "Custom Symbols:", code_custom_symbols_var, indent=15, label_width=20)

def populate_test_pad_ui(parent):
    global g_test_pad_input_text, g_test_pad_output_text
    
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(1, weight=1)

    test_pad_header = ctk.CTkFrame(parent, fg_color="transparent")
    test_pad_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    ctk.CTkLabel(test_pad_header, text="Test Pad", font=("", 16, "bold"), text_color="black").pack(side=LEFT, anchor=W)
    ctk.CTkButton(test_pad_header, text="Run Test with Current Settings", command=run_test_pad_processing,
                  fg_color="white", text_color="black", border_color="black", border_width=1, hover_color="white").pack(side=RIGHT)

    pw = PanedWindow(parent, orient=tk.HORIZONTAL, sashrelief=RAISED, bg="white", sashwidth=6)
    pw.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

    input_frame = ctk.CTkFrame(pw, fg_color="white")
    pw.add(input_frame, width=450)
    input_frame.grid_rowconfigure(1, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(input_frame, text="PASTE TEXT TO TEST HERE", font=("", 12, "bold"), text_color="black").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
    g_test_pad_input_text = ctk.CTkTextbox(input_frame, wrap="word", undo=True, fg_color="white", text_color="black", border_width=1)
    g_test_pad_input_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0,5))
    
    output_frame = ctk.CTkFrame(pw, fg_color="white")
    pw.add(output_frame)
    output_frame.grid_rowconfigure(1, weight=1)
    output_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(output_frame, text="FILTERED OUTPUT", font=("", 12, "bold"), text_color="black").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
    g_test_pad_output_text = ctk.CTkTextbox(output_frame, wrap="word", state=DISABLED, fg_color="white", text_color="black", border_width=1)
    g_test_pad_output_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0,5))

def run_test_pad_processing():
    input_text = g_test_pad_input_text.get("1.0", "end-1c")
    params = {var_name: globals()[var_name].get() for var_name in SETTINGS_CONFIG.keys()}
    output_text = process_text(input_text, params)
    g_test_pad_output_text.configure(state=NORMAL)
    g_test_pad_output_text.delete("1.0", END)
    g_test_pad_output_text.insert("1.0", output_text)
    g_test_pad_output_text.configure(state=DISABLED)

# --- MAIN APPLICATION STARTUP ---
if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = CTkinterDnD() if DND_AVAILABLE else ctk.CTk()
    root.configure(fg_color="white")
        
    root.title(f"File Text Extractor v{APP_VERSION}"); root.geometry("1200x800")
    root.minsize(800, 600)
    setup_variables(); load_app_settings()
    def on_main_window_close(): save_app_settings(); root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_main_window_close)
    
    main_pane = PanedWindow(root, orient=VERTICAL, sashrelief=RAISED, bg="white", sashwidth=6)
    main_pane.pack(fill=BOTH, expand=True, padx=10, pady=10)

    settings_container_frame = ctk.CTkFrame(main_pane, border_width=2, fg_color="white", border_color="black")
    main_pane.add(settings_container_frame, height=360, minsize=200) 
    populate_settings_content(settings_container_frame)

    test_pad_container_frame = ctk.CTkFrame(main_pane, border_width=2, fg_color="white", border_color="black")
    main_pane.add(test_pad_container_frame, minsize=150)
    populate_test_pad_ui(test_pad_container_frame)

    file_processing_container_frame = ctk.CTkFrame(main_pane, border_width=2, fg_color="white", border_color="black")
    main_pane.add(file_processing_container_frame, height=140, minsize=140)
    
    file_processing_container_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(file_processing_container_frame, text="Process Files", font=("", 16, "bold"), text_color="black").pack(anchor=W, padx=10, pady=(5,2))
    
    drop_target_frame = ctk.CTkFrame(file_processing_container_frame, fg_color="white", border_color="black", border_width=1, corner_radius=10)
    drop_target_frame.pack(padx=10, pady=(5,5), fill=X)
    
    drop_target_label = ctk.CTkLabel(drop_target_frame, text="Drag & Drop Files Here", 
                                     fg_color="white", text_color="black", height=46)
    drop_target_label.pack(padx=2, pady=2, fill=BOTH, expand=True)

    if DND_AVAILABLE:
        drop_target_label.drop_target_register(DND_FILES)
        drop_target_label.dnd_bind('<<Drop>>', drop_handler)
    
    # Create a frame for the buttons to sit side-by-side
    button_frame = ctk.CTkFrame(file_processing_container_frame, fg_color="transparent")
    button_frame.pack(padx=10, pady=(0, 10), fill=X)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    process_list_button = ctk.CTkButton(button_frame, text="Process Files from List (.txt)", command=process_file_list,
                                        fg_color="white", text_color="black", border_color="black", border_width=1, hover_color="white")
    process_list_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

    g_stop_button = ctk.CTkButton(button_frame, text="Stop Processing", command=stop_processing,
                                  fg_color="white", text_color="black", border_color="black", border_width=1, hover_color="white",
                                  state=DISABLED)
    g_stop_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    log_frame = ctk.CTkFrame(main_pane, border_width=2, fg_color="white", border_color="black")
    main_pane.add(log_frame, height=150, minsize=100)
    
    log_frame.grid_rowconfigure(0, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)
    status_log = ctk.CTkTextbox(log_frame, wrap="word", state=DISABLED, fg_color="white", text_color="black", border_width=0)
    status_log.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    status_log.tag_config("error", foreground="#FF5555")

    initial_status_text = f"Settings loaded. Ready. (v{APP_VERSION})"
    if not DND_AVAILABLE: initial_status_text += " (DND Disabled)"
    log_message(initial_status_text)
    
    root.mainloop()
