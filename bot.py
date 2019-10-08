import backups
import config
from db import db, save

if "restart" in db:
    config.app.start()
    config.app.edit_message_text(db["restart"]["cid"], db["restart"]["mid"],'Reiniciado')
    del db["restart"]
    save(db)
    config.app.stop()


if config.backups_chat:
	print('ok...')
	backups.backup_service()

config.app.run()