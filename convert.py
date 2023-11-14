import json
import db
from tortoise import run_async

async def main():
    await db.connect_database()
    with open("db.json", "r") as fp:
        odb = json.load(fp)
    
    for i in odb["notes"]:
        if odb["notes"][i]["type"] == "text":
            print(i, odb["notes"][i]["type"], odb["notes"][i]["value"])
            await db.Notes.create(name=i, type=odb["notes"][i]["type"], content=odb["notes"][i]["value"])

run_async(main())