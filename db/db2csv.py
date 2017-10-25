import MySQLdb as mysql
import pandas as pd

conector=mysql.connect(host="localhost",user="root",passwd="pum",db="tQuakes")
sql="select * from Quakes"
df=pd.read_sql(sql,con=conector)
df.to_csv("sismos-1993-2017.csv")

