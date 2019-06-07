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

'''


# cpu占用率, top命令数据
class CpuUsage(Base):
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
class MemUsage(Base):
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
class DiskUsage(Base):
    __tablename__ = "disk_usage"
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    disk = Column(String(64),nullable=False, comment='时间戳')


    time_stamp = Column(Integer, nullable=False, comment='时间戳')

    def __repr__(self):
        return "MemUsage:total:{},used:{}".format(self.total, self.used)

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
