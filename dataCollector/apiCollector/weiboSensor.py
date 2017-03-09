# coding= utf-8
import os.path
import datetime
from sensor import Sensor
from util import configReader, logger

sensor = Sensor()
apiCollectorLog = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, "logs","api_data_collector.log"))
def computeNextInterval(statusCount,intervalOfLastTime,initial_interval):
        """
            根据上次返回的结果数量动态决定下次调用API获取微博数据的时间间隔
        """
        if statusCount < 25:    #请求100条数据，当返回的结果数据小于25条时
            return int(intervalOfLastTime*1.3)  #下次请求的时间间隔是上次请求时间间隔的1.3倍
        elif statusCount < 50:
            return int(intervalOfLastTime*1.1)
        elif statusCount <75:
            nextInterval=int(intervalOfLastTime*0.8)
            if nextInterval< initial_interval:
                nextInterval=initial_interval
            return nextInterval
        else:
            nextInterval=int(intervalOfLastTime*0.5)
            if nextInterval < initial_interval:
                nextInterval = initial_interval
            return nextInterval
def retrieveData(interval,account_type,sensorScheduler):
        countOfStatus=sensor.retrieveAccountsData(account_type)
        initial_interval = int(configReader.getOptionValue('retrieve_interval_seconds', account_type))
        nextTimeInterval=computeNextInterval(countOfStatus, interval, initial_interval)
        logmessage = "Now is " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": This time retrieved " + str(countOfStatus) + " " + account_type + " statuses. Will retrieve again in " + str(nextTimeInterval) + " seconds.\n"
        logger.logging(apiCollectorLog, logmessage)
        sensorScheduler.enter(nextTimeInterval, 0, retrieveData, (nextTimeInterval, account_type,sensorScheduler))
def start_sensor(sensorScheduler):
        intervalOfOfficial=int(configReader.getOptionValue('retrieve_interval_seconds', 'official'))
        intervalOfMedia=int(configReader.getOptionValue('retrieve_interval_seconds', 'media'))
        sensorScheduler.enter(0, 0, retrieveData, (intervalOfOfficial, "official",sensorScheduler))
        sensorScheduler.enter(0, 1, retrieveData, (intervalOfMedia, "media",sensorScheduler))

if __name__ == '__main__':
    start_sensor()
