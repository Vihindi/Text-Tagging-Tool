# Sinhala Text Tagging Tool

## Overview

A small Streamlit web utility for tagging Sinhala text with XML-like labels. Paste text into the editor, select a word/sentence/phrase, then click a tag button to wrap the selection with the chosen tag.

<img width="1223" height="582" alt="Screenshot 2026-06-16 190311" src="https://github.com/user-attachments/assets/58040ef1-650b-4112-ad1b-978d9189d93d" />

## Key features

- Add `<sns>...<ens>` around a selected span.
- Add `<eos>` at the end of the document.
- Add `<psi>` immediately after the current selection.
- Copy the final tagged text to clipboard.
- Download the final tagged text as a `.txt` file.
- Clear the editor to start over.

## Usage

1. Open the app (requires Streamlit).
2. Paste your Sinhala text into the large editor area.
3. Select the word, phrase, or sentence you want to tag.
4. Click one of the tag buttons (for example, `Add <sns>...<ens>`).
5. Use `Copy final text` to copy the tagged output or `Download .txt` to save it.
6. Use `Clear` to reset the editor.

## Example

Selecting a word like බුද්ධි and clicking the `Add <sns>...<ens>` button will produce:

```
<sns>බුද්ධි</ens>
```

## Run locally

Requirements:

- Python 3.8+
- Streamlit

Install Streamlit:

```bash
pip install streamlit
```

Run the app:

```bash
streamlit run app.py
```

## Files

- `app.py` — Streamlit application providing the editor and tagging controls.
- `Screenshot 2026-06-16 190311.png` — reference screenshot used in this README.

---

This README was generated/expanded from the provided app screenshot.
