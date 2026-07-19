"""Crop masters + encode site finals (AVIF/WebP/JPEG at responsive widths).

usage: python make_finals.py <masters-dir> <img-root> [--verify-only]
Writes <img-root>/<area>/<name>-<w>.{avif,webp,jpg} plus a _finals-verify.png montage
of the cropped sources so framing can be checked before/after encoding.
"""
import sys
from pathlib import Path

import pillow_avif  # noqa: F401  (registers AVIF codec)
from PIL import Image, ImageDraw

# name -> (master, crop (l, t, r, b) relative or None)
CROPS = {
    "hero-cortile": ("vetrate-cortile", (0.00, 0.00, 0.775, 0.79)),
    "row-porte": ("porte-bianche", (0.03, 0.045, 0.97, 0.555)),
    "row-serramenti": ("pvc-camino", (0.02, 0.02, 0.98, 0.98)),
    "row-vetrate": ("vetrate-notte", (0.00, 0.00, 0.655, 0.84)),
    "row-pedana": ("pedana-flyer", (0.045, 0.165, 0.955, 0.60)),
    "row-pergole": ("vetrate-pergola", (0.00, 0.25, 0.615, 1.00)),
    "row-piscine": ("vetrate-piscina", (0.00, 0.00, 0.63, 0.80)),
    "essenze": ("materica-essenze", (0.00, 0.00, 0.50, 1.00)),
    "tramonto-wide": ("vetrate-tramonto", (0.00, 0.00, 0.60, 0.80)),
    "c-collezione-2025": ("collezione2025-ral", None),
    "c-porte-interni": ("porte-scena", None),
    "c-filomuro": ("filomuro-cover", None),
    "c-materica": ("materica-salotto", (0.03, 0.00, 0.58, 0.965)),
    "c-loft-lumina": ("loftlumina-cover", None),
    "c-rei": ("rei-cover", (0.00, 0.00, 1.00, 0.845)),
    "c-tagliafuoco": ("tagliafuoco-p6", (0.015, 0.115, 0.50, 0.52)),
    "c-pvc": ("pvc-cover", None),
    "c-vetrate": ("vetrate-tramonto", (0.03, 0.00, 0.55, 0.80)),
    "c-pedana": ("pedana-flyer", (0.28, 0.15, 0.72, 0.60)),
    "c-controtelai": ("controtelai-cover", None),
    "logo": ("pvc-cover", (0.10, 0.02, 0.60, 0.14)),
}

# name -> (area-dir, widths)
OUT = {
    "hero-cortile": ("home", [480, 960, 1600]),
    "essenze": ("home", [480, 960, 1600]),
    "tramonto-wide": ("home", [480, 960, 1600]),
    "row-porte": ("prodotti", [480, 960]),
    "row-serramenti": ("prodotti", [480, 960]),
    "row-vetrate": ("prodotti", [480, 960]),
    "row-pedana": ("prodotti", [480, 960]),
    "row-pergole": ("prodotti", [480, 960]),
    "row-piscine": ("prodotti", [480, 960]),
    "c-collezione-2025": ("cataloghi/covers", [480, 960]),
    "c-porte-interni": ("cataloghi/covers", [480, 960]),
    "c-filomuro": ("cataloghi/covers", [480, 960]),
    "c-materica": ("cataloghi/covers", [480, 960]),
    "c-loft-lumina": ("cataloghi/covers", [480, 960]),
    "c-rei": ("cataloghi/covers", [480, 960]),
    "c-tagliafuoco": ("cataloghi/covers", [480, 960]),
    "c-pvc": ("cataloghi/covers", [480, 960]),
    "c-vetrate": ("cataloghi/covers", [480, 960]),
    "c-pedana": ("cataloghi/covers", [480, 960]),
    "c-controtelai": ("cataloghi/covers", [480, 960]),
    "logo": ("", [600]),
}

def main(masters: Path, img_root: Path, verify_only: bool):
    cropped = {}
    for name, (master, crop) in CROPS.items():
        im = Image.open(masters / f"{master}.png").convert("RGB")
        if crop:
            l, t, r, b = crop
            im = im.crop((int(l * im.width), int(t * im.height), int(r * im.width), int(b * im.height)))
        cropped[name] = im

    # verification montage
    cols, tw, cap = 6, 300, 22
    scaled = [(n, im.resize((tw, int(im.height * tw / im.width)))) for n, im in cropped.items()]
    row_h = max(t.height for _, t in scaled) + cap
    rows = (len(scaled) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw, rows * row_h), "white")
    d = ImageDraw.Draw(canvas)
    for i, (n, t) in enumerate(scaled):
        x, y = (i % cols) * tw, (i // cols) * row_h
        canvas.paste(t, (x, y))
        d.text((x + 4, y + t.height + 3), n, fill="red")
    canvas.save(masters / "_finals-verify.png")
    if verify_only:
        print("verify montage only")
        return

    total = 0
    for name, im in cropped.items():
        area, widths = OUT[name]
        out_dir = img_root / area if area else img_root
        out_dir.mkdir(parents=True, exist_ok=True)
        for w in widths:
            if w >= im.width:
                scaled_im = im
                w = im.width
            else:
                scaled_im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
            if name == "logo":
                scaled_im.save(out_dir / f"{name}-{w}.png")
                total += 1
                continue
            scaled_im.save(out_dir / f"{name}-{w}.avif", quality=62)
            scaled_im.save(out_dir / f"{name}-{w}.webp", quality=80, method=6)
            scaled_im.save(out_dir / f"{name}-{w}.jpg", quality=82, optimize=True, progressive=True)
            total += 3
        print(f"{name}: {im.width}x{im.height} -> {widths}")
    print(f"{total} files -> {img_root}")

if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), "--verify-only" in sys.argv)
