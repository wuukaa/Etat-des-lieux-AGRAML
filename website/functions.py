from .models import *

specialList = ['&', '*', '?', '!', '(', ')', '=', '<', '>', "'", '"', '-', '+', '/']
upperCaseList = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numberList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

Rules = [specialList, upperCaseList, numberList]

def passWdCheck(string):
    respect = [False, False, False]
    for character in string:
        for i, rulesList in enumerate(Rules):
            if character in rulesList:
                respect[i] = True
    if respect == [True, True, True]:
        return True
    return False

nonAllowed = [' ', '-', 'é', 'à', 'ç', ',', ';', '=', ':']

def userNmCheck(string):
    if len(string) < 6:
        return False
    for character in string:
        if character in (nonAllowed + upperCaseList + specialList):
            return False
    return True

def getDataFromDatabase(logement):
    type_logement = Logement.query.get(logement).type_logement

    information_query = select(EDL).where(logement == EDL.id_logement)
    information_keys = db.session.execute(information_query.select()).keys()
    information_values = db.session.execute(information_query.select()).first()

    autre_query = select(AUTRE).where(AUTRE.id == EDL.id_a).where(EDL.id_logement == logement)
    autre_keys = db.session.execute(autre_query.select()).keys()
    autre_values = db.session.execute(autre_query.select()).first()

    chambre_query = select(CHAMBRE).where(CHAMBRE.id == EDL.id_c).where(EDL.id_logement == logement)
    chambre_keys = db.session.execute(chambre_query.select()).keys()
    chambre_values = db.session.execute(chambre_query.select()).first()

    kitchen_query = select(KITCHENETTE).where(KITCHENETTE.id == EDL.id_k).where(EDL.id_logement == logement)
    kitchen_keys = db.session.execute(kitchen_query.select()).keys()
    kitchen_values = db.session.execute(kitchen_query.select()).first()

    sdb_query = select(SALLE_DE_BAIN).where(SALLE_DE_BAIN.id == EDL.id_sdb).where(EDL.id_logement == logement)
    sdb_keys = db.session.execute(sdb_query.select()).keys()
    sdb_values = db.session.execute(sdb_query.select()).first()

    sdv_query = select(SALLE_DE_VIE).where(SALLE_DE_VIE.id == EDL.id_sdv).where(EDL.id_logement == logement)
    sdv_keys = db.session.execute(sdv_query.select()).keys()
    sdv_values = db.session.execute(sdv_query.select()).first()

    wc_query = select(WC).where(WC.id == EDL.id_wc).where(EDL.id_logement == logement)
    wc_keys = db.session.execute(wc_query.select()).keys()
    wc_values = db.session.execute(wc_query.select()).first()
    
    Data = {"Information":None,
            "Kitchenette":None,
            "Salle de vie":None,
            "Salle de bain":None,
            "WC":None,
            "Chambre":None,
            "Autres":None}
    
    Values_and_keys = [ [information_keys, information_values],
                        [kitchen_keys, kitchen_values],
                        [sdv_keys, sdv_values],
                        [sdb_keys, sdb_values],
                        [wc_keys, wc_values],
                        [chambre_keys, chambre_values],
                        [autre_keys, autre_values] ]
    
    for i, cat in enumerate(Data.keys()):
        Dtemp = dict()
        for j, col in enumerate(Values_and_keys[i][0]):
            if Values_and_keys[i][1] != None:
                Dtemp[col] = Values_and_keys[i][1][j]
        Data[cat] = Dtemp
    return type_logement, Data

def listCritere(logement):
    type_logement, Data = getDataFromDatabase(logement)
    if type_logement == 0:
        return 'Chambre', Data
    elif type_logement == 1:
        return 'Studio', Data
    else:
        return 'Collocation', Data