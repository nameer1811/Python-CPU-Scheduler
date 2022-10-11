from process import process

class controller:
    def __init__(self):
        self.processes = []
        self.quantum = 1
    
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
    def generate_processes(self,file : str):
        # adding all the processes from a file one by one with thier relevant information
        for id, process_line in enumerate(open(file)):
            # import 
            data = [id] + list(map(int,process_line.strip().split(" ")[1::]))
            
            cpu_bursts = []
            io_bursts  = []
            
            # adding the potentially infinite alternating burst types
            for burst_type, burst in enumerate(data[3::]):
                # it's a cpu burst
                if burst_type % 2 == 0:
                    cpu_bursts.append(burst)
                else: # it's an io burst
                    io_bursts.append(burst)

            self.processes.append(process(data[0], data[1], data[2], cpu_bursts, io_bursts))

    # first come first server
    def fcfs(self):
        self.processes.sort(key = lambda x: x.arr_time)

    # shortest job first
    def sjf(self):
        self.processes.sort(key = lambda x: x.cpu_bursts[0]) 

    def round_robin(self):
        self.fcfs()

        for proc in self.processes:
            # If there's bursts left for the process, then process it
            if len(proc.cpu_bursts) > 0:
                proc.cpu_bursts[0] -= self.quantum
            elif len(proc.cpu_bursts) > 0:
                # Remove empty time bursts from the CPU bursts stack
                proc.cpu_bursts = proc.cpu_bursts[1::]

    def priority_scheduling(self):
        self.processes.sort(key = lambda x: x.priority, reverse=True)

    