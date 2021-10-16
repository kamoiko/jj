from os import listdir, path, walk 
import os 
import shutil
import datetime
import time

global history

history=[]

def deletehistory():
    import shutil
    shutil.rmtree(f'./{history[0]}_copyfile')

if __name__ == '__main__':
    
    mypath="."
    currentdata= datetime.datetime.now()
    cur = currentdata.strftime("%Y_%m_%d_at_%H_%M_%S")
    history.append(cur)
    print(cur)
    os.makedirs(f'./{cur}_copyfile',exist_ok=True)

    to_be_copy=[]

    for root,dirs,files in walk(mypath):
        for f in files:
            fullpath= os.path.abspath(os.path.join(root,f))
            to_be_copy.append(fullpath)
            print(fullpath)
    print('-------------')

    for x in to_be_copy:
        shutil.copy(x,f'./{cur}_copyfile')
        print(x)
    
    if input()=='yes':
        deletehistory()

