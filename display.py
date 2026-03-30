"""
display.py - CLI Rendering Engine
Beautiful terminal output: Gantt charts, metric tables, menus, banners.
Uses ANSI escape codes for color; gracefully degrades if not supported.
"""

import os
import sys
import shutil

# ── Terminal color/style codes ─────────────────────────────────────────────

class C:
    """ANSI color palette."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    BRIGHT_WHITE  = "\033[97m"
    BRIGHT_CYAN   = "\033[96m"
    BRIGHT_GREEN  = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE   = "\033[94m"
    BRIGHT_RED    = "\033[91m"

    # Backgrounds
    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"

    BG_BRIGHT_BLACK  = "\033[100m"
    BG_BRIGHT_BLUE   = "\033[104m"
    BG_BRIGHT_CYAN   = "\033[106m"
    BG_BRIGHT_GREEN  = "\033[102m"
    BG_BRIGHT_MAGENTA= "\033[105m"


# Process color cycling (background colors for Gantt blocks)
PROCESS_COLORS = [
    C.BG_BLUE, C.BG_GREEN, C.BG_MAGENTA, C.BG_CYAN,
    C.BG_RED, C.BG_YELLOW, C.BG_BRIGHT_BLUE, C.BG_BRIGHT_CYAN,
    C.BG_BRIGHT_GREEN, C.BG_BRIGHT_MAGENTA,
]

def _proc_color(pid: str) -> str:
    """Return a consistent background color for a given PID."""
    if pid == "IDLE":
        return C.BG_BRIGHT_BLACK
    # Hash on numeric suffix or whole pid
    try:
        idx = int("".join(c for c in pid if c.isdigit())) % len(PROCESS_COLORS)
    except ValueError:
        idx = sum(ord(c) for c in pid) % len(PROCESS_COLORS)
    return PROCESS_COLORS[idx]


def term_width() -> int:
    """Get current terminal width, default 100."""
    return shutil.get_terminal_size((100, 24)).columns


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ── Banner ─────────────────────────────────────────────────────────────────

BANNER = r"""
   ██████╗██████╗ ██╗   ██╗    ███████╗ ██████╗██╗  ██╗███████╗██████╗
  ██╔════╝██╔══██╗██║   ██║    ██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗
  ██║     ██████╔╝██║   ██║    ███████╗██║     ███████║█████╗  ██║  ██║
  ██║     ██╔═══╝ ██║   ██║    ╚════██║██║     ██╔══██║██╔══╝  ██║  ██║
  ╚██████╗██║     ╚██████╔╝    ███████║╚██████╗██║  ██║███████╗██████╔╝
   ╚═════╝╚═╝      ╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝
