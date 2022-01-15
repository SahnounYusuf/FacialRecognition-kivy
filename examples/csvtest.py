
import csv
import mysql.connector
import sys

mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
cur = mydb.cursor()

sql = 'SELECT department_id,absence_date FROM absence'

cur.execute(sql)

# rows = cur.fetchall()
# fp = open('file.csv', 'w')
# myFile = csv.writer(fp,lineterminator='\n')
# myFile.writerows(rows)
# fp.close()

result = cur.fetchall()

#Getting Field Header names
column_names = [i[0] for i in cur.description]
fp = open('ptestfile.csv', 'w')
myFile = csv.writer(fp, lineterminator = '\n') #use lineterminator for windows
myFile.writerow(column_names)
myFile.writerows(result)
fp.close()