"""
algorithms.py - CPU Scheduling Algorithm Implementations
Implements: FCFS, SJF (non-preemptive), SRT (preemptive), RR, MLFQ
"""

from process import Process, clone_processes


# ---------------------------------------------------------------------------
# Helper type: GanttEntry = (pid_label, start, end)
# ---------------------------------------------------------------------------

def _finish(procs: list[Process], timeline: list) -> None:
    """Compute metrics for all processes given a completed Gantt timeline."""
    for p in procs:
        p.compute_metrics()


# ---------------------------------------------------------------------------
# 1. FCFS – First Come First Serve (non-preemptive)
# ---------------------------------------------------------------------------

def fcfs(processes: list[Process]) -> tuple[list[Process], list]:
    """
    Schedule processes in order of arrival time (FIFO).
    Ties in arrival are broken by PID lexicographic order.
    Returns cloned processes with metrics and a Gantt timeline.
    """
    procs = clone_processes(processes)
    # Sort by arrival time, then by PID for stable tie-breaking
    queue = sorted(procs, key=lambda p: (p.arrival, p.pid))

    timeline = []   # List of (label, start, end)
    time = 0

    for p in queue:
        # CPU may be idle if next process hasn't arrived yet
        if time < p.arrival:
            timeline.append(("IDLE", time, p.arrival))
            time = p.arrival

        # Record first response
        p.start_time = time
        time += p.burst
        p.finish_time = time

        timeline.append((p.pid, p.start_time, p.finish_time))

    _finish(procs, timeline)
    return procs, timeline
3

# ---------------------------------------------------------------------------
# 2. SJF – Shortest Job First (non-preemptive)
# ---------------------------------------------------------------------------

def sjf(processes: list[Process]) -> tuple[list[Process], list]:
    """
    At each scheduling point pick the available process with shortest burst.
    Non-preemptive: once a process starts it runs to completion.
    """
    procs = clone_processes(processes)
    remaining = list(procs)  # processes not yet started
    timeline = []
    time = 0

    while remaining:
        # Collect all processes that have arrived
        available = [p for p in remaining if p.arrival <= time]

        if not available:
            # CPU idle – jump to the next arrival
            next_arrival = min(p.arrival for p in remaining)
            timeline.append(("IDLE", time, next_arrival))
            time = next_arrival
            continue

        # Pick shortest burst; break ties by arrival then PID
        chosen = min(available, key=lambda p: (p.burst, p.arrival, p.pid))
        remaining.remove(chosen)

        chosen.start_time = time
        time += chosen.burst
        chosen.finish_time = time
        timeline.append((chosen.pid, chosen.start_time, chosen.finish_time))

    _finish(procs, timeline)
    return procs, timeline


# # ---------------------------------------------------------------------------
# # 3. SRT – Shortest Remaining Time (preemptive SJF)
# # ---------------------------------------------------------------------------

# def srt(processes: list[Process]) -> tuple[list[Process], list]:
#     """
#     Preemptive version of SJF.  At every time unit check if a newly arrived
#     process has a shorter remaining time than the running one; if so preempt.
#     Timeline entries are merged when the same process runs consecutively.
#     """
#     procs = clone_processes(processes)
#     remaining = list(procs)   # processes not yet finished
#     timeline = []
#     time = 0
#     current = None

#     # Determine simulation end
#     end_time = sum(p.burst for p in procs) + max(p.arrival for p in procs)

#     while remaining or current:
#         # Processes that have arrived (including currently running)
#         available = [p for p in remaining if p.arrival <= time]
#         if current and current in available:
#             available_check = available
#         elif current:
#             available_check = available + [current] if current.remaining > 0 else available
#         else:
#             available_check = available

#         # Re-evaluate available at this tick
#         ready = [p for p in remaining if p.arrival <= time]

#         if not ready and current is None:
#             # CPU idle
#             next_arr = min(p.arrival for p in remaining)
#             timeline.append(("IDLE", time, next_arr))
#             time = next_arr
#             continue

#         if ready:
#             # Pick process with shortest remaining time; tie-break arrival, PID
#             candidate = min(ready, key=lambda p: (p.remaining, p.arrival, p.pid))
#         else:
#             candidate = None

#         # Decide who runs this tick
#         if current is None:
#             current = candidate
#             if current:
#                 remaining.remove(current) if current in remaining else None
#         elif candidate and candidate.remaining < current.remaining:
#             # Preempt: put current back conceptually (it stays in procs list)
#             current = candidate
#             if current in remaining:
#                 remaining.remove(current)

