import sqlite3
import os 
import datetime
import shutil
import pathlib
import hashlib
import json
path_to_scan=set()
#幫我用r-string 過濾 file_location 的跳脫字元
#file_location 參數為絕對位置 (可以為目錄或檔案)
def control_copy_file(if_create,file_location):
    if(if_create == True):
        path_to_scan.add(file_location)#增加追蹤的目錄或檔案位置
        currentdata= datetime.datetime.now()
        cur = currentdata.strftime("%Y_%m_%d_at_%H_%M_")
        print(cur)
        to_be_copy=[] #要複製目錄中檔案的絕對位置
        if os.path.isdir(file_location):
            for root,dirs,files in os.walk(file_location):
                for f in files:
                    fullpath= os.path.abspath(os.path.join(root,f))
                    to_be_copy.append(fullpath)
        else:
            to_be_copy.append(file_location)
        
        for x in to_be_copy:
            path=pathlib.Path(x)
            hash_name=sha256(x)
            #push_database(path.name,x,hash_name,cur) #(file_name,absolute_path,sha256,time)
            shutil.copy(x,f'./copyfile/{hash_name}{path.suffix}')
            print(f'tracing.....{x}')
    else:
        #db_delete_file(file_location) #包含資料夾和檔案(需要區分)
        path_to_scan.remove(file_location)
        print('cancel tracing....file_location')

def sha256(filename):
    sha256_hash = hashlib.sha256()
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        print(f'hashing....{filename}....',end='')
        print(sha256_hash.hexdigest())
    return sha256_hash.hexdigest()

def scan_file():#由 api 定時呼叫
    json_information=dict()
    for i in path_to_scan:
        if os.path.isdir(i):
             for root,dirs,files in os.walk(i):
                for f in files:
                    fullpath= os.path.abspath(os.path.join(root,f))
                    file_hash=sha256(fullpath)
                    #db_check_ifsame(path.name,fullpath,file_hash,json_information) #add a dict message(where is not same)
        else:
            file_hash=sha256(i)
            path=pathlib.Path(i)
            #db_check_ifsame(path.name,fullpath,file_hash,json_information) #add a dict message(where is not same)
     #return json.dump(json_information)

def recover(keep,path,version=-1): #new to cover old or keep record & path is absolute path & version=-1 -1 is the latest version
    if(keep==True):
        control_copy_file(True,path)
    else:
        if os.path.isdir(path):
            for root,dirs,files in os.walk(path):
                for f in files:
                    fullpath= os.path.abspath(os.path.join(root,f))
                    #cover=db_find(fullpath,version) return sha256 of 檔案 in the directory in a list mode(afterall,push cover version to the latest)
                    extension = os.path.splitext(f)[1]
                    shutil(f'./copyfile/{cover}{extension}',fullpath)
        else:
            #cover=db_find(path,version)
            extension = os.path.splitext(path)[1]
            shutil(f'./copyfile/{cover}{extension}',path)
                    
def setdatabase(): #設定DB
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
        c.execute(f"INSERT INTO DATAS(SHA256,FILENAME,POSITION,VERSION)\
        VALUES({sha256},{filename},{position},{temp},{time}")

def findnewest(position):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = conn.execute(f"SELECT Max(VERSION) from DATAS WHERE POSITION={position}")
        return cursor[0]

def db_delete_file(position):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(f"DELETE from DATAS WHERE POSITION LIKE {position}+'%'")

def db_check_ifsame(filename,position,sha256,json_information):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = c.execute(f"SELECT SHA256, TIME from DATAS WHERE FILENAME={filename} AND POSITION={position}")
        if(sha256==cursor[0]):
            json_information= {"mode":"true","time":cursor[1]}
        else:
            json_information= {"mode":"false","time":cursor[1]}
            extension = os.path.splitext(position)[1]
            fullpath= os.path.abspath(os.path.join('./copyfile',f'{sha256}{extension}'))
            with open(fullpath,"r") as old,open(position,"r") as new:
                for i in old,new:
                    if(old[i] != new[i]):
                        json_information[f'line:{i}'].append(f'{old[i]} different from  {new[i]}')

#def db_delete_version(參數):

#def db_show_allversion():

  

