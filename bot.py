import backups
import config

if config.backups_chat:
	print('ok...')
	backups.backup_service()

config.app.run()