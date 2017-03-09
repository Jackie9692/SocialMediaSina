# encoding=utf-8
import os.path
import traceback
import ConfigParser
from mongoengine import connect
configFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.ini"))
class logger:
    @classmethod
    def errorLog(cls,errorlogfile):
	    errorLogFile = open(errorlogfile, "a")
	    traceback.print_exc(file=errorLogFile)
	    errorLogFile.flush()
	    errorLogFile.close()
    @classmethod
    def logging(cls, logfilepath, message):
        with open(logfilepath, "a") as logfile:
            logfile.write(message)
class datatimeFormat:
    @classmethod
    def strip_status_created_time(cls, createdStr):
        if createdStr:
            zone_index = createdStr.find('+0800')
            createdTimeStr = createdStr[0:zone_index] + createdStr[-5:]
            return createdTimeStr
class configReader():
    @classmethod
    def getConfig(cls):
        config = ConfigParser.ConfigParser()
        with open(name=configFile, mode='r+') as configInfo:
            config.readfp(configInfo)
        return config
    @classmethod
    def getOptionValue(cls ,section, key):
        config = cls.getConfig()
        value = config.get(section=section, option=key)
        return value
    @classmethod
    def getSectionAsDict(cls, section):
        config = cls.getConfig()
        optionsKeys=config.options(section)
        sectionDic={}
        for optionkey in optionsKeys:
             optionvalue = config.get(section, optionkey)
             sectionDic[optionkey] = optionvalue
        return sectionDic
    @classmethod
    def getOptions(cls, section):
        config = cls.getConfig()
        options = config.options(section)
        return options
    @classmethod
    def getOptionsValus(cls, section):
        optionskeys=cls.getOptions( section)
        optionsValues=[]
        for optionkey in optionskeys:
            optionvalue=cls.getOptionValue(section, optionkey)
            optionsValues.append(optionvalue)
        return optionsValues

class databaseConnector():
        """
        数据库连接获取工具类
        """
        default_raw_database = configReader.getSectionAsDict('db')
        @classmethod
        #默认连接到源数据库
        def connect(cls, dbname=default_raw_database.get("raw_data_name"), host=default_raw_database.get("db_host"), port=int(default_raw_database.get('db_port')), alias="default"):
            connect(db=dbname, port=port, host=host, alias=alias)
if __name__ == "__main__":
    for name in configReader.getOptionsValus('official_users'):        pass