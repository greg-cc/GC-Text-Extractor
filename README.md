
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
      * Output text area to display filtered results immediately.
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

      * Download the main Python script file (e.g., `text_stripper.py`) from this repository.
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
    Once the dependencies are installed, navigate to the directory where you saved the script (e.g., `text_stripper.py`) and run it from your terminal or command prompt:

    ```bash
    python text_stripper.py
    ```

    *(Or `python3 text_stripper.py` on some systems).*

## How to Use

1.  **Launch the Application:** Run `text_stripper.py`.
2.  **Configure Filters (Top Section):**
      * The settings panel is scrollable and organized into four columns.
      * Adjust basic settings (word counts, alphanumeric criteria, segmentation) in the first column.
      * Set file handling preferences (extensions to include/ignore, processing mode, output suffix, URL extraction) and main advanced filter toggles in the second column.
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

## Detailed Filter Settings Guide (Reflecting v1.6.7+ features)

This guide provides an in-depth explanation of each configurable setting available in the GC Text Extractor. The settings are organized into four columns in the application's "Filter Settings" area.

-----

### Column 1: Basic, Segmentation & Alphanumeric Filters

This column handles fundamental text properties, how the initial text is broken down, and broad alphanumeric content checks.

#### Basic & Segmentation Filters

  * **Min Words (General Seq):**

      * **Purpose:** Sets the minimum number of words a line or segment of text (that doesn't end with clear sentence punctuation) must contain to be kept. Shorter general segments are discarded.
      * **Control:** Slider with manual number entry.
      * **Default:** 11
      * **Range:** 1 to 100

  * **Min Words (Punctuated Sent.):**

      * **Purpose:** Sets a specific minimum word count for lines or segments that *do* end with sentence punctuation (e.g., `.`, `!`, `?`).
      * **Control:** Slider with manual number entry.
      * **Default:** 5
      * **Range:** 1 to 50

  * **Max Chars Seg (for newline split):**

      * **Purpose:** During initial text segmentation, if a segment (like a line from input or part of a paragraph not split by sentence punctuation) is longer than this character limit AND contains internal newlines, it will be further broken down by those newlines. Lowering this value can help break up very long lines from sources like web pages.
      * **Control:** Slider with manual number entry.
      * **Default:** 350 characters
      * **Range:** 50 to 2000 (increment 50)

#### Alphanumeric Filter

  * **Enable Alphanumeric Filter:**
      * **Purpose:** Main toggle (ON/OFF) for the entire Alphanumeric filter block. When ON, segments are evaluated based on their alphanumeric content using the sub-settings below.
      * **Control:** Checkbox.
      * **Default:** ON (Checked)
  * **Ratio Threshold:** (Active when Alphanumeric Filter is ON)
      * **Purpose:** Sets the minimum ratio of alphanumeric characters (letters and numbers) to total characters that a segment must have to pass this filter. For example, a value of 0.75 means at least 75% of the characters must be alphanumeric.
      * **Control:** Slider with manual number entry.
      * **Default:** 0.75
      * **Range:** 0.0 to 1.0 (resolution 0.01)
  * **Min Seg Len for Ratio Test:** (Active when Alphanumeric Filter is ON)
      * **Purpose:** Segments shorter than this character length will bypass the "Ratio Threshold" test. Instead, these very short segments are kept as long as they contain at least one alphanumeric character.
      * **Control:** Slider with manual number entry.
      * **Default:** 5 characters
      * **Range:** 1 to 50
  * **Abs Alnum Fallback Count:** (Active when Alphanumeric Filter is ON)
      * **Purpose:** If a segment *fails* the "Ratio Threshold" test (and is long enough for that test), it gets a second chance. If the segment contains at least this many *absolute* alphanumeric characters, it will be kept ("rescued").
      * **Control:** Slider with manual number entry.
      * **Default:** 15 characters
      * **Range:** 0 to 100

-----

### Column 2: File & Output Options / Main Advanced Filter Toggles

This column manages how files are handled, output options, and provides the main ON/OFF switches for the more specialized advanced filters.

#### File Handling & Output

  * **File Processing Mode:**
      * **Purpose:** Determines how the application handles dropped files with unrecognized extensions.
      * **Control:** Radio buttons.
      * **Default:** "Specified Extensions Only"
      * **Options:**
          * "Specified Extensions Only": Processes only `.docx`, `.pdf`, `.txt`, extensions listed in "Process ONLY these", or (if "Process ONLY these" is empty) extensions listed in "Additional Text Exts".
          * "Attempt All Dropped Files": Attempts to process any dropped file type (after checking the ignore list). Unrecognized types are treated as plain text.
  * **Process ONLY these (,.ext):**
      * **Purpose:** If filled (e.g., `.log, .md`), the application will *only* attempt to process files with these extensions (plus `.docx` and `.pdf`). This overrides the "File Processing Mode" and "Additional Text Exts" for inclusion. Extensions are comma-separated, starting with a dot. Treated as plain text if not .docx/.pdf.
      * **Control:** Text Entry.
      * **Default:** "" (empty)
  * **Always IGNORE these (,.ext):**
      * **Purpose:** A comma-separated list of file extensions (e.g., `.exe, .zip, .jpg`) that will *always* be skipped, taking precedence over all other settings.
      * **Control:** Text Entry.
      * **Default:** A pre-filled list of common binary/image/archive types.
  * **Additional Text Exts (,.ext):**
      * **Purpose:** A comma-separated list of extensions to be treated as plain text. Used if "Process ONLY these" is empty AND "File Processing Mode" is "Specified Extensions Only".
      * **Control:** Text Entry.
      * **Default:** "" (empty)
  * **Output File Suffix:**
      * **Purpose:** Text to append to the original filename (before the final `.txt` extension) for output files.
      * **Control:** Text Entry.
      * **Default:** "\_processed" (e.g., `inputfile_processed.txt`)
  * **Extract and list URLs from text:**
      * **Purpose:** If checked, scans the *original raw text* for URLs. A deduplicated, sorted list is appended to the filtered output.
      * **Control:** Checkbox.
      * **Default:** OFF (Unchecked)

#### Advanced Filter Main Toggles

  * **Enable 'Too Many Numbers' Filter:**
      * **Purpose:** Turns the "Too Many Numbers" filter ON or OFF.
      * **Control:** Checkbox.
      * **Default:** OFF (Un
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
more:
## Detailed Filter Settings Guide (v1.6.7+)

This guide provides an in-depth explanation of each configurable setting available in the GC Text Extractor. The settings are organized into four columns in the application's "Filter Settings" area.

---

### Column 1: Basic, Segmentation & Alphanumeric Filters

This column handles fundamental text properties, how the initial text is broken down, and broad alphanumeric content checks.

#### Basic & Segmentation Filters
* **Min Words (General Seq):**
    * **Purpose:** Sets the minimum number of words a line or segment of text (that doesn't end with clear sentence punctuation) must contain to be kept. Shorter general segments are discarded.
    * **Control:** Slider with manual number entry.
    * **Default:** 11
    * **Range:** 1 to 100

* **Min Words (Punctuated Sent.):**
    * **Purpose:** Sets a specific minimum word count for lines or segments that *do* end with sentence punctuation (e.g., `.`, `!`, `?`).
    * **Control:** Slider with manual number entry.
    * **Default:** 5
    * **Range:** 1 to 50

* **Max Chars Seg (for newline split):**
    * **Purpose:** During initial text segmentation, if a segment (like a line from input or part of a paragraph not split by sentence punctuation) is longer than this character limit AND contains internal newlines, it will be further broken down by those newlines. Lowering this value can help break up very long lines from sources like web pages.
    * **Control:** Slider with manual number entry (was Spinbox, now updated for consistency).
    * **Default:** 350 characters
    * **Range:** 50 to 2000 (typical increment 50)

#### Alphanumeric Filter
* **Enable Alphanumeric Filter:**
    * **Purpose:** Main toggle (ON/OFF) for the entire Alphanumeric filter block. When ON, segments are evaluated based on their alphanumeric content using the sub-settings below.
    * **Control:** Checkbox.
    * **Default:** ON (Checked)
* **Ratio Threshold:** (Active when Alphanumeric Filter is ON)
    * **Purpose:** Sets the minimum ratio of alphanumeric characters (letters and numbers) to total characters that a segment must have to pass this filter. For example, a value of 0.75 means at least 75% of the characters must be alphanumeric.
    * **Control:** Slider with manual number entry.
    * **Default:** 0.75
    * **Range:** 0.0 to 1.0 (resolution 0.01)
* **Min Seg Len for Ratio Test:** (Active when Alphanumeric Filter is ON)
    * **Purpose:** Segments shorter than this character length will bypass the "Ratio Threshold" test. Instead, these very short segments are kept as long as they contain at least one alphanumeric character. This prevents the ratio test from incorrectly discarding very short, valid items (e.g., "OK.", "ID: A").
    * **Control:** Slider with manual number entry.
    * **Default:** 5 characters
    * **Range:** 1 to 50
* **Abs Alnum Fallback Count:** (Active when Alphanumeric Filter is ON)
    * **Purpose:** If a segment *fails* the "Ratio Threshold" test (and is long enough for that test), it gets a second chance. If the segment contains at least this many *absolute* alphanumeric characters, it will be kept ("rescued") despite its low ratio. This helps preserve longer segments with substantial text that might have many spaces or some symbols.
    * **Control:** Slider with manual number entry.
    * **Default:** 15 characters
    * **Range:** 0 to 100

---

### Column 2: File & Output Options / Main Advanced Filter Toggles

This column manages how files are handled, output options, and provides the main ON/OFF switches for the more specialized advanced filters.

#### File Handling & Output
* **File Processing Mode:**
    * **Purpose:** Determines how the application handles dropped files with unrecognized extensions.
    * **Control:** Radio buttons.
    * **Default:** "Specified Extensions Only"
    * **Options:**
        * "Specified Extensions Only": Processes only `.docx`, `.pdf`, `.txt`, extensions listed in "Process ONLY these", or (if "Process ONLY these" is empty) extensions listed in "Additional Text Exts".
        * "Attempt All Dropped Files": Attempts to process any dropped file type (after checking the ignore list). Unrecognized types are treated as plain text.
* **Process ONLY these (,.ext):**
    * **Purpose:** If filled (e.g., `.log, .md`), the application will *only* attempt to process files with these extensions (plus `.docx` and `.pdf`). This overrides the "File Processing Mode" and "Additional Text Exts" for inclusion. Extensions are comma-separated, starting with a dot. Treated as plain text if not .docx/.pdf.
    * **Control:** Text Entry.
    * **Default:** "" (empty)
* **Always IGNORE these (,.ext):**
    * **Purpose:** A comma-separated list of file extensions (e.g., `.exe, .zip, .jpg`) that will *always* be skipped, taking precedence over all other settings.
    * **Control:** Text Entry.
    * **Default:** A pre-filled list of common binary/image/archive types.
* **Additional Text Exts (,.ext):**
    * **Purpose:** A comma-separated list of extensions to be treated as plain text. Used if "Process ONLY these" is empty AND "File Processing Mode" is "Specified Extensions Only".
    * **Control:** Text Entry.
    * **Default:** "" (empty)
* **Output File Suffix:**
    * **Purpose:** Text to append to the original filename (before the final `.txt` extension) for output files.
    * **Control:** Text Entry.
    * **Default:** "_processed" (e.g., `inputfile_processed.txt`)
* **Extract and list URLs from text:**
    * **Purpose:** If checked, scans the *original raw text* for URLs. A deduplicated, sorted list is appended to the filtered output.
    * **Control:** Checkbox.
    * **Default:** OFF (Unchecked)

#### Advanced Filter Main Toggles
* **Enable 'Too Many Numbers' Filter:**
    * **Purpose:** Turns the "Too Many Numbers" filter ON or OFF.
    * **Control:** Checkbox.
    * **Default:** OFF (Unchecked)
* **Enable Code Block Filter:**
    * **Purpose:** Turns the "Code-like Block Filter" ON or OFF.
    * **Control:** Checkbox.
    * **Default:** ON (Checked)
* **Concatenated: Remove Entirely:** (This is the primary toggle for the Concatenated Word Filter's *behavior*)
    * **Purpose:** If ON (checked), identified long concatenated tokens are completely removed. If OFF (unchecked), they are abbreviated (e.g., "First...Last"). The identification of these tokens is always active based on sensitivity settings in Column 3.
    * **Control:** Checkbox.
    * **Default:** ON (Checked)
* **Enable Symbol-Enclosed Filter:**
    * **Purpose:** Turns the "Symbol-Enclosed Word Filter" ON or OFF.
    * **Control:** Checkbox.
    * **Default:** ON (Checked)
* **Enable Custom Regex Filter:**
    * **Purpose:** Turns the "Custom Regex Filter" ON or OFF.
    * **Control:** Checkbox.
    * **Default:** OFF (Unchecked)

---

### Column 3: Advanced Filter Sensitivity (Part 1)

This column contains detailed sensitivity parameters for some of the advanced filters. These controls are typically active only if their corresponding main filter toggle in Column 2 is enabled.

#### 'Too Many Numbers' Filter Sensitivity
(Active when "'Too Many Numbers' Filter" in Column 2 is ON)
* **Digit Ratio Threshold >:**
    * **Purpose:** If the ratio of digit characters to total characters in a segment exceeds this, the segment is flagged (subject to "Min Digits for Ratio Check").
    * **Control:** Slider with manual number entry.
    * **Default:** 0.50 (50%)
    * **Range:** 0.10 to 1.0
* **Min Digits for Ratio Check:**
    * **Purpose:** The "Digit Ratio Threshold" only applies if the segment has at least this many digits.
    * **Control:** Slider with manual number entry.
    * **Default:** 5
    * **Range:** 1 to 50
* **Max Consecutive Digits:**
    * **Purpose:** If a sequence of more than this many digits is found (e.g., a long timestamp), the segment is flagged.
    * **Control:** Slider with manual number entry.
    * **Default:** 8
    * **Range:** 3 to 50 (or 0 to effectively disable this specific check if not desired alongside ratio)
* **Min Words to Exempt:**
    * **Purpose:** If a segment has more than this many words, it bypasses the "Too Many Numbers" filter entirely.
    * **Control:** Slider with manual number entry.
    * **Default:** 10
    * **Range:** 0 to 50

#### Concatenated Word Definition
(These parameters are always active and define *what constitutes* a "concatenated word" for the filter whose behavior is toggled in Column 2.)
* **Min Length to Check:**
    * **Purpose:** A token (word) must be at least this long to be examined for concatenation.
    * **Control:** Slider with manual number entry.
    * **Default:** 18
    * **Range:** 10 to 50
* **Min Sub-Words to Act:**
    * **Purpose:** After internal splitting (e.g., `MyWordExample` -> `['My', 'Word', 'Example']`), it must result in at least this many "sub-words" for the filter (abbreviation or removal) to apply.
    * **Control:** Slider with manual number entry.
    * **Default:** 3
    * **Range:** 2 to 10

#### Symbol-Enclosed Sensitivity
(Active when "Enable Symbol-Enclosed Filter" in Column 2 is ON)
* **Max Symbols Around:**
    * **Purpose:** Defines the maximum number of non-alphanumeric characters on each side of a word the filter will consider as "surrounding symbols" for removal.
    * **Control:** Slider with manual number entry.
    * **Default:** 3
    * **Range:** 1 to 5

---

### Column 4: Advanced Filter Sensitivity (Part 2) & Custom Regex Details

This column continues with sensitivity controls for advanced filters and houses the detailed settings for the Custom Regex filter.

#### Code Filter Sensitivity
(Active when "Enable Code Block Filter" in Column 2 is ON)
* **Min Keywords:**
    * **Purpose:** Minimum programming/markup keywords needed (in conjunction with symbols or density) to flag a segment as code.
    * **Control:** Slider with manual number entry.
    * **Default:** 1
    * **Range:** 0 to 20
* **Min Code Symbols:**
    * **Purpose:** Minimum common code symbols (e.g., `{ } ( ) ; =`) needed (in conjunction with keywords) to flag a segment as code.
    * **Control:** Slider with manual number entry.
    * **Default:** 2
    * **Range:** 0 to 30
* **Min Words in Segment (for Code Check):**
    * **Purpose:** The code filter only applies to segments with at least this many words.
    * **Control:** Slider with manual number entry.
    * **Default:** 2
    * **Range:** 1 to 20
* **Symbol Density > (for Code Check):**
    * **Purpose:** If the ratio of recognized code symbols to total characters in a segment exceeds this, it may be flagged as code.
    * **Control:** Slider with manual number entry.
    * **Default:** 0.20 (20%)
    * **Range:** 0.01 to 0.50

#### Custom Regex Details
(Active when "Enable Custom Regex Filter" in Column 2 is ON)
* **Regex Pattern:**
    * **Purpose:** Enter your Python-compatible regular expression.
    * **Control:** Text Entry.
    * **Default:** "" (empty)
* **Mode:**
    * **Purpose:** How the regex is applied:
        * "Remove Matches": Surgically removes only parts of segments matching the regex.
        * "Keep Matches Only": Keeps entire segments that contain at least one regex match; others are discarded.
    * **Control:** Radio buttons.
    * **Default:** "Remove Matches"
* **Case Sensitive:**
    * **Purpose:** If checked, regex matching is case-sensitive. Unchecked (default) means case-insensitive.
    * **Control:** Checkbox.
    * **Default:** OFF (Unchecked / Case-insensitive)


*License: (You should add your chosen open-source license here, e.g., MIT, Apache 2.0. If you haven't chosen one, consider adding one\!)*
