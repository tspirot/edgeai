"""Процена трајања батерије — чиста рачуница за планирање теренског рада."""

from __future__ import annotations


def average_power_w(active_w: float, sleep_w: float,
                    triggers_per_hour: float, seconds_per_trigger: float) -> float:
    """Просечна снага уз дати ритам догађаја (остатак времена уређај спава)."""
    active_seconds = min(3600.0, max(0.0, triggers_per_hour * seconds_per_trigger))
    sleep_seconds = 3600.0 - active_seconds
    return (active_w * active_seconds + sleep_w * sleep_seconds) / 3600.0


def estimated_runtime_h(battery_wh: float, active_w: float, sleep_w: float,
                        triggers_per_hour: float, seconds_per_trigger: float = 6.0) -> float:
    """Колико сати уређај издржи на једном пуњењу."""
    avg = average_power_w(active_w, sleep_w, triggers_per_hour, seconds_per_trigger)
    if avg <= 0:
        return float("inf")
    return battery_wh / avg
