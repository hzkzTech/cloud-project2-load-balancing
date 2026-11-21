import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"e:\University_of_Macau\course\CISC7403-cloud\2026-11-20\project2-load-balancing\outputs\report\figures"
os.makedirs(OUT, exist_ok=True)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"

SPECS = [
    ("shot_load_balancing.png", (1600, 700),
     "SCREENSHOT 1 - LOAD BALANCING",
     ["$ for i in $(seq 1 10); do curl -s http://localhost:6120/; echo; done",
      "Must show: responses alternating between \"backend1\" and \"backend2\"",
      "-> Report Section 3, Figure 'load balancing'"]),

    ("shot_fault_stopped.png", (1200, 700),
     "SCREENSHOT 2a - BACKEND2 STOPPED",
     ["$ docker stop backend2",
      "$ docker compose ps",
      "$ curl -s http://localhost:6120/",
      "Must show: backend2 down, responses still from backend1",
      "-> Report Section 4, Figure 'fault tolerance' (left)"]),

    ("shot_fault_restored.png", (1200, 700),
     "SCREENSHOT 2b - BACKEND2 RESTARTED",
     ["$ docker start backend2",
      "$ for i in 1 2 3 4; do curl -s http://localhost:6120/; echo; done",
      "Must show: backend1 and backend2 both answering again",
      "-> Report Section 4, Figure 'fault tolerance' (right)"]),

    ("shot_wrk_2backends.png", (1200, 700),
     "SCREENSHOT 3a - WRK, 2 BACKENDS",
     ["$ wrk -t2 -c20 -d10s http://localhost:6120/work",
      "Must show: Requests/sec  +  Latency (average)",
      "copy both numbers into the result table",
      "-> Report Section 5, Figure 'wrk' (left)"]),

    ("shot_wrk_1backend.png", (1200, 700),
     "SCREENSHOT 3b - WRK, 1 BACKEND",
     ["$ docker compose down",
      "$ docker compose -f docker-compose.single.yml up -d --build",
      "$ wrk -t2 -c20 -d10s http://localhost:6120/work",
      "Must show: Requests/sec  +  Latency (average)",
      "-> Report Section 5, Figure 'wrk' (right)"]),
]

for name, size, title, lines in SPECS:
    img = Image.new("RGB", size, (246, 247, 249))
    d = ImageDraw.Draw(img)
    w, h = size

    dash = 14
    for x in range(0, w, dash * 2):
        d.line([(x, 5), (min(x + dash, w), 5)], fill=(160, 160, 165), width=3)
        d.line([(x, h - 5), (min(x + dash, w), h - 5)], fill=(160, 160, 165), width=3)
    for y in range(0, h, dash * 2):
        d.line([(5, y), (5, min(y + dash, h))], fill=(160, 160, 165), width=3)
        d.line([(w - 5, y), (w - 5, min(y + dash, h))], fill=(160, 160, 165), width=3)

    f_title = ImageFont.truetype(FONT_BOLD, 30)
    f_body = ImageFont.truetype(FONT_REG, 22)

    tb = d.textbbox((0, 0), title, font=f_title)
    d.text(((w - (tb[2] - tb[0])) / 2, 40), title, font=f_title, fill=(190, 45, 45))

    y = 104
    for ln in lines:
        f = f_body
        col = (110, 110, 120) if ln.startswith("->") else (55, 55, 62)
        bb = d.textbbox((0, 0), ln, font=f)
        x = max(30, (w - (bb[2] - bb[0])) / 2)
        d.text((x, y), ln, font=f, fill=col)
        y += 34

    d.text((30, h - 36), "replace this file (same name, same folder)",
           font=ImageFont.truetype(FONT_REG, 17), fill=(150, 150, 158))
    img.save(os.path.join(OUT, name))
    print("wrote", name, img.size)