"""

SUB_BANNER = "  CPU Process Scheduling Algorithm Simulator  |  OS Project"


def print_banner():
    w = term_width()
    print(C.BRIGHT_CYAN + C.BOLD + BANNER + C.RESET)
    print(C.CYAN + SUB_BANNER.center(w) + C.RESET)
    print(C.DIM + ("─" * w) + C.RESET)
    print()


# ── Section headers ─────────────────────────────────────────────────────────

def section(title: str):
    w = term_width()
    bar = "═" * w
    print()
    print(C.BRIGHT_YELLOW + C.BOLD + bar + C.RESET)
    print(C.BRIGHT_YELLOW + C.BOLD + f"  {title}" + C.RESET)
    print(C.BRIGHT_YELLOW + C.BOLD + bar + C.RESET)


def sub_section(title: str):
    w = term_width()
    print()
    print(C.CYAN + C.BOLD + f"  ▶  {title}" + C.RESET)
    print(C.DIM + "  " + "─" * (w - 4) + C.RESET)


def info(msg: str):
    print(f"  {C.BRIGHT_GREEN}✔{C.RESET}  {msg}")


def warn(msg: str):
    print(f"  {C.BRIGHT_YELLOW}⚠{C.RESET}  {msg}")


def error(msg: str):
    print(f"  {C.BRIGHT_RED}✖{C.RESET}  {C.RED}{msg}{C.RESET}")


def prompt(msg: str) -> str:
    return input(f"  {C.BRIGHT_CYAN}❯{C.RESET}  {msg} ")


# ── Process input table ─────────────────────────────────────────────────────

def print_process_table(processes: list) -> None:
    """Print the list of processes in a formatted table."""
    if not processes:
        warn("No processes defined.")
        return

    has_priority = any(p.priority != 0 for p in processes)
    print()
    # Header
    if has_priority:
        header = f"  {'PID':<8} {'Arrival':<12} {'Burst':<10} {'Priority':<10}"
    else:
        header = f"  {'PID':<8} {'Arrival':<12} {'Burst':<10}"
    print(C.BOLD + C.WHITE + header + C.RESET)
    print(C.DIM + "  " + "─" * (len(header) - 2) + C.RESET)

    for p in processes:
        color = _proc_color(p.pid)
        tag = f"{color}{C.BOLD} {p.pid:<4} {C.RESET}"
        if has_priority:
            row = f"  {tag}   {str(p.arrival):<12} {str(p.burst):<10} {str(p.priority):<10}"
        else:
            row = f"  {tag}   {str(p.arrival):<12} {str(p.burst):<10}"
        print(row)
    print()


# ── Gantt Chart ─────────────────────────────────────────────────────────────

def print_gantt(timeline: list, scale: int = 2) -> None:
    """
    Render a visual Gantt chart from timeline = [(label, start, end), ...].
    `scale` controls how many chars per time unit (min 1).
    """
    if not timeline:
        warn("No timeline to display.")
        return

    # Merge consecutive same-pid entries for cleaner chart
    merged = []
    for entry in timeline:
        if merged and merged[-1][0] == entry[0]:
            merged[-1] = (merged[-1][0], merged[-1][1], entry[2])
        else:
            merged.append(list(entry))

    w = term_width()
    total_time = merged[-1][2]

    # Auto-scale if chart would be wider than terminal
    # Each unit needs scale chars + borders
    needed = sum((e[2] - e[1]) * scale + 1 for e in merged) + 2
    while needed > w - 4 and scale > 1:
        scale -= 1
        needed = sum((e[2] - e[1]) * scale + 1 for e in merged) + 2

    print()
    print(C.BOLD + "  Gantt Chart" + C.RESET)
    print()

    # ── Top border ──
    top = "  ┌"
    for i, (label, s, e) in enumerate(merged):
        width = (e - s) * scale
        top += "─" * max(width, len(label) + 2)
        top += "┬" if i < len(merged) - 1 else "┐"
    print(top)

    # ── Content row ──
    row = "  │"
    for label, s, e in merged:
        width = (e - s) * scale
        cell_w = max(width, len(label) + 2)
        text = label.center(cell_w)
        color = _proc_color(label)
        fg = C.BLACK if label != "IDLE" else C.DIM
        row += f"{color}{fg}{C.BOLD}{text}{C.RESET}│"
    print(row)

    # ── Bottom border ──
    bot = "  └"
    for i, (label, s, e) in enumerate(merged):
        width = (e - s) * scale
        bot += "─" * max(width, len(label) + 2)
        bot += "┴" if i < len(merged) - 1 else "┘"
    print(bot)

    # ── Time markers ──
    times = "  "
    for label, s, e in merged:
        width = (e - s) * scale
        cell_w = max(width, len(label) + 2)
        marker = str(s)
        times += marker.ljust(cell_w)
    times += str(total_time)
    print(C.DIM + times + C.RESET)
    print()


# ── Metrics Table ───────────────────────────────────────────────────────────

def print_metrics_table(procs: list, averages: dict) -> None:
    """Print WT, TAT, RT table with averages row."""
    print()
    # Column widths
    cols = ["Process", "Arrival", "Burst", "Finish", "Waiting", "Turnaround", "Response"]
    widths = [9, 8, 7, 8, 9, 12, 10]

    def fmt_header():
        h = "  "
        for col, w in zip(cols, widths):
            h += C.BOLD + C.WHITE + col.center(w) + C.RESET + " "
        return h

    def divider(char="─"):
        return "  " + C.DIM + (char * (sum(widths) + len(widths))) + C.RESET

    print(fmt_header())
    print(divider())

    for p in sorted(procs, key=lambda x: x.pid):
        color = _proc_color(p.pid)
        pid_cell = f"{color}{C.BOLD} {p.pid:<5}{C.RESET}"
        def cell(val, w):
            return str(val).center(w)

        row = (f"  {pid_cell}  "
               f"{cell(p.arrival, widths[1])} "
               f"{cell(p.burst,   widths[2])} "
               f"{cell(p.finish_time, widths[3])} "
               f"{C.BRIGHT_GREEN}{cell(p.waiting_time,    widths[4])}{C.RESET} "
               f"{C.BRIGHT_CYAN }{cell(p.turnaround_time, widths[5])}{C.RESET} "
               f"{C.BRIGHT_YELLOW}{cell(p.response_time,  widths[6])}{C.RESET}")
        print(row)

    print(divider())

    # Averages row
    avg_row = (f"  {'AVERAGE'.center(widths[0])}  "
               f"{'':>{widths[1]}} "
               f"{'':>{widths[2]}} "
               f"{'':>{widths[3]}} "
               f"{C.BRIGHT_GREEN}{C.BOLD}{str(averages['avg_wt']).center(widths[4])}{C.RESET} "
               f"{C.BRIGHT_CYAN }{C.BOLD}{str(averages['avg_tat']).center(widths[5])}{C.RESET} "
               f"{C.BRIGHT_YELLOW}{C.BOLD}{str(averages['avg_rt']).center(widths[6])}{C.RESET}")
    print(avg_row)
    print()


# ── Comparison Table ────────────────────────────────────────────────────────

def print_comparison_table(results: dict) -> None:
    """
    results = {algo_name: {"avg_wt": x, "avg_tat": y, "avg_rt": z}}
    Highlights best (lowest) value in each column.
    """
    if not results:
        return

    section("Comparative Analysis — All Algorithms")

    cols = ["Algorithm", "Avg Wait", "Avg Turnaround", "Avg Response"]
    widths = [18, 12, 16, 14]

    def hdr():
        h = "  "
        for col, w in zip(cols, widths):
            h += C.BOLD + C.WHITE + col.center(w) + " " + C.RESET
        return h

    def div():
        return "  " + C.DIM + "─" * (sum(widths) + len(widths)) + C.RESET

    print()
    print(hdr())
    print(div())

    # Find bests
    best_wt  = min(v["avg_wt"]  for v in results.values())
    best_tat = min(v["avg_tat"] for v in results.values())
    best_rt  = min(v["avg_rt"]  for v in results.values())

    for algo, metrics in results.items():
        wt  = metrics["avg_wt"]
        tat = metrics["avg_tat"]
        rt  = metrics["avg_rt"]

        wt_s  = (C.BRIGHT_GREEN + C.BOLD + "★ " + str(wt).center(10) + C.RESET) if wt  == best_wt  else str(wt).center(widths[1])
        tat_s = (C.BRIGHT_GREEN + C.BOLD + "★ " + str(tat).center(12) + C.RESET) if tat == best_tat else str(tat).center(widths[2])
        rt_s  = (C.BRIGHT_GREEN + C.BOLD + "★ " + str(rt).center(12)  + C.RESET) if rt  == best_rt  else str(rt).center(widths[3])

        print(f"  {algo:<{widths[0]}} {wt_s} {tat_s} {rt_s}")

    print(div())
    print()
    print(f"  {C.BRIGHT_GREEN}★{C.RESET} = Best (lowest) value in that metric")
    print()


# ── Main Menu ───────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("1", "Add / Edit Processes"),
    ("2", "Load Processes from CSV / JSON"),
    ("3", "Load Sample Scenario  (P1–P4)"),
    ("4", "Run a Specific Algorithm"),
    ("5", "Run ALL Algorithms & Compare"),
    ("6", "Export Results to File"),
    ("7", "Clear Processes"),
    ("0", "Exit"),
]

ALGO_MENU = [
    ("1", "FCFS  — First Come First Serve"),
    ("2", "SJF   — Shortest Job First (Non-preemptive)"),
    ("3", "SRT   — Shortest Remaining Time (Preemptive)"),
    ("4", "RR    — Round Robin"),
    ("5", "MLFQ  — Multilevel Feedback Queue"),
    ("0", "Back"),
]


def print_menu(items: list, title: str = "Main Menu") -> None:
    w = term_width()
    print()
    print(C.BOLD + C.BRIGHT_BLUE + f"  ╔{'═' * (w - 4)}╗" + C.RESET)
    print(C.BOLD + C.BRIGHT_BLUE + f"  ║{('  ' + title).ljust(w - 4)}║" + C.RESET)
    print(C.BOLD + C.BRIGHT_BLUE + f"  ╠{'═' * (w - 4)}╣" + C.RESET)
    for key, label in items:
        line = f"  ║  [{C.BRIGHT_YELLOW}{key}{C.BOLD}{C.BRIGHT_BLUE}]  {label}"
        padding = w - 4 - 7 - len(label)
        print(C.BOLD + C.BRIGHT_BLUE + line + " " * max(0, padding) + "║" + C.RESET)
    print(C.BOLD + C.BRIGHT_BLUE + f"  ╚{'═' * (w - 4)}╝" + C.RESET)
    print()


def hr():
    print(C.DIM + "─" * term_width() + C.RESET)
