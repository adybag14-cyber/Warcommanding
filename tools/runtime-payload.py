from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "windows-x64"
PAYLOAD_DIR = ROOT / "payloads" / "runtime-windows-x64"
PART_MANIFEST = ROOT / "manifests" / "runtime-payload-parts.sha256"
RUNTIME_MANIFEST = ROOT / "manifests" / "runtime-windows-x64.sha256"
ARCHIVE_NAME = "runtime-windows-x64.zip"
PART_SIZE = 90 * 1024 * 1024
FIXED_ZIP_TIME = (2026, 7, 25, 12, 0, 0)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(path: Path) -> dict[str, tuple[str, int]]:
    entries: dict[str, tuple[str, int]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        checksum, size, rel = line.split(maxsplit=2)
        entries[rel] = (checksum, int(size))
    return entries


def verify_manifest(root: Path, manifest: Path) -> bool:
    expected = parse_manifest(manifest)
    actual = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    ok = True
    for rel, (checksum, size) in expected.items():
        path = actual.pop(rel, None)
        if path is None:
            print(f"missing: {rel}")
            ok = False
        elif path.stat().st_size != size:
            print(f"size mismatch: {rel}")
            ok = False
        elif digest(path) != checksum:
            print(f"hash mismatch: {rel}")
            ok = False
    for rel in sorted(actual):
        print(f"unexpected: {rel}")
        ok = False
    return ok


def create() -> None:
    if not RUNTIME.exists():
        raise FileNotFoundError(f"Recovered runtime is missing: {RUNTIME}")
    if not verify_manifest(RUNTIME, RUNTIME_MANIFEST):
        raise RuntimeError("Recovered runtime does not match its SHA-256 manifest")

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for old in PAYLOAD_DIR.glob(f"{ARCHIVE_NAME}.part*"):
        old.unlink()

    with tempfile.TemporaryDirectory(prefix="warcommanding-payload-") as tmp:
        archive = Path(tmp) / ARCHIVE_NAME
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as zf:
            for path in sorted(p for p in RUNTIME.rglob("*") if p.is_file()):
                rel = path.relative_to(RUNTIME).as_posix()
                info = zipfile.ZipInfo(rel, date_time=FIXED_ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                with path.open("rb") as src, zf.open(info, "w", force_zip64=True) as dst:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)

        parts: list[Path] = []
        with archive.open("rb") as src:
            index = 1
            while True:
                block = src.read(PART_SIZE)
                if not block:
                    break
                part = PAYLOAD_DIR / f"{ARCHIVE_NAME}.part{index:03d}"
                part.write_bytes(block)
                parts.append(part)
                index += 1

    lines = [f"{digest(p)}  {p.stat().st_size:>12}  {p.name}" for p in parts]
    PART_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    PART_MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"created {len(parts)} payload parts totalling {sum(p.stat().st_size for p in parts)} bytes")


def verify_parts() -> bool:
    if not PART_MANIFEST.exists():
        print(f"missing: {PART_MANIFEST}")
        return False
    expected = parse_manifest(PART_MANIFEST)
    ok = True
    for name, (checksum, size) in expected.items():
        path = PAYLOAD_DIR / name
        if not path.exists():
            print(f"missing payload part: {name}")
            ok = False
        elif path.stat().st_size != size:
            print(f"payload size mismatch: {name}")
            ok = False
        elif digest(path) != checksum:
            print(f"payload hash mismatch: {name}")
            ok = False
    unexpected = {p.name for p in PAYLOAD_DIR.glob(f"{ARCHIVE_NAME}.part*")} - set(expected)
    for name in sorted(unexpected):
        print(f"unexpected payload part: {name}")
        ok = False
    print("payload parts verified" if ok else "payload verification failed")
    return ok


def restore(destination: Path | None = None) -> None:
    if not verify_parts():
        raise RuntimeError("Payload verification failed")
    destination = destination or RUNTIME
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    entries = parse_manifest(PART_MANIFEST)
    ordered = [PAYLOAD_DIR / name for name in sorted(entries)]
    with tempfile.TemporaryDirectory(prefix="warcommanding-restore-") as tmp:
        archive = Path(tmp) / ARCHIVE_NAME
        with archive.open("wb") as dst:
            for part in ordered:
                with part.open("rb") as src:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(destination)

    if not verify_manifest(destination, RUNTIME_MANIFEST):
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError("Restored runtime failed SHA-256 verification")
    print(f"restored and verified runtime at {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create, verify or restore the split recovered Windows runtime payload.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("create")
    sub.add_parser("verify")
    restore_parser = sub.add_parser("restore")
    restore_parser.add_argument("--destination", type=Path)
    args = parser.parse_args()

    if args.command == "create":
        create()
    elif args.command == "verify":
        return 0 if verify_parts() else 1
    else:
        restore(args.destination.resolve() if args.destination else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
