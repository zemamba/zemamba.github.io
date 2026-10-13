"""Build both localized websites, plain-text resumes, and US Letter PDFs.

Usage: python3 tools/build_resume.py (requires reportlab).
Resume content lives in resume.json and resume.ru.json.
"""
import html
import json
import shutil
from pathlib import Path
from string import Template

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
PDF_NAMES = {
    "en": "Alexander-Belskiy-Resume.pdf",
    "ru": "Alexander-Belskiy-Resume-RU.pdf",
}
LABELS = {
    "en": {
        "skip_label": "Skip to resume", "language_label": "Language", "contact_label": "Contact",
        "download_label": "Download resume", "alternate_download_label": "Russian PDF",
        "page_label": "1 page", "profile_label": "Profile", "skills_label": "Core skills",
        "experience_label": "Experience", "earlier_label": "Earlier experience",
        "education_label": "Education & training", "links_label": "Links",
        "updated_label": "Updated October 2026",
    },
    "ru": {
        "skip_label": "Перейти к резюме", "language_label": "Язык", "contact_label": "Контакты",
        "download_label": "Скачать резюме", "alternate_download_label": "PDF на английском",
        "page_label": "1 страница", "profile_label": "О себе", "skills_label": "Ключевые навыки",
        "experience_label": "Опыт работы", "earlier_label": "Предыдущий опыт",
        "education_label": "Образование и курсы", "links_label": "Ссылки",
        "updated_label": "Обновлено в октябре 2026",
    },
}
e = html.escape


def build_html(data, lang):
    fields = {key: e(value) for key, value in data.items() if isinstance(value, str)}
    fields.update({key: e(value) for key, value in data["education"].items()})
    fields.update({key: e(value) for key, value in LABELS[lang].items()})
    other = "ru" if lang == "en" else "en"
    fields.update({
        "lang": lang,
        "description": e(data["summary"]),
        "canonical": "https://zemamba.github.io/ru/" if lang == "ru" else "https://zemamba.github.io/",
        "asset_prefix": "../assets/" if lang == "ru" else "assets/",
        "pdf_name": PDF_NAMES[lang], "other_pdf_name": PDF_NAMES[other], "other_lang": other,
        "en_current": 'aria-current="page"' if lang == "en" else "",
        "ru_current": 'aria-current="page"' if lang == "ru" else "",
    })
    fields["skills"] = "\n".join(
        f'<div><dt>{e(label)}</dt><dd>{e(value)}</dd></div>'
        for label, value in data["skills"])
    jobs = []
    for job in data["experience"]:
        bullets = "".join(f'<li>{e(b)}</li>' for b in job["bullets"])
        jobs.append(f'''<article class="job">
        <div class="job-heading"><h3>{e(job["company"])}</h3><p class="dates">{e(job["start"])} – {e(job["end"])}</p></div>
        <p class="role">{e(job["role"])}</p><ul>{bullets}</ul>
      </article>''')
    fields["experience"] = "\n".join(jobs)
    fields["earlier"] = "".join(
        f'<li><strong>{e(j["company"])}</strong> · {e(j["role"])} '
        f'<span class="earlier-dates">({e(j["start"])} – {e(j["end"])})</span>. {e(j["result"])}</li>'
        for j in data["earlier"])
    template = Template((ROOT / "tools" / "index.template.html").read_text())
    destination = ROOT / "index.html" if lang == "en" else ROOT / "ru" / "index.html"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(template.substitute(fields))


def ascii_punctuation(text):
    return text.replace("–", "-").replace("—", "-").replace("·", " | ")


