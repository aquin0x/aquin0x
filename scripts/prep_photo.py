"""One-off photo prep for the ASCII portrait: cut background, boost local contrast, put on white.

    pip install -r scripts/requirements-portrait.txt
    python scripts/prep_photo.py my-photo.jpg        # -> assets/source-prepped.png
    python scripts/make_ascii_svg.py
"""

import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = os.path.join(os.path.dirname(__file__), "..")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/prep_photo.py <photo>")
    cut = remove(Image.open(sys.argv[1]).convert("RGB"))  # RGBA, background transparent
    rgba = np.asarray(cut)
    gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
    alpha = rgba[..., 3].astype(np.float32) / 255.0
    out = (gray * alpha + 255 * (1 - alpha)).astype(np.uint8)  # composite onto pure white
    dst = os.path.join(ROOT, "assets", "source-prepped.png")
    Image.fromarray(out, "L").save(dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
