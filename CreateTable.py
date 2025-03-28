
import MySQLdb
DB_USERNAME = 'admin'
DB_PASSWORD = 'password'
DB_NAME = 'photodb'

conn = MySQLdb.connect(host = "photodb.cluster-c3qeq46sa3tg.us-east-2.rds.amazonaws.com",
                        user = DB_USERNAME,
                        passwd = DB_PASSWORD,
                        db = DB_NAME, 
                        port = 3306)

cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")

cursor.execute ("CREATE TABLE photogallery2 ( \
    PhotoID int PRIMARY KEY NOT NULL AUTO_INCREMENT, \
    CreationTime TEXT NOT NULL, \
    Title TEXT NOT NULL, \
    Description TEXT NOT NULL, \
    Tags TEXT NOT NULL, \
    URL TEXT NOT NULL,\
    EXIF TEXT NOT NULL\
    );")

cursor.close ()
conn.close ()