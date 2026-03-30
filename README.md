# CPU Scheduling Algorithm Simulator

A fully-featured, interactive CLI simulator for classic CPU scheduling algorithms,
built in Python with a clean, colorful terminal UI.

---

## Features

| Algorithm | Type | Description |
|-----------|------|-------------|
| **FCFS** | Non-preemptive | First Come First Serve |
| **SJF**  | Non-preemptive | Shortest Job First |
| **SRT**  | Preemptive     | Shortest Remaining Time |
| **RR**   | Preemptive     | Round Robin (configurable quantum) |
| **MLFQ** | Preemptive     | 3-level Multilevel Feedback Queue with aging |

- Colorized Gantt chart rendered in the terminal
- Per-process and average Waiting Time, Turnaround Time, Response Time
- Side-by-side comparison table across all algorithms (best highlighted ★)
- Add processes interactively, load from CSV/JSON, or use the built-in sample
- Export results to a plain-text file

---

## Requirements

- Python 3.10 or higher (uses `list[...]` type hints)
- No third-party libraries required — standard library only
- Works on Linux, macOS, and Windows Terminal (with ANSI color support)

---

## Project Structure

```
scheduler/
├── main.py          # Entry point — interactive CLI menu
├── algorithms.py    # FCFS, SJF, SRT, RR, MLFQ implementations
├── process.py       # Process data model
├── display.py       # CLI rendering: Gantt, tables, menus, colors
└── file_io.py       # CSV/JSON import, results export
```

---

## How to Run

### Interactive Mode (recommended)
```bash
python main.py
```

### Load sample scenario (P1–P4) and run all algorithms immediately
```bash
python main.py --sample
```

### Load processes from a file, then open the interactive menu
```bash
python main.py --file processes.csv
python main.py --file processes.json
```

---

## Sample Input Files

From the interactive menu choose **"Load Processes from CSV/JSON"** and
then **"y"** to generate template files, or create them manually:

**sample_processes.csv**
```csv
pid,arrival,burst
P1,0,5
P2,1,3
P3,2,8
P4,3,6
```

**sample_processes.json**
```json
[
  {"pid": "P1", "arrival": 0, "burst": 5},
  {"pid": "P2", "arrival": 1, "burst": 3},
  {"pid": "P3", "arrival": 2, "burst": 8},
  {"pid": "P4", "arrival": 3, "burst": 6}
]
```

An optional `priority` field is supported (used by MLFQ tie-breaking).

---

## Sample Output (FCFS, sample scenario)

```
  Gantt Chart

  ┌──────────┬──────┬────────────────┬────────────┐
  │    P1    │  P2  │       P3       │     P4     │
  └──────────┴──────┴────────────────┴────────────┘
  0         5     8               16          22

  Process  Arrival  Burst   Finish  Waiting  Turnaround  Response
  ─────────────────────────────────────────────────────────────────
   P1         0       5       5        0          5          0
   P2         1       3       8        4          7          4
   P3         2       8       16       6          14         6
   P4         3       6       22       13         19         13
  ─────────────────────────────────────────────────────────────────
  AVERAGE                             5.75       11.25      5.75
```

---

## Algorithm Descriptions

### FCFS — First Come First Serve
Processes are executed in order of arrival. Simple FIFO queue. No preemption.
CPU may be idle if no process has arrived. Tie in arrival time is broken by PID.

### SJF — Shortest Job First (Non-preemptive)
At each scheduling point the available process with the shortest burst time is
selected. Once started it runs to completion. Can cause starvation of long jobs.

### SRT — Shortest Remaining Time (Preemptive SJF)
At every clock tick the ready process with the smallest remaining burst time is
chosen. A newly arrived process can preempt the current one if its burst is
shorter. Tracks remaining time per process with per-tick simulation.

### Round Robin
Processes take turns on the CPU for at most `quantum` time units. If a process
doesn't finish in its turn it is re-queued at the back. Newly arrived processes
are inserted before the current process is re-queued (standard variant).

### MLFQ — Multilevel Feedback Queue
Three queues with decreasing priority:

| Queue | Algorithm | Quantum |
|-------|-----------|---------|
| Q0 (highest) | Round Robin | q (default 2) |
| Q1 | Round Robin | 2q (default 4) |
| Q2 (lowest)  | FCFS | ∞ |

- **Demotion**: A process that exhausts its full quantum is moved to the next lower queue.
- **Promotion (aging)**: A process waiting more than `aging_threshold` (default 10) ticks is promoted one level to prevent starvation.
- New arrivals always enter Q0.

---

## Metrics

| Metric | Formula |
|--------|---------|
| **Turnaround Time (TAT)** | Finish Time − Arrival Time |
| **Waiting Time (WT)** | TAT − Burst Time |
| **Response Time (RT)** | First CPU Time − Arrival Time |

---

## Exporting Results

After running all algorithms, choose **"Export Results to File"** from the
main menu to save a formatted plain-text report (default: `scheduling_results.txt`).
