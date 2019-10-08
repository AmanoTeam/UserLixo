import json

try:
    db = json.load(open('db.json','r'))
except FileNotFoundError:
    with open('db.json','w') as memoria:
        memoria.write('{"chats": {}, "privates": {}}')
    db = json.load(open('db.json','r'))

def save(rq):
    mem = open('db.json','w')
    json.dump(rq,mem)
    mem.close()
    return True