"""Builds HCI_Task2_Report.pdf (Task 2 write-up).

Edit NAME and STUDENT_ID below, then run:   python build_report.py
Requires reportlab (pip install reportlab).  All numbers in the text come from
analysis_summary.txt, produced by `python analyze.py results_P01.csv`.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

NAME = "Dziwornu Edith"
STUDENT_ID = "21151366"
COURSE = "Human-Computer Interaction"
OUT = Path(__file__).resolve().parent / "HCI_Task2_Report.pdf"

NAVY, GREY = colors.HexColor("#14213D"), colors.HexColor("#555555")

base = getSampleStyleSheet()["Normal"]
body = ParagraphStyle("body", parent=base, fontName="Helvetica", fontSize=9.2,
                      leading=11.7, alignment=TA_JUSTIFY, spaceAfter=4)
h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=15,
                    leading=18, textColor=NAVY, alignment=0, spaceAfter=1)
sub = ParagraphStyle("sub", parent=body, fontSize=8.5, textColor=GREY, alignment=0,
                     spaceAfter=5)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=10.5,
                    leading=13, textColor=NAVY, alignment=0, spaceBefore=6, spaceAfter=2)
cap = ParagraphStyle("cap", parent=body, fontSize=8, textColor=GREY, alignment=0,
                     spaceAfter=3)


def P(text, style=body):
    return Paragraph(text, style)


def table(rows, widths):
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8.3),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 8.3),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F3F8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9CFDC")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ]))
    return t


story = [
    P("Task 2: Analysis &amp; HCI Reflection", h1),
    P(f"Human Perception &amp; Performance Tester &nbsp;|&nbsp; {NAME} &nbsp;|&nbsp; "
      f"{STUDENT_ID} &nbsp;|&nbsp; {COURSE}", sub),

    P("<b>Method.</b> My roommate (participant P01, not the developer) completed 8 "
      "identification trials and three target-hitting blocks of 18 clicks (54 trials). "
      "Contrast, size and brightness were changed with the app's controls and every trial "
      "was logged automatically to the CSV file. With one participant the results are "
      "indicative only; I note where practice or the fixed block order may have affected them."),

    P("a. Human limits", h2),
    P("<b>Identification.</b> Practice affected these times more than any visual setting: "
      "the first trial took 15.7 s, while later High-contrast trials took 5.2, 5.3 and 1.3 s. "
      "The clearest condition effect came from low contrast. The Necker cube at Low contrast "
      "(1.9:1, Large size) took 4.05 s and was rated 1/5 for ease, the only 1 given, "
      "about three times slower than the same figure at High contrast (21:1) a few trials "
      "earlier (1.30 s). Size also changed in that trial, so I treat it as suggestive, not "
      "proof. The two dimmed trials (51% and 57% brightness) were answered quickly (1.46 s and "
      "1.13 s) but both were rated only 2/5, and they came after the participant had practised."),
    P("<b>Target hitting.</b> Dimming the screen to 49% made targets harder to acquire: mean "
      "time rose from 1.44 s to 1.62 s (+12%), misses per trial rose from 0.05 to 0.28, and "
      "the ease rating fell from 5 to 2. Low contrast did not slow the clicks (1.35 s) but "
      "lowered the ease rating to 3, so the user worked harder for the same speed. The targets "
      "were large filled circles, which remain detectable at 1.9:1, and the blocks were not "
      "counterbalanced, so practice may have hidden a slowdown."),
    table([["Target-hitting block (18 trials each)", "Mean time (s)", "Misses / trial",
            "Ease (1-5)"],
           ["High contrast, 100% brightness", "1.44", "0.05", "5"],
           ["Low contrast (1.9:1), 100% brightness", "1.35", "0.11", "3"],
           ["High contrast, 49% brightness", "1.62", "0.28", "2"]],
          [7.2 * cm, 3.0 * cm, 3.0 * cm, 2.6 * cm]),
    Spacer(1, 4),
    P("These limits come from the visual system: contrast sensitivity falls as the luminance "
      "difference shrinks, acuity depends on the visual angle an object covers, and a dim "
      "display reduces the usable luminance difference. They explain familiar failures. Early "
      "ATM screens were small, dim and low-contrast, and sunlight glare made prompts easy to "
      "misread. Many websites use light-grey text on white below the WCAG minimum of 4.5:1, "
      "which slows reading. My ratings fell further than my times, which shows why timing "
      "alone underestimates the cost: users compensate with effort and frustration."),

    P("b. Applying Fitts' Law", h2),
    P("Fitts' Law predicts MT = a + b log<sub>2</sub>(D/W + 1): larger targets (W) and shorter "
      "distances (D) are faster."),
    table([["Target diameter", "20 px", "45 px", "90 px", "Distance", "100 px", "200 px",
            "320 px"],
           ["Mean time (s)", "1.81", "1.39", "1.20", "Mean time (s)", "1.44", "1.49", "1.47"],
           ["Misses / trial", "0.39", "0.00", "0.06", "Misses / trial", "0.11", "0.22", "0.11"]],
          [3.0 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm, 3.0 * cm, 1.8 * cm, 1.8 * cm, 1.8 * cm]),
    Spacer(1, 4),
    P("<b>Larger targets clearly reduced movement time</b> (34% faster from 20 px to 90 px) and "
      "small targets caused far more misses. <b>Shorter distances did not:</b> the three "
      "distances differ by only 0.03 s. A straight-line fit over all 54 trials gave "
      "MT = 0.89 + 0.24 log<sub>2</sub>(D/W + 1) seconds, with r = 0.34."),
    P("<b>Does this match Fitts' Law? Partly.</b> The direction is right and the size is "
      "realistic: a slope of 0.24 s/bit predicts about 0.7 s between the easiest and hardest "
      "combinations (1.1 to 4.1 bits), and I observed 0.74 s (1.13 s for 100 px distance with "
      "a 90 px target, 1.87 s for 320 px with a 20 px target). The weak correlation and flat "
      "distance effect do not match. Likely reasons: distances covered only 100 to 320 px, so "
      "extra distance added little compared with the aiming and reaction time in every "
      "measurement; my design changed width 4.5 times but distance only 3.2 times, so width "
      "dominated the difficulty; and each combination was repeated just twice by one "
      "participant. A wider range of distances and more repetitions would test the distance "
      "term properly."),

    P("c. Design for diversity", h2),
    P("<b>Colour-blind user.</b> My conditions varied luminance (black to grey on white), which "
      "colour-vision deficiency barely changes, so I would expect similar performance here. "
      "The risk is any design that carries meaning by colour alone, such as red/green status "
      "messages or coloured chart lines, which about 1 in 12 men cannot separate. Adding "
      "labels, icons or patterns gives a redundant cue. <b>Elderly user with reduced acuity.</b> "
      "Ageing lowers acuity and contrast sensitivity and often slows and unsteadies the hand. "
      "My participant, with normal vision, already rated dim and low-contrast conditions "
      "2 to 3 out of 5 and missed small targets most (0.39 misses per trial), so I would "
      "expect larger penalties and a steeper Fitts slope for an older user. The remedies are "
      "high contrast, larger text and large, well-spaced targets of at least 44 px, with no "
      "need for precise or timed movements."),

    P("d. Recognition vs recall", h2),
    P("The interface keeps information on screen so users never have to remember steps. "
      "Identification answers are visible buttons (Vase / Faces / Both / Unsure), so the "
      "participant picks rather than types or recalls a word. The Fitts task shows a labelled "
      "START circle, a \"Trial n of 18\" counter and an instruction on every trial. The 1 to 5 "
      "rating buttons carry their meaning (\"1 = very difficult ... 5 = very easy\") each time. "
      "For the experimenter, the panel always shows the current condition and contrast ratio, "
      "a preview of sample text shows the effect of each setting, and controls lock during a "
      "task so settings cannot be changed or forgotten by accident."),

    P("Limitations", h2),
    P("One participant, 8 identification trials spread across conditions (some changed two "
      "settings at once), and fixed block order. A stronger study would test several people, "
      "counterbalance the order of conditions, change one setting at a time and repeat each "
      "combination more often."),
]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                        topMargin=1.5 * cm, bottomMargin=1.4 * cm,
                        title="Task 2: Analysis & HCI Reflection", author=NAME)
doc.build(story)
print(f"Saved {OUT.name}")
