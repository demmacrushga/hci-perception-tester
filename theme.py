"""Visual-variable model for the Human Perception & Performance Tester.

This module turns the experimenter's three choices (contrast mode, size scale,
brightness) into one concrete ``Theme`` of colours and font sizes.  Keeping the
maths here means the GUI code never hard-codes a colour, and the same function
is used by the live preview, the tasks and the CSV log.

Contrast  -> text/object colour against a white background (WCAG-style ratios)
Size      -> font size in points and a scale factor for drawn figures
Brightness-> every colour is multiplied towards black, like a dimmer screen
"""

from dataclasses import dataclass

# (foreground, background).  Ratios are the WCAG 2.x contrast ratio.
CONTRAST_MODES = {
    "High": ("#000000", "#FFFFFF"),    # about 21 : 1  (best case)
    "Medium": ("#6E6E6E", "#FFFFFF"),  # about 5 : 1   (passes WCAG AA)
    "Low": ("#BDBDBD", "#FFFFFF"),     # about 1.9 : 1 (fails WCAG AA)
}

# Visual-angle approximation: we change font / icon size only, as the brief allows.
SIZE_MODES = {
    "Small": {"font_pt": 9, "scale": 0.5},
    "Medium": {"font_pt": 16, "scale": 0.9},
    "Large": {"font_pt": 26, "scale": 1.35},
}

BRIGHTNESS_MIN = 20     # percent; below this the screen is effectively black
BRIGHTNESS_MAX = 100
BRIGHTNESS_DEFAULT = 100


# ---------------------------------------------------------------- colour maths
def hex_to_rgb(colour):
    colour = colour.lstrip("#")
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in rgb))


def scale_colour(colour, factor):
    """Multiply a colour by ``factor`` (0..1) - this is how brightness is simulated."""
    return rgb_to_hex(tuple(c * factor for c in hex_to_rgb(colour)))


def blend(colour_a, colour_b, t):
    """Linear blend: t=0 gives colour_a, t=1 gives colour_b."""
    a, b = hex_to_rgb(colour_a), hex_to_rgb(colour_b)
    return rgb_to_hex(tuple(x + (y - x) * t for x, y in zip(a, b)))


def relative_luminance(colour):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in hex_to_rgb(colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(colour_a, colour_b):
    """WCAG contrast ratio between two colours (1.0 .. 21.0)."""
    la, lb = relative_luminance(colour_a), relative_luminance(colour_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


# ----------------------------------------------------------------------- theme
@dataclass(frozen=True)
class Theme:
    contrast_name: str
    size_name: str
    brightness: int
    fg: str
    bg: str
    widget_bg: str
    border: str
    font_pt: int
    scale: float
    ratio: float

    @property
    def condition_text(self):
        """Human-readable visual condition, written to the CSV."""
        return (f"contrast={self.contrast_name}; size={self.size_name}; "
                f"brightness={self.brightness}%")


def build_theme(contrast_name, size_name, brightness):
    fg, bg = CONTRAST_MODES[contrast_name]
    size = SIZE_MODES[size_name]
    factor = max(BRIGHTNESS_MIN, min(BRIGHTNESS_MAX, brightness)) / 100

    fg, bg = scale_colour(fg, factor), scale_colour(bg, factor)
    return Theme(
        contrast_name=contrast_name,
        size_name=size_name,
        brightness=int(round(factor * 100)),
        fg=fg,
        bg=bg,
        widget_bg=blend(bg, fg, 0.08),   # buttons sit just off the background
        border=blend(bg, fg, 0.45),
        font_pt=size["font_pt"],
        scale=size["scale"],
        ratio=contrast_ratio(fg, bg),
    )
