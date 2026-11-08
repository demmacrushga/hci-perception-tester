"""Human Perception & Performance Tester - main window.

Run with:   python app.py      (or double-click run.bat on Windows)

Left  : experimenter control panel (fixed, always-readable style)
Right : the stage, which obeys the chosen contrast / size / brightness

Files
  app.py                  this window and the experimenter controls
  stage.py                the stimulus area shared by both tasks
  theme.py                contrast / size / brightness -> colours and fonts
  identification_task.py  ambiguous-figure task
  fitts_task.py           target-hitting task
  data_logger.py          CSV writing
  analyze.py              summary statistics from results.csv
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk

from data_logger import LoggerError, ResultLogger
from fitts_task import FittsTask, trial_count
from identification_task import IdentificationTask
from stage import Stage
from theme import (BRIGHTNESS_DEFAULT, BRIGHTNESS_MAX, BRIGHTNESS_MIN,
                   CONTRAST_MODES, SIZE_MODES, build_theme)

# Fixed palette for the experimenter panel (independent of the test conditions).
NAVY, NAVY_SOFT = "#14213D", "#A9B4D0"
PANEL_BG, CARD_BG, CARD_LINE = "#EEF1F6", "#FFFFFF", "#DDE2EA"
INK, MUTED, ACCENT, ACCENT_DARK = "#1F2937", "#6B7280", "#2457D6", "#1B45B0"
FONT = "Segoe UI"


class App(tk.Tk):
    def __init__(self, logger=None):
        super().__init__()
        self.title("Human Perception & Performance Tester")
        self.configure(bg=PANEL_BG)
        self.resizable(False, False)

        self.logger = logger or ResultLogger()
        self._trial_counters = {}
        self._active_task = None
        self._lockable = []

        self.participant_var = tk.StringVar()
        self.contrast_var = tk.StringVar(value="High")
        self.size_var = tk.StringVar(value="Medium")
        self.brightness_var = tk.DoubleVar(value=BRIGHTNESS_DEFAULT)

        self._style()
        self._build_panel()
        self.stage = Stage(self, self.theme)
        self.stage.pack(side="left", padx=(0, 18), pady=18, anchor="n")

        self.identification = IdentificationTask(self.stage, self)
        self.fitts = FittsTask(self.stage, self)

        self.bind("<Escape>", lambda _e: self.abort())
        self._refresh_condition()
        self._show_ready()

    # -------------------------------------------------- session API for tasks
    @property
    def theme(self):
        return build_theme(self.contrast_var.get(), self.size_var.get(),
                           int(round(self.brightness_var.get())))

    @property
    def participant_id(self):
        return self.participant_var.get().strip()

    def next_trial(self, task_type, count=1):
        """Return the first trial number for this participant & task, and reserve ``count``."""
        key = (self.participant_id, task_type)
        first = self._trial_counters.get(key, 0) + 1
        self._trial_counters[key] = first + count - 1
        return first

    def record(self, rows):
        """Save rows to the CSV.  Offers a retry (e.g. file open in Excel)."""
        while True:
            try:
                self.logger.write(rows)
                self._update_count()
                return True
            except LoggerError as err:
                if not messagebox.askretrycancel("Could not save results", str(err)):
                    self.finished("Results were NOT saved.", ok=False)
                    return False

    def finished(self, message, ok=True):
        self._active_task = None
        self._set_locked(False)
        self._show_ready(message, ok)

    # ---------------------------------------------------------------- styling
    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=PANEL_BG, foreground=INK, font=(FONT, 10))

        # card text
        style.configure("Card.TLabel", background=CARD_BG, foreground=INK)
        style.configure("CardHead.TLabel", background=CARD_BG, foreground=MUTED,
                        font=(FONT, 8, "bold"))
        style.configure("CardMuted.TLabel", background=CARD_BG, foreground=MUTED,
                        font=(FONT, 9))
        style.configure("Plain.TLabel", background=PANEL_BG, foreground=MUTED,
                        font=(FONT, 9))
        style.configure("Count.TLabel", background=PANEL_BG, foreground=INK,
                        font=(FONT, 9, "bold"))

        style.configure("TEntry", fieldbackground="white", padding=5,
                        bordercolor=CARD_LINE, lightcolor=CARD_LINE, darkcolor=CARD_LINE)
        style.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)])

        style.configure("Card.Horizontal.TScale", background=CARD_BG, troughcolor="#D7DCE5")

        # segmented toggle buttons
        style.configure("Seg.Toolbutton", background="#E8EBF1", foreground=INK,
                        padding=(8, 6), borderwidth=0, relief="flat", anchor="center",
                        font=(FONT, 10))
        style.map("Seg.Toolbutton",
                  background=[("disabled", "selected", "#8FA3D9"), ("disabled", "#F1F3F7"),
                              ("selected", ACCENT), ("active", "#D9DEE8")],
                  foreground=[("disabled", "selected", "white"), ("disabled", "#A0A7B4"),
                              ("selected", "white")])

        # action buttons
        style.configure("Primary.TButton", background=ACCENT, foreground="white",
                        padding=(10, 9), font=(FONT, 10, "bold"), borderwidth=0)
        style.map("Primary.TButton",
                  background=[("disabled", "#A9B9E6"), ("active", ACCENT_DARK)],
                  foreground=[("disabled", "#F4F6FD")])
        style.configure("Ghost.TButton", background="#E8EBF1", foreground=INK,
                        padding=(10, 7), borderwidth=0)
        style.map("Ghost.TButton",
                  background=[("disabled", "#F1F3F7"), ("active", "#D9DEE8")],
                  foreground=[("disabled", "#A0A7B4")])
        style.configure("Small.TButton", background="#E3E7EF", foreground=INK,
                        padding=(8, 4), borderwidth=0, font=(FONT, 9))
        style.map("Small.TButton", background=[("active", "#D3D9E4")])

    # ------------------------------------------------------------- the panel
    def _card(self, parent, title):
        """White card with a small caps heading; returns the inner frame."""
        outer = tk.Frame(parent, bg=CARD_BG, highlightbackground=CARD_LINE,
                         highlightthickness=1)
        outer.pack(fill="x", pady=(0, 8))
        ttk.Label(outer, text=title.upper(), style="CardHead.TLabel").pack(
            anchor="w", padx=12, pady=(9, 4))
        inner = tk.Frame(outer, bg=CARD_BG)
        inner.pack(fill="x", padx=12, pady=(0, 11))
        return inner

    def _segmented(self, parent, label, variable, options):
        ttk.Label(parent, text=label, style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        row = tk.Frame(parent, bg=CARD_BG)
        row.pack(fill="x", pady=(0, 9))
        for column, option in enumerate(options):
            row.columnconfigure(column, weight=1, uniform="seg")
            button = ttk.Radiobutton(row, text=option, value=option, variable=variable,
                                     command=self._on_change, style="Seg.Toolbutton",
                                     takefocus=False)
            button.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 3, 0))
            self._lockable.append(button)

    def _build_panel(self):
        panel = tk.Frame(self, bg=PANEL_BG, width=312)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        # --- header band with a bullseye logo
        header = tk.Frame(panel, bg=NAVY)
        header.pack(fill="x")
        logo = tk.Canvas(header, width=40, height=40, bg=NAVY, highlightthickness=0)
        logo.pack(side="left", padx=(16, 10), pady=14)
        for radius, colour in ((18, "#FFFFFF"), (12, NAVY), (6, "#5B8CFF")):
            logo.create_oval(20 - radius, 20 - radius, 20 + radius, 20 + radius,
                             fill=colour, outline="")
        titles = tk.Frame(header, bg=NAVY)
        titles.pack(side="left", pady=12)
        tk.Label(titles, text="Perception Tester", bg=NAVY, fg="white",
                 font=(FONT, 14, "bold")).pack(anchor="w")
        tk.Label(titles, text="Experimenter controls", bg=NAVY, fg=NAVY_SOFT,
                 font=(FONT, 9)).pack(anchor="w")

        body = tk.Frame(panel, bg=PANEL_BG)
        body.pack(fill="both", expand=True, padx=14, pady=(14, 8))

        # --- participant
        card = self._card(body, "Participant")
        entry = ttk.Entry(card, textvariable=self.participant_var)
        entry.pack(fill="x")
        self._lockable.append(entry)

        # --- visual conditions
        card = self._card(body, "Visual conditions")
        self._segmented(card, "Contrast", self.contrast_var, list(CONTRAST_MODES))
        self._segmented(card, "Size (text / figure scale)", self.size_var, list(SIZE_MODES))

        ttk.Label(card, text="Brightness", style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        row = tk.Frame(card, bg=CARD_BG)
        row.pack(fill="x")
        scale = ttk.Scale(row, from_=BRIGHTNESS_MIN, to=BRIGHTNESS_MAX,
                          variable=self.brightness_var, command=self._on_change,
                          style="Card.Horizontal.TScale")
        scale.pack(side="left", fill="x", expand=True)
        self.brightness_label = ttk.Label(row, width=5, anchor="e", style="Card.TLabel")
        self.brightness_label.pack(side="left", padx=(8, 0))
        self._lockable.append(scale)

        self.ratio_label = ttk.Label(card, style="CardMuted.TLabel")
        self.ratio_label.pack(anchor="w", pady=(8, 0))

        # --- tasks
        card = self._card(body, "Tasks")
        self.ident_button = ttk.Button(
            card, text="Start identification trial", style="Primary.TButton",
            command=lambda: self._start(self.identification))
        self.ident_button.pack(fill="x", pady=(0, 6))
        self.fitts_button = ttk.Button(
            card, text=f"Start target-hitting block ({trial_count()} trials)",
            style="Primary.TButton", command=lambda: self._start(self.fitts))
        self.fitts_button.pack(fill="x", pady=(0, 6))
        self.abort_button = ttk.Button(card, text="Abort current task  (Esc)",
                                       style="Ghost.TButton", command=self.abort,
                                       state="disabled")
        self.abort_button.pack(fill="x")
        self._lockable += [self.ident_button, self.fitts_button]

        # --- footer: rows saved + open folder
        footer = tk.Frame(body, bg=PANEL_BG)
        footer.pack(fill="x", pady=(2, 0))
        self.count_label = ttk.Label(footer, style="Count.TLabel")
        self.count_label.pack(side="left")
        ttk.Button(footer, text="Open folder", style="Small.TButton",
                   command=self._open_folder).pack(side="right")
        self._update_count()

    # --------------------------------------------------------------- behaviour
    def _on_change(self, *_):
        self._refresh_condition()
        if self._active_task is None:
            self._show_ready()

    def _refresh_condition(self):
        theme = self.theme
        self.brightness_label.configure(text=f"{theme.brightness}%")
        if theme.ratio >= 4.5:
            verdict = "passes WCAG AA"
        elif theme.ratio >= 3:
            verdict = "large text only"
        else:
            verdict = "fails WCAG AA"
        self.ratio_label.configure(text=f"Contrast {theme.ratio:.1f} : 1  -  {verdict}")

    def _show_ready(self, message=None, ok=True):
        self.stage.apply_theme(self.theme)
        if message is None:
            self.stage.show_idle(
                "Ready",
                "1  Set the conditions     2  Press a task     3  Hand over the mouse")
        else:
            self.stage.show_idle(message, "Change the conditions or start the next task.",
                                 icon="check" if ok else "cross")

    def _update_count(self):
        self.count_label.configure(
            text=f"Rows saved: {self.logger.count()}   ({self.logger.path.name})")

    def _set_locked(self, locked):
        for widget in self._lockable:
            widget.state(["disabled"] if locked else ["!disabled"])
        self.abort_button.state(["!disabled"] if locked else ["disabled"])

    def _start(self, task):
        if not self.participant_id:
            messagebox.showinfo("Participant ID needed",
                                "Please enter a participant ID (e.g. P01) first.")
            return
        self._active_task = task
        self._set_locked(True)
        self.stage.apply_theme(self.theme)
        task.start()

    def abort(self):
        if self._active_task is None:
            return
        self._active_task.abort()
        self.finished("Task aborted - nothing was saved.", ok=False)

    def _open_folder(self):
        folder = self.logger.path.parent
        try:
            os.startfile(folder)               # Windows
        except AttributeError:
            messagebox.showinfo("Results location", str(folder))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
