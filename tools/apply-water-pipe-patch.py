from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELATIVE_ASSETS = [
    Path("game/assets/buildings/1/top.1.png"),
    Path("game/assets/buildings/1/anim.1.png"),
    Path("game/assets/buildingbuttons/1-1-s.jpg"),
]


def md5(path: Path) -> str:
    h = hashlib.md5()  # Required by the recovered launcher's cache manifest format.
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def update_manifest(cache_root: Path) -> None:
    manifest_path = cache_root / ".cache-manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"version": 1, "files": {}}
    data.setdefault("version", 1)
    data.setdefault("files", {})
    for rel in RELATIVE_ASSETS:
        path = cache_root / rel
        stat = path.stat()
        data["files"][rel.as_posix()] = {
            "hash": md5(path),
            "mtimeMs": stat.st_mtime_ns / 1_000_000,
            "size": stat.st_size,
        }
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply or restore the recovered darker-brown water-pipe asset set.")
    parser.add_argument("cache_root", type=Path)
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    cache_root = args.cache_root.resolve()
    source_kind = "original-assets" if args.restore else "patched-assets"
    source_root = ROOT / "patches" / "water-pipe" / source_kind
    for rel in RELATIVE_ASSETS:
        src = source_root / rel
        dst = cache_root / rel
        if not src.exists():
            raise FileNotFoundError(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    update_manifest(cache_root)
    print(("Restored original" if args.restore else "Applied darker-brown") + f" water-pipe assets in {cache_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
