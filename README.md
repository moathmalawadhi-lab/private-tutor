# Private Tutor — مدرّس خصوصي لـ Claude

<div dir="rtl">

مهارة (Skill) تحوّل Claude إلى مدرّس خصوصي لأي مادة. ترفع كتاب المادة، و Claude:

1. **يقرأ الكتاب كاملاً** فصلاً فصلاً، ويتأكد إنه ما فوّت ولا فصل.
2. **يسوي خطة دروس** على حسب مستواك وهدفك (اختبار، واجب، فهم عام).
3. **يشرح لك المادة الملخصة درساً درساً بالفيديو**: كل درس فيديو (شرائح + صوت يشرح)، وبعده سؤال يتأكد فيه إنك فهمت قبل ما ينتقل للدرس اللي بعده. تقدر تختار اللهجة (كويتي، سعودي، مصري، إماراتي…).
4. **يسلمك ملخص المادة كاملة بملف PDF** بعد ما يخلص الشرح.

يدعم العربي (بإتجاه من اليمين لليسار) والإنجليزي وأي لغة ثانية.

## التثبيت

**Claude Code:**

```bash
git clone https://github.com/moathmalawadhi-lab/private-tutor ~/.claude/skills/private-tutor
```

**Claude.ai / تطبيق Claude:** حمّل المجلد كملف ZIP، ثم من *Settings → Capabilities → Skills* ارفعه.

## الاستخدام

ارفع الكتاب (PDF أو Word أو صور) واكتب مثلاً:

> هذا كتاب مادة الفيزياء، ابيك تشرحه لي، عندي اختبار بعد أسبوعين

Claude يكمل الباقي. إذا انقطعت المحادثة، Claude يحفظ تقدمك في ملف `plan.md` ويكمل من آخر درس.

</div>

---

## English

A Claude skill that turns Claude into a private tutor for any course book. Upload the book and Claude will:

1. **Read the entire book**, chapter by chapter, with a coverage check.
2. **Build a lesson plan** tailored to your level and goal.
3. **Teach the summarized material one lesson at a time through video** — narrated slides rendered to MP4 — followed by comprehension checks, adapting to your answers.
4. **Deliver the full summary as a PDF** once the course is finished.

Progress is saved in `plan.md`, so a course can resume in a new conversation.

### Install

- **Claude Code:** clone into `~/.claude/skills/private-tutor`.
- **Claude.ai:** download as ZIP and upload under *Settings → Capabilities → Skills*.

### Requirements

- **Lesson videos** (`scripts/make_video.py`): `pip install edge-tts imageio-ffmpeg truststore`, Chrome/Edge/Chromium, and internet access (voices come from Microsoft Edge's free TTS). If video can't be rendered, Claude teaches the lesson as text.
- **Summary PDF** (`scripts/make_pdf.py`): [WeasyPrint](https://weasyprint.org) or Chrome/Edge/Chromium.

See `example-lesson.mp4` and `example-summary.pdf` for sample output.

## License

MIT
