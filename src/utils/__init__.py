import time


def calculate_duration(start_time: float) -> float:
    """Return duration in milliseconds since start_time."""
    return round((time.perf_counter() - start_time) * 1000, 2)
