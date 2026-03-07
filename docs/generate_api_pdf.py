from pathlib import Path
import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

SRC = Path(__file__).with_name('API_Documentation.md')
OUT = Path(__file__).with_name('API_Documentation.pdf')


def render():
    lines = SRC.read_text(encoding='utf-8').splitlines()

    page_w, page_h = A4
    margin_x = 18 * mm
    margin_y = 18 * mm
    y = page_h - margin_y
    line_h = 5.2 * mm

    pdf = canvas.Canvas(str(OUT), pagesize=A4)
    pdf.setTitle('Coffee API Documentation')

    for raw in lines:
        line = raw.expandtabs(2)

        if not line.strip():
            y -= line_h * 0.6
            if y < margin_y:
                pdf.showPage()
                y = page_h - margin_y
            continue

        if line.startswith('# '):
            pdf.setFont('Helvetica-Bold', 16)
            wrapped = textwrap.wrap(line[2:].strip(), width=65)
        elif line.startswith('## '):
            pdf.setFont('Helvetica-Bold', 13)
            wrapped = textwrap.wrap(line[3:].strip(), width=75)
        elif line.startswith('### '):
            pdf.setFont('Helvetica-Bold', 11)
            wrapped = textwrap.wrap(line[4:].strip(), width=85)
        elif line.startswith('```'):
            pdf.setFont('Helvetica-Oblique', 9)
            wrapped = ['[code block]']
        elif line.startswith('- '):
            pdf.setFont('Helvetica', 10)
            wrapped = textwrap.wrap(f'• {line[2:].strip()}', width=95)
        elif line.startswith('|'):
            pdf.setFont('Courier', 8.5)
            wrapped = textwrap.wrap(line, width=120)
        else:
            pdf.setFont('Helvetica', 10)
            wrapped = textwrap.wrap(line, width=100)

        for text_line in wrapped or ['']:
            if y < margin_y:
                pdf.showPage()
                y = page_h - margin_y
            pdf.drawString(margin_x, y, text_line)
            y -= line_h

    pdf.save()


if __name__ == '__main__':
    render()
    print(OUT)
