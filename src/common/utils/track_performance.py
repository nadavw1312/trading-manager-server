import psutil
import time

class TrackPerformance:
    def __init__(self, title=""):
        self.title = title
    
    def __enter__(self):
        # Measure CPU usage before execution
        self.cpu_usage_before = psutil.cpu_percent(interval=None)
        self.start_time = time.time()
        return self  # Returning self allows access to the CPU usage and timing information
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Measure CPU usage after execution
        self.end_time = time.time()
        self.cpu_usage_after = psutil.cpu_percent(interval=None)
        self.execution_time = self.end_time - self.start_time
        log = (f"{self.title} CPU usage before: {self.cpu_usage_before}%\n"
               f"CPU usage after: {self.cpu_usage_after}%\n"
               f"Execution time: {self.execution_time:.4f} seconds")
        print(log)

    def log(self):
        print(f"Execution time: {self.execution_time:.4f} seconds.")
        print(f"CPU usage before: {self.cpu_usage_before}%")
        print(f"CPU usage after: {self.cpu_usage_after}%")
