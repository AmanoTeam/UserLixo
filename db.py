import json

db = json.load(open('db.json','r'))

def save(rq):
    mem = open('db.json','w')
    json.dump(rq,mem)
    mem.close()
    return True