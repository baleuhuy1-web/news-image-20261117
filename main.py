"""Deliver the day's news image to the grader's output directory.

The composed front page lives beside this file as ``entry.png``.  Running
the program copies it to ``entry.png`` inside the directory named by the
MAKEFUN_OUTPUT_DIR environment variable (``/output`` by default), which
is where the make.fun harness looks for it.  Standard library only, and
no network access is needed.
"""

import filecmp
import os
import shutil
import struct
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
MAX_BYTES = 1_048_576  # the competition's 1 MiB cap
MAX_SIDE = 1024        # the competition's per-side pixel cap
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def check_source(path: Path) -> None:
    """Fail loudly if the bundled image breaks the entry rules."""
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"{path.name} is {len(data)} bytes, over the cap")
    if data[:8] != PNG_SIGNATURE:
        raise SystemExit(f"{path.name} is not a PNG file")
    width, height = struct.unpack(">II", data[16:24])  # IHDR dimensions
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(f"{path.name} is {width}x{height}, over the cap")


def main() -> None:
    check_source(SOURCE)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    if not filecmp.cmp(SOURCE, target, shallow=False):
        raise SystemExit("copied entry.png does not match the source")


if __name__ == "__main__":
    main()