def build_pdf(data, lang):
    output = ROOT / "output" / "pdf" / PDF_NAMES[lang]
    output.parent.mkdir(parents=True, exist_ok=True)
    if lang == "ru":
        font_dir = ROOT / "tools" / "fonts"
        pdfmetrics.registerFont(TTFont("DejaVu", str(font_dir / "DejaVuSansCondensed.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(font_dir / "DejaVuSansCondensed-Bold.ttf")))
        pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")
    normal = "DejaVu" if lang == "ru" else "Helvetica"
    bold = "DejaVu-Bold" if lang == "ru" else "Helvetica-Bold"
    scale = 0.92 if lang == "ru" else 1

    def style(name, font, size, leading, **options):
        return ParagraphStyle(name, fontName=font, fontSize=size * scale,
                              leading=leading * scale, **options)

    styles = {
        "name": style("name", bold, 22, 25, spaceAfter=4),
        "title": style("title", normal, 11, 14, spaceAfter=4),
        "contact": style("contact", normal, 8.4, 11, textColor=colors.HexColor("#555555"), spaceAfter=3),
        "section": style("section", bold, 9, 12, spaceBefore=11 * scale, spaceAfter=5 * scale),
        "body": style("body", normal, 9.2, 12),
        "job": style("job", bold, 9.4, 12, spaceBefore=6 * scale, spaceAfter=3 * scale),
        "bullet": style("bullet", normal, 9.2, 12, leftIndent=9, firstLineIndent=-9, spaceAfter=2 * scale),
        "small": style("small", normal, 8.8, 11.5, spaceAfter=3 * scale),
    }

    def p(text, style="body"):
        return Paragraph(ascii_punctuation(text), styles[style])

    story = [p(e(data["name"]), "name"), p(e(data["title"]), "title")]
    story += [p(f'{e(data["location"])} | {e(data["phone"])} | <link href="mailto:{data["email"]}">{e(data["email"])}</link>', "contact")]
    story += [p(f'<link href="{data["linkedin"]}">linkedin.com/in/abelskiy</link> | <link href="https://t.me/{data["telegram"]}">t.me/{data["telegram"]}</link> | <link href="https://zemamba.github.io/">zemamba.github.io</link>', "contact")]
    story += [p(e(data["availability"]), "contact"), p(e(LABELS[lang]["profile_label"]).upper(), "section"), p(e(data["summary"]))]
    story += [p(e(LABELS[lang]["skills_label"]).upper(), "section")]
    for label, value in data["skills"]:
        story.append(p(f'<b>{e(label)}:</b> {e(value)}', "small"))
    story.append(p(e(LABELS[lang]["experience_label"]).upper(), "section"))
    for job in data["experience"]:
        group = [p(f'{e(job["company"])} | {e(job["role"])} | {e(job["start"])} - {e(job["end"])}', "job")]
        group += [p(f'• {e(b)}', "bullet") for b in job["bullets"]]
        story.append(KeepTogether(group))
    story.append(Spacer(1, 6))
    for job in data["earlier"]:
        story.append(p(f'<b>{e(job["company"])}:</b> {e(job["role"])} ({e(job["start"])} - {e(job["end"])}). {e(job["result"])}', "small"))
    story.append(p(e(LABELS[lang]["education_label"]).upper(), "section"))
    school = data["education"]
    story += [p(f'<b>{e(school["school"])}</b> | {e(school["year"])}', "small"), p(e(school["qualification"]), "small")]
    story += [p(e(data["training"]), "small"), p(e(data["languages"]), "small")]
    doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=32, bottomMargin=30,
                            title=f'{data["name"]} - Resume', author=data["name"], pageCompression=1)
    doc.build(story)
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copyfile(output, assets / PDF_NAMES[lang])
    print(f"Built {output}")


def build_text(data, lang):
    lines = [data["name"], data["title"], data["location"], data["availability"], data["email"], data["phone"], f'https://t.me/{data["telegram"]}', data["linkedin"], "", LABELS[lang]["profile_label"].upper(), data["summary"], "", LABELS[lang]["skills_label"].upper()]
    lines += [f'{label}: {value}' for label, value in data["skills"]]
    lines += ["", LABELS[lang]["experience_label"].upper()]
    for job in data["experience"]:
        lines += ["", f'{job["company"]} | {job["role"]} | {job["start"]} - {job["end"]}']
        lines += [f'- {b}' for b in job["bullets"]]
    for job in data["earlier"]:
        lines += ["", f'{job["company"]} | {job["role"]} | {job["start"]} - {job["end"]}', job["result"]]
    school = data["education"]
    lines += ["", LABELS[lang]["education_label"].upper(), f'{school["school"]} | {school["year"]}', school["qualification"], data["training"], data["languages"]]
    output = ROOT / "resume.txt" if lang == "en" else ROOT / "ru" / "resume.txt"
    output.parent.mkdir(exist_ok=True)
    output.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    for locale, filename in (("en", "resume.json"), ("ru", "resume.ru.json")):
        resume = json.loads((ROOT / filename).read_text())
        build_html(resume, locale)
        build_pdf(resume, locale)
        build_text(resume, locale)
