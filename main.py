#!/usr/bin/env python3
"""
main.py - CPU Scheduling Algorithm Simulator
Entry point for the interactive CLI application.

Run:
    python main.py
    python main.py --sample          # Load sample scenario and run all algos
    python main.py --file input.csv  # Load from file then open menu
"""

import sys
import os

from process import Process
from algorithms import fcfs, sjf, srt, round_robin, mlfq, compute_averages
from display import (
    C, clear, print_banner, section, sub_section,
    info, warn, error, prompt, hr,
    print_process_table, print_gantt, print_metrics_table,
    print_comparison_table, print_menu, MENU_ITEMS, ALGO_MENU,
)
from file_io import load_file, export_results, write_sample_files

# ─── Global state ────────────────────────────────────────────────────────────

processes: list   = []   # Current process list
quantum:   int    = 2    # Default time quantum for RR & MLFQ
last_results: dict = {}  # Stores most recent run-all results

# ─── Sample scenario ─────────────────────────────────────────────────────────

SAMPLE_PROCESSES = [
    Process("P1", arrival=0, burst=5),
    Process("P2", arrival=1, burst=3),
    Process("P3", arrival=2, burst=8),
    Process("P4", arrival=3, burst=6),
]

# ─── Input helpers ────────────────────────────────────────────────────────────

def read_int(msg: str, min_val: int = 0, max_val: int = 9999,
             default: int = None) -> int:
    """Prompt for an integer with validation. Returns default on empty if given."""
    while True:
        raw = prompt(msg).strip()
        if raw == "" and default is not None:
            return default
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            error(f"Enter a value between {min_val} and {max_val}.")
        except ValueError:
            error("Please enter a valid integer.")


def read_choice(valid: list, msg: str = "Choice") -> str:
    """Prompt until user enters a value in the valid list."""
    while True:
        ch = prompt(msg).strip()
        if ch in valid:
            return ch
        error(f"Invalid choice. Options: {', '.join(valid)}")


# ─── Process management ───────────────────────────────────────────────────────

def add_processes():
    """Interactive process entry wizard."""
    global processes
    section("Add / Edit Processes")

    if processes:
        print_process_table(processes)
        ch = prompt("(A)dd more, (R)eplace all, (C)ancel? [A/R/C]").upper().strip()
        if ch == "C":
            return
        if ch == "R":
            processes = []

    print()
    info("Enter process details. Leave PID empty to finish.")
    info("PID is auto-generated if left blank (P1, P2, ...)")
    print()

    while True:
        idx = len(processes) + 1
        pid_raw = prompt(f"PID [default P{idx}]").strip()
        pid = pid_raw if pid_raw else f"P{idx}"

        if any(p.pid == pid for p in processes):
            error(f"PID '{pid}' already exists.")
            continue

        arrival  = read_int("Arrival Time",       min_val=0, default=0)
        burst    = read_int("Burst Time",          min_val=1, default=1)
        priority = read_int("Priority (0 = none)", min_val=0, default=0)

        processes.append(Process(pid, arrival, burst, priority))
        info(f"Process {pid} added.  (Total: {len(processes)})")
        print()

        if prompt("Add another? [Y/n]").strip().lower() in ("n", "no"):
            break

    section("Current Processes")
    print_process_table(processes)


def load_from_file():
    """Load processes from a CSV or JSON file."""
    global processes
    section("Load Processes from File")
    info("Supported formats: .csv  .json")
    print()

    if prompt("Generate sample template files first? [y/N]").strip().lower() in ("y","yes"):
        write_sample_files()
        info("sample_processes.csv and sample_processes.json created.")
        print()

    path = prompt("File path").strip()
    if not path:
        warn("No path entered.")
        return
    if not os.path.exists(path):
        error(f"File not found: {path}")
        return
    try:
        loaded = load_file(path)
        if not loaded:
            warn("File contained no valid processes.")
            return
        processes = loaded
        info(f"Loaded {len(processes)} process(es) from '{path}'")
        print_process_table(processes)
    except Exception as exc:
        error(f"Failed to load: {exc}")


def load_sample():
    """Load the assignment sample scenario."""
    global processes
    processes = [Process(p.pid, p.arrival, p.burst, p.priority)
                 for p in SAMPLE_PROCESSES]
    info("Sample scenario loaded → P1(0,5)  P2(1,3)  P3(2,8)  P4(3,6)")
    print_process_table(processes)


def clear_processes():
    """Remove all processes."""
    global processes
    if not processes:
        warn("No processes to clear.")
        return
    if prompt("Clear all processes? [y/N]").strip().lower() in ("y","yes"):
        processes = []
        info("Process list cleared.")


# ─── Algorithm runner ─────────────────────────────────────────────────────────

