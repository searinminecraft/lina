from datetime import datetime

def log(srv: str, msg: str):
    print(f'{datetime.now()}   {srv:13}: {msg}')
