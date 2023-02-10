import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', db='parking')
cur = conn.cursor()
