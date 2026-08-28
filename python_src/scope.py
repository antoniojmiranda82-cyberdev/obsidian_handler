import os
from pathlib import PurePosixPath

ASSET_DREAM_ROOT = os.getenv("ASSET_DREAM_ROOT", "Projects/asset-dream").strip("/")


def _normalize_relative(value: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or not normalized or ".." in path.parts:
        raise ValueError("Path must stay inside the Asset Dream project scope")
    return path.as_posix()


def asset_dream_path(relative: str) -> str:
    relative_path = _normalize_relative(relative)
    return f"{ASSET_DREAM_ROOT}/{relative_path}"


def proposal_path(source_path: str) -> str:
    normalized = source_path.replace("\\", "/").strip("/")
    root_prefix = f"{ASSET_DREAM_ROOT}/"
    if not normalized.startswith(root_prefix):
        raise ValueError("Source note is outside the Asset Dream project scope")
    source = PurePosixPath(normalized)
    if ".." in source.parts or not source.name:
        raise ValueError("Invalid source note path")
    return (source.parent / f"propuesta-{source.name}").as_posix()
