"""Rewrite <img src=jpg srcset=avif...> into <picture> with AVIF + WebP sources
and a responsive JPEG fallback. Safari without AVIF support would otherwise show
broken images (srcset candidates do not fall back to src).

usage: python to_picture.py <file.html> [more.html ...]
"""
import re
import sys
from pathlib import Path

IMG_RE = re.compile(r"<img\s+([^>]*?srcset=\"[^\"]*avif[^\"]*\"[^>]*?)>", re.DOTALL)
ATTR_RE = re.compile(r"([a-zA-Z-]+)=\"([^\"]*)\"")

def rewrite(match: re.Match) -> str:
    attrs = dict(ATTR_RE.findall(match.group(1)))
    avif = attrs.pop("srcset")
    sizes = attrs.get("sizes", "")
    webp = avif.replace(".avif", ".webp")
    jpg = avif.replace(".avif", ".jpg")

    # indentation of the original tag
    line_start = match.string.rfind("\n", 0, match.start()) + 1
    indent = ""
    for ch in match.string[line_start:match.start()]:
        indent += ch if ch in " \t" else ""

    img_attrs = []
    for k, v in attrs.items():
        img_attrs.append(f'{k}="{v}"')
        if k == "src":
            img_attrs.append(f'srcset="{jpg}"')
    if "loading" in attrs and "decoding" not in attrs:
        img_attrs.append('decoding="async"')

    inner = indent + "  "
    return (
        f"<picture>\n"
        f'{inner}<source type="image/avif" srcset="{avif}" sizes="{sizes}">\n'
        f'{inner}<source type="image/webp" srcset="{webp}" sizes="{sizes}">\n'
        f'{inner}<img {" ".join(img_attrs)}>\n'
        f"{indent}</picture>"
    )

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        html = p.read_text(encoding="utf-8")
        new, n = IMG_RE.subn(rewrite, html)
        p.write_text(new, encoding="utf-8", newline="")
        print(f"{p.name}: {n} images wrapped")
