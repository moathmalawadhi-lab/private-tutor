#!/usr/bin/env python3
"""Render a summary HTML fragment into a styled PDF.

Usage: python make_pdf.py summary.html out.pdf --title "Book - Summary" --lang ar

Uses WeasyPrint if installed, otherwise headless Chrome / Edge / Chromium.
"""
import argparse
import html
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RTL_LANGS = {"ar", "fa", "he", "ur", "ps", "yi"}

# Google Fonts load when online; the local fallbacks cover offline use.
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&family=Noto+Sans:wght@400;700&display=swap');
@page { size: A4; margin: 18mm 16mm 20mm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #888; } }
body { font-family: 'Noto Sans', 'Noto Naskh Arabic', 'Segoe UI', Tahoma, Arial, sans-serif;
  font-size: 11.5pt; line-height: 1.7; color: #1d1d1f; }
:lang(ar), :lang(fa), :lang(ur) { font-family: 'Noto Naskh Arabic', 'Segoe UI', Tahoma, Arial, sans-serif; }
h1 { font-size: 24pt; color: #1a4d8f; border-bottom: 3px solid #1a4d8f; padding-bottom: 6px; }
h2 { font-size: 17pt; color: #1a4d8f; break-before: page; margin-top: 0; }
h1 + .meta + h2, h1 + h2 { break-before: auto; }
h3 { font-size: 13pt; color: #333; margin-bottom: 4px; }
h2, h3 { break-after: avoid; }
.meta { color: #666; font-size: 10pt; }
.def, .formula, .tip, .warn { padding: 8px 12px; margin: 10px 0; border-radius: 6px; break-inside: avoid;
  border-inline-start: 4px solid; }
.def { background: #eef4fc; border-color: #1a4d8f; }
.formula { background: #f6f6f6; border-color: #555; text-align: center; font-size: 13pt; direction: ltr; }
.tip { background: #eefaf0; border-color: #2e8b57; }
.warn { background: #fff4e5; border-color: #d9822b; }
.answer { color: #2e6b45; margin: 2px 0 10px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 5px 8px; text-align: start; vertical-align: top; }
th { background: #eef4fc; }
"""


def find_browser():
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge", "microsoft-edge"):
        if path := shutil.which(name):
            return path
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    return next((p for p in candidates if os.path.exists(p)), None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("body", help="HTML fragment with the summary content")
    ap.add_argument("out", help="output PDF path")
    ap.add_argument("--title", default="Summary")
    ap.add_argument("--lang", default="en", help="summary language code, e.g. ar, en")
    args = ap.parse_args()

    body = Path(args.body).read_text(encoding="utf-8")
    lang = args.lang.lower()
    direction = "rtl" if lang.split("-")[0] in RTL_LANGS else "ltr"
    doc = (f'<!doctype html><html lang="{lang}" dir="{direction}"><head><meta charset="utf-8">'
           f"<title>{html.escape(args.title)}</title><style>{CSS}</style></head><body>{body}</body></html>")
    out = Path(args.out).resolve()

    try:
        from weasyprint import HTML
        HTML(string=doc, base_url=str(Path(args.body).resolve().parent)).write_pdf(out)
        print(f"PDF written (WeasyPrint): {out}")
        return
    except ImportError:
        pass

    browser = find_browser()
    if not browser:
        sys.exit("No PDF engine found. Run `pip install weasyprint` or install Chrome/Edge, then retry.")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "summary.html"
        page.write_text(doc, encoding="utf-8")
        subprocess.run([browser, "--headless", "--disable-gpu", "--no-sandbox",
                        f"--user-data-dir={tmp}", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                        "--virtual-time-budget=10000", f"--print-to-pdf={out}", page.as_uri()],
                       check=True, capture_output=True)
    if not out.exists():
        sys.exit("Browser ran but no PDF was produced.")
    print(f"PDF written (headless browser): {out}")


if __name__ == "__main__":
    main()
