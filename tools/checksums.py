from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ROOT / "runtime" / "windows-x64": ROOT / "manifests" / "runtime-windows-x64.sha256",
    ROOT / "seed-assets" / "asset-cache": ROOT / "manifests" / "asset-cache.sha256",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def generate(root: Path, manifest: Path) -> None:
    lines = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{digest(path)}  {path.stat().st_size:>12}  {rel}")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {manifest.relative_to(ROOT)} ({len(lines)} files)")


def verify(root: Path, manifest: Path) -> bool:
    if not manifest.exists():
        print(f"missing manifest: {manifest}", file=sys.stderr)
        return False
    expected = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        checksum, size, rel = line.split(maxsplit=2)
        expected[rel] = (checksum, int(size))
    actual_paths = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    ok = True
    for rel, (checksum, size) in expected.items():
        path = actual_paths.pop(rel, None)
        if path is None:
            print(f"missing: {root.name}/{rel}", file=sys.stderr)
            ok = False
            continue
        if path.stat().st_size != size:
            print(f"size mismatch: {root.name}/{rel}", file=sys.stderr)
            ok = False
            continue
        if digest(path) != checksum:
            print(f"hash mismatch: {root.name}/{rel}", file=sys.stderr)
            ok = False
    for rel in sorted(actual_paths):
        print(f"untracked by manifest: {root.name}/{rel}", file=sys.stderr)
        ok = False
    print(f"{'verified' if ok else 'failed'} {manifest.relative_to(ROOT)} ({len(expected)} files)")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["generate", "verify"])
    args = parser.parse_args()
    if args.command == "generate":
        for root, manifest in TARGETS.items():
            generate(root, manifest)
        return 0
    return 0 if all(verify(root, manifest) for root, manifest in TARGETS.items()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
