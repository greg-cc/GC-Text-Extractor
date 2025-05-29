# GC-Text-Extractor
Extract text from non binary files with sliders and preview. Drag and drop.

![GC Text Extractor Interface](https://raw.githubusercontent.com/greg-cc/GC-Text-Extractor/refs/heads/main/GC%20text%20extractor.png)

The **GC Text Extractor** efficiently extracts meaningful text from your documents (`.txt`, `.docx`, `.pdf`) by intelligently filtering out unwanted content like code, stray symbols, or irrelevant short lines. Its unified, single-window interface provides comprehensive control over the cleaning process.

## Key Areas & Usage

**1. Filter Settings (Scrollable Top Section):**
Fine-tune your extraction with a comprehensive set of controls. Adjust basic filters (like minimum word counts and alphanumeric ratio) and advanced filters (for code blocks, long concatenated words, and symbol-enclosed words). Each advanced filter has its own sensitivity sliders and toggles. All your settings are automatically saved and reloaded between sessions.

**2. Filter Test Pad (Resizable Middle Section):**
Instantly see how your current filter settings will affect sample text. Paste your text into the input area, click "Process Pasted Text," and the filtered output appears immediately in the adjacent output area. This allows for quick and precise tuning of the filters.

**3. Process Files (Bottom Section):**
Simply drag and drop your documents onto the designated area. The GC Text Extractor applies all your active filter settings and saves the cleaned text to a new file in the same directory as the original (e.g., `yourfile_txtextract123.txt`).

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
