from bs4 import BeautifulSoup
import requests
import sys
import pickle
import json

tournaments = dict()
stats = dict()
participants = dict()
rankings = dict()


def checkAndSanitize(data):
    res = ''
    if data is not None:
        if data.string is not None:
            res = data.string.replace('\r\n', '\n ')
    return res


def getStats(data, doc):
    def parseStats(stat):
        stat = checkAndSanitize(stat)
        return stat.replace(':', '').strip()
    html_doc = doc.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    items = soup.find_all('td', class_='papi_liste_c')
    parsed_stats = [parseStats(item) for item in items if items]
    labels = parsed_stats[0::2]
    values = parsed_stats[1::2]
    res = dict(list(zip(labels, values)))

    data['stats'] = res

    return data


def getData(index, doc):
    res = dict()

    html_doc = doc.text
    soup = BeautifulSoup(html_doc, 'html.parser')

    res['id'] = index
    res['tournament_name'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelNom'}
    ))
    res['tournament_place'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelLieu'}
    ))
    res['dates'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelDates'}
    ))
    res['national_elo'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelEloNat'}
    ))
    res['quick_elo'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelEloRapide'}
    ))
    res['fide_elo'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelEloFide'}
    ))
    res['approved_by'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelHomologuePar'}
    ))
    res['rounds_count'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelNbrRondes'}
    ))
    res['rhythm'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelCadence'}
    ))
    res['pairings'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelAppariements'}
    ))
    res['organizer'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelOrganisateur'}
    ))
    res['entry_young'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelInscriptionJeune'}
    ))
    res['entry_old'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelInscriptionSenior'}
    ))
    res['arbitrator'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelArbitre'}
    ))
    res['address'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelAdresse'}
    ))
    res['contact'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelContact'}
    ))
    res['announcement'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelAnnonce'}
    ))

    res['prices_total'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelPrixTotal'}
    ))
    res['first_price'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelPrix1'}
    ))
    res['second_price'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelPrix2'}
    ))
    res['third_price'] = checkAndSanitize(soup.find(
        'span', {'id': 'ctl00_ContentPlaceHolderMain_LabelPrix3'}
    ))
    return res


def participantsData(data, doc):
    def parseStats(stat):
        stat = checkAndSanitize(stat)
        return stat.replace(':', '').strip()
    html_doc = doc.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    res = list()
    i = 0
    head = list()
    for row in soup.findAll('tr'):
        aux = row.findAll('td')
        if i == 2:
            head = [checkAndSanitize(dd) for dd in aux if aux]
        elif i > 2:
            dtt = [checkAndSanitize(dd) for dd in aux if aux]
            zipped = zip(head, dtt)
            res.append(dict(list(zipped)))
        i += 1

        for item in res:
            item.pop('\u00a0', None)

    data['participantsData'] = res

    return data


def rankingsData(data, doc):
    def parseStats(stat):
        stat = checkAndSanitize(stat)
        return stat.replace(':', '').strip()
    html_doc = doc.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    res = list()
    i = 0
    head = list()
    for row in soup.findAll('tr'):
        aux = row.findAll('td')
        if i == 2:
            head = [checkAndSanitize(dd) for dd in aux if aux]
        elif i > 2:
            dtt = [checkAndSanitize(dd) for dd in aux if aux]
            zipped = zip(head, dtt)
            res.append(dict(list(zipped)))
        i += 1

        for item in res:
            item.pop('\u00a0', None)
            item.pop('Fede', None)

    data['rankings'] = res

    return data


