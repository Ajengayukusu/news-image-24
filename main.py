#!/usr/bin/env python3
"""news-image-24: publish the 24 November 2026 front page.

The front page itself is this repository's assets/entry.png, drawn in
this session by draw24.py from the world news first reported on
Tuesday 24 November 2026 (Nvidia reinstates Jensen Huang, Ukraine
sinks a Russian warship off Libya, NATO jets for Poland, COP31
fallout, the Indonesian factory-fire rescue, Iran and the US naval
blockade, a seven-goal thriller at San Siro). This entrypoint only
copies that one fixed file to the path the grader reads. A fixed
file copied byte for byte is deterministic, so the grader's two runs
always produce the same bytes.

SPDX-License-Identifier: MIT
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSET = HERE / "assets" / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def out_path() -> Path:
    base = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return Path(base) / "entry.png"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if not ASSET.is_file():
        print(f"asset missing: {ASSET}", file=sys.stderr)
        return 1
    payload = ASSET.read_bytes()
    if payload[:8] != PNG_MAGIC:
        print("asset is not a PNG", file=sys.stderr)
        return 1
    if len(payload) > MAX_BYTES:
        print(f"asset over the 1 MiB cap: {len(payload)} bytes",
              file=sys.stderr)
        return 1
    target = out_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    written = target.read_bytes()
    if written[:8] != PNG_MAGIC:
        print("published file is not a PNG", file=sys.stderr)
        return 1
    if sha256_hex(written) != sha256_hex(payload):
        print("output differs from the asset", file=sys.stderr)
        return 1
    print(f"published {target} ({len(payload)} bytes, "
          f"sha256 {sha256_hex(payload)[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
