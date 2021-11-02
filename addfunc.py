import sqlite3import

def setdatabase():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE DATAS.
                (VERSION INT PRIMARY KEY NOT NULL
                SHA256 INT NOT NULL
                FILENAME TEXT NOT NULL
                POSITION TEXT NOT NULL
                TIME TEXT NOT NULL
                );''')

def push_database(filename,position,sha256,time):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        temp=findnewest(position)+1
        c.execute("INSERT INTO DATAS(SHA256,FILENAME,POSITION,VERSION)\
        VALUES(sha256,filename,position,temp,time")

def findnewest(position):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = conn.execute("SELECT Max(VERSION) from DATAS WHERE POSITION=position")
        return cursor[0]

def db_delete_file(position):
        c.execute("DELETE from DATAS WHERE POSITION LIKE position+'%'")

def db_check_ifsame(filename,position,sha256,json_information):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = conn.execute("SELECT SHA256, TIME from DATAS WHERE FILENAME=filename AND POSITION=position")
        if(sha256==cursor[0])
                return ["mod":"true","time":cursor[1]]
        else
        #章魚寫