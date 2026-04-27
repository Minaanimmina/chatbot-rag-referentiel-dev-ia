"""
Script to convert the PDF reference file to markdown using the PdfConverter
from the marker library.
"""

from config import PDF_PATH, DATA_PATH
import pymupdf4llm
import json

md_text = pymupdf4llm.to_markdown(PDF_PATH)

with open(DATA_PATH, "w", encoding="utf-8") as f:
    if isinstance(md_text, str):
        f.write(md_text)
    else:
        f.write(json.dumps(md_text, ensure_ascii=False, indent=2))
print(f"Conversion terminée : {DATA_PATH}")
