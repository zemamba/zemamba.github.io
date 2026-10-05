# Alexander Belskiy — Resume

Minimal, responsive resume website at https://zemamba.github.io/.
GitHub Pages publishes the repository root from `main`.

## Update the resume

Edit `resume.json`, then rebuild the HTML, plain text, and one-page US Letter PDF:

```sh
python3 -m pip install reportlab
python3 tools/build_resume.py
```

Review `index.html` and `output/pdf/Alexander-Belskiy-Resume.pdf` before publishing.
The download button serves the same PDF from `assets/Alexander-Belskiy-Resume.pdf`.
Check that the PDF is still one page after content changes. Dates and education
follow the supplied resume; no academic degree equivalence is inferred.

For a local preview, run `python3 -m http.server 8000` from this directory.
The website has no JavaScript or framework dependency. Inter is loaded
from Google Fonts, with system fonts as a fallback.
