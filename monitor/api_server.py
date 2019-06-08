# coding:utf-8
import sys, os, json

current_path = os.path.abspath(__file__)
current_dir = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
project_dir = '{}/../'.format(current_dir)
sys.path.append(project_dir)

from sqlalchemy.orm import sessionmaker
from monitor.model import Base, engine, CpuUsage, MemUsage, DiskUsage, NetUsage
from monitor.util import *
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Process
from flask import Flask, request

app = Flask(__name__)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
# 创建Session类实例
session = Session()


def peformance_monitor():
    # 多进程session不能贡献
    # 创建Session类实例
    p_session = Session()

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
    p_session.add(mCpuUsage)

    mem_usage_data_dict = get_mem_useage_data()
    print(mem_usage_data_dict)
    for mem_type in mem_usage_data_dict:
        mem_usage_data = mem_usage_data_dict.get(mem_type)
        mMemUsage = MemUsage()

        mMemUsage.type = mem_type
        mMemUsage.total = mem_usage_data.total
        mMemUsage.used = mem_usage_data.used
        mMemUsage.free = mem_usage_data.free
        mMemUsage.time_stamp = getTime()
        if mem_type == 'mem':
            mMemUsage.shared = mem_usage_data.shared
            mMemUsage.buff_cache = mem_usage_data.buffers
            mMemUsage.available = mem_usage_data.available
        p_session.add(mMemUsage)

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
        p_session.add(mDiskUsage)

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

        p_session.add(mNetUsage)
    p_session.commit()
    # 过期秒数
    expire_second = 60 * 60
    current_time_stamp = getTime()
    # 过期时间戳
    expire_time_stamp = current_time_stamp - expire_second
    p_session.query(CpuUsage).filter(CpuUsage.time_stamp < expire_time_stamp).delete(synchronize_session=False)
    p_session.query(MemUsage).filter(MemUsage.time_stamp < expire_time_stamp).delete(synchronize_session=False)
    p_session.query(DiskUsage).filter(DiskUsage.time_stamp < expire_time_stamp).delete(synchronize_session=False)
    p_session.query(NetUsage).filter(NetUsage.time_stamp < expire_time_stamp).delete(synchronize_session=False)
    p_session.commit()


def scheduler_job():
    scheduler = BlockingScheduler()
    # 采用固定时间间隔（interval）的方式，每隔1秒钟执行一次
    scheduler.add_job(peformance_monitor, 'interval', seconds=1)
    scheduler.start()


def summary_list_data(target_list):
    data_min = data_max = data_avg = 0
    if len(target_list) > 0:
        data_min, data_max = min(target_list), max(target_list)
        data_sum = 0
        for data in target_list:
            data_sum += data

        data_avg = float('%.2f' % (data_sum / len(target_list)))

    return {
        'Avg': data_avg,
        'Max': data_max,
        'Min': data_min
    }


# 获取性能数据
@app.route('/server/performance', methods=['GET'])
def get_server_performance_data():
    response = {"code": 0, "msg": "success", "data": {}}
    data = response['data']
    start_timestamp, end_timestamp = request.args.get("start_timestamp"), request.args.get("end_timestamp")
    if not start_timestamp or not end_timestamp:
        response['code'], response['msg'] = 100, u'缺少必要参数'
    else:
        try:
            start_timestamp, end_timestamp = int(start_timestamp), int(end_timestamp)
        except Exception:
            response['code'], response['msg'] = 200, u'参数格式错误'
        else:
            mCpuUsage_qs = session.query(CpuUsage).filter(CpuUsage.time_stamp >= start_timestamp,
                                                          CpuUsage.time_stamp <= end_timestamp).all()
            # 空闲数据列表
            cpu_idle_data_list = [x.idle for x in mCpuUsage_qs]
            # cpu占用数据
            cpu_usage_data_list = []
            for idle in cpu_idle_data_list:
                cpu_usage = 100 - idle
                cpu_usage_data_list.append(cpu_usage)

            # 生成cpu占用数据汇总
            data['CpuUsage'] = summary_list_data(cpu_usage_data_list)

            # 计算物理内存占用,忽略swap分区
            mMemUsage_qs = session.query(MemUsage).filter(MemUsage.time_stamp >= start_timestamp,
                                                          MemUsage.time_stamp <= end_timestamp,
                                                          MemUsage.type == 'mem').all()
            # mem占用数据
            mem_usage_data_list = []
            for mMemUsage in mMemUsage_qs:
                total, available = mMemUsage.total, mMemUsage.available
                available_percent = float('%.4f' % (available / total))
                usage = 100 - available_percent * 100
                mem_usage_data_list.append(usage)
            # 生成cpu占用数据汇总
            data['MemUsage'] = summary_list_data(mem_usage_data_list)
    return json.dumps(response), 200, {'Content-Type': 'application/json;charset=utf-8'}


if __name__ == '__main__':
    Process(target=scheduler_job, args=()).start()
    app.run(host='0.0.0.0', port=8080)
