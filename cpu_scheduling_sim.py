from controller import controller, ALGORITHMS
from process import VALID_STATES
import sys, time, threading

ALGORITHM_STRINGS = dict((v, k) for k, v in ALGORITHMS.items())

if len(sys.argv) > 1:
    file = sys.argv[1]

    manager = controller()
    manager.generate_processes(file)
    FPS = 60
    auto_mode = ("-auto" in sys.argv)

    try:
        manager.set_algorithm(["-"+a.lower() in sys.argv for a in ALGORITHMS].index(True)) 
    except:
        pass

    if not auto_mode:
        print("-"*128)
        print()
        print("Press ENTER to begin and advance the program")
        print()
        print("-"*128)

    if ("-fps" in sys.argv):
        try:
            FPS = int(sys.argv[sys.argv.index("-fps")+1])
        except:
            print("Invalid or Null FPS entered, defaulting to 60")

    if ("-quantum" in sys.argv):
        try:
            manager.set_quantum(int(sys.argv[sys.argv.index("-quantum")+1]))
        except:
            print("Invalid or Null quantum entered, defaulting to 3")

    paused = False
    running = True

    def printer():
        global paused
        sim_time= 0
        start_time = None

        while not paused and running:
            # If the sim isn't paused, update the CPU sim according to our desired FPS
            if start_time != None:
                delta = time.process_time() - start_time
                sim_time += delta

                # Seeing if we're within the delta range to our desired update interval
                # We do this to avoid floating point issues
                if (sim_time % (1/FPS) < delta):
                    show_gui()

            start_time = time.process_time()
        sys.exit()

    def show_gui():
        global paused, running
        header = " TIME: " + str(manager.system_time)+"ms "
        tick_num = max(0,128-len(header))//2
        print()
        print("-"*tick_num+header+"-"*(128-len(header)-tick_num))
        
        manager.update()

        footer = f"ALGORITHM: {ALGORITHM_STRINGS[manager.algorithm]}"
        tick_num = max(0,128-len(footer))//2
        print("-"*tick_num+footer+"-"*(128-len(footer)-tick_num))

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
            running = False

    # Multithreading is used to achieve pausing and unpausing with console input
    if __name__ == '__main__':
        while running:
            if auto_mode:
                if paused:
                    print("-"*128)
                    print()
                    print("You paused")
                    print()
                    print("-"*128)
                else:              
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
        sys.exit()
    else:
        print("No File Provided, Closing")