#         if current is None:
#             time += 1
#             continue

#         # Record first CPU access
#         if current.start_time == -1:
#             current.start_time = time

#         # Append to Gantt (merge consecutive same-process entries)
#         if timeline and timeline[-1][0] == current.pid:
#             timeline[-1] = (timeline[-1][0], timeline[-1][1], time + 1)
#         else:
#             timeline.append((current.pid, time, time + 1))

#         current.remaining -= 1
#         time += 1

#         if current.remaining == 0:
#             current.finish_time = time
#             current = None

#     _finish(procs, timeline)
#     return procs, timeline

def srt(processes: list[Process]) -> tuple[list[Process], list]:
    procs = clone_processes(processes)
    remaining = list(procs)
    timeline = []
    time = 0
    current = None

    # Initialize remaining burst and start time
    for p in procs:
        p.remaining = p.burst
        p.start_time = None

    while remaining or current:
        # Processes that have arrived
        available = [p for p in remaining if p.arrival <= time]

        if not available and current is None:
            # CPU idle
            next_arrival = min(p.arrival for p in remaining)
            timeline.append(("IDLE", time, next_arrival))
            time = next_arrival
            continue

        # Choose process with shortest remaining burst
        candidate = None
        if available:
            candidate = min(available, key=lambda p: (p.remaining, p.arrival, p.pid))

        # Preemption
        if current is None:
            current = candidate
            if current in remaining:
                remaining.remove(current)
        elif candidate and candidate.remaining < current.remaining:
            # Preempt current
            if current.remaining > 0:
                remaining.append(current)
            current = candidate
            remaining.remove(current)

        # Record first start time
        if current.start_time is None:
            current.start_time = time

        # Add to timeline
        if timeline and timeline[-1][0] == current.pid:
            timeline[-1] = (timeline[-1][0], timeline[-1][1], time + 1)
        else:
            timeline.append((current.pid, time, time + 1))

        # Run for 1 unit
        current.remaining -= 1
        time += 1

        # Finish
        if current.remaining == 0:
            current.finish_time = time
            current = None

    _finish(procs, timeline)  # compute WT, TAT, RT
    return procs, timeline


# ---------------------------------------------------------------------------
# 4. Round Robin (preemptive, configurable quantum)
# ---------------------------------------------------------------------------

def round_robin(processes: list[Process], quantum: int = 2) -> tuple[list[Process], list]:
    """
    Each process gets at most `quantum` time units per turn.
    Newly arrived processes are added to the back of the ready queue.
    If a process doesn't finish in its quantum it's re-queued at the back.
    """
    procs = clone_processes(processes)
    # Sort by arrival for initial ordering
    not_arrived = sorted(procs, key=lambda p: (p.arrival, p.pid))
    ready_queue = []   # deque-style list of process references
    timeline = []
    time = 0

    # Seed: enqueue processes that arrive at time 0
    for p in not_arrived:
        if p.arrival <= time:
            ready_queue.append(p)
    not_arrived = [p for p in not_arrived if p not in ready_queue]

    while ready_queue or not_arrived:
        if not ready_queue:
            # CPU idle
            next_arr = min(p.arrival for p in not_arrived)
            timeline.append(("IDLE", time, next_arr))
            time = next_arr
            # Enqueue all that arrived
            newly = [p for p in not_arrived if p.arrival <= time]
            for p in sorted(newly, key=lambda x: (x.arrival, x.pid)):
                ready_queue.append(p)
            not_arrived = [p for p in not_arrived if p not in ready_queue]
            continue

        proc = ready_queue.pop(0)

        if proc.start_time == -1:
            proc.start_time = time

        run_time = min(quantum, proc.remaining)
        start = time
        time += run_time
        proc.remaining -= run_time

        timeline.append((proc.pid, start, time))

        # Enqueue newly arrived processes BEFORE re-queueing current
        newly = [p for p in not_arrived if p.arrival <= time]
        for p in sorted(newly, key=lambda x: (x.arrival, x.pid)):
            ready_queue.append(p)
        not_arrived = [p for p in not_arrived if p not in ready_queue]

        if proc.remaining > 0:
            ready_queue.append(proc)   # re-queue at back
        else:
            proc.finish_time = time

    _finish(procs, timeline)
    return procs, timeline


