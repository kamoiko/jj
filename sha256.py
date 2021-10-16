import hashlib
import time
from os import walk


for root,a,files in walk('.'):
    for f in files:
        m=hashlib.sha256()
        f=str(f)
        if f[-3:] == 'txt':
            with open(f) as handle:
                for i in handle:
                    m.update(i.encode('utf-8'))
                    print(m.hexdigest())

             



