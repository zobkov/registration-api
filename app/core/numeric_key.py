from secrets import randbelow


def generate_numeric_key() -> str:
    """Return a zero-padded 6-digit key (000000-999999)."""
    return f"{randbelow(1_000_000):06d}"
