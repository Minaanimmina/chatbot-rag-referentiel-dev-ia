"""
Script to convert the PDF reference file to markdown using the PdfConverter from the marker library.
"""

from config import PDF_PATH, DATA_PATH
import pymupdf4llm

md_text = pymupdf4llm.to_markdown(PDF_PATH)
with open(DATA_PATH, "w", encoding="utf-8") as f:
    f.write(md_text)
print(f"Conversion terminée : {DATA_PATH}")