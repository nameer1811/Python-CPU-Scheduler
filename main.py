from re import L
from controller import controller
import sys, time, threading

# First-come first-serve
# Round Robin
# Shortest Job First
# Priority Scheduling
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

file = sys.argv[1]
manager = controller()
manager.generate_processes(file)
FPS = 60
QUANTUM = 3

auto_mode = ("-auto" in sys.argv)

if ("-fps" in sys.argv):
    try:
        FPS = int(sys.argv[sys.argv.index("-fps")+1])
    except:
        print("Invalid or Null FPS entered, defaulting to 60")

if ("-quantum" in sys.argv):
    try:
        QUANTUM = int(sys.argv[sys.argv.index("-quantum")+1])
    except:
        print("Invalid or Null quantum entered, defaulting to 3")

paused = False

def printer():
    global paused
    sim_time= 0
    start_time = None

    while not paused:
        # If the sim isn't paused, update the CPU sim according to our desired FPS
        if start_time != None:
            delta = time.process_time() - start_time
            sim_time += delta

            # Seeing if we're within the delta range to our desired update interval
            # We do this to avoid floating point issues
            if (sim_time % (1/FPS) < delta):
                #print("{:.2f}".format(sim_time))
                manager.update()
                print("-"*128)
                manager.print_process_info()
                manager.print_cpu_io_info()

        start_time = time.process_time()


# Multithreading is used to achieve pausing and unpausing with console input
if __name__ == '__main__':
    while True:

        if auto_mode:
            if paused:
                print("You paused")
            else:
                print("Unpaused")              
                printing_proc = threading.Thread(target=printer, daemon=True)
                printing_proc.start()
            
            command = input()

            if command == "":
                paused = 1 - paused
        else:
            command = input()

            if command == "":
                manager.update()
                print("-"*128)
                manager.print_process_info()
                manager.print_cpu_io_info()