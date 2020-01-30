import config

from db import db, save

if "restart" in db:
    config.app.start()
    config.app.edit_message_text(db["restart"]["cid"], db["restart"]["mid"], 'Reiniciado')
    del db["restart"]
    save(db)
    config.app.stop()

config.app.run()
