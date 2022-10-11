VALID_STATES = {0: "NEW", 1: "READY",
                2: "RUNNING", 3: "WAITING", 4: "TERMINATED"}

class process:
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
    def __init__(self, id, arr_time, priority, cpu_bursts, io_bursts, start=0, finish=0, wait=0, wait_io=0, status=0):
        self.id = id
        self.arr_time = arr_time
        self.priority = priority
        self.cpu_bursts = cpu_bursts
        self.io_bursts = io_bursts
        self.start = start
        self.finish = finish
        self.wait = wait
        self.wait_io = wait_io
        self.status = status
    
    def set_status(self, new_status):
        self.status = new_status

    def get_status(self, new_status):
        return self.status
