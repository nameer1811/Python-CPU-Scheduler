from re import L
from controller import controller
from process import VALID_STATES
import sys, time, threading

# still needs quantum and choosing of algorithm

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
                show_gui()

        start_time = time.process_time()

def show_gui():
    global paused
    header = " TIME: " + str(manager.system_time)+"ms "
    tick_num = max(0,128-len(header))//2
    print()
    print("-"*tick_num+header+"-"*(128-len(header)-tick_num))
    manager.update()
    print("-"*128)
    manager.print_process_info()
    manager.print_cpu_io_info()
    manager.print_queueing_info()
    print()
    manager.print_performance_metrics()

    # if all the processes are terminated, pause and then write a message
    if all([p.get_status() == VALID_STATES["TERMINATED"] for p in manager.processes]):
        paused = True
        print("ALL PROCESSES DONE!")
        manager.log_file.close()

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

            # if you press enter, progress
            if command == "" or command:
                paused = 1 - paused
        else:
            command = input()

            if command == "" or command:
                show_gui()