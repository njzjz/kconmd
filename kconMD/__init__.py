import time
__author__='Jinzhe Zeng'

def kconmd_logging(*message):
    localtime = time.asctime( time.localtime(time.time()) )
    print(localtime,'kconMD',*message)
