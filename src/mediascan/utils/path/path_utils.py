from pathlib import Path


def get_human_readable_size(size: int) -> str:
    value: float = size
    UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in UNITS:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        if unit != UNITS[-1]:
            value /= 1024.0
    return f"{value:.2f} {UNITS[-1]}"


def get_size_bytes(path: Path) -> int:
    return path.stat().st_size

def get_size_human_readable(path: Path) -> str:
    return get_human_readable_size(path.stat().st_size)
