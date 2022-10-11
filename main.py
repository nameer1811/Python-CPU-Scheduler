from process import process
from controller import controller
import sys

# First-come first-serve
# Round Robin
# Shortest Job First
# Priority Scheduling

processes = []
fps = 0

# process has:
# id 
# arrival time
# priority
# cpu bursts
# io bursts
# start time
# finish time
# wait time
# wait io time
# state/status: new, ready, running, waiting, terminated

# performance metrics:
# cpu utilization, throughput, turnaround time, waiting time, response time

# needs simulation mode, 0 for auto, 1 for manual mode
# simulation unit time in miliseconds the time taken between tow steps (FPS basically)
# quantum time slice

file = sys.argv[-1]
manager = controller()
manager.generate_processes(file)
manager.priority_scheduling()