"""Hi-res render of curated catalogue pages -> master PNGs (+ verification montage).

usage: python make_masters.py <pdf-dir> <masters-dir>
Crops are applied in a second pass (see crop map below) after visual verification.
"""
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

# (pdf_stem, page_1based, rotate_deg_ccw, out_name)
PICKS = [
    ("vetrate-panoramiche", 15, 270, "vetrate-piscina"),
    ("vetrate-panoramiche", 17, 270, "vetrate-notte"),
    ("vetrate-panoramiche", 31, 270, "vetrate-pergola"),
    ("vetrate-panoramiche", 37, 270, "vetrate-tramonto"),
    ("vetrate-panoramiche", 46, 270, "vetrate-cortile"),
    ("collezione-materica", 15, 270, "materica-essenze"),
    ("collezione-materica", 28, 270, "materica-salotto"),
    ("porte-interni", 4, 0, "porte-scena"),
    ("porte-interni", 19, 0, "porte-bianche"),
    ("porte-filomuro", 1, 0, "filomuro-cover"),
    ("serramenti-pvc", 1, 0, "pvc-cover"),
    ("serramenti-pvc", 12, 0, "pvc-camino"),
    ("pedana-termica", 7, 0, "pedana-flyer"),
    ("collezione-loft-lumina", 1, 0, "loftlumina-cover"),
    ("porte-collezione-2025", 22, 0, "collezione2025-finiture"),
    ("porte-collezione-2025", 32, 0, "collezione2025-ral"),
    ("porte-rei", 1, 0, "rei-cover"),
    ("porte-tagliafuoco", 6, 0, "tagliafuoco-p6"),
    ("controtelai", 1, 0, "controtelai-cover"),
]

LONG_SIDE = 2400

def main(pdf_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for stem, pno, rot, name in PICKS:
        doc = fitz.open(pdf_dir / f"{stem}.pdf")
        page = doc[pno - 1]
        scale = LONG_SIDE / max(page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if rot:
            img = img.rotate(rot, expand=True)
        img.save(out_dir / f"{name}.png")
        thumbs.append((name, img))
        doc.close()

    # verification montage
    cols, tw, cap = 5, 330, 24
    scaled = []
    for name, im in thumbs:
        th = int(im.height * tw / im.width)
        scaled.append((name, im.resize((tw, th))))
    row_h = max(t.height for _, t in scaled) + cap
    rows = (len(scaled) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw, rows * row_h), "white")
    d = ImageDraw.Draw(canvas)
    for i, (name, t) in enumerate(scaled):
        x, y = (i % cols) * tw, (i // cols) * row_h
        canvas.paste(t, (x, y))
        d.text((x + 4, y + t.height + 3), name, fill="red")
    canvas.save(out_dir / "_verify.png")
    print(f"{len(thumbs)} masters -> {out_dir}")

if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
