

# GC-Text-Extractor
Advanced tool to extract and refine text from various file types using a highly configurable filtering pipeline. Features a unified UI with a test pad, drag &amp; drop, and persistent settings.

![GC Text Extractor Interface](https://github.com/greg-cc/GC-Text-Extractor/blob/7f7c3e2787c217ffe94eb142275e2a2768302e02/GC%20text%20extractor.png)

The **GC Text Extractor** is a powerful desktop application designed to help you extract meaningful text from documents (`.txt`, `.docx`, `.pdf`, and user-defined types). It provides a comprehensive suite of filters to clean and refine the extracted content, removing noise like code, HTML tags, overly symbolic lines, or number-heavy sequences. After this, a regex can be applied to the filtered data and viewed realtime. All settings are highly configurable through a single-window interface and are saved between sessions.

## Key Features

**1. Robust File Handling:**

  * **Multi-Format Extraction:** Natively processes `.txt`, `.docx` (Microsoft Word), and `.pdf` files.
  * **Customizable Extension Processing:**
      * **Process ONLY these extensions:** Specify a list of extensions (e.g., `.log, .md`) that (along with `.docx`/`.pdf`) will be exclusively processed (as text if not DOCX/PDF).
      * **Always IGNORE these extensions:** Define a list of extensions (e.g., `.exe, .zip, .jpg`) to always skip.
      * **File Processing Mode (if "Process ONLY" is empty):**
          * *Specified Extensions Only:* Processes `.txt` and "Additional Text Exts".
          * *Attempt All Dropped Files:* Tries to process any dropped file as plain text if its type is unknown (after checking ignore/include lists and special types).
      * **Additional Text Exts:** A fallback list of custom extensions to treat as plain text when in "Specified Extensions Only" mode and the "Process ONLY" list is empty.
  * **Drag & Drop:** Easily process files by dragging them onto the application.
  * **Customizable Output:**
      * Define a custom suffix for output filenames (e.g., `_cleaned`). Output is always `.txt`.
      * Default suffix (`_processed`) is used if the custom field is empty to prevent accidental overwrites.

**2. Unified User Interface:**

  * **Single-Window Design:** All controls, the test pad, and file processing area are visible and accessible without switching tabs or opening multiple dialogs.
  * **Scrollable Filter Settings:** A comprehensive 4-column layout for filter settings, scrollable vertically to accommodate all options.
  * **Filter Test Pad:**
      * Resizable input and output text areas.
      * "Process Pasted Text" button to instantly test current filter configurations on sample text.
  * **Status Bar:** Provides feedback on operations, errors, and the application version.

**3. Comprehensive & Configurable Filtering Pipeline:**

  * **Settings Persistence:** All filter configurations are automatically saved to `text_extractor_settings.json` and reloaded on startup.
  * **Initial Text Segmentation:**
      * Pre-processes text to isolate HTML tags by adding newlines around them.
      * Splits text into segments based on paragraphs, then sentences, with a fallback to newlines for very long or unstructured segments.
      * **Configurable:** "Max Chars for Seg (b4 newline split)" allows tuning this stage.
  * **Basic Text Filters:**
      * **Min Words (General Sequence):** Minimum word count for general text lines.
      * **Min Words (Punctuated Sentences):** Minimum word count for punctuated lines.
      * **Alphanumeric Filter (Toggle & Sensitivity):**
          * Filters segments based on the ratio of alphanumeric characters.
          * *Sensitivity:* Ratio Threshold, Min Segment Length for Ratio Test, and Absolute Alphanumeric Fallback Count.
  * **Advanced Word/Block Filters (Each with Enable/Disable Toggle & Sensitivity):**
      * **Attempt to remove code-like blocks:**
          * Identifies and removes segments resembling computer code or markup (HTML, JS, CSS).
          * *Sensitivity:* Min keywords (includes common web tags), min code symbols, min words in segment, symbol density threshold.
      * **"Too Many Numbers" Filter:**
          * Removes segments overloaded with digits (e.g., long timestamps, numerical data lines).
          * *Sensitivity:* Digit ratio threshold, min digits for ratio check, max allowed consecutive digits, and min words to exempt a segment.
      * **Concatenated Word Filter:**
          * Targets long tokens that appear to be multiple words joined without spaces (e.g., `CamelCaseStrings`).
          * *Behavior Toggle:* Option to remove tokens entirely or abbreviate them (e.g., `First...Last`).
          * *Sensitivity:* Min token length to check, min internal sub-words to trigger.
      * **Symbol-Enclosed Word Filter:**
          * Removes words surrounded by non-alphanumeric symbols (e.g., `*word*`, `_text_`).
          * *Sensitivity:* Max number of symbols around the word to consider.
      * **Custom Regex Filter:**
          * Allows user-defined regular expressions for highly specific filtering.
          * *Modes:* "Remove segments matching regex" (surgically removes only matched parts from segments) or "Keep only segments matching regex" (keeps entire segment if a match is found).
          * *Toggle:* Case-sensitive matching.
  * **URL Extraction (Optional):**
      * A checkbox in settings to enable/disable.
      * If enabled, extracts all URLs from the **original raw text** of the document.
      * Deduplicates, sorts (case-insensitively), and appends the list of unique URLs to the end of the filtered text output under a "--- Detected URLs ---" heading.

## Installation

1.  **Prerequisites:**

      * Python 3 (preferably 3.7 or newer) from [python.org](https://www.python.org/).
      * `pip` (Python's package installer), usually included with Python.

2.  **Download or Clone:**

      * Download the main script file (e.g., `text_stripper.py`) from this repository.
      * Or, clone with Git:
        ```bash
        git clone [https://github.com/greg-cc/GC-Text-Extractor.git](https://github.com/greg-cc/GC-Text-Extractor.git)
        cd GC-Text-Extractor
        ```

3.  **Install Dependencies:**
    Open your terminal or command prompt and run:

    ```bash
    pip install tkinterdnd2 python-docx PyPDF2
    ```

    *(Note: You might need to use `pip3` on some systems).*

4.  **Run the Application:**
    Navigate to the script's directory and execute:

    ```bash
    python text_stripper.py
    ```

    *(Or `python3 text_stripper.py` on some systems).*

## How to Use

1.  **Launch the Application:** Run `text_stripper.py`.
2.  **Configure Filters (Top Section):**
      * The settings panel is scrollable and organized into four columns.
      * Adjust basic settings (word counts, alphanumeric criteria) in the first column.
      * Set file handling preferences (extensions to include/ignore, processing mode, output suffix, URL extraction) in the second column.
      * Enable/disable advanced filters using the toggles in the second column.
      * Fine-tune the sensitivity of enabled advanced filters using the sliders and input boxes in the third and fourth columns.
      * Settings are saved automatically when you close the application.
3.  **Test Filters (Middle Section - Test Pad):**
      * Paste any sample text into the left input area.
      * Click "Process Pasted Text".
      * The output, reflecting your current filter settings, will appear in the right area. This is great for quick tuning.
4.  **Process Files (Bottom Section):**
      * Drag and drop your `.txt`, `.docx`, `.pdf`, or other configured file types onto the designated area.
      * The script will process them according to your settings.
      * Output files (always `.txt`) will be saved in the same directory as the originals, with your chosen suffix (default `_processed`).
5.  **Check Status Bar:** For feedback, error messages, and version info.

## Common Uses

  * Cleaning text from OCR or web scrapes by removing HTML/code and noise.
  * Extracting core textual content from mixed-content documents.
  * Preparing datasets for Natural Language Processing (NLP) tasks.
  * Standardizing text extracted from various sources.

GC Text Extractor offers a highly adaptable environment to refine and extract precisely the text you need from your documents.

-----

*License: (You should add your chosen open-source license here, e.g., MIT, Apache 2.0. If you haven't chosen one, consider adding one\!)*
