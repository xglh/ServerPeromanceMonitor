import time
from psutil import *

while True:
    print('=============================================================')
    print(cpu_times_percent(interval=1))
    # print(virtual_memory())
    # print(swap_memory())
    # print(disk_io_counters())
    # print(net_io_counters(pernic=True))

