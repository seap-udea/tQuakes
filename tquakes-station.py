from tquakes import *
conf=loadConf("configuration")

# ##################################################
# GENERATE INFORMATION ABOUT THE STATION
# ##################################################
print "Station properties:"

# UNIQUE IDENTIFIER
station_id=System("hostid").upper()
suffix1=System("sudo dmidecode -t system |grep UUID |head -n 1")[-3:].upper()
suffix2=System("/sbin/ifconfig |md5sum |cut -f 1 -d ' '")[-3:].upper()
station_id=station_id+suffix1+suffix2
print "\tStation ID:",station_id

# ARCHITECTURE
station_arch=System("uname -ar")
station_arch=station_arch.replace("#","")
print "\tArchitecture:",station_arch

# NUMBER OF PROCESSORS
station_nproc=int(System("grep '^processor' /proc/cpuinfo | wc -l"))
if station_nproc>1:station_nproc-=1
print "\tNumber of processors:",station_nproc

# RAM
station_mem=int(int(System("grep 'MemTotal' /proc/meminfo | awk '{print $2}'"))/1024.0)
print "\tRAM memory:",station_mem

# MAC ADDRESS
ifconfig=System("/sbin/ifconfig")
search=re.search("\w+:\w+:\w+:\w+:\w+:\w+",ifconfig)
station_mac=search.group(0)
print "\tMac Address:",station_mac

# ##################################################
# CREATE STATION FILE
# ##################################################
fs=open(".stationrc","w")
fs.write("station_id='%s';\n"%station_id);
fs.write("station_arch='%s';\n"%station_arch);
fs.write("station_nproc=%d;\n"%station_nproc);
fs.write("station_mem=%d;\n"%station_mem);
fs.write("station_mac='%s';\n"%station_mac);
fs.close()

# ##################################################
# GET STATION
# ##################################################
out=System("links -dump '%s/index.php?action=preregister&station_id=%s&station_arch=%s&station_nproc=%d&station_mem=%d&station_mac=%s'"%\
           (conf.WEBSERVER,
            station_id,
            station_arch,
            station_nproc,
            station_mem,
            station_mac))
if 'Not Found' in out:
    print "Webserver '%s' not found."%conf.WEBSERVER
    exit(1)

print "\nYour station has been preregistered.  Please go to '%s/index.php?if=register' to finish the regsitration of the calculation station."%(conf.WEBSERVER)
print "\nSTATION ID: %s"%station_id
print "\nSTATION PUBLIC KEY:\n"
system("cat $HOME/.ssh/id_rsa.pub")
print

# ##################################################
# INFORMATION ABOUT STATION
# ##################################################
