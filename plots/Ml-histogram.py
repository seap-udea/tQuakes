from tquakes import *
import matplotlib.pyplot as plt
basename=fileBase(argv[0])

# ############################################################
# CONNECT TO DATABASE
# ############################################################
connection=connectDatabase()
db=connection.cursor()

# ############################################################
# READ DATA
# ############################################################
Ml=mysqlArray("select Ml from Quakes;",db)
Ml=[float(M[0]) for M in Ml]

# ############################################################
# GET HISTOGRAM
# ############################################################
fig=plt.figure()
ax=plt.gca()
fig.savefig("plots/%s.png"%basename)
