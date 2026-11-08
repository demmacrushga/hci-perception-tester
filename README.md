# Human Perception & Performance Tester

A Tkinter app for testing how contrast, size and brightness affect human performance, with two
tasks (ambiguous-figure identification and Fitts'-Law target hitting) and automatic CSV logging.

**Requirements:** Python 3.8+ with Tkinter (included in the standard Windows/macOS installers). No other packages.

```bash
python app.py
```

## Files
| File | Purpose |
|---|---|
| `app.py` | Main window and experimenter controls |
| `stage.py` | Stimulus area shared by both tasks |
| `theme.py` | Contrast / size / brightness → colours and fonts (incl. WCAG contrast ratio) |
| `identification_task.py` | Rubin vase and Necker cube identification |
| `fitts_task.py` | Target-hitting block (3 sizes × 3 distances × 2 reps = 18 trials) |
| `data_logger.py` | Appends every trial to `results.csv` |
| `analyze.py` | Summary statistics and Fitts fit from the CSV |
| `Report_Task2_TEMPLATE.md` | Task 2 write-up with blanks for your numbers |

## How the brief's requirements are met
- **Contrast** (High / Medium / Low) – text and figure colour against a white background (ratios ≈ 21 : 1, 5 : 1, 1.9 : 1, shown live).
- **Size** (Small / Medium / Large) – font size and figure scale (visual angle approximated, as allowed).
- **Brightness** slider (20–100 %) – multiplies every colour towards black, like a dimmer display.
- **Identification task** – two ambiguous figures; answer options are buttons; repeatable under any condition.
- **Target-hitting task** – click START, then hit a circle at a known distance (100/200/320 px) and size (20/45/90 px); time recorded from target appearing to the hitting click; misses counted.
- **CSV logging** – automatic, one row per trial, header included.

## Running a test session
1. Enter a participant ID (e.g. `P01`) – the participant must be someone other than you.
2. Set the conditions, press a task button, hand over the mouse. Controls lock during a task; **Esc** aborts (nothing is saved).
3. After each identification answer, and after each 18-trial block, the participant clicks a 1–5 ease rating.

Suggested minimum per participant (about 5 minutes):
| Task | Conditions |
|---|---|
| Identification (6+ trials) | High/Medium; Medium/Medium; Low/Medium; High/Small; High/Large; Low/Small (all at 100 % brightness) |
| Identification (1–2 trials) | High/Medium at ~40 % brightness |
| Target hitting (3 blocks) | High/Medium/100 %; Low/Medium/100 %; High/Medium/40 % |

## CSV columns
`timestamp, participant_id, task_type, visual_condition, contrast, size_scale, brightness_pct, contrast_ratio, trial, stimulus, target_diameter_px, distance_px, response, misses, time_seconds, ease_rating`

The four required fields are `visual_condition`, `task_type`, `time_seconds` and `ease_rating`. In a Target Hitting block every trial row carries that block's single ease rating.
If `results.csv` is open in Excel the app offers a **Retry** when saving, so close it first.

## Analysis
```bash
python analyze.py
```
Prints and saves `analysis_summary.txt` (times and ease by condition, Fitts' fit `MT = a + b·log2(D/W+1)`, plain-language findings). Saves `fitts_chart.png` too if matplotlib is installed.

## Design notes
- The **experimenter panel stays in a fixed readable style**; only the stimulus stage obeys the visual conditions, so Low-contrast testing never locks the experimenter out.
- Canvas and response bar are **fixed size**, so pixel distances are identical every trial.
- Measured Fitts time includes a little reaction time (a roughly constant offset), so comparisons between sizes and distances remain valid.
- Rows are written only after the rating is given, so aborted tasks leave no partial data.

## Submission checklist
- [ ] All `.py` files
- [ ] `results.csv` from **real** sessions (delete any test rows first, or keep only genuine ones)
- [ ] Task 2 as PDF (from the template) or a 2-minute video
