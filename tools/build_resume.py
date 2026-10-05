"""Build the website, plain-text resume, and one-page US Letter PDF.

Usage: python3 tools/build_resume.py (requires reportlab).
All resume content lives in resume.json.
"""
import html
import json
import shutil
from pathlib import Path
from string import Template

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "resume.json").read_text())
PDF_NAME = "Alexander-Belskiy-Resume.pdf"
e = html.escape


def build_html():
    fields = {key: e(value) for key, value in DATA.items() if isinstance(value, str)}
    fields.update({key: e(value) for key, value in DATA["education"].items()})
    fields["pdf_name"] = PDF_NAME
    fields["skills"] = "\n".join(
        f'<div><dt>{e(label)}</dt><dd>{e(value)}</dd></div>'
        for label, value in DATA["skills"])
    jobs = []
    for job in DATA["experience"]:
        bullets = "".join(f'<li>{e(b)}</li>' for b in job["bullets"])
        jobs.append(f'''<article class="job">
        <div class="job-heading"><h3>{e(job["company"])}</h3><p class="dates">{e(job["start"])} – {e(job["end"])}</p></div>
        <p class="role">{e(job["role"])}</p><ul>{bullets}</ul>
      </article>''')
    fields["experience"] = "\n".join(jobs)
    fields["earlier"] = "".join(
        f'<li><strong>{e(j["company"])}</strong> · {e(j["role"])} '
        f'<span class="earlier-dates">({e(j["start"])} – {e(j["end"])})</span>. {e(j["result"])}</li>'
        for j in DATA["earlier"])
    template = Template((ROOT / "tools" / "index.template.html").read_text())
    (ROOT / "index.html").write_text(template.substitute(fields))


def ascii_punctuation(text):
    return text.replace("–", "-").replace("—", "-").replace("·", " | ")


def build_pdf():
    output = ROOT / "output" / "pdf" / PDF_NAME
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = {
        "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=22, leading=25, spaceAfter=4),
        "title": ParagraphStyle("title", fontName="Helvetica", fontSize=11, leading=14, spaceAfter=4),
        "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.4, leading=11, textColor=colors.HexColor("#555555"), spaceAfter=3),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=9, leading=12, spaceBefore=11, spaceAfter=5),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=12),
        "job": ParagraphStyle("job", fontName="Helvetica-Bold", fontSize=9.4, leading=12, spaceBefore=6, spaceAfter=3),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.2, leading=12, leftIndent=9, firstLineIndent=-9, spaceAfter=2),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.8, leading=11.5, spaceAfter=3),
    }

    def p(text, style="body"):
        return Paragraph(ascii_punctuation(text), styles[style])

    story = [p(e(DATA["name"]), "name"), p(e(DATA["title"]), "title")]
    story += [p(f'{e(DATA["location"])} | {e(DATA["phone"])} | <link href="mailto:{DATA["email"]}">{e(DATA["email"])}</link>', "contact")]
    story += [p(f'<link href="{DATA["linkedin"]}">linkedin.com/in/abelskiy</link> | <link href="https://t.me/{DATA["telegram"]}">t.me/{DATA["telegram"]}</link> | <link href="https://zemamba.github.io/">zemamba.github.io</link>', "contact")]
    story += [p(e(DATA["availability"]), "contact"), p("PROFILE", "section"), p(e(DATA["summary"]))]
    story += [p("CORE SKILLS", "section")]
    for label, value in DATA["skills"]:
        story.append(p(f'<b>{e(label)}:</b> {e(value)}', "small"))
    story.append(p("EXPERIENCE", "section"))
    for job in DATA["experience"]:
        group = [p(f'{e(job["company"])} | {e(job["role"])} | {e(job["start"])} - {e(job["end"])}', "job")]
        group += [p(f'• {e(b)}', "bullet") for b in job["bullets"]]
        story.append(KeepTogether(group))
    story.append(Spacer(1, 6))
    for job in DATA["earlier"]:
        story.append(p(f'<b>{e(job["company"])}:</b> {e(job["role"])} ({e(job["start"])} - {e(job["end"])}). {e(job["result"])}', "small"))
    story.append(p("EDUCATION &amp; TRAINING", "section"))
    school = DATA["education"]
    story += [p(f'<b>{e(school["school"])}</b> | {e(school["year"])}', "small"), p(e(school["qualification"]), "small")]
    story += [p(e(DATA["training"]), "small"), p(e(DATA["languages"]), "small")]
    doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=32, bottomMargin=30,
                            title=f'{DATA["name"]} - Resume', author=DATA["name"], pageCompression=1)
    doc.build(story)
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copyfile(output, assets / PDF_NAME)
    print(f"Built {output}")


def build_text():
    lines = [DATA["name"], DATA["title"], DATA["location"], DATA["availability"], DATA["email"], DATA["phone"], f'https://t.me/{DATA["telegram"]}', DATA["linkedin"], "", "PROFILE", DATA["summary"], "", "CORE SKILLS"]
    lines += [f'{label}: {value}' for label, value in DATA["skills"]]
    lines += ["", "EXPERIENCE"]
    for job in DATA["experience"]:
        lines += ["", f'{job["company"]} | {job["role"]} | {job["start"]} - {job["end"]}']
        lines += [f'- {b}' for b in job["bullets"]]
    for job in DATA["earlier"]:
        lines += ["", f'{job["company"]} | {job["role"]} | {job["start"]} - {job["end"]}', job["result"]]
    school = DATA["education"]
    lines += ["", "EDUCATION & TRAINING", f'{school["school"]} | {school["year"]}', school["qualification"], DATA["training"], DATA["languages"]]
    (ROOT / "resume.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    build_html()
    build_pdf()
    build_text()
