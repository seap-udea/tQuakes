from tquakes import *
#from spiceypy.wrapper import *

jd=customdate2jd("12/01/2015 00:00:000.0 UTC-5")
print jd

#et=str2et("12-01-2015 00:00:00 UTC")
#print et

#t=datetime(2015,2,1)
#print t

#datetime.strftime
#datetime.strptime()
t=datetime.datetime(2015,12,31,3,0,0)
print t

t=datetime.datetime.now()
print t

jd=date2jd(t)
print jd

t=datetime.datetime.strptime("2015/12/31 15:01:03","%Y/%m/%d %H:%M:%S")
jd=date2jd(t)
print jd

t=datetime.datetime.strptime("2015/12/31 00:00:00","%Y/%m/%d %H:%M:%S")
jd=date2jd(t)
print jd

