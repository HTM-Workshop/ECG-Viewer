from typing import Callable

def debug_timer(func: Callable) -> Callable:
    """Debug timer decorator. Outputs to console."""
    def timer(*args):
        from time import time
        init_time = time()
        ret = func(*args)
        total_time = time() - init_time
        print("{} : {}".format(func.__name__, total_time), flush = True)
        return ret
    return timer