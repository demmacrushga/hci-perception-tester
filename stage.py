"""The stimulus area shared by both tasks.

The stage is the only part of the window that obeys the visual conditions
(contrast / size / brightness).  The experimenter's control panel stays in a
fixed, readable style so a Low-contrast test never makes the *experimenter*
unable to operate the software.

Layout: a fixed-size canvas (so pixel distances are identical on every trial)
above a fixed-height response bar (so the canvas never shifts when the bar's
contents change).
"""

import tkinter as tk
from tkinter import font as tkfont

CANVAS_W, CANVAS_H, BAR_H = 840, 480, 150


class Stage(tk.Frame):
    def __init__(self, parent, theme):
        super().__init__(parent, highlightthickness=1, bd=0)
        self.family = tkfont.nametofont("TkDefaultFont").actual("family")
        self.canvas = tk.Canvas(self, width=CANVAS_W, height=CANVAS_H,
                                highlightthickness=0, bd=0)
        self.canvas.pack(side="top")
        self.bar = tk.Frame(self, width=CANVAS_W, height=BAR_H)
        self.bar.pack(side="top", fill="x")
        self.bar.pack_propagate(False)       # keep the bar height constant
        self.apply_theme(theme)

    # ------------------------------------------------------------- appearance
    def apply_theme(self, theme):
        self.theme = theme
        self.configure(bg=theme.bg, highlightbackground=theme.border,
                       highlightcolor=theme.border)
        self.canvas.configure(bg=theme.bg)
        self.bar.configure(bg=theme.bg)

    def font(self, factor=1.0, bold=False):
        size = max(7, round(self.theme.font_pt * factor))
        return (self.family, size, "bold" if bold else "normal")

    # --------------------------------------------------------------- clearing
    def reset(self):
        """Wipe the canvas, the response bar and any click handler."""
        self.canvas.unbind("<Button-1>")
        self.canvas.delete("all")
        self.canvas.configure(cursor="")
        for child in self.bar.winfo_children():
            child.destroy()

    def clear_bar(self):
        for child in self.bar.winfo_children():
            child.destroy()

    # ------------------------------------------------------------ bar widgets
    def bar_label(self, text, factor=0.8):
        tk.Label(self.bar, text=text, bg=self.theme.bg, fg=self.theme.fg,
                 font=self.font(factor)).pack(pady=(10, 6))

    def bar_buttons(self, items, factor=0.9):
        """Show a row of (text, callback) buttons - choices are always visible,
        so the user *recognises* an answer instead of having to recall one."""
        row = tk.Frame(self.bar, bg=self.theme.bg)
        row.pack()
        for text, command in items:
            tk.Button(
                row, text=text, command=command, font=self.font(factor),
                bg=self.theme.widget_bg, fg=self.theme.fg,
                activebackground=self.theme.border, activeforeground=self.theme.fg,
                relief="solid", bd=1, padx=14, pady=4, cursor="hand2",
                highlightthickness=0,
            ).pack(side="left", padx=6)

    def ask_rating(self, on_rating):
        """1-5 ease-of-use prompt; calls ``on_rating(n)`` when a button is clicked."""
        self.clear_bar()
        self.bar_label("How easy was that?   1 = very difficult  ...  5 = very easy",
                       factor=0.75)
        self.bar_buttons([(str(n), lambda n=n: on_rating(n)) for n in range(1, 6)])

    # ------------------------------------------------------------ idle screen
    def _icon(self, kind, cx, cy, r=34):
        """Small status icon drawn in the current theme colours."""
        c, fg = self.canvas, self.theme.fg
        if kind == "target":                      # resting: a bullseye
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=fg, width=4)
            c.create_oval(cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62,
                          outline=fg, width=4)
            c.create_oval(cx - r * .24, cy - r * .24, cx + r * .24, cy + r * .24,
                          fill=fg, outline="")
            return
        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=fg, width=4)
        if kind == "check":
            c.create_line(cx - 14, cy + 1, cx - 4, cy + 12, cx + 16, cy - 12,
                          fill=fg, width=6, capstyle="round", joinstyle="round")
        else:                                     # "cross"
            c.create_line(cx - 12, cy - 12, cx + 12, cy + 12, fill=fg, width=6,
                          capstyle="round")
            c.create_line(cx - 12, cy + 12, cx + 12, cy - 12, fill=fg, width=6,
                          capstyle="round")

    def show_idle(self, headline, detail, icon="target"):
        """Resting / result screen.  Drawn in the current condition, so the
        preview box lets the experimenter see contrast, size and brightness."""
        self.reset()
        canvas, theme, mid = self.canvas, self.theme, CANVAS_W // 2
        self._icon(icon, mid, 80)

        factor = 1.4 if len(headline) <= 25 else 1.0
        head = canvas.create_text(mid, 135, anchor="n", text=headline, fill=theme.fg,
                                  font=self.font(factor, bold=True), width=CANVAS_W - 80,
                                  justify="center")
        bottom = canvas.bbox(head)[3]
        canvas.create_text(mid, bottom + 12, anchor="n", text=detail, fill=theme.fg,
                           font=self.font(0.75), width=CANVAS_W - 120, justify="center")

        # Preview card
        left, right, top, bot = 170, CANVAS_W - 170, 316, 464
        canvas.create_rectangle(left, top, right, bot, outline=theme.border, width=2)
        canvas.create_text(left + 14, top + 8, anchor="nw", text="PREVIEW",
                           fill=theme.border, font=self.font(0.5, bold=True))
        canvas.create_text(mid, (top + bot) // 2 + 14, text="The quick brown fox 0123456789",
                           fill=theme.fg, font=self.font(1.0), width=right - left - 40,
                           justify="center")
