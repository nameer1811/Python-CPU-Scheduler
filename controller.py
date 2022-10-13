from process import process, VALID_STATES
import csv, os

# for generating performance reports, I'm just gonna keep this here
#performance_metrics = csv.writer(open('performance0.csv', 'w'))
#performance_metrics.writerow(["CPU Utilization","Throughput","AVG Turnaround Time","AVG Waiting Time","AVG Response Time"])

ALGORITHMS = {"FCFS": 0, "SJF": 1, "RR": 2, "PS": 3}
STATE_STRING = dict((v, k) for k, v in VALID_STATES.items())

class controller:
    def __init__(self):
        self.processes = []
        # when there is instances in these, the timer should add numbers to them :3
        self.ready_queue = []
        self.cpu_focus = None
        self.focus_time = 0
        self.quantum = 3
        self.io_queue = []
        self.io_focus = None  # the process the io device is focusing on
        self.algorithm = ALGORITHMS["FCFS"]
        self.system_time = 0
        self.idle_time = 0
        self.log_file = None

    '''
    Make processes objects from a file
    '''
    def generate_processes(self, file : str):
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

            self.processes.append(process(data[0], data[1], data[2], cpu_bursts, io_bursts))
        
        # keeping a log file for processing this
        folder = "".join(file.split("/")[1:-1])
        file_name = file.split("/")[-1]

        if os.path.isdir(folder):
            os.mkdir(folder+"log/")
        
        self.log_file = open(folder+"log/"+file_name+"_log","w")
    '''
    Updating the CPU sim's system time and processing accordingly
    '''
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

        self.process_cpu()
        self.process_io()

        # advancing the system clock
        self.system_time += 1

    '''
    A method to put a process in the ready queue dynamically according to the algorithm used 
    '''
    def add_to_ready_queue(self,process):
        self.print_and_log("PROCESS",process.id,"ADDED TO READY QUEUE")
        self.ready_queue.append(process)
        process.set_status(VALID_STATES["READY"])

        if self.algorithm == ALGORITHMS["SJF"]:
            self.sjf()
        elif self.algorithm == ALGORITHMS["PS"]:
            self.priority_scheduling()
        elif self.algorithm == ALGORITHMS["RR"]:
            pass
        
    '''
    Sets state of a process to ready and adds a start time if necessary
    '''
    def dispatch(self):
        self.cpu_focus = self.ready_queue[0]
        self.ready_queue = self.ready_queue[1::]

        # change the process status to running and remove it from the ready queue
        self.print_and_log("PROCESS",self.cpu_focus.id,"DISPATCHED TO CPU")
        self.cpu_focus.set_status(VALID_STATES["RUNNING"])

        # Show the time the process started
        if self.cpu_focus.start == -1:
            self.cpu_focus.start = self.system_time

    def preempt(self):
        preempted_process = self.cpu_focus
        self.print_and_log("PROCESS",preempted_process.id,"PREMPTED")

        # set new focus process and remove the focus from the ready queue
        self.dispatch()

        # move prempted process to ready queue
        self.add_to_ready_queue(preempted_process)

    def terminate(self):
        self.cpu_focus.set_status(VALID_STATES["TERMINATED"])
        self.print_and_log("PROCESS",self.cpu_focus.id,
        "FINISHED, TURNAROUND: " + str(self.cpu_focus.get_turnaround_time())+ 
        "ms, CPU WAIT: " + str(self.cpu_focus.wait_time) +
        "ms, IO WAIT: "+ str(self.cpu_focus.io_wait_time)+"ms")

    '''
    Handle CPU bursts according to the algorithms and parameters chosen
    '''
    def process_cpu(self):
        # Process the cpu's focus
        if self.cpu_focus != None:
            # prempted processes need this check for waiitng processes if there are none in ready queue
            if len(self.ready_queue) > 0:
                # Preempting in priority scheduling
                if self.algorithm == ALGORITHMS["PS"]:
                    if len(self.ready_queue) > 0:
                        # if the current process's priority is lower than another ready process, premept
                        if self.cpu_focus.priority > self.ready_queue[0].priority:
                            self.preempt()

                # in round robin make sure quantum rule is abided by
                if self.algorithm == ALGORITHMS["RR"]:
                    # preempt after reaching quantum and reset focus clock
                    if self.focus_time == self.quantum:
                        self.preempt()
                        self.focus_time = 0
                    self.focus_time += 1

            # decrease the burst time
            if (len(self.cpu_focus.cpu_bursts) > 0):
                self.cpu_focus.cpu_bursts[0] -= 1

                # if the burst has gotten down to zero, either terminate the process, or check if it needs to wait on I/O
                if self.cpu_focus.cpu_bursts[0] == 0:
                    # For RR, reset the quantum time checker
                    self.focus_time = 0

                    # Terminate because there's no more bursts
                    if self.cpu_focus.cpu_bursts[-1] == 0:
                        self.terminate()

                        # reflect the time the process ended
                        self.cpu_focus.finish = self.system_time

                    else:
                        # adding the process to the IO queue if it has IO bursts and setting the process status to reflect that
                        if len(self.cpu_focus.io_bursts) != 0:
                            self.io_queue.append(self.cpu_focus)
                            self.cpu_focus.set_status(VALID_STATES["WAITING"])
                            self.print_and_log("PROCESS",self.cpu_focus.id,"SENT TO IO QUEUE")
                    
                    # delete the burst now that it's at 0
                    self.cpu_focus.cpu_bursts = self.cpu_focus.cpu_bursts[1::]
                    self.cpu_focus = None
            
        # If the system is idle, it finds the next relevant process
        if self.cpu_focus == None:
            if len(self.ready_queue) > 0:
                # Dispatch relevant process as the CPU's focus
                self.dispatch()
            else:
                self.idle_time += 1

    '''
    Handle IO bursts
    '''
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
                self.print_and_log("PROCESS",self.io_focus.id,"DONE WITH IO")
                self.io_focus = None
        
        # If the IO device is available and there's still processes in the IO queue give the process the IO device
        if self.io_focus == None:
            if len(self.io_queue) > 0:
                # allocate the IO device
                self.io_focus = self.io_queue[0]

                # remove it from the IO queue
                self.io_queue = self.io_queue[1::]
    
    '''
    Set the algorithm used by the CPU processor (SJF, PS, etc)
    '''
    def set_algorithm(self, algorithm):
        global performance_metrics
        self.algorithm = algorithm
        performance_metrics = csv.writer(open(f'performance{algorithm}.csv', 'w'))

    '''
    print out all the relevant process info in a nify format
    '''
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
    
    '''
    printing out the cpu and io device's current status and what process they're focusing on if any
    '''
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

    '''
    printing out what processes are in the ready and io queues
    '''
    def print_queueing_info(self):
        # Display ready queue
        display_am = min(len(self.ready_queue), 10)
        ready_str = ", ".join(["process " + str(p.id) for p in self.ready_queue[:display_am]])
        
        if len(self.ready_queue) > display_am:
            ready_str += "..."
        
        print("Ready Queue:", ready_str)

        # Display IO queue
        display_am = min(len(self.io_queue), 10)
        io_str = ", ".join(["process " + str(p.id) for p in self.io_queue[:display_am]])
        
        if len(self.io_queue) > display_am:
            io_str += "..."
        
        print("IO Queue:", io_str)
    
    # for generating performance reports, I'm just gonna keep this here
    '''
    def print_performance_metrics(self):
        global performance_metrics
        utilization = round(100*((self.system_time-self.idle_time)/self.system_time))
        avg_turnaround_time = 0
        avg_wait_time = 0
        avg_response_time = 0
        throughput = 0
        started_processes = [p for p in self.processes if p.start != -1]
        
        for p in started_processes:
            avg_turnaround_time += (p.get_turnaround_time())
            avg_wait_time += (p.wait_time)

            if p.start != -1:
                avg_response_time += p.start-p.arr_time

            if (p.get_turnaround_time()) > 0:
                throughput += (p.get_status() == VALID_STATES["TERMINATED"])/(p.get_turnaround_time()/1000)
        avg_turnaround_time /= len(self.processes)
        avg_wait_time /= len(self.processes)
        avg_response_time /= len(self.processes)
        
        print("CPU Utilization: " + str(utilization) +"%")
        print("Throughput: " + "{0:.2f}".format(throughput)+" processes/s")
        print("AVG Turnaround Time: " + "{0:.0f}".format(avg_turnaround_time)+"ms")
        print("AVG Waiting Time: " + "{0:.0f}".format(avg_wait_time)+"ms")
        print("AVG Response Time: " + "{0:.0f}".format(avg_response_time)+"ms")

        performance_metrics.writerow([utilization,throughput,avg_turnaround_time,avg_wait_time,avg_response_time])
    '''

    '''
    Takes a variable number of messages to log and print it at the system time
    '''
    def print_and_log(self,*messages : str):
        messages = [m if type(m) == str else str(m) for m in messages]
        print(" ".join(messages))
        self.log_file.write(f"{self.system_time}ms: "+" ".join(messages)+"\n")

    def set_quantum(self, quantum):
        self.quantum = quantum

    # first come first serve
    def fcfs(self):
        # might be superfluous
        self.ready_queue.sort(key=lambda x: x.arr_time)

    # shortest job first, non-preemptive
    def sjf(self):
        self.ready_queue.sort(key=lambda x: x.cpu_bursts[0])

    def priority_scheduling(self):
        self.ready_queue.sort(key=lambda x: x.priority)
