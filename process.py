"""
process.py - Process data model for CPU Scheduling Simulator
"""

class Process:
    """Represents a single CPU process with scheduling metadata."""

    def __init__(self, pid: str, arrival: int, burst: int, priority: int = 0):
        self.pid = pid                    # Process identifier (e.g. P1)
        self.arrival = arrival            # Arrival time in the ready queue
        self.burst = burst                # Total CPU burst time needed
        self.priority = priority          # Priority (used by MLFQ)

        # Metrics computed after scheduling
        self.start_time = -1              # First time process gets CPU
        self.finish_time = 0             # Time process completes execution
        self.waiting_time = 0            # Total time spent waiting
        self.turnaround_time = 0         # finish_time - arrival_time
        self.response_time = 0           # start_time - arrival_time

        # Internal state for simulation
        self.remaining = burst           # Remaining burst (used by preemptive)

    def reset(self):
        """Reset computed fields so the same process can be re-simulated."""
        self.start_time = -1
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = 0
        self.remaining = self.burst

    def compute_metrics(self):
        """Calculate WT, TAT, RT after finish_time and start_time are set."""
        self.turnaround_time = self.finish_time - self.arrival
        self.waiting_time = self.turnaround_time - self.burst
        self.response_time = self.start_time - self.arrival

    def __repr__(self):
        return (f"Process({self.pid}, arr={self.arrival}, "
                f"burst={self.burst}, rem={self.remaining})")


def clone_processes(processes: list[Process]) -> list[Process]:
    """Return fresh copies of a process list with reset state."""
    clones = []
    for p in processes:
        c = Process(p.pid, p.arrival, p.burst, p.priority)
        clones.append(c)
    return clones
