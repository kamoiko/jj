import sqlite3

conn = sqlite3.connect('test.db')

print("Opened database successfully")
c = conn.cursor()
c.execute('''CREATE TABLE COMPANY
       (ID            INT PRIMARY KEY     NOT NULL,
       error_stats    TEXT    NOT NULL,
       line            INT     NOT NULL,
       time_line       INT    NOT NULL);''')
print("Table created successfully")
conn.commit()
conn.close()