# ---------------------------------------------------------------------------
# 5. MLFQ – Multilevel Feedback Queue
#    Queue 0: RR q=2  |  Queue 1: RR q=4  |  Queue 2: FCFS
#    Demotion: process uses full quantum → moved to lower queue
#    Promotion (aging): process waits > aging_threshold ticks → promoted
# ---------------------------------------------------------------------------

def mlfq(processes: list[Process],
         quantums: list[int] = None,
         aging_threshold: int = 10) -> tuple[list[Process], list]:
    """
    3-level Multilevel Feedback Queue.
    quantums: [q0, q1]  (queue 2 is FCFS, no quantum limit)
    aging_threshold: ticks a process waits before being promoted one level.
    """
    if quantums is None:
        quantums = [2, 4]   # Queue 0 and Queue 1 quantums; Queue 2 = FCFS

    procs = clone_processes(processes)
    not_arrived = sorted(procs, key=lambda p: (p.arrival, p.pid))

    # Three queues; each holds (process, queue_level)
    queues = [[], [], []]          # queues[0] = highest priority
    queue_levels = {p.pid: 0 for p in procs}   # Track current queue of each
    wait_since = {}                # pid -> time when it started waiting in queue

    timeline = []
    time = 0

    def enqueue(proc, level):
        """Add a process to a queue and record when it started waiting."""
        level = max(0, min(2, level))
        queues[level].append(proc)
        queue_levels[proc.pid] = level
        wait_since[proc.pid] = time

    def dequeue_from_level(level):
        """Pop the first process from a queue level."""
        if queues[level]:
            proc = queues[level].pop(0)
            return proc
        return None

    # Enqueue processes that have arrived at time 0
    for p in not_arrived:
        if p.arrival <= time:
            enqueue(p, 0)
    not_arrived = [p for p in not_arrived if p not in queues[0]]

    max_ticks = sum(p.burst for p in procs) * 3 + 50  # safety limit

    while any(queues) or not_arrived:
        # --- Aging: promote processes that have waited too long ---
        for level in range(1, 3):
            for proc in list(queues[level]):
                waited = time - wait_since.get(proc.pid, time)
                if waited >= aging_threshold:
                    queues[level].remove(proc)
                    new_level = level - 1
                    enqueue(proc, new_level)

        # --- Find highest-priority non-empty queue ---
        chosen_level = None
        for lvl in range(3):
            if queues[lvl]:
                chosen_level = lvl
                break

        if chosen_level is None:
            # CPU idle
            if not_arrived:
                next_arr = min(p.arrival for p in not_arrived)
                timeline.append(("IDLE", time, next_arr))
                time = next_arr
                newly = [p for p in not_arrived if p.arrival <= time]
                for p in sorted(newly, key=lambda x: (x.arrival, x.pid)):
                    enqueue(p, 0)
                not_arrived = [p for p in not_arrived if p not in
                               queues[0] + queues[1] + queues[2]]
            continue

        proc = dequeue_from_level(chosen_level)

        if proc.start_time == -1:
            proc.start_time = time

        # Determine quantum for this level
        if chosen_level == 0:
            q = quantums[0]
        elif chosen_level == 1:
            q = quantums[1]
        else:
            q = proc.remaining   # FCFS: run to completion

        run_time = min(q, proc.remaining)
        start = time
        time += run_time
        proc.remaining -= run_time

        timeline.append((proc.pid, start, time))

        # Enqueue newly arrived processes at queue 0
        newly = [p for p in not_arrived if p.arrival <= time]
        for p in sorted(newly, key=lambda x: (x.arrival, x.pid)):
            enqueue(p, 0)
        not_arrived = [p for p in not_arrived if p not in
                      queues[0] + queues[1] + queues[2]]

        if proc.remaining > 0:
            # Used full quantum → demote (unless already at bottom)
            if proc.remaining < proc.burst:  # it actually ran a full quantum
                new_level = min(chosen_level + 1, 2)
            else:
                new_level = chosen_level
            enqueue(proc, new_level)
        else:
            proc.finish_time = time

    _finish(procs, timeline)
    return procs, timeline


# ---------------------------------------------------------------------------
# Metrics Summary Helper
# ---------------------------------------------------------------------------

def compute_averages(procs: list[Process]) -> dict:
    """Return dict with average WT, TAT, RT across all processes."""
    n = len(procs)
    return {
        "avg_wt":  round(sum(p.waiting_time    for p in procs) / n, 2),
        "avg_tat": round(sum(p.turnaround_time for p in procs) / n, 2),
        "avg_rt":  round(sum(p.response_time   for p in procs) / n, 2),
    }
