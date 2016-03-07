from tquakes import *
qdatetime=argv[1]
qdate=datetime.datetime.strptime(qdatetime,DATETIME_FORMAT)
qjd=date2jd(qdate)
print qjd
