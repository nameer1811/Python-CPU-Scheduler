from process import process, VALID_STATES

ALGORITHMS = {"FCFS": 0, "SJF": 1, "RR": 2, "PS": 3}
STATE_STRING = dict((v, k) for k, v in VALID_STATES.items())

class controller:
    def __init__(self):
        self.processes = []
        # when there is instances in these, the timer should add numbers to them :3
        self.ready_queue = []
        self.cpu_focus = None
        self.io_queue = []
        self.io_focus = None  # the process the io device is focusing on
        self.algorithm = ALGORITHMS["PS"]
        self.system_time = 0

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
    def generate_processes(self, file: str):
        # adding all the processes from a file one by one with their relevant information
        for id, process_line in enumerate(open(file)):
            # import
            data = [id] + list(map(int, process_line.strip().split(" ")[1::]))

            cpu_bursts = []
            io_bursts = []

            # adding the potentially infinite alternating burst types
            for burst_type, burst in enumerate(data[3::]):
                # it's a cpu burst
                if burst_type % 2 == 0:
                    cpu_bursts.append(burst)
                else:  # it's an io burst
                    io_bursts.append(burst)

            self.processes.append(
                process(data[0], data[1], data[2], cpu_bursts, io_bursts))

    # Updating the CPU sim's system time and processing accordingly
    def update(self):
        # Handeling state changes
        # checks for processes which have arrived in the system and sets their state to ready, putting them in the queue
        for process in self.processes:
            if process.arr_time == self.system_time:
                self.add_to_ready_queue(process)

            # incremeneting onto the respective wait time counters of each process in the ready queue or io queue
            if process.get_status() == VALID_STATES["READY"]:
                process.wait_time += 1
            elif process.get_status() == VALID_STATES["WAITING"]:
                process.io_wait_time += 1

            # incremeneting the turnaround time counter
            process.life += 1

        self.process_cpu()
        self.process_io()

        # advancing the system clock
        self.system_time += 1

    def add_to_ready_queue(self,process):
        self.ready_queue.append(process)
        process.set_status(VALID_STATES["READY"])

        if self.algorithm == ALGORITHMS["SJF"]:
            self.sjf()
        elif self.algorithm == ALGORITHMS["PS"]:
            self.priority_scheduling()
        elif self.algorithm == ALGORITHMS["RR"]:
            pass
        
    # Sets state to ready and adds a start time if necessary
    def execute(self,process):
        # change the process status to running and remove it from the ready queue
        process.set_status(VALID_STATES["RUNNING"])
        self.ready_queue.remove(process)

        # Show the time the process started
        if process.start == -1:
            process.start = self.system_time

    def process_cpu(self):
        # Process the cpu's focus
        if self.cpu_focus != None:
            # Preempting in priority scheduling
            if self.algorithm == ALGORITHMS["PS"]:
                if len(self.ready_queue) > 0:
                    # if the current process's priority is lower than another ready process, premept
                    if self.cpu_focus.priority > self.ready_queue[0].priority:
                        preempted_process = self.cpu_focus

                        # set new focus process and remove the focus from the ready queue
                        self.cpu_focus = self.ready_queue[0]
                        self.execute(self.cpu_focus)

                        # move prempted process to ready queue
                        self.add_to_ready_queue(preempted_process)

            if self.algorithm != ALGORITHMS["RR"]:
                # decrease the burst time
                self.cpu_focus.cpu_bursts[0] -= 1

                # if the burst has gotten down to zero, either terminate the process, or check if it needs to wait on I/O
                if self.cpu_focus.cpu_bursts[0] == 0:
                    if self.cpu_focus.cpu_bursts[-1] == 0:
                        self.cpu_focus.set_status(VALID_STATES["TERMINATED"])

                        # reflect the time the process ended
                        self.cpu_focus.finish = self.system_time

                    else:
                        # adding the process to the IO queue if it has IO bursts and setting the process status to reflect that
                        if len(self.cpu_focus.io_bursts) != 0:
                            self.io_queue.append(self.cpu_focus)
                            self.cpu_focus.set_status(VALID_STATES["WAITING"])
                    
                    # delete the burst now that it's at 0
                    self.cpu_focus.cpu_bursts = self.cpu_focus.cpu_bursts[1::]
                    self.cpu_focus = None

        # If the system is idle, it finds the next relevant process
        if self.cpu_focus == None:
            if len(self.ready_queue) > 0:
                # Dispatch relevant process as the CPU's focus
                self.cpu_focus = self.ready_queue[0]

                self.execute(self.cpu_focus)



    def process_io(self):
        # if the IO device has a process to work on, it works on it 
        if self.io_focus != None:
            # decrease the burst time
            self.io_focus.io_bursts[0] -= 1

            # if io_burst time gets down to zero, clear it from the burst list, clear it from the IO device, and put it in the ready queue
            if self.io_focus.io_bursts[0] == 0:
                # remove the burst from the burst list now that it's at 0
                self.io_focus.io_bursts = self.io_focus.io_bursts[1::]
                self.add_to_ready_queue(self.io_focus)
                self.io_focus = None
        
        # If the IO device is available and there's still processes in the IO queue give the process the IO device
        if self.io_focus == None:
            if len(self.io_queue) > 0:
                # allocate the IO device
                self.io_focus = self.io_queue[0]

                # remove it from the IO queue
                self.io_queue = self.io_queue[1::]
    
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    # print out all the relevant process info
    def print_process_info(self):
        print("ID".ljust(12), "Arrival".ljust(12), "Priority".ljust(12), "CPU Bursts".ljust(12), "IO Bursts".ljust(12), "Start Time".ljust(12), "End Time".ljust(12),
              "Wait Time".ljust(12), "Wait IO Time".ljust(12), "Status".ljust(12))

        for process in self.processes:
            # fancily formats some output, a giant mess
            id = str(process.id).ljust(12)
            arr = str(process.arr_time).ljust(12)
            prio = str(process.priority).ljust(12)

            # formatting the bursts to just show the first one and last ones, there may be no CPU bursts so also say N/A
            if len(process.cpu_bursts) > 2:
                c_bursts = (str(process.cpu_bursts[0])+",...,"+str(process.cpu_bursts[-1])).ljust(12)
            elif len(process.cpu_bursts) == 2:
                c_bursts = (str(process.cpu_bursts[0])+", "+str(process.cpu_bursts[-1])).ljust(12)
            elif len(process.cpu_bursts) == 1:
                c_bursts = (str(process.cpu_bursts[0])).ljust(12)
            else:
                c_bursts = "N/A".ljust(12)

            # formatting the bursts to just show the first one and last ones, there may be no IO bursts so also say N/A
            if len(process.io_bursts) > 2:
                io_bursts = (str(process.io_bursts[0])+"..."+str(process.io_bursts[-1])).ljust(12)
            elif len(process.io_bursts) == 2:
                io_bursts = (str(process.io_bursts[0])+", "+str(process.io_bursts[-1])).ljust(12)
            elif len(process.io_bursts) == 1:
                io_bursts = (str(process.io_bursts[0])).ljust(12)
            else:
                io_bursts = "N/A".ljust(12)

            start = ("N/A" if process.start == -1 else str(process.start)).ljust(12)
            finish = ("N/A" if process.finish == -1 else str(process.finish)).ljust(12)
            wait = str(process.wait_time).ljust(12)
            wait_io = str(process.io_wait_time).ljust(12)
            state = STATE_STRING[process.get_status()].ljust(12)

            print(id, arr, prio, c_bursts, io_bursts, start, finish, wait, wait_io, state)
    
    # printing out the cpu and io device's current status and what process they're focusing on if any
    def print_cpu_io_info(self):
        cpu_id = ("N/A" if self.cpu_focus == None else str(self.cpu_focus.id))
        io_id =  ("N/A" if self.io_focus == None else str(self.io_focus.id))

        cpu_edge = "─"*25
        cpu_middle = ("│" + "CPU: proccess " + cpu_id)
        cpu_middle += " "*max(0,26-len(cpu_middle)) + "│"

        io_edge = "─"*25
        io_middle = ("│" + "IO: proccess " + io_id)
        io_middle += " "*max(0,26-len(io_middle)) + "│"
        
        print("┌"+cpu_edge+"┐","┌"+io_edge+"┐")
        print(cpu_middle,io_middle)
        print("└"+cpu_edge+"┘","└"+io_edge+"┘")

    # first come first serve
    def fcfs(self):
        # might be superfluous
        self.ready_queue.sort(key=lambda x: x.arr_time)

    # shortest job first
    def sjf(self):
        self.ready_queue.sort(key=lambda x: x.cpu_bursts[0])

    def round_robin(self):
        '''self.fcfs()

        for proc in self.processes:
            # If there's bursts left for the process, then process it
            if len(proc.cpu_bursts) > 0:
                proc.cpu_bursts[0] -= self.quantum
            elif len(proc.cpu_bursts) > 0:
                # Remove empty time bursts from the CPU bursts stack
                proc.cpu_bursts = proc.cpu_bursts[1::]'''
        pass

    def priority_scheduling(self):
        self.ready_queue.sort(key=lambda x: x.priority)
