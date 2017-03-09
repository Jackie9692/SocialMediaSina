#coding=utf-8
#datacleaning 入口
import sys
import os.path
cleaningScriptPath = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(cleaningScriptPath, '..'))
print cleaningScriptPath
import time
import sys
from sched import scheduler
import zc.lockfile
import zope.testing.loggingsupport
from util import configReader
from keywordsCleaner import keywordsCleaner
from taskScanner import cleaningTaskScaner

def run_cleaning_tasks():
    #一次扫描完成后启动该次扫描过程中发现的新的清洗任务
    task_scanner = cleaningTaskScaner()
    tasks_new = task_scanner.get_need_start_tasks()
    if tasks_new:
        for task in tasks_new:
            cleanner = keywordsCleaner(task)
            cleanner.start()
def cyclic_scan(scan_interval,scheduler):
    # 循环扫描
    run_cleaning_tasks()
    scheduler.enter(scan_interval, 0, cyclic_scan, (scan_interval, scheduler))
    scheduler.run()

def reactiveTasks():
    """
     修改所有未完成的清洗任务的状态为"created"
    """
    task_scanner = cleaningTaskScaner()
    task_scanner.reactive_tasks_need()
def start():
    """
     0、首先扫描数据库中所有的清洗任务，将状态为running或waitting的状态的任务状态修改成created（从意外中断中恢复）
     1、周期扫描清洗任务
    """
    reactiveTasks()
    scan_interval = int(configReader.getOptionValue('scanner_interval', 'interval'))
    scan_scheduler = scheduler(time.time, time.sleep)
    cyclic_scan(scan_interval, scan_scheduler)

if __name__ == "__main__":
    handler = zope.testing.loggingsupport.InstalledHandler('zc.lockfile')
    try:
        lockFile = os.path.join(cleaningScriptPath, "dataCleaning.lck") #获取唯一性互斥访问文件锁
        dataCleaningScriptLock = zc.lockfile.LockFile(lockFile)
    except zc.lockfile.LockError:
        #锁定文件失败，表明该脚本已经在执行了，不允许重复执行该脚本
        print("There is already one instance of dataCleaning script running current! will exit in 3 seconds. ")
        time.sleep(3)
        sys.exit()
    else:
        start()
