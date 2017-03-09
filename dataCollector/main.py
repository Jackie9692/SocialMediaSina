#coding=utf-8
import sched
import sys
import os.path
script_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(script_path, '..'))
import zope.testing.loggingsupport
import zc.lockfile
from dataCollector.apiCollector.weiboSensor import *
from dataCollector.dataMerger.statusMerger import *
from dataCollector.commentsUpdater.commentsUpdate import *

dataCollectorScheduler = sched.scheduler(time.time, time.sleep)
if __name__ == "__main__":
    handler = zope.testing.loggingsupport.InstalledHandler('zc.lockfile')
    try:
        lockFile = os.path.join(script_path, "dataCollector.lck")  # 获取唯一性互斥访问文件锁
        dataCleaningScriptLock = zc.lockfile.LockFile(lockFile)
    except zc.lockfile.LockError:
        # 锁定文件失败，表明该脚本已经在执行了，不允许重复执行该脚本
        print("There is already one instance of dataCollector script running current! will exit in 3 seconds. ")
        time.sleep(3)
        sys.exit()
    else:
        start_comments_updater()    #启动comments ReCollect模块
        start_sensor(dataCollectorScheduler)    #启动API Retrieve模块
        mergerStart(dataCollectorScheduler) #启动Status Merge模块
        dataCollectorScheduler.run()