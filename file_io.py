"""
file_io.py - Import processes from CSV/JSON; export results to file.
"""

import csv
import json
import os
from process import Process


# ── Import ──────────────────────────────────────────────────────────────────

def load_csv(path: str) -> list[Process]:
    """
    Load processes from a CSV file.
    Expected columns: pid, arrival, burst  (optional: priority)
    First row may be a header.
    """
    processes = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize field names to lowercase
        for row in reader:
            row = {k.strip().lower(): v.strip() for k, v in row.items()}
            pid      = row.get("pid") or row.get("id") or f"P{len(processes)+1}"
            arrival  = int(row.get("arrival", 0))
            burst    = int(row.get("burst", 1))
            priority = int(row.get("priority", 0))
            processes.append(Process(pid, arrival, burst, priority))
    return processes


def load_json(path: str) -> list[Process]:
    """
    Load processes from a JSON file.
    Expected: list of objects with pid, arrival, burst  (optional: priority)
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    processes = []
    for i, item in enumerate(data):
        pid      = item.get("pid") or item.get("id") or f"P{i+1}"
        arrival  = int(item.get("arrival", 0))
        burst    = int(item.get("burst", 1))
        priority = int(item.get("priority", 0))
        processes.append(Process(pid, arrival, burst, priority))
    return processes


def load_file(path: str) -> list[Process]:
    """Auto-detect CSV or JSON by extension and load."""
    _, ext = os.path.splitext(path.lower())
    if ext == ".json":
        return load_json(path)
    elif ext == ".csv":
        return load_csv(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}  (use .csv or .json)")


# ── Sample templates ─────────────────────────────────────────────────────────

SAMPLE_CSV_TEMPLATE = """pid,arrival,burst
P1,0,5
P2,1,3
P3,2,8
P4,3,6
"""

SAMPLE_JSON_TEMPLATE = """[
  {"pid": "P1", "arrival": 0, "burst": 5},
  {"pid": "P2", "arrival": 1, "burst": 3},
  {"pid": "P3", "arrival": 2, "burst": 8},
  {"pid": "P4", "arrival": 3, "burst": 6}
]
"""


def write_sample_files():
    """Write sample input files to current directory."""
    with open("sample_processes.csv", "w") as f:
        f.write(SAMPLE_CSV_TEMPLATE)
    with open("sample_processes.json", "w") as f:
        f.write(SAMPLE_JSON_TEMPLATE)


# ── Export ───────────────────────────────────────────────────────────────────

def export_results(all_results: dict, filename: str = "scheduling_results.txt") -> str:
    """
    Export all algorithm results to a plain-text file.
    all_results = {algo_name: (procs, timeline, averages)}
    Returns the absolute path of the written file.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("  CPU SCHEDULING SIMULATOR — RESULTS EXPORT")
    lines.append("=" * 70)

    for algo_name, (procs, timeline, averages) in all_results.items():
        lines.append("")
        lines.append(f"  ALGORITHM: {algo_name}")
        lines.append("  " + "─" * 60)

        # Gantt (text)
        lines.append("")
        lines.append("  Gantt Chart (text):")
        merged = []
        for entry in timeline:
            if merged and merged[-1][0] == entry[0]:
                merged[-1] = (merged[-1][0], merged[-1][1], entry[2])
            else:
                merged.append(list(entry))

        bar = "  |"
        times = "  "
        for label, s, e in merged:
            w = max((e - s) * 2, len(label) + 2)
            bar += label.center(w) + "|"
            times += str(s).ljust(w + 1)
        times += str(merged[-1][2])
        lines.append(bar)
        lines.append(times)

        # Metrics table
        lines.append("")
        lines.append(f"  {'PID':<8} {'Arrival':<10} {'Burst':<8} {'Finish':<8} "
                     f"{'WT':<8} {'TAT':<12} {'RT':<10}")
        lines.append("  " + "─" * 60)
        for p in sorted(procs, key=lambda x: x.pid):
            lines.append(f"  {p.pid:<8} {p.arrival:<10} {p.burst:<8} "
                         f"{p.finish_time:<8} {p.waiting_time:<8} "
                         f"{p.turnaround_time:<12} {p.response_time:<10}")
        lines.append("  " + "─" * 60)
        lines.append(f"  {'AVERAGE':<8} {'':<10} {'':<8} {'':<8} "
                     f"{averages['avg_wt']:<8} {averages['avg_tat']:<12} "
                     f"{averages['avg_rt']:<10}")

    lines.append("")
    lines.append("=" * 70)

    abs_path = os.path.abspath(filename)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return abs_path
