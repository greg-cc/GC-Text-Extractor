# GC-Text-Extractor (work in progress)
Extract text from non binary files with sliders and preview. Drag and drop.

![GC Text Extractor Interface](https://raw.githubusercontent.com/greg-cc/GC-Text-Extractor/GC%20text%20extractor.png)

The **GC Text Extractor** efficiently extracts meaningful text from your documents (`.txt`, `.docx`, `.pdf`, `.epub` or any non binary file) by intelligently filtering out unwanted content like code, stray symbols, or irrelevant short lines. Its unified, single-window interface provides comprehensive control over the cleaning process.

## Key Areas & Usage

**1. Filter Settings (Scrollable Top Section):**
Fine-tune your extraction. All your settings are automatically saved and reloaded between sessions.

**2. Filter Test Pad (Resizable Middle Section):**
Instantly see affect on your sample text.

**3. Process Files (Bottom Section):**
Simply drag and drop. Saves the cleaned text to a new file in the same directory as the original + 'txtextract123.txt`.

#   - Enabled filters are applied sequentially
## Basic Filters

* **Min Words (General Seq):** Define the minimum number of words a general, non-punctuated sequence of text must have to be kept.
* **Min Words (Punctuated Sent.):** Set a specific minimum word count for text segments that end with sentence punctuation (like '.', '!', '?').
* **Alphanumeric Filter:** A toggle (**ON/OFF** via a small slider) to enable a filter that checks the ratio of letters and numbers in a text segment.
* **Alphanumeric Threshold (if ON):** If the Alphanumeric Filter is **ON**, this slider and entry box let you set the minimum required ratio (0.0 to 1.0) of alphanumeric characters. Segments below this ratio are discarded. This is a powerful first line of defense against code or very noisy text.

## Advanced Word/Block Filters

Each of these has a main toggle (checkbox) and then specific sensitivity controls that become active when the filter is enabled.

### Attempt to remove code-like blocks
When **ON** (checked), this filter tries to identify and completely remove segments that resemble computer code rather than natural language.
* **Sensitivity:** You can control the minimum number of programming keywords, code symbols, and words in a segment to check, as well as the symbol density threshold.

### Concatenated Word Filter
This targets very long "words" that look like multiple words joined without spaces (e.g., `LongCamelCaseString`).
* **Behavior Toggle:** `[ ] Remove long concatenated words entirely (don't abbreviate)`
    * If **OFF** (unchecked), such words are abbreviated (e.g., `Long...String`).
    * If **ON** (checked), they are completely removed.
* **Sensitivity:** Controls for "Min Length to Check" (how long a token must be) and "Min Sub-Words to Act" (how many internal "words" it must split into).

### Symbol-Enclosed Word Filter
This removes words surrounded by symbols (e.g., `*important*`, `_variable_`).
* **Main Toggle:** `[ ] Remove words enclosed by symbols`
* **Sensitivity:** The "Max Symbols Around" setting defines how many symbols on each side of a word the filter will consider for removal along with the word.

#    - Custom Regex Filter:
            - Allows users to input a custom regular expression.
            - Modes: "Remove segments matching regex" or "Keep only segments matching regex".
            - Toggle for case-sensitive matching.
            - Invalid regex patterns are flagged in the status bar.

## Installation

1.  **Prerequisites:**

      * Ensure you have Python 3 installed on your system (preferably Python 3.7 or newer). You can download it from [python.org](https://www.python.org/).
      * `pip` (Python's package installer) is usually included with your Python installation.

2.  **Download or Clone the Script:**

      * Download the main Python script file (e.g., `text_stripper.py`) from this repository.
      * Or, if you have Git installed, you can clone the repository:
        ```bash
        git clone <your_repository_url_here>
        cd GC-Text-Extractor 
        ```
        (Replace `<your_repository_url_here>` with the actual URL of your GitHub repository).

3.  **Install Dependencies:**
    Open your terminal or command prompt and run the following command to install the necessary Python libraries:

    ```bash
    pip install tkinterdnd2 python-docx PyPDF2
    ```

    *(Note: Depending on your Python setup, you might need to use `pip3` instead of `pip` if `pip` defaults to an older Python version).*

4.  **Run the Application:**
    Once the dependencies are installed, navigate to the directory where you saved the script (e.g., `text_stripper.py`) and run it from your terminal or command prompt:

    ```bash
    python text_stripper.py
    ```

    *(Similarly, you might need to use `python3` instead of `python` on some systems, particularly macOS and Linux).*

## Common Uses

  * Cleaning text from OCR or web scrapes.
  * Extracting core content by removing code, boilerplate, or UI elements.
  * Preparing text for data analysis or import into other systems.

GC Text Extractor gives you powerful, direct control to refine and extract precisely the text you need.
