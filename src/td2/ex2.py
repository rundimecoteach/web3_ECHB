import json
from tinydb import TinyDB, Query

if __name__ == "__main__":
    json_content = json.load(open('../../resources/dump.json'))
    db = TinyDB('../../resources/db.json')
    db.insert(json_content)
    Tournament = Query()
    print(db.search(Tournament.id == '30000'))
