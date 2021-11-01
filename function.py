
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

def scan_file():#應該要用threading來叫\
    json_information=dict()
    for i in path_to_scan:
        if os.path.isdir(i):
             for root,dirs,files in os.walk(i):
                for f in files:
                    fullpath= os.path.abspath(os.path.join(root,f))
                    file_hash=sha256(fullpath)
                    #db_check_ifsame(path.name,i,file_hash,json_information) #add a dict message(where is not same)
        else:
            file_hash=sha256(i)
            path=pathlib.Path(i)
            #db_check_ifsame(path.name,i,file_hash,json_information) #add a dict message(where is not same)
     #return json.dump(json_information)

def recover(keep,path,version=-1): #new to cover old or keep record & path is absolute path & version=-1 -1 is the latest version
    if(keep==True):
        control_copy_file(True,path)
    else:
        #cover=db_find(path,version) return sha256,absolute_path  of 檔案 in the directory in a dict mode(afterall,push cover version to the latest)
        ''' #這邊可以直接db的function 處理
        for i in cover:
            path_object = pathlib.Path(i)
            shutil.copy(f'./copyfile/{i}{path_object.suffix}',cover[i])
        '''

#def db_delete_version(參數):

#def db_show_allversion():

  

