"""
Script to convert the PDF reference file to markdown using the PdfConverter
from the marker library.
"""

from config import PDF_PATH, DATA_PATH
import pymupdf4llm
import json
import re

md_text = pymupdf4llm.to_markdown(PDF_PATH)


def clean_markdown(text):
    # Supprimer les <br>
    text = text.replace("<br>", "\n")
    # Supprimer les numéros de page
    text = re.sub(r"Page \*\*\d+\*\* / \*\*25\*\*", "", text)
    # Supprimer les références images
    picture_pattern = "**==> picture [91 x 32] intentionally omitted <==**"
    text = text.replace(picture_pattern, "")
    return text


md_text = clean_markdown(md_text)

with open(DATA_PATH, "w", encoding="utf-8") as f:
    if isinstance(md_text, str):
        f.write(md_text)
    else:
        f.write(json.dumps(md_text, ensure_ascii=False, indent=2))
print(f"Conversion terminée : {DATA_PATH}")
