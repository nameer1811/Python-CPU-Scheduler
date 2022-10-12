# Valid states the process can have and a relevant enum dictionary
VALID_STATES = {"NEW" : 0, "READY" : 1,
                "RUNNING" : 2, "WAITING" : 3, "TERMINATED" : 4}

class process:
    # initialize with that doesn't need to be created later on/when the program executes
    def __init__(self, id, arr_time, priority, cpu_bursts, io_bursts):
        self.id = id
        self.arr_time = arr_time
        self.priority = priority
        self.cpu_bursts = cpu_bursts
        self.io_bursts = io_bursts
        self.start = -1
        self.finish = -1
        self.wait_time = 0
        self.io_wait_time = 0
        self.status = VALID_STATES["NEW"]

    def get_turnaround_time(self):
        return max(0,self.finish-self.start)
    
    def set_status(self, new_status):
        self.status = new_status

    def get_status(self):
        return self.status
