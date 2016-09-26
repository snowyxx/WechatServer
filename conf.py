# coding:utf-8

import logging
import logging.handlers

# loging settings
format = '%(asctime)s %(levelname)s %(message)s'
logFileName = r'output.log'
formatter = logging.Formatter(format)
wxLogger = logging.getLogger("infoLog")
wxLogger.setLevel(logging.INFO)
infoHandler = logging.handlers.RotatingFileHandler(
    logFileName, 'a', 1024*1024, 3)
infoHandler.setLevel(logging.INFO)
infoHandler.setFormatter(formatter)
wxLogger.addHandler(infoHandler)

products = [
    {"name": "myname",
     "shortname": "mn",
     "webSite": "http://www.bac.com.cn/",
     "ifzh_CN": True,
     "lastBuild": "",
     "des": "从强中小企业到世界500",
     "archives": "http://archives.bac.com/"},
    ]
