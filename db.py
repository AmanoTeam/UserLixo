import json
default_db = {"chats": {}, "privates": {}, "personal_data":{}, "notes":{}}

try:
    with open('db.json', 'r') as fp:
        db = json.load(fp)
        
    for key,val in default_db.items():
        if key not in db:
            db[key] = val
except FileNotFoundError:
    db = default_db
    with open('db.json', 'w') as fp:
        json.dump(db, fp)


def save(rq):
    mem = open('db.json', 'w')
    json.dump(rq, mem)
    mem.close()
    return True
