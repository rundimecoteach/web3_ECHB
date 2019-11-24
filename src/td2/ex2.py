import json
import sys
import operator
from tinydb import TinyDB, Query


def getAllParticipants():
    Tournament = Query()
    Participation = Query()
    return db.search(
        Tournament.participantsData.all(Participation.Nom != '')
    )


def firstInRanking(name):
    Tournament = Query()
    Ranking = Query()
    return db.search(
        Tournament.rankings.any(
            ((Ranking.Pl == '1') & (Ranking.Nom == name))
        )
    )


def participateIn(name):
    Tournament = Query()
    Participation = Query()
    return db.search(
        Tournament.participantsData.any(Participation.Nom == name)
    )


if __name__ == "__main__":
    db = TinyDB('../../resources/db.json')

    if len(sys.argv) == 2 and sys.argv[1] == 'insert':
        db.purge()
        json_content = json.load(open('../../resources/dump.json'))
        for tournament in json_content['tournaments']:
            db.insert(tournament)

    wonCount = dict()
    for tournament in getAllParticipants():
        for participant in tournament['participantsData']:
            nbOfWon = len(firstInRanking(participant['Nom']))
            if nbOfWon != 0:
                wonCount[participant['Nom']] = nbOfWon
    winners = wonCount.items()#sorted(wonCount.items(), key=operator.itemgetter(0))
    print(len(winners))
    print(winners)
