from docx import Document

d = Document(r"e:\University_of_Macau\course\CISC7403-cloud\CISC7403Role Declaration Page.docx")

print("== paragraphs ==")
for i, p in enumerate(d.paragraphs):
    print(i, repr(p.text), "| runs:", [r.text for r in p.runs])

print("\n== tables ==")
for ti, t in enumerate(d.tables):
    print("table", ti, "rows", len(t.rows), "cols", len(t.columns))
    for ri, row in enumerate(t.rows):
        print("  row", ri, [c.text for c in row.cells])
        for ci, c in enumerate(row.cells):
            for pi, p in enumerate(c.paragraphs):
                print("    cell", ri, ci, "par", pi, repr(p.text), [r.text for r in p.runs])
