"""Auto-extract the Fly System logo from a master page render via non-white bbox,
then report its dominant colors for palette tuning.

usage: python extract_logo.py <master.png> <out-dir>
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

def main(src: Path, out_dir: Path):
    im = Image.open(src).convert("RGB")
    # search the top band of the page where the logo sits
    band = im.crop((0, 0, im.width, int(im.height * 0.20)))
    # bbox of non-near-white pixels
    gray = band.convert("L").point(lambda v: 255 if v < 235 else 0)
    bbox = gray.getbbox()
    if not bbox:
        print("no non-white content found in top band")
        return
    pad = 14
    l, t, r, b = bbox
    logo = band.crop((max(0, l - pad), max(0, t - pad), min(band.width, r + pad), min(band.height, b + pad)))
    out_dir.mkdir(parents=True, exist_ok=True)
    logo.save(out_dir / "logo-600.png")
    logo.resize((300, int(logo.height * 300 / logo.width)), Image.LANCZOS).save(out_dir / "logo-300.png")
    print(f"logo: {logo.width}x{logo.height} bbox={bbox}")

    cnt = Counter()
    for px in logo.getdata():
        if sum(px) < 690:
            cnt[(px[0] // 12 * 12, px[1] // 12 * 12, px[2] // 12 * 12)] += 1
    for (cr, cg, cb), n in cnt.most_common(10):
        print(f"#{cr:02X}{cg:02X}{cb:02X}  {n}")

if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
