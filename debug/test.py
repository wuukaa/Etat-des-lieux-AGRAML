
import math

dictionnaire = {"a": 12,
                "b": 25,
                "c": 54,
                "d": 47,
                "e": 32,
                "f": 10,
                "g": 0,
                "h": 178,
                "i": 21,
                "j": 23}
            
liste = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

def pagination(Item: list | dict, n_item_max: int) -> list | dict:
    n_page = math.ceil((len(Item)) /n_item_max)
    if type(Item) == dict:
        Scindage = [dict() for _ in range(n_page)]
        for i, key in enumerate(Item.keys()):
            pos = int(i/n_item_max)
            Scindage[pos][key] = Item[key]
    elif type(Item) == list:
        Scindage = [list() for _ in range(n_page)]
        for i in range(len(Item)):
            pos = int(i/n_item_max)
            Scindage[pos].append(Item[i])
    return Scindage

import requests



x = requests.post("http://localhost/requete_etat_des_lieux?id_edl=9&id_logement=1")

while(True):
    requests.post("http://localhost/requete_etat_des_lieux?id_edl=9&id_logement=1")
print(x.text)
