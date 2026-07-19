"""Render catalogue PDF pages to JPEGs + build contact-sheet montages for curation.

usage: python pdf_extract.py <pdf-dir> <out-dir>
  out-dir/pages/<name>/p001.jpg ...   (720px wide, for curation + later hi-res re-render)
  out-dir/sheets/<name>-1.png ...     (contact sheets, 6 cols, filename captions)
"""
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

COLS, THUMB_W, CAP = 6, 300, 22
PAGE_W = 720

def render(pdf_path: Path, pages_dir: Path):
    doc = fitz.open(pdf_path)
    out = pages_dir / pdf_path.stem
    out.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(doc, 1):
        scale = PAGE_W / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        pix.save(out / f"p{i:03d}.jpg", jpg_quality=82)
    n = doc.page_count
    doc.close()
    return n

def sheet(pages_dir: Path, sheets_dir: Path, name: str):
    files = sorted((pages_dir / name).glob("p*.jpg"))
    sheets_dir.mkdir(parents=True, exist_ok=True)
    per_sheet = COLS * 6
    for s in range(0, len(files), per_sheet):
        chunk = files[s : s + per_sheet]
        thumbs = []
        for f in chunk:
            im = Image.open(f)
            th = int(im.height * THUMB_W / im.width)
            thumbs.append((f.stem, im.resize((THUMB_W, th))))
        row_h = max(t.height for _, t in thumbs) + CAP
        rows = (len(thumbs) + COLS - 1) // COLS
        canvas = Image.new("RGB", (COLS * THUMB_W, rows * row_h), "white")
        d = ImageDraw.Draw(canvas)
        for i, (stem, t) in enumerate(thumbs):
            x, y = (i % COLS) * THUMB_W, (i // COLS) * row_h
            canvas.paste(t, (x, y))
            d.text((x + 4, y + t.height + 3), stem, fill="black")
        canvas.save(sheets_dir / f"{name}-{s // per_sheet + 1}.png")

if __name__ == "__main__":
    pdf_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    for pdf in sorted(pdf_dir.glob("*.pdf")):
        n = render(pdf, out_dir / "pages")
        sheet(out_dir / "pages", out_dir / "sheets", pdf.stem)
        print(f"{pdf.stem}: {n} pages")
