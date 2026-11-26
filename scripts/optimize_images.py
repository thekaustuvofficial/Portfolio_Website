from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets"
MAX_EDGE = 1440
QUALITY = 83
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def optimize(source: Path) -> tuple[int, int] | None:
    target = source.with_suffix(".webp")
    temporary = target.with_name(f"{target.name}.tmp")

    with Image.open(source) as opened:
        if getattr(opened, "n_frames", 1) > 1 and opened.format != "MPO":
            return None
        if opened.format == "MPO":
            opened.seek(0)

        image = ImageOps.exif_transpose(opened)
        image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
        if image.mode not in ("RGB", "RGBA"):
            has_alpha = "A" in image.getbands() or "transparency" in opened.info
            image = image.convert("RGBA" if has_alpha else "RGB")

        save_options = {"format": "WEBP", "quality": QUALITY, "method": 6, "exact": True}
        icc_profile = opened.info.get("icc_profile")
        if icc_profile:
            save_options["icc_profile"] = icc_profile
        image.save(temporary, **save_options)

    original_size = source.stat().st_size
    optimized_size = temporary.stat().st_size
    if target.exists() and optimized_size >= target.stat().st_size:
        temporary.unlink()
        return original_size, target.stat().st_size

    temporary.replace(target)
    return original_size, optimized_size


def main() -> None:
    candidates = [
        path
        for path in ASSET_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    source_stems = {
        (path.parent, path.stem.lower())
        for path in candidates
        if path.suffix.lower() != ".webp"
    }
    candidates = [
        path
        for path in candidates
        if path.suffix.lower() != ".webp"
        or (path.parent, path.stem.lower()) not in source_stems
    ]
    profile = ROOT / "profile.jpg"
    if profile.exists():
        candidates.append(profile)

    processed = 0
    source_bytes = 0
    output_bytes = 0
    for source in candidates:
        result = optimize(source)
        if result is None:
            print(f"Skipped animated image: {source.relative_to(ROOT)}")
            continue
        before, after = result
        processed += 1
        source_bytes += before
        output_bytes += after

    saved = source_bytes - output_bytes
    percent = (saved / source_bytes * 100) if source_bytes else 0
    print(
        f"Optimized {processed} images: {source_bytes / 1_000_000:.2f} MB "
        f"source set -> {output_bytes / 1_000_000:.2f} MB WebP set "
        f"({saved / 1_000_000:.2f} MB / {percent:.1f}% smaller)."
    )


if __name__ == "__main__":
    main()
