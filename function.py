#加上新註解
#幫我用r-string 過濾 傳入 file_location 時的跳脫字元
#傳位置的參數都是絕對路徑 例如file_location
#有bug 我忘了考慮隱藏檔案 之後會改一點點
import sqlite3
import os 
import datetime
import shutil
import pathlib
import hashlib
import json
import difflib
path_to_scan=set()# 正在追蹤的目錄或檔案位置

#設定DATABASE
#沒有回傳
def setdatabase(): #設定DB 
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE DATAS
                (VERSION INT,
                SHA256 INT NOT NULL,
                FILENAME TEXT NOT NULL,
                POSITION TEXT NOT NULL,
                TIME TEXT NOT NULL
                );''')

#傳入(bool,絕對位置 (可以為目錄或檔案))true為創建檔案false為刪除
#沒有回傳
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
            push_database(path.name,x,hash_name,cur) #(file_name,absolute_path,sha256,time)
            shutil.copy(x,f'./copyfile/{hash_name}{path.suffix}')
            print(f'tracing.....{x}')
    else:
        db_delete_file(file_location) #包含資料夾和檔案(需要區分)
        path_to_scan.remove(file_location)
        print('cancel tracing....file_location')
    print(f'current controling {path_to_scan}')
    print('\n')
#掃描檔案的函數(目前沒有定時掃描，看是要寫在這邊還是API那邊)
#回傳json格式的資訊(沒有異動的回傳值:"mode":"true","time":(#file_create_time)   有異動的回傳: "mode":"false","time":(#file_create_time),'wrong_information': (#lists of diff information))
def scan_file():
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
#傳入(是否保留,絕對路徑(可以為目錄或檔案),檔案版本) #函數目的為還原檔案 #如果沒有傳入version 則預設為最新版本
#沒有回傳值
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

#傳入(位置,版本) 跟 db_delete_file 很像 但可以選定版本
#刪除此位置的該版本
def db_delete_version(position,version):   
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
    c.execute("UPDATE DATAS SET VERSION=VERSION-1 WHERE POSITION LIKE ?",[position+'%'])       
    conn.commit()

#傳入位置
#回傳json格式的(所有該位置所有版本的版本,檔名,時間)
def db_show_allversion(position):  
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

#(這下面的函數都包含在上面的函數)
#############################################################################
#傳入(位置,版本) 找到該位置和版本的sha256 (#如果沒有傳入version 則預設為最新版本)
#回傳sha256
def db_find(fullpath,version=-1): 
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

#傳入檔名
#回傳hash value
def sha256(filename):
    sha256_hash = hashlib.sha256()
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        print(f'hashing....{filename}....',end='')
        print(sha256_hash.hexdigest())
    return sha256_hash.hexdigest()

#傳入(檔名,位置,hash,時間)將此資料在db中建立
#沒有回傳
def push_database(filename,position,sha256,time):
        conn = sqlite3.connect('database.db')
        temp=findnewest(position)+1
        conn.execute("INSERT INTO DATAS(SHA256,FILENAME,POSITION,VERSION,TIME)\
        VALUES(?,?,?,?,?)",[sha256,filename,position,temp,time])
        conn.commit()

#傳入(絕對位置(僅限檔案沒有目錄))找到最新的檔案版本數
#回傳(INT)最新檔案的版本
def findnewest(position): 
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        cursor = c.execute("SELECT Max(VERSION) from DATAS WHERE POSITION= ?",[position])
        for i in cursor:
            if(i[0]==None):
                return 0
            return i[0]

#傳入(檔案名稱,絕對路徑(限檔案沒目錄),目前檔案的sha256) 比對同個位置的檔案是否有異動
#回傳dict (沒有異動的回傳值:"mode":"true","time":(#file_create_time)   有異動的回傳: "mode":"false","time":(#file_create_time),'wrong_information': (#lists of diff information))
def db_check_ifsame(filename,position,sha256): 
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

#傳入絕對路徑(可以為目錄或檔案)刪除在db中此位置下的所有檔案 同時也刪除備份檔案(包括所有版本紀錄)
# 沒有回傳            
def db_delete_file(position): 
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