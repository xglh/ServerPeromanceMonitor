import time

from psutil import *


# 获取网卡信息,排除掉lo环路
def get_netcard():
    netcard_info = {}
    info = net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                netcard_info[k] = item[1]
    return netcard_info


def getTime(timeGap=0):
    '''
    获取当前时间戳
    :param timeGap:与当前时间的间隔
    :return:currentTimeStamp - timeGap
    '''
    currentTimeStamp = int(time.time())
    return int(currentTimeStamp - timeGap)


# 获取cpu利用率
def get_cpu_useage_data():
    # 返回整体数据,不区分多核
    return cpu_times_percent()


# 获取内存利用率
def get_mem_useage_data():
    # 物理内存
    mem = virtual_memory()
    # swap分区
    swap = swap_memory()
    return {
        'mem': mem,
        'swap': swap
    }


# 获取磁盘占用率
def get_disk_useage_data():
    result = {}
    # 按设备区分
    disk_usage_data_dict = disk_io_counters(perdisk=True)
    # 获取磁盘盘符
    device_list = []
    for disk_info in disk_partitions():
        device_path = disk_info.device
        device = device_path.split('/')[-1]
        device_list.append(device)
    for device in disk_usage_data_dict:
        if device in device_list:
            result[device] = disk_usage_data_dict.get(device)
    return result


# 获取网络占用率
def get_net_useage_data():
    result = {}
    net_usage_data_dict = net_io_counters(pernic=True)
    # 获取网络接口,排除掉lo
    iface_info_dict = get_netcard()
    for iface in net_usage_data_dict:
        if iface in iface_info_dict:
            addr = iface_info_dict.get(iface)
            result[iface] = net_usage_data_dict.get(iface)
    return result
