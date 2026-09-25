"""Illustrative daily-life schedules (rates in concern-relevant events per minute, 1-min bins)."""
import numpy as np

NIGHT, CALM, DENSE, STREAM = 0.2, 0.5, 2.0, 8.0
DAY = 1440
WAKE, SLEEP, BLOCK = 7 * 60, 23 * 60, 90   # waking 07:00-23:00, alternating 90-min blocks


def day(sessions=(), stream_rate=STREAM):
    """One day: night, then waking hours alternating calm (e.g. studying) and dense
    (e.g. social) 90-min blocks, starting with calm at 07:00.
    `sessions` = iterable of (start_minute, length_minutes) of social media use."""
    lam = np.full(DAY, NIGHT)
    for m in range(WAKE, SLEEP):
        lam[m] = CALM if ((m - WAKE) // BLOCK) % 2 == 0 else DENSE
    for start, length in sessions:
        lam[start:start + length] = stream_rate
    return lam


def days(*day_arrays):
    return np.concatenate(day_arrays)


# Patterns of use -------------------------------------------------------------
def spread(n_sessions, length, first=WAKE, last=SLEEP):
    """n sessions of `length` minutes, evenly spread over waking hours."""
    step = (last - first) / n_sessions
    return [(int(first + k * step + (step - length) / 2), length) for k in range(n_sessions)]


HEAVY = spread(16, 10)            # 16 x 10 min per day (160 min)
LIGHT = [(12 * 60 + 30, 10)]      # one 10-min session per day

# Same total time (160 min / day), increasingly fragmented
FRAGMENTATION = {
    "1 x 160 min": [(10 * 60, 160)],
    "4 x 40 min": spread(4, 40),
    "16 x 10 min": spread(16, 10),
    "32 x 5 min": spread(32, 5),
}


def block_mask(lam_day, rate):
    return lam_day == rate
