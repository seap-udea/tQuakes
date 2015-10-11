from tquakespice import *

et=str2et("01/01/2015 00:00:00.000 UTC")
state,ltime=spkezr("MOON",et,"J2000","NONE","EARTH")
state,ltime=spkezr("SUN",et,"J2000","NONE","EARTH")

print et
print state
print mag(state[:3])/1e8
print mag(state[3:])
