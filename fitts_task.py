"""Task 2b - Target hitting (Fitts' Law).

Each trial:
  1. The participant clicks the START circle in the centre of the stage
     (this fixes the cursor's starting point).
  2. A circular target appears at a known DISTANCE and with a known SIZE.
  3. The time from the target appearing to the click that hits it is recorded.
     Clicks that miss are counted and the trial carries on until it is hit.

A block crosses every target size with every distance, ``REPS`` times, in random
order.  Rows are written once, after the participant rates the block's ease of
use, so an aborted block leaves no half-finished data.

Note: the measured time includes a little reaction time (noticing the target).
That adds roughly the same constant to every trial, so *comparisons* between
sizes and distances stay valid.
"""

import itertools
import math
import random
import time

from stage import CANVAS_H, CANVAS_W

TASK_TYPE = "Target Hitting"

TARGET_SIZES_PX = {"Small": 20, "Medium": 45, "Large": 90}   # diameters
DISTANCES_PX = (100, 200, 320)                                # start -> target centre
REPS = 2                                                      # 3 x 3 x 2 = 18 trials
START_RADIUS = 28
START = (CANVAS_W // 2, CANVAS_H // 2)


def trial_count():
    return len(TARGET_SIZES_PX) * len(DISTANCES_PX) * REPS


def target_position(distance, radius):
    """Random direction at exactly ``distance`` from START that keeps the whole
    target inside the canvas."""
    margin = radius + 10
    for _ in range(200):
        angle = random.uniform(0, 2 * math.pi)
        x = START[0] + distance * math.cos(angle)
        y = START[1] + distance * math.sin(angle)
        if margin <= x <= CANVAS_W - margin and margin <= y <= CANVAS_H - margin:
            return x, y
    return START[0] + distance, START[1]       # horizontal fallback (always fits)


class FittsTask:
    def __init__(self, stage, session):
        self.stage = stage
        self.session = session
        self._trials = []
        self._index = 0
        self._results = []
        self._state = "idle"
        self._target = None
        self._misses = 0
        self._t0 = 0.0

    # ------------------------------------------------------------------ block
    def start(self):
        combos = list(itertools.product(TARGET_SIZES_PX.items(), DISTANCES_PX))
        self._trials = combos * REPS
        random.shuffle(self._trials)
        self._index = 0
        self._results = []
        self.stage.reset()
        self.stage.canvas.bind("<Button-1>", self._on_click)
        self._show_start()

    def abort(self):
        self._state = "idle"
        self.stage.reset()

    # ----------------------------------------------------------------- trials
    def _progress(self):
        theme = self.session.theme
        self.stage.canvas.create_text(
            14, 12, anchor="nw", fill=theme.fg, font=self.stage.font(0.6),
            text=f"Trial {self._index + 1} of {len(self._trials)}")

    def _show_start(self):
        stage, theme = self.stage, self.session.theme
        stage.canvas.delete("all")
        self._progress()
        x, y = START
        stage.canvas.create_oval(x - START_RADIUS, y - START_RADIUS,
                                 x + START_RADIUS, y + START_RADIUS,
                                 fill=theme.widget_bg, outline=theme.fg, width=3)
        stage.canvas.create_text(x, y, text="START", fill=theme.fg,
                                 font=stage.font(0.55, bold=True))
        stage.clear_bar()
        stage.bar_label("Click START, then click the circle as fast and accurately as you can.",
                        factor=0.7)
        self._state = "await_start"

    def _show_target(self):
        stage, theme = self.stage, self.session.theme
        (_, diameter), distance = self._trials[self._index]
        radius = diameter / 2
        x, y = target_position(distance, radius)
        self._target = (x, y, radius)
        self._misses = 0

        stage.canvas.delete("all")
        self._progress()
        stage.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                 fill=theme.fg, outline="")
        stage.canvas.update_idletasks()
        self._t0 = time.perf_counter()           # clock starts when the target is drawn
        self._state = "await_target"

    def _on_click(self, event):
        if self._state == "await_start":
            if math.hypot(event.x - START[0], event.y - START[1]) <= START_RADIUS:
                self._show_target()
        elif self._state == "await_target":
            elapsed = time.perf_counter() - self._t0
            x, y, radius = self._target
            if math.hypot(event.x - x, event.y - y) <= radius:
                self._record_hit(elapsed)
            else:
                self._misses += 1

    def _record_hit(self, elapsed):
        (size_name, diameter), distance = self._trials[self._index]
        self._results.append({
            "trial_in_block": self._index + 1, "size_name": size_name,
            "diameter": diameter, "distance": distance,
            "misses": self._misses, "seconds": elapsed,
        })
        self._index += 1
        if self._index < len(self._trials):
            self._show_start()
        else:
            self._state = "rating"
            self.stage.canvas.unbind("<Button-1>")
            self.stage.reset()
            self.stage.ask_rating(self._finish)

    # ----------------------------------------------------------------- finish
    def _finish(self, rating):
        session = self.session
        first_trial = session.next_trial(TASK_TYPE, count=len(self._results))
        rows = []
        for offset, r in enumerate(self._results):
            rows.append(session.logger.make_row(
                session.theme, session.participant_id, TASK_TYPE, first_trial + offset,
                stimulus=f"circle target ({r['size_name']})",
                target_diameter_px=r["diameter"],
                distance_px=r["distance"],
                response="hit",
                misses=r["misses"],
                time_seconds=f"{r['seconds']:.3f}",
                ease_rating=rating,
            ))
        if not session.record(rows):
            return                               # save failed; user chose to cancel
        mean = sum(r["seconds"] for r in self._results) / len(self._results)
        session.finished(f"Block saved: {len(rows)} trials, mean {mean:.2f} s, "
                         f"ease {rating}/5.")
