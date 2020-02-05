from db import db, save

print('Confifurando...')
con = open('config.py.example','r').read()
a = ['api_id','api_hash']

for i in a:
    exec(f"{i} = input('{i}: ')")
    con = con.replace(f"{i} = ''",f"{i} = '{eval(i)}'")

open('config.py','w').write(con)

from config import app

print('login')
app.start()
b = app.get_chat(app.get_me().id)
a = app.get_profile_photos("me", limit=1)[0]
try:
    app.download_media(a.file_id, a.file_ref, file_name='./avatar.png')
except Exception as e:
        print(f'not saved\n\nCause: {e}')

personal_data = dict(
    first_name=b.first_name,
    last_name=b.last_name or '',
    description=b.description or ''
)
db['personal_data'] = personal_data
save(db)
app.stop()