def configure_quantum() -> int:
    """Ask user to confirm or change the time quantum."""
    global quantum
    val = read_int(f"Time quantum [current: {quantum}, press Enter to keep]",
                   min_val=1, default=quantum)
    quantum = val
    info(f"Time quantum = {quantum}")
    return quantum


def run_algorithm(choice: str):
    """Run one algorithm by menu choice. Returns (name, procs, timeline, avgs) or None."""
    global quantum

    if not processes:
        warn("No processes loaded. Add or load processes first.")
        return None

    if choice in ("4", "5"):
        configure_quantum()

    if   choice == "1":
        name  = "FCFS"
        procs, timeline = fcfs(processes)
    elif choice == "2":
        name  = "SJF"
        procs, timeline = sjf(processes)
    elif choice == "3":
        name  = "SRT"
        procs, timeline = srt(processes)
    elif choice == "4":
        name  = f"Round Robin (q={quantum})"
        procs, timeline = round_robin(processes, quantum)
    elif choice == "5":
        name  = f"MLFQ (q={quantum}/{quantum*2}/FCFS)"
        procs, timeline = mlfq(processes, quantums=[quantum, quantum * 2])
    else:
        return None

    avgs = compute_averages(procs)

    section(f"Results — {name}")
    sub_section("Gantt Chart")
    print_gantt(timeline)
    sub_section("Metrics Table")
    print_metrics_table(procs, avgs)
    print(f"  {C.DIM}Averages:{C.RESET}  "
          f"WT={C.BRIGHT_GREEN}{avgs['avg_wt']}{C.RESET}   "
          f"TAT={C.BRIGHT_CYAN}{avgs['avg_tat']}{C.RESET}   "
          f"RT={C.BRIGHT_YELLOW}{avgs['avg_rt']}{C.RESET}")

    return name, procs, timeline, avgs


def run_all():
    """Run all 5 algorithms and print comparison."""
    global last_results, quantum

    if not processes:
        warn("No processes loaded. Add or load processes first.")
        return

    configure_quantum()
    section("Running ALL Algorithms")

    configs = [
        ("FCFS",                          lambda: fcfs(processes)),
        ("SJF",                           lambda: sjf(processes)),
        ("SRT",                           lambda: srt(processes)),
        (f"Round Robin (q={quantum})",    lambda: round_robin(processes, quantum)),
        (f"MLFQ (q={quantum}/{quantum*2}/FCFS)",
                                          lambda: mlfq(processes,
                                                        quantums=[quantum, quantum*2])),
    ]

    comparison  = {}
    last_results = {}

    for name, func in configs:
        sub_section(name)
        procs, timeline = func()
        avgs = compute_averages(procs)
        print_gantt(timeline)
        print_metrics_table(procs, avgs)
        comparison[name]   = avgs
        last_results[name] = (procs, timeline, avgs)
        hr()

    print_comparison_table(comparison)


def do_export():
    """Export the most recent run-all results to a file."""
    if not last_results:
        warn("No results to export. Run algorithms first.")
        return
    fname = prompt("Output filename [scheduling_results.txt]").strip()
    if not fname:
        fname = "scheduling_results.txt"
    try:
        path = export_results(last_results, fname)
        info(f"Results exported to: {path}")
    except Exception as exc:
        error(f"Export failed: {exc}")


# ─── Sub-menus ────────────────────────────────────────────────────────────────

def algo_menu():
    while True:
        section("Algorithm Selection")
        print_menu(ALGO_MENU, title="Choose an Algorithm")
        ch = read_choice([k for k, _ in ALGO_MENU])
        if ch == "0":
            break
        result = run_algorithm(ch)
        if result:
            last_results[result[0]] = (result[1], result[2], result[3])
        prompt("\nPress Enter to continue...")


# ─── Main loop ────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    clear()
    print_banner()

    # Non-interactive flags
    if "--sample" in args:
        load_sample()
        run_all()
        return

    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 < len(args):
            try:
                global processes
                processes = load_file(args[idx + 1])
                info(f"Loaded {len(processes)} processes.")
            except Exception as exc:
                error(str(exc))

    # Interactive menu loop
    while True:
        if processes:
            print_process_table(processes)
        print_menu(MENU_ITEMS, title="CPU Scheduling Simulator  v1.0")
        ch = read_choice([k for k, _ in MENU_ITEMS])

        if ch == "0":
            print()
            info("Thank you for using CPU Scheduling Simulator. Goodbye!")
            print()
            break
        elif ch == "1":  add_processes()
        elif ch == "2":  load_from_file()
        elif ch == "3":  load_sample()
        elif ch == "4":  algo_menu()
        elif ch == "5":  run_all()
        elif ch == "6":  do_export()
        elif ch == "7":  clear_processes()

        prompt("\nPress Enter to return to menu...")
        clear()
        print_banner()


if __name__ == "__main__":
    main()
