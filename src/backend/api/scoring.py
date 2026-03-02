from __future__ import annotations

def _sim_band_weight(level_number: int) -> float:
    if level_number <= 5:
        return 0.90
    if level_number <= 10:
        return 1.05
    if level_number <= 15:
        return 1.20
    return 1.45  # 16-20


def _mode_weight(mode: str, level_number: int) -> float:
    if mode == "arcade":
        return 0.60
    if mode == "pvp":
        return 1.30
    # simulation
    return _sim_band_weight(level_number)


def _time_mult(duration_ms: int, emails_total: int, par_per_email_ms: int) -> float:
    # mild effect; clamp so time never dominates accuracy
    emails_total = max(1, int(emails_total or 1))
    duration_ms = max(1, int(duration_ms or 1))

    par_ms = max(1, par_per_email_ms * emails_total)
    ratio = par_ms / duration_ms

    mult = ratio ** 0.25  # gentle curve
    if mult < 0.85:
        return 0.85
    if mult > 1.15:
        return 1.15
    return float(mult)


def compute_levelrun_points(run) -> int:
    """
    Points for completed simulation/pvp runs.
    - Wrongness penalized harder than slowness.
    - Time effect is mild and clamped.
    """
    correct = int(getattr(run, "correct", 0) or 0)
    incorrect = int(getattr(run, "incorrect", 0) or 0)
    level_number = int(getattr(run, "level_number", 1) or 1)
    mode = str(getattr(run, "mode", "simulation") or "simulation")
    emails_total = int(getattr(run, "emails_total", 1) or 1)

    # prefer client duration when provided
    dur = getattr(run, "client_duration_ms", None)
    if dur is None:
        dur = getattr(run, "duration_ms", 0)
    dur = int(dur or 0)

    # base score (accuracy dominated)
    base = (correct * 100) - (incorrect * 180)
    if base < 0:
        base = 0

    w = _mode_weight(mode, level_number)

    if mode == "pvp":
        par_per_email_ms = 28_000
    else:
        par_per_email_ms = 30_000  # simulation

    tm = _time_mult(dur, emails_total, par_per_email_ms)

    return int(round(base * w * tm))