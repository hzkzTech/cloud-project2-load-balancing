import os
import shutil
from docx import Document
from docx.shared import Pt

SRC = r"e:\University_of_Macau\course\CISC7403-cloud\CISC7403Role Declaration Page.docx"
OUTDIR = r"e:\University_of_Macau\course\CISC7403-cloud\2026-11-20\project2-load-balancing\outputs\role-declaration"
OUT = os.path.join(OUTDIR, "CISC7403_Role_Declaration.docx")
os.makedirs(OUTDIR, exist_ok=True)
shutil.copyfile(SRC, OUT)

doc = Document(OUT)


def set_cell(cell, text):
    p = cell.paragraphs[0]
    if not p.runs:
        p.add_run(text)
        return
    p.runs[0].text = text
    for r in p.runs[1:]:
        r.text = ""


# --- header: team number and members ---------------------------------
line = doc.paragraphs[1]
member_idx = 0
for run in line.runs:
    if run.text.strip() == "_______":
        run.text = " [XX]"
    elif run.text.strip().startswith("___________________________"):
        member_idx += 1
        run.text = f" [Member {member_idx} (student ID)] "

# --- declared roles table -------------------------------------------
roles = doc.tables[0]
set_cell(roles.rows[1].cells[0], "[Member 1]")
set_cell(roles.rows[1].cells[1], "Lead / Coordinator; Analyst / Developer")
set_cell(roles.rows[1].cells[2],
         "Backend service and Dockerfile, Nginx load balancer, load-balancing and fault-tolerance tests.")
set_cell(roles.rows[2].cells[0], "[Member 2]")
set_cell(roles.rows[2].cells[1], "Writer / Editor; Researcher")
set_cell(roles.rows[2].cells[2],
         "Docker Compose deployment and networking, wrk benchmark, report writing and figures.")
set_cell(roles.rows[3].cells[0], "[Member 3]")
set_cell(roles.rows[3].cells[1], "")
set_cell(roles.rows[3].cells[2], "")
set_cell(roles.rows[4].cells[0], "[Member 4]")
set_cell(roles.rows[4].cells[1], "")
set_cell(roles.rows[4].cells[2], "")

# --- evaluation table ------------------------------------------------
ev = doc.tables[1]
set_cell(ev.rows[1].cells[0], "[Member 1]")
set_cell(ev.rows[1].cells[1], "[100]")
set_cell(ev.rows[2].cells[0], "[Member 2]")
set_cell(ev.rows[2].cells[1], "[100]")
set_cell(ev.rows[3].cells[0], "")
set_cell(ev.rows[3].cells[1], "")

# --- reflection (optional, <=100 words) ------------------------------
import copy
from docx.text.paragraph import Paragraph

prompt = doc.paragraphs[10]
new_el = copy.deepcopy(prompt._p)
prompt._p.addnext(new_el)
new_p = Paragraph(new_el, prompt._parent)
for r in new_p.runs[1:]:
    r._r.getparent().remove(r._r)
new_p.runs[0].text = (
    "[Replace this bracket with 2-3 sentences, e.g.: Member 1 containerised the backend and "
    "configured Nginx; Member 2 built the Compose deployment, ran the wrk benchmark and wrote "
    "the report. We reviewed each other's work and tested the service together on the VM.]"
)

doc.save(OUT)
print("saved", OUT)
