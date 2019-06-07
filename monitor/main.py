import sys, os

current_path = os.path.abspath(__file__)
current_dir = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
project_dir = '{}/../'.format(current_dir)
sys.path.append(project_dir)

from sqlalchemy.orm import sessionmaker
from monitor.model import Base, engine, CpuUsage, MemUsage, DiskUsage, NetUsage
from monitor.util import *
from apscheduler.schedulers.blocking import BlockingScheduler

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
# 创建Session类实例
session = Session()


def peformance_monitor():
    cpu_usage_data = get_cpu_useage_data()
    print(cpu_usage_data)
    mCpuUsage = CpuUsage()
    mCpuUsage.user = cpu_usage_data.user
    mCpuUsage.nice = cpu_usage_data.nice
    mCpuUsage.system = cpu_usage_data.system
    mCpuUsage.idle = cpu_usage_data.idle
    mCpuUsage.iowait = cpu_usage_data.iowait
    mCpuUsage.hard_irq = cpu_usage_data.irq
    mCpuUsage.soft_irq = cpu_usage_data.softirq
    mCpuUsage.steal = cpu_usage_data.steal
    mCpuUsage.time_stamp = getTime()
    session.add(mCpuUsage)

    mem_usage_data_dict = get_mem_useage_data()
    print(mem_usage_data_dict)
    for mem_type in mem_usage_data_dict:
        mem_usage_data = mem_usage_data_dict.get(mem_type)
        mMemUsage = MemUsage()

        mMemUsage.type = mem_type
        mMemUsage.total = mem_usage_data.total
        mMemUsage.used = mem_usage_data.used
        mMemUsage.free = mem_usage_data.free
        if mem_type == 'mem':
            mMemUsage.shared = mem_usage_data.shared
            mMemUsage.buff_cache = mem_usage_data.buffers
            mMemUsage.available = mem_usage_data.available
            mMemUsage.time_stamp = getTime()
        session.add(mMemUsage)

    disk_usage_data_dict = get_disk_useage_data()
    print(disk_usage_data_dict)
    for device in disk_usage_data_dict:
        disk_usage_data = disk_usage_data_dict.get(device)

        mDiskUsage = DiskUsage()
        mDiskUsage.device = device
        mDiskUsage.read_count = disk_usage_data.read_count
        mDiskUsage.read_merged_count = disk_usage_data.read_merged_count
        mDiskUsage.read_time = disk_usage_data.read_merged_count
        # iostat命令 kB_read数据
        mDiskUsage.read_bytes = disk_usage_data.read_merged_count
        mDiskUsage.write_count = disk_usage_data.read_merged_count
        mDiskUsage.write_merged_count = disk_usage_data.read_merged_count
        mDiskUsage.write_time = disk_usage_data.read_merged_count
        # iostat命令 kB_wrtn数据
        mDiskUsage.write_bytes = disk_usage_data.read_merged_count
        mDiskUsage.busy_time = disk_usage_data.read_merged_count
        mDiskUsage.time_stamp = getTime()
        session.add(mDiskUsage)

    net_usage_data_dict = get_net_useage_data()
    print(net_usage_data_dict)
    for iface in net_usage_data_dict:
        net_usage_data = net_usage_data_dict.get(iface)
        mNetUsage = NetUsage()
        mNetUsage.iface = iface
        mNetUsage.bytes_sent = net_usage_data.bytes_sent
        mNetUsage.bytes_recv = net_usage_data.bytes_recv
        mNetUsage.packets_recv = net_usage_data.packets_recv
        mNetUsage.packets_sent = net_usage_data.packets_sent
        mNetUsage.errin = net_usage_data.errin
        mNetUsage.errout = net_usage_data.errout
        mNetUsage.dropin = net_usage_data.dropin
        mNetUsage.dropout = net_usage_data.dropout
        mNetUsage.time_stamp = getTime()

        session.add(mNetUsage)
    session.commit()


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # 采用固定时间间隔（interval）的方式，每隔5秒钟执行一次
    scheduler.add_job(peformance_monitor, 'interval', seconds=1)
    scheduler.start()
