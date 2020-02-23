import json

try:
	with open('db.json', 'r') as fp:
        db = json.load(fp)
except FileNotFoundError:
	db = {"chats": {}, "privates": {}, "personal_data":{}, "notes":{}}
    with open('db.json', 'w') as fp:
        json.dump(db, fp)


def save(rq):
    mem = open('db.json', 'w')
    json.dump(rq, mem)
    mem.close()
    return True
