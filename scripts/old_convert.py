"""
Script to convert the PDF reference file to markdown using the PdfConverter from the marker library.
"""

from config import PDF_PATH, DATA_PATH
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)
rendered = converter(PDF_PATH)
text, _, images = text_from_rendered(rendered)

with open(DATA_PATH, "w", encoding="utf-8") as f:
    f.write(text)
    print(f"Conversion terminée : {DATA_PATH}")