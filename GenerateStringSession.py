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
app.stop()
con = con.replace('кк',b.first_name)
if b.last_name:
    con = con.replace('εαε мεη',b.last_name)
else:
    con = con.replace('εαε мεη','')
if b.description:
    con = con.replace('userbot da @AmanoTeam',b.description)
else:
    con = con.replace('userbot da @AmanoTeam','')
open('config.py','w').write(con)
