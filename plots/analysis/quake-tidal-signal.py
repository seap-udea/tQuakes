# ############################################################
# IMPORT TOOLS
# ############################################################
from tquakes import *
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
confile=prepareScript()
conf=execfile(confile)
quake=loadConf("quake.conf")

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# PLOT
# ############################################################
fig=plotSignal(quake.quakeid,component,plt)

# ############################################################
# SAVING FIGURE
# ############################################################
saveFigure(confile,fig)
