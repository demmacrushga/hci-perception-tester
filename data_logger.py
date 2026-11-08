"""CSV data logging.

Every finished trial is appended to ``results.csv`` immediately, so no data is
lost if the app is closed or crashes.  The file is created with a header row
the first time it is used and can be opened directly in Excel or pandas.
"""

import csv
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / "results.csv"

# The four columns the brief requires are marked with (*).
FIELDS = [
    "timestamp",
    "participant_id",
    "task_type",           # (*) Identification | Target Hitting
    "visual_condition",    # (*) e.g. "contrast=Low; size=Small; brightness=60%"
    "contrast",
    "size_scale",
    "brightness_pct",
    "contrast_ratio",
    "trial",
    "stimulus",            # figure name, or "circle target"
    "target_diameter_px",  # Target Hitting only
    "distance_px",         # Target Hitting only
    "response",            # what the user chose (Identification) / "hit"
    "misses",              # clicks that missed the target before the hit
    "time_seconds",        # (*) time to answer / to click the target
    "ease_rating",         # (*) 1 = very difficult ... 5 = very easy
]


class LoggerError(Exception):
    """Raised when the CSV cannot be written (e.g. it is open in Excel)."""


class ResultLogger:
    def __init__(self, path=None):
        self.path = Path(path) if path else DEFAULT_PATH

    def make_row(self, theme, participant_id, task_type, trial, **extra):
        """Build one CSV row; ``extra`` supplies the task-specific columns."""
        row = {field: "" for field in FIELDS}
        row.update(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            participant_id=participant_id,
            task_type=task_type,
            visual_condition=theme.condition_text,
            contrast=theme.contrast_name,
            size_scale=theme.size_name,
            brightness_pct=theme.brightness,
            contrast_ratio=f"{theme.ratio:.2f}",
            trial=trial,
        )
        row.update(extra)
        return row

    def write(self, rows):
        """Append rows to the CSV, writing the header if the file is new."""
        try:
            new_file = not self.path.exists() or self.path.stat().st_size == 0
            with self.path.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                if new_file:
                    writer.writeheader()
                writer.writerows(rows)
        except PermissionError as err:
            raise LoggerError(
                f"Cannot write to {self.path.name}. Close it if it is open in "
                "Excel, then try again."
            ) from err
        except OSError as err:
            raise LoggerError(f"Could not save results: {err}") from err

    def count(self):
        """Number of data rows already saved."""
        if not self.path.exists():
            return 0
        with self.path.open(newline="", encoding="utf-8") as handle:
            return max(0, sum(1 for _ in handle) - 1)