if __name__ == "__main__":
    argc = len(sys.argv)
    iterations = range(30000, 30500)
    base_url = 'http://echecs.asso.fr/FicheTournoi.aspx?Ref={}'
    urls = list(map(lambda x: (x, base_url.format(x)), iterations))
    content = dict()
    print("\n========== Descriptions ==========")
    if argc >= 2 and 'save' in sys.argv[1]:
        for index, url in urls:
            doc = requests.get(url)
            tournaments[index] = doc
        for index, doc in tournaments.items():
            content[index] = getData(index, doc)
        pickle.dump(
            content,
            open('../../resources/td2.save', mode='wb+')
        )
    else:
        content = pickle.load(
            open('../../resources/td2.save', mode='rb')
        )
    print("\n========== Stats ==========")
    if argc >= 2 and 'stats' in sys.argv[1]:
        content_with_stats = dict()
        base_url = 'http://echecs.asso.fr/Resultats.aspx?URL=Tournois/Id/{}/{}&Action=Stats'
        urls = list(map(lambda x: (x, base_url.format(x, x)), iterations))
        for index, url in urls:
            doc = requests.get(url)
            stats[index] = doc
        for index, doc in stats.items():
            content_with_stats[index] = getStats(content[index], doc)
        pickle.dump(
            content_with_stats,
            open('../../resources/td2_with_stats.save', mode='wb+')
        )
    else:
        content_with_stats = pickle.load(
            open('../../resources/td2_with_stats.save', mode='rb')
        )
    print("\n========== Participants ==========")
    if argc >= 2 and 'part' in sys.argv[1]:
        content_with_stats_and_part = dict()
        base_url = 'http://echecs.asso.fr/Resultats.aspx?URL=Tournois/Id/{}/{}&Action=Ls'
        urls = list(map(lambda x: (x, base_url.format(x, x)), iterations))
        for index, url in urls:
            doc = requests.get(url)
            participants[index] = doc
        for index, doc in participants.items():
            content_with_stats_and_part[index] = participantsData(
                content_with_stats[index], doc)
        pickle.dump(
            content_with_stats_and_part,
            open('../../resources/td2_with_stats_part.save', mode='wb+')
        )
    else:
        content_with_stats_and_part = pickle.load(
            open('../../resources/td2_with_stats_part.save', mode='rb')
        )
    print("\n========== Rankings ==========")
    if argc >= 2 and 'rank' in sys.argv[1]:
        content_with_stats_and_part_rank = dict()
        base_url = 'http://echecs.asso.fr/Resultats.aspx?URL=Tournois/Id/{}/{}&Action=Ga'
        urls = list(map(lambda x: (x, base_url.format(x, x)), iterations))
        for index, url in urls:
            doc = requests.get(url)
            rankings[index] = doc
        for index, doc in rankings.items():
            content_with_stats_and_part_rank[index] = rankingsData(
                content_with_stats_and_part[index], doc)
        pickle.dump(
            content_with_stats_and_part_rank,
            open('../../resources/td2_with_stats_part_rank.save', mode='wb+')
        )
    else:
        content_with_stats_and_part_rank = pickle.load(
            open('../../resources/td2_with_stats_part_rank.save', mode='rb')
        )
    jsonPrep = dict()
    jsonPrep['tournaments'] = list(content_with_stats_and_part_rank.values())
    json.dump(jsonPrep, open(
        '../../resources/dump.json', mode='w+', encoding='utf-8'), ensure_ascii=False)

    # Ajout d'un traitement pour avoir un dictionnaire des participants ou pour chaque participant on a son nom, prenom, et une liste (tournoi et place , pts)
    set_of_participants= set()
    for items in content_with_stats_and_part_rank.values():
        for item in items['rankings']:
            if(item['Nom']!=''):
                set_of_participants.add(item['Nom'])
    
    participants_list=list()
    #print(set_of_participants)

    for person in set_of_participants:
        temp=dict()
        temp['name']=person
        participations=list()
        for items in content_with_stats_and_part_rank.values():
            for item in items['rankings']:
                if(item['Nom'] == person):
                    temp_tournoi=dict()
                    temp_tournoi['id_tournois']=items['id']
                    temp_tournoi['pl']=item['Pl']
                    if 'Elo' in item.keys():
                        temp_tournoi['elo']=item['Elo']
                    if 'perf' in item.keys():
                        temp_tournoi['perf']=item['Perf']
                    participations.append(temp_tournoi)
        temp['participations']=participations
        participants_list.append(temp)
    jsonPrepParticipants = dict()
    jsonPrepParticipants['participants'] = list(participants_list)
    json.dump(jsonPrepParticipants, open(
        '../../resources/participants.json', mode='w+', encoding='utf-8'), ensure_ascii=False)


        



