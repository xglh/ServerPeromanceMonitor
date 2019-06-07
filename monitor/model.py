#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 23:30
# @Author  : liuhui
# @Detail  :

from sqlalchemy import create_engine, Column, Integer, String, Enum, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker

engine = create_engine('sqlite:///sqlite.db')
Base = declarative_base()

'''

user=0.0, nice=0.0, system=0.0, idle=99.0, iowait=0.0, irq=0.0, softirq=0.0, steal=0.0, guest=0.0, guest_nice=0.0


free -b
              total        used        free      shared  buff/cache   available
Mem:     1040912384   378675200   103882752      163840   558354432   451342336
Swap:    2147479552   664649728  1482829824

cat /proc/diskstats
1 0 sda  505235  28461  7421219  6259625  2397331 3804539  49818500  25885599  0  6122393 32152888
设备号 编号 设备  读完成次数  合并完成次数   读扇区次数   读操作花费毫秒数   写完成次数   合并写完成次数   写扇区次数   写操作花费的毫秒数   正在处理的输入/输出请求数   输入/输出操作花费的毫秒数   输入/输出操作花费的加权毫秒数。

iostat
Device:            tps    kB_read/s    kB_wrtn/s    kB_read    kB_wrtn
vda               4.93        24.41        24.85  140214513  142724860
vdb               0.38         0.04         3.28     234673   18852596
scd0              0.00         0.00         0.00        820          0


cat /proc/net/dev
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
br-f9005f353be3:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
br-966e7b802cb3:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
  eth0: 3733636998 36794561    0    0    0     0          0         0 4395900342 35994779    0    0    0     0       0          0
    lo: 8550052712 42601685    0    0    0     0          0         0 8550052712 42601685    0    0    0     0       0          0
br-0933f72140bd:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
docker0: 1893566   34994    0    0    0     0          0         0 190006982   45068    0    0    0     0       0          0
'''

# json序列化与反序列化基类
class JsonSerializer:

    def to_json(self):
        jsonData = {}
        for name, value in vars(self).items():
            if not name.startswith("_"):
                jsonData[name] = value
        return jsonData

    def init_from_json(self, jsonData):
        if jsonData is not None:
            for name, value in vars(self).items():
                if jsonData.get(name) is not None :
                    setattr(self, name, jsonData.get(name))
        return self

# cpu占用率, top命令数据
class CpuUsage(Base,JsonSerializer):
    __tablename__ = "cpu_usage"
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(FLOAT, nullable=False, comment='us — 用户空间占用CPU的百分比')
    nice = Column(FLOAT, nullable=False, comment='sy — 内核空间占用CPU的百分比')
    system = Column(FLOAT, nullable=False, comment='ni — 改变过优先级的进程占用CPU的百分比')
    idle = Column(FLOAT, nullable=False, comment='id — 空闲CPU百分比')
    iowait = Column(FLOAT, nullable=False, comment='wa — IO等待占用CPU的百分比')
    hard_irq = Column(FLOAT, nullable=False, comment='hi — 硬中断（Hardware IRQ）占用CPU的百分比')
    soft_irq = Column(FLOAT, nullable=False, comment='si — 软中断（Software Interrupts）占用CPU的百分比')
    steal = Column(FLOAT, nullable=False, comment='st - 实时')
    time_stamp = Column(Integer, nullable=False, comment='时间戳')

    def __repr__(self):
        return "CpuUsage:idle:{}".format(self.idle)


# 内存占用率, free命令数据
class MemUsage(Base,JsonSerializer):
    __tablename__ = "mem_usage"
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum('mem', 'swap'), comment='类型')
    total = Column(Integer, nullable=False, comment='total')
    used = Column(Integer, nullable=False, comment='used')
    free = Column(Integer, nullable=False, comment='free')
    shared = Column(Integer, comment='shared')
    buff_cache = Column(Integer, comment='buff/cache')
    available = Column(Integer, comment='available')
    time_stamp = Column(Integer, nullable=False, comment='时间戳')

    def __repr__(self):
        return "MemUsage:total:{},used:{}".format(self.total, self.used)


# 磁盘占用率, cat /proc/diskstats命令数据
class DiskUsage(Base,JsonSerializer):
    __tablename__ = "disk_usage"
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    device = Column(String(64), nullable=False, comment='设备号')
    read_count = Column(Integer, nullable=False, comment='读完成次数')
    read_merged_count = Column(Integer, nullable=False, comment='合并读完成次数')
    read_time = Column(Integer, nullable=False, comment='读操作花费毫秒数')
    # iostat命令 kB_read数据
    read_bytes = Column(Integer, nullable=False, comment='读完成字节')
    write_count = Column(Integer, nullable=False, comment='写完成次数')
    write_merged_count = Column(Integer, nullable=False, comment='合并写完成次数')
    write_time = Column(Integer, nullable=False, comment='写操作花费的毫秒数')
    # iostat命令 kB_wrtn数据
    write_bytes = Column(Integer, nullable=False, comment='写完成字节')
    busy_time = Column(Integer, nullable=False, comment='输入/输出操作花费的毫秒数')
    time_stamp = Column(Integer, nullable=False, comment='时间戳')

    def __repr__(self):
        return "DiskUsage:device:{},read_bytes:{},:{}write_bytes".format(self.device, self.read_bytes, self.write_bytes)


# 网络占用, free命令数据
class NetUsage(Base,JsonSerializer):
    __tablename__ = "net_usage"
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    iface = Column(String(64), nullable=False, comment='网卡接口')
    bytes_sent = Column(Integer, nullable=False, comment='发送字节')
    bytes_recv = Column(Integer, nullable=False, comment='接收字节')
    packets_sent = Column(Integer, nullable=False, comment='发送数据包数')
    packets_recv = Column(Integer, nullable=False, comment='接收数据包数')
    errin = Column(Integer, nullable=False, comment='接收错误数据包数')
    errout = Column(Integer, nullable=False, comment='发送错误数据包数')
    dropin = Column(Integer, nullable=False, comment='接收数据包丢弃数')
    dropout = Column(Integer, nullable=False, comment='发送数据包丢弃数')
    time_stamp = Column(Integer, nullable=False, comment='时间戳')

    def __repr__(self):
        return "NetUsage:iface:{},bytes_sent:{},bytes_recv:{}".format(self.iface, self.bytes_sent, self.bytes_recv)


if __name__ == '__main__':
    Base.metadata.create_all(engine)

    # 创建User类实例
    memUsage = MemUsage(type='mem', total=1000, used=20, free=20, shared=30, buff_cache=40, available=50,
                        time_stamp=11111111111)
    Session = sessionmaker(bind=engine)
    # 创建Session类实例
    session = Session()
    # 将该实例插入到users表
    session.add(memUsage)

    # # 一次插入多条记录形式
    # session.add_all(
    #     [User(name='wendy', fullname='Wendy Williams', password='foobar'),
    #      User(name='mary', fullname='Mary Contrary', password='xxg527'),
    #      User(name='fred', fullname='Fred Flinstone', password='blah')]
    # )
    session.commit()
