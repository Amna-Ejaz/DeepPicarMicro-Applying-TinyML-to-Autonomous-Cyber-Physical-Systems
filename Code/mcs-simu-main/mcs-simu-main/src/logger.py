# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

class Logger:
    def __int__(self, file_dir):
        self.log_file_dir = file_dir

    def log_event(self, msg):
        # write message into a log file
        pass

    # [todo] only write buffer to the log file when necessary, to reduce the amount of I/O operations.
    # this is partially done by the OS
    def log_write_to_file(self):
        pass

    def log_stat(self, msg):
        pass
