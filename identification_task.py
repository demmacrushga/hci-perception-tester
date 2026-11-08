"""Task 2a - Identification (vision & perception).

Shows an ambiguous figure and asks the participant what they see.  The answer
options are displayed as buttons (recognition, not recall), the time to answer
is measured, and the participant then rates how easy the figure was to see.

Two classic ambiguous figures are used, alternated at random:
  * Rubin's vase  - a vase, or two faces in profile
  * Necker cube   - which square is the front face?
"""

import random
import time

TASK_TYPE = "Identification"


# ------------------------------------------------------------------- figures
def draw_rubin_vase(canvas, cx, cy, s, fg, bg):
    """Dark panel with a light vase-shaped hole: the dark sides read as two faces."""
    half = 125 * s
    canvas.create_rectangle(cx - half, cy - 150 * s, cx + half, cy + 150 * s,
                            fill=fg, outline="")
    # (y, half-width) of the contour; the same curve is a vase edge and a face profile.
    profile = [(-150, 55), (-120, 48), (-100, 40), (-85, 62), (-65, 42), (-50, 50),
               (-38, 38), (-25, 48), (-5, 36), (20, 58), (50, 36), (110, 30),
               (135, 50), (150, 75)]
    right = [(cx + w * s, cy + y * s) for y, w in profile]
    left = [(cx - w * s, cy + y * s) for y, w in reversed(profile)]
    canvas.create_polygon(right + left, fill=bg, outline="")


def draw_necker_cube(canvas, cx, cy, s, fg, bg):
    """Wire-frame cube with no depth cues, so the front face can flip."""
    a = 160 * s           # square side
    o = 0.45 * a          # offset between the two squares
    width = max(2, round(4 * s))
    x1, y1 = cx - (a + o) / 2, cy - (a - o) / 2           # lower-left square
    x2, y2 = x1 + o, y1 - o                                # upper-right square
    for x, y in ((x1, y1), (x2, y2)):
        canvas.create_rectangle(x, y, x + a, y + a, outline=fg, width=width)
    for dx, dy in ((0, 0), (a, 0), (0, a), (a, a)):
        canvas.create_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, fill=fg, width=width)


FIGURES = [
    {"name": "Rubin vase", "draw": draw_rubin_vase,
     "question": "What do you see FIRST?",
     "options": ["Vase", "Faces", "Both", "Unsure"]},
    {"name": "Necker cube", "draw": draw_necker_cube,
     "question": "Which square looks like the FRONT of the cube?",
     "options": ["Lower", "Upper", "It flips", "Unsure"]},
]


# ---------------------------------------------------------------------- task
class IdentificationTask:
    def __init__(self, stage, session):
        self.stage = stage
        self.session = session
        self._figure = None
        self._answer = None
        self._seconds = None
        self._t0 = None
        self._last_name = None

    def start(self):
        """Show one figure and wait for the participant's answer."""
        stage = self.stage
        stage.reset()
        choices = [f for f in FIGURES if f["name"] != self._last_name] or FIGURES
        self._figure = random.choice(choices)
        self._last_name = self._figure["name"]

        theme = self.session.theme
        self._figure["draw"](stage.canvas, 420, 240, theme.scale, theme.fg, theme.bg)
        stage.bar_label(self._figure["question"], factor=0.85)
        stage.bar_buttons([(opt, lambda o=opt: self._answered(o))
                           for opt in self._figure["options"]])

        stage.canvas.update_idletasks()
        self._t0 = time.perf_counter()          # clock starts when the figure is on screen

    def _answered(self, option):
        self._seconds = time.perf_counter() - self._t0
        self._answer = option
        self.stage.canvas.delete("all")         # hide the figure while rating
        self.stage.ask_rating(self._rated)

    def _rated(self, rating):
        session = self.session
        row = session.logger.make_row(
            session.theme, session.participant_id, TASK_TYPE,
            session.next_trial(TASK_TYPE),
            stimulus=self._figure["name"],
            response=self._answer,
            time_seconds=f"{self._seconds:.3f}",
            ease_rating=rating,
        )
        if not session.record([row]):
            return                               # save failed; the app already reset
        session.finished(f"Recorded: {self._answer} in {self._seconds:.2f} s, "
                         f"ease {rating}/5.")

    def abort(self):
        self.stage.reset()
