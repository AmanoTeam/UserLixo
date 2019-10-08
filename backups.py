import os
import time
import schedule
from datetime import datetime
from utils import backup_sources
from threading import Thread
from config import backups_chat, backup_hours, app

def backup_func():
    print('ok...4')
    cstrftime = datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
    file = backup_sources()
    app.send_document(backups_chat, file, caption="📅 " + cstrftime + "\n__Auto generated.__")
    os.remove(file)
def backup_scheduler(target):
    print('ok...3')
    for hour in backup_hours:
        print(hour)
        schedule.every().day.at(hour).do(target)
    while True:
        schedule.run_pending()
        time.sleep(2)
def backup_service():
    print('ok...2')
    t = Thread(target=backup_scheduler, args=(backup_func,))
    t.start()
