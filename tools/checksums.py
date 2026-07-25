from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "seed-assets" / "asset-cache"
ASSET_MANIFEST = ROOT / "manifests" / "asset-cache.sha256"
RUNTIME_ROOT = ROOT / "runtime" / "windows-x64"
RUNTIME_MANIFEST = ROOT / "manifests" / "runtime-windows-x64.sha256"
PAYLOAD_ROOT = ROOT / "payloads" / "runtime-windows-x64"
PAYLOAD_MANIFEST = ROOT / "manifests" / "runtime-payload-parts.sha256"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(manifest: Path) -> dict[str, tuple[str, int]]:
    expected: dict[str, tuple[str, int]] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        checksum, size, rel = line.split(maxsplit=2)
        expected[rel] = (checksum, int(size))
    return expected


def generate_tree(root: Path, manifest: Path) -> None:
    lines = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{digest(path)}  {path.stat().st_size:>12}  {rel}")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {manifest.relative_to(ROOT)} ({len(lines)} files)")


def generate_parts() -> None:
    parts = sorted(PAYLOAD_ROOT.glob("runtime-windows-x64.zip.part*"))
    lines = [f"{digest(path)}  {path.stat().st_size:>12}  {path.name}" for path in parts]
    PAYLOAD_MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {PAYLOAD_MANIFEST.relative_to(ROOT)} ({len(lines)} files)")


def verify(root: Path, manifest: Path, label: str) -> bool:
    if not manifest.exists():
        print(f"missing manifest: {manifest}", file=sys.stderr)
        return False
    if not root.exists():
        print(f"missing directory: {root}", file=sys.stderr)
        return False
    expected = parse_manifest(manifest)
    actual_paths = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    ok = True
    for rel, (checksum, size) in expected.items():
        path = actual_paths.pop(rel, None)
        if path is None:
            print(f"missing: {label}/{rel}", file=sys.stderr)
            ok = False
            continue
        if path.stat().st_size != size:
            print(f"size mismatch: {label}/{rel}", file=sys.stderr)
            ok = False
            continue
        if digest(path) != checksum:
            print(f"hash mismatch: {label}/{rel}", file=sys.stderr)
            ok = False
    for rel in sorted(actual_paths):
        print(f"untracked by manifest: {label}/{rel}", file=sys.stderr)
        ok = False
    print(f"{'verified' if ok else 'failed'} {manifest.relative_to(ROOT)} ({len(expected)} files)")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["generate", "verify"])
    args = parser.parse_args()

    if args.command == "generate":
        generate_tree(ASSET_ROOT, ASSET_MANIFEST)
        if RUNTIME_ROOT.exists():
            generate_tree(RUNTIME_ROOT, RUNTIME_MANIFEST)
        generate_parts()
        return 0

    checks = [
        verify(ASSET_ROOT, ASSET_MANIFEST, "asset-cache"),
        verify(PAYLOAD_ROOT, PAYLOAD_MANIFEST, "runtime-payload"),
    ]
    if RUNTIME_ROOT.exists():
        checks.append(verify(RUNTIME_ROOT, RUNTIME_MANIFEST, "runtime"))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
