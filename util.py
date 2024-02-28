import os
import datetime
import threading


def mkdir(path):
    path = os.path.normpath(path)
    path1 = path.split(os.sep) 
    
    for i, _ in enumerate(path1):
        ptmp = os.path.join('c:\\', *(path1[1:i+1]))
        print(ptmp)
        try: 
            os.mkdir(ptmp)
        except: 
            pass
    
    return


def getdate():
    date = datetime.datetime.today().isoformat()[:10]
    return date


def make_unique_name(file_name):
    uniq = 1
    while os.path.exists(file_name + '.txt'):
        uniq += 1
        file_name = f'{file_name}_{uniq}'
    return file_name


class BaseThread(threading.Thread):
    def __init__(self, target, args=(), callback=None, callback_args=()):
        super().__init__(target=self.target_with_callback)
        self.target = target
        self.target_args = args
        self.callback = callback
        self.callback_args = callback_args

    def target_with_callback(self):
        self.target(*self.callback_args)
        if self.callback is not None:
            self.callback(*self.callback_args)
