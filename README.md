# Alexander Belskiy — Resume

Minimal, responsive bilingual resume website at https://zemamba.github.io/.
GitHub Pages publishes the repository root from `main`.
The English page is at `/`; the Russian page is at `/ru/`. Each page offers
the PDF in its own language.

## Update the resume

Edit `resume.json` and `resume.ru.json`, then rebuild both HTML pages, plain-text
resumes, and one-page US Letter PDFs:

```sh
python3 -m pip install reportlab
python3 tools/build_resume.py
```

Review `index.html`, `ru/index.html`, and both PDFs in `output/pdf/` before
publishing. The buttons serve copies from `assets/`. Check that each PDF is
still one page after content changes. Dates and education follow the supplied
resume; no academic degree equivalence is inferred.

For a local preview, run `python3 -m http.server 8000` from this directory.
The homepage detects the browser's preferred language and redirects Russian
visitors to `/ru/`. The language switch saves an explicit EN/RU choice in
`localStorage`; direct visits to `/ru/` are never redirected. If JavaScript or
storage is unavailable, both pages and their language links remain usable.
Inter is loaded from Google Fonts, with system fonts as a fallback.
The PDF builder uses the bundled DejaVu Sans Condensed fonts for Cyrillic;
their redistribution terms are in `tools/fonts/LICENSE-DejaVu.txt`.
