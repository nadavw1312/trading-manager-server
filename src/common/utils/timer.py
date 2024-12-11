from time import perf_counter

class Timer:
    def __init__(self,title = ""):
        self.title = title
    
    def __enter__(self):
        self.start_time = perf_counter()
        return self  # Returning self allows access to attributes like `execution_time`

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = perf_counter()
        self.execution_time = self.end_time - self.start_time
        log = self.title + f" {self.execution_time:.4f} seconds to execute."
        print(log)


    def log(self):
        print(f"Execution time was {self.execution_time:.4f} seconds.")


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper