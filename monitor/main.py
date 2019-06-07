import sys,os

current_path = os.path.abspath(__file__)
current_dir = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
project_dir = '{}/../'.format(current_dir)
sys.path.append(project_dir)

from sqlalchemy.orm import sessionmaker
from monitor.model import Base, engine, CpuUsage, MemUsage, DiskUsage, NetUsage
from monitor.util import *
from apscheduler.schedulers.blocking import BlockingScheduler

Base.metadata.create_all(engine)


def peformance_monitor():
    # 创建User类实例
    # memUsage = MemUsage(type='mem', total=1000, used=20, free=20, shared=30, buff_cache=40, available=50,
    #                     time_stamp=11111111111)
    Session = sessionmaker(bind=engine)
    # 创建Session类实例
    session = Session()

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

    session.add(mCpuUsage)
    session.commit()


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # 采用固定时间间隔（interval）的方式，每隔5秒钟执行一次
    scheduler.add_job(peformance_monitor, 'interval', seconds=1)
    scheduler.start()
