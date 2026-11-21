import sys, os
import pdfplumber
from docx import Document

pdf_path = r"e:\University_of_Macau\course\CISC7403-cloud\Project2_Scalable_Web_Service_Load_Balancing.pdf"
out = []

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages, 1):
        out.append(f"\n===== PAGE {i} =====")
        txt = page.extract_text() or ""
        out.append(txt)
        tables = page.extract_tables()
        for j, t in enumerate(tables, 1):
            out.append(f"--- TABLE {j} ---")
            for row in t:
                out.append(" | ".join("" if c is None else str(c).replace("\n", " ") for c in row))

text = "\n".join(out)
with open(r"e:\University_of_Macau\course\CISC7403-cloud\2026-11-20\project2-load-balancing\work\pdf_text.txt", "w", encoding="utf-8") as f:
    f.write(text)

docx_path = r"e:\University_of_Macau\course\CISC7403-cloud\CISC7403Role Declaration Page.docx"
d = Document(docx_path)
parts = []
for p in d.paragraphs:
    parts.append(p.text)
for ti, table in enumerate(d.tables, 1):
    parts.append(f"--- DOCX TABLE {ti} ---")
    for row in table.rows:
        parts.append(" | ".join(c.text.replace("\n", " ") for c in row.cells))
with open(r"e:\University_of_Macau\course\CISC7403-cloud\2026-11-20\project2-load-balancing\work\docx_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(parts))

print(text)
