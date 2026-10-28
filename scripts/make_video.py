#!/usr/bin/env python3
"""Render a lesson (slides + narration) into an MP4 video.

Usage: python make_video.py lesson.json out.mp4 --lang ar [--voice ar-KW-FahedNeural]

lesson.json:
  {"title": "Lesson 1 - ...",
   "slides": [{"html": "<h1>...</h1><p>...</p>", "say": "narration for this slide"}, ...]}

Needs: pip install edge-tts imageio-ffmpeg truststore (or ffmpeg on PATH), Chrome/Edge/Chromium, internet for the voice.
"""
import argparse
import asyncio
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from make_pdf import RTL_LANGS, find_browser

DEFAULT_VOICES = {"ar": "ar-SA-HamedNeural", "en": "en-US-AndrewNeural", "fr": "fr-FR-HenriNeural",
                  "es": "es-ES-AlvaroNeural", "de": "de-DE-ConradNeural", "tr": "tr-TR-AhmetNeural",
                  "ur": "ur-PK-AsadNeural", "fa": "fa-IR-FaridNeural"}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;700&family=Noto+Sans:wght@400;700&display=swap');
html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; }
body { box-sizing: border-box; padding: 90px 130px; background: linear-gradient(135deg, #f7f9fc, #e8eef8);
  font-family: 'Noto Sans', 'Noto Naskh Arabic', 'Segoe UI', Tahoma, Arial, sans-serif;
  font-size: 46px; line-height: 1.6; color: #1d1d1f; display: flex; flex-direction: column; justify-content: center; }
:lang(ar), :lang(fa), :lang(ur) { font-family: 'Noto Naskh Arabic', 'Segoe UI', Tahoma, Arial, sans-serif; }
h1 { font-size: 84px; color: #1a4d8f; margin: 0 0 30px; line-height: 1.3; }
h2 { font-size: 64px; color: #1a4d8f; margin: 0 0 30px; border-bottom: 5px solid #1a4d8f; padding-bottom: 12px; }
p, ul, ol { margin: 14px 0; } li { margin: 10px 0; }
.def, .formula, .tip, .warn { padding: 22px 34px; margin: 22px 0; border-radius: 16px; border-inline-start: 12px solid; }
.def { background: #dfeafa; border-color: #1a4d8f; }
.formula { background: #fff; border-color: #555; text-align: center; font-size: 64px; direction: ltr; }
.tip { background: #e2f5e7; border-color: #2e8b57; }
.warn { background: #fdebd3; border-color: #d9822b; }
.footer { position: fixed; bottom: 34px; inset-inline-start: 130px; font-size: 28px; color: #7a8699; }
table { border-collapse: collapse; width: 100%; } th, td { border: 2px solid #b8c4d6; padding: 12px 20px; text-align: start; }
th { background: #dfeafa; }
"""


def ffmpeg_exe():
    if path := shutil.which("ffmpeg"):
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found. Run `pip install imageio-ffmpeg` or install ffmpeg.")


async def tts(text, voice, out):
    try:  # use the OS certificate store (fixes SSL errors behind antivirus/corporate proxies on Windows)
        import truststore
        truststore.inject_into_ssl()
    except ImportError:
        pass
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson", help="lesson JSON file")
    ap.add_argument("out", help="output MP4 path")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--voice", help="edge-tts voice name (list: python -m edge_tts --list-voices)")
    args = ap.parse_args()

    lesson = json.loads(Path(args.lesson).read_text(encoding="utf-8"))
    lang = args.lang.lower()
    base = lang.split("-")[0]
    voice = args.voice or DEFAULT_VOICES.get(base)
    if not voice:
        sys.exit(f"No default voice for '{lang}'; pass --voice (see python -m edge_tts --list-voices).")
    direction = "rtl" if base in RTL_LANGS else "ltr"
    browser = find_browser()
    if not browser:
        sys.exit("Chrome, Edge or Chromium is required to draw the slides.")
    ffmpeg = ffmpeg_exe()
    out = Path(args.out).resolve()
    footer = html.escape(lesson.get("title", ""))
    slides = lesson["slides"]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        segments = []
        for i, slide in enumerate(slides, 1):
            print(f"slide {i}/{len(slides)}", flush=True)
            page, png, mp3, seg = (tmp / f"{i}.{ext}" for ext in ("html", "png", "mp3", "mp4"))
            page.write_text(f'<!doctype html><html lang="{lang}" dir="{direction}"><head><meta charset="utf-8">'
                            f"<style>{CSS}</style></head><body>{slide['html']}"
                            f'<div class="footer">{footer} · {i}/{len(slides)}</div></body></html>', encoding="utf-8")
            subprocess.run([browser, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                            f"--user-data-dir={tmp / 'profile'}", "--window-size=1920,1080",
                            "--virtual-time-budget=8000", f"--screenshot={png}", page.as_uri()],
                           check=True, capture_output=True)
            asyncio.run(tts(slide["say"], voice, mp3))
            # apad leaves a short pause after each slide; -shortest ends the looped image with the audio
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-i", str(mp3),
                            "-af", "apad=pad_dur=0.8", "-shortest", "-r", "24", "-c:v", "libx264", "-tune", "stillimage",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", str(seg)], check=True)
            segments.append(seg)

        listing = tmp / "list.txt"
        listing.write_text("".join(f"file '{s.as_posix()}'\n" for s in segments), encoding="utf-8")
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    print(f"Video written: {out}")


if __name__ == "__main__":
    main()
