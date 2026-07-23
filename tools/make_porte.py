"""Render + crop + encode door/scene photography for the home Porte section
and extra bands. Two modes:
  verify  : render candidate pages full at 1000px into a montage for crop-picking
  encode  : apply CROPS and emit AVIF/WebP/JPEG at the given widths

usage: python make_porte.py <pdf-dir> <img-root> verify|encode
"""
import sys
from pathlib import Path

import fitz
import pillow_avif  # noqa: F401
from PIL import Image, ImageDraw

# candidate pages to inspect in verify mode
CANDIDATES = [
    ("porte-interni", 4), ("porte-interni", 9), ("porte-interni", 13),
    ("porte-interni", 19), ("porte-filomuro", 1), ("porte-filomuro", 3),
]

# name -> (pdf_stem, page_1based, crop (l,t,r,b) relative, widths)
JOBS = {
    "porte/interni-uvlam": ("porte-interni", 9,  (0.00, 0.00, 0.605, 1.00), [480, 960]),
    "porte/hotel":         ("porte-rei", 1,      (0.00, 0.325, 1.00, 0.795), [480, 960, 1440]),
    "porte/filomuro":      ("porte-filomuro", 1, (0.00, 0.42, 1.00, 1.00),  [480, 960, 1440]),
}

LONG = 3100

def render(pdf_dir, stem, pno):
    doc = fitz.open(pdf_dir / f"{stem}.pdf")
    page = doc[pno - 1]
    scale = LONG / max(page.rect.width, page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img

def main(pdf_dir, img_root, mode):
    if mode == "verify":
        thumbs = []
        for stem, pno in CANDIDATES:
            im = render(pdf_dir, stem, pno)
            tw = 460
            thumbs.append((f"{stem}-p{pno:03d}", im.resize((tw, round(im.height * tw / im.width)))))
        cols = 3
        rowh = max(t.height for _, t in thumbs) + 24
        rows = (len(thumbs) + cols - 1) // cols
        canvas = Image.new("RGB", (cols * 460, rows * rowh), "white")
        d = ImageDraw.Draw(canvas)
        for i, (n, t) in enumerate(thumbs):
            x, y = (i % cols) * 460, (i // cols) * rowh
            canvas.paste(t, (x, y))
            d.text((x + 4, y + t.height + 4), n, fill="red")
        (img_root / "_porte-verify.png").parent.mkdir(parents=True, exist_ok=True)
        canvas.save(img_root / "_porte-verify.png")
        print("verify montage ->", img_root / "_porte-verify.png")
        return

    for name, (stem, pno, crop, widths) in JOBS.items():
        im = render(pdf_dir, stem, pno)
        l, t, r, b = crop
        im = im.crop((int(l * im.width), int(t * im.height), int(r * im.width), int(b * im.height)))
        out = img_root / name
        out.parent.mkdir(parents=True, exist_ok=True)
        for w in widths:
            s = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if w < im.width else im
            ww = min(w, im.width)
            s.save(f"{out}-{ww}.avif", quality=62)
            s.save(f"{out}-{ww}.webp", quality=80, method=6)
            s.save(f"{out}-{ww}.jpg", quality=82, optimize=True, progressive=True)
        print(f"{name}: {im.width}x{im.height} -> {widths}")

if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
