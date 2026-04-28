"""
Script to convert the PDF reference file to markdown using pdfplumber.
Handles multi-column tables and page breaks correctly.
"""

from config import PDF_PATH, DATA_PATH
import pdfplumber
import re


def clean_text(text: str) -> str:
    text = re.sub(r"Page \d+ / \d+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def convert_pdf_to_markdown(pdf_path: str) -> str:
    result = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        cellules = []
                        for cell in row:
                            if cell:
                                cleaned = cell.strip().replace("\n", " ")
                                cellules.append(cleaned)
                        if cellules:
                            result.append(" | ".join(cellules))
            else:
                text = page.extract_text(layout=True)
                if text:
                    result.append(clean_text(text))
    return "\n\n".join(result)


md_text = convert_pdf_to_markdown(PDF_PATH)

with open(DATA_PATH, "w", encoding="utf-8") as f:
    f.write(md_text)

print(f"Conversion terminée : {DATA_PATH}")
