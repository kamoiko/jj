import sqlite3
import os 
import datetime
import shutil
import pathlib
import hashlib
import json
import numpy as np
import difflib
path_to_scan=set()
#幫我用r-string 過濾 file_location 的跳脫字元
#file_location 參數為絕對位置 (可以為目錄或檔案)
def control_copy_file(if_create,file_location): #done
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
            push_database(path.name,x,hash_name,cur) #(file_name,absolute_path,sha256,time)
            shutil.copy(x,f'./copyfile/{hash_name}{path.suffix}')
            print(f'tracing.....{x}')
    else:
        db_delete_file(file_location) #包含資料夾和檔案(需要區分)
        path_to_scan.remove(file_location)
        print('cancel tracing....file_location')
    print(f'current controling {path_to_scan}')
    print('\n')

def sha256(filename):#done
    sha256_hash = hashlib.sha256()
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        print(f'hashing....{filename}....',end='')
        print(sha256_hash.hexdigest())
    return sha256_hash.hexdigest()

def scan_file():#由 api 定時呼叫 #done
    for i in path_to_scan:
        if os.path.isdir(i):
             for root,dirs,files in os.walk(i):
                for f in files:
                    fullpath= os.path.abspath(os.path.join(root,f))
                    path=pathlib.Path(fullpath)
                    file_hash=sha256(fullpath)
                    json_information=db_check_ifsame(path.name,fullpath,file_hash) #add a dict message(where is not same)
        else:
            file_hash=sha256(i)
            path=pathlib.Path(i)
            json_information=db_check_ifsame(path.name,i,file_hash) #add a dict message(where is not same)
    return json.dumps(json_information)

def recover(keep,path,version=-1): #new to cover old or keep record & path is absolute path & version=-1 -1 is the latest version
    if(keep==True):
        control_copy_file(True,path)
    else:
        if os.path.isdir(path):
            for root,dirs,files in os.walk(path):
                for f in files:
                    fullpath= os.path.abspath(os.path.join(root,f))
                    cover=db_find(fullpath,version) 
                    extension = os.path.splitext(f)[1]
                    shutil.copy(f'./copyfile/{cover}{extension}',fullpath)
        else:
            cover=db_find(path,version)
            extension = os.path.splitext(path)[1]
            shutil.copy(f'./copyfile/{cover}{extension}',path)
                    
def setdatabase(): #設定DB #done
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE DATAS
                (VERSION INT,
                SHA256 INT NOT NULL,
                FILENAME TEXT NOT NULL,
                POSITION TEXT NOT NULL,
                TIME TEXT NOT NULL
                );''')

def push_database(filename,position,sha256,time): #done
        conn = sqlite3.connect('database.db')
        temp=findnewest(position)+1
        conn.execute("INSERT INTO DATAS(SHA256,FILENAME,POSITION,VERSION,TIME)\
        VALUES(?,?,?,?,?)",[sha256,filename,position,temp,time])
        conn.commit()
        


def findnewest(position): #done
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = c.execute("SELECT Max(VERSION) from DATAS WHERE POSITION= ?",[position])
        for i in cursor:
            if(i[0]==None):
                return 0
            return i[0]
            
def db_delete_file(position): #done
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor=c.execute("Select SHA256,FILENAME from DATAS WHERE POSITION LIKE ? ",[position+'%'])
        for i in cursor:
            try:
                extension = os.path.splitext(i[1])[1]
                os.remove(f'./copyfile/{i[0]}{extension}')
                print('deleting hash file....')
            except:
                pass
        c.execute("DELETE from DATAS WHERE POSITION LIKE ? ",[position+'%'])
        conn.commit()

def db_check_ifsame(filename,position,sha256): #done but need to fix file size problem
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = c.execute("SELECT SHA256, TIME from DATAS WHERE FILENAME=? AND POSITION=?",[filename,position])
        for i in cursor:
            if(sha256==i[0]):
                json_information= {"mode":"true","time":i[1]}
            else:
                json_information= {"mode":"false","time":i[1]}
                extension = os.path.splitext(position)[1]
                old_file_sha256=db_find(position)
                if(old_file_sha256==0):json_information['No file']='true'
                fullpath= os.path.abspath(os.path.join('./copyfile',f'{old_file_sha256}{extension}'))
                with open(fullpath) as old:
                    old_text = old.readlines()
                with open(position) as new:
                    new_text = new.readlines()
                wrong_information=[]
                for line in difflib.unified_diff(old_text,new_text, fromfile=fullpath,tofile=position, lineterm=''):
                    wrong_information.append(line)
                json_information['wrong_information']= wrong_information
        return json_information

def db_delete_version(position,version):   #done
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        cursor=c.execute("Select SHA256,FILENAME,POSITION from DATAS WHERE POSITION LIKE ? AND VERSION=?",[position+'%',version])
    except:
        print("No such version")
        return 
    for i in cursor:
        try:
            place=i[2]
            extension = os.path.splitext(i[1])[1]
            os.remove(f'./copyfile/{i[0]}{extension}')
            print('deleting hash file....')
            c.execute("DELETE from DATAS WHERE POSITION=? AND VERSION=?",[place,version])
        except:
            pass
    c.execute("UPDATE DATAS SET VERSION=VERSION-1 WHERE POSITION LIKE ?",[position+'%'])     #不確定    
    conn.commit()

def db_show_allversion(position):  #problem
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    json_information=dict()
    cursor = c.execute("SELECT VERSION,FILENAME,TIME from DATAS WHERE POSITION=?",[position])
    allversion=[]
    for i in cursor:
        filename=i[1]
        temp =[[i[0],i[2]]]
        allversion=allversion+temp
    json_information[filename]=allversion
    return json.dumps(json_information,ensure_ascii=False).encode('utf-8').decode()
  
def db_find(fullpath,version=-1): #done
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if(version==-1): 
        cursor=c.execute("Select SHA256 from DATAS WHERE  VERSION= (SELECT MAX(VERSION) FROM DATAS WHERE POSITION=?) AND POSITION= ?",[fullpath,fullpath])
    else:
        cursor=c.execute("Select SHA256 from DATAS WHERE VERSION=? AND  POSITION=?",[version,fullpath])
    for i in cursor:
        if(i[0]==None):
            return 0
        return i[0]