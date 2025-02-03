from flask import request
from sqlalchemy import select
from .models import Logement, EDL, User, Valeur, Element, CategorieElement
from . import db

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

# Fonction qui récupère la liste de tous les logement selon le type
def getLogements(type_logement):
    logement_query = select(Logement).where(Logement.type_logement == type_logement)
    #logement_keys = db.session.execute(logement_query.select()).keys()
    logement_values = db.session.execute(logement_query.select()).fetchall()
    Logements = dict()
    for tuple in logement_values:
        Logements[tuple[1]] = tuple[0]
    return Logements

# Fonction qui récupère les information d'un utilisateur (user) en fonction de son id
def getUser(id_user):
    user_query = select(User).where(User.id == id_user)
    user_keys = db.session.execute(user_query.select()).keys()
    user_values = db.session.execute(user_query.select()).first()
    User_information = dict()
    for i, col in enumerate(user_keys):
        if col is not 'password':
            User_information[col] = user_values[i]
    return User_information

# Fonction qui récupère la liste des EDL par logement spécifique
def getEtat_des_lieux(id_logement):
    edl_query = select(EDL).where(EDL.id_logement == id_logement)
    edl_keys = db.session.execute(edl_query.select()).keys()
    edl_values = db.session.execute(edl_query.select()).fetchall()
    EDLs = []
    for j, value in enumerate(edl_values):
        Dict = dict()
        user = getUser(edl_values[j][2])
        for i, col in enumerate(edl_keys):
            if col == 'effectue_par':
                Dict[col] = user
            else:
                Dict[col] = value[i]
        EDLs.append(Dict)
    return EDLs

# Fonction qui récupère les données d'un état des lieux en fonction de son id
def getValeurs(id_edl):
    valeurs_query = select(Valeur).where(Valeur.id_edl == id_edl)
    valeurs_keys = db.session.execute(valeurs_query.select()).keys()
    valeurs_values = db.session.execute(valeurs_query.select()).fetchall()
    Valeurs = dict()
    for valeur in valeurs_values:
        val = valeur[3]
        observation = valeur[4]
        id_element = valeur[2]
        id = valeur[0]
        element_query = select(Element).where(Element.id == id_element)
        element_values = db.session.execute(element_query.select()).first()
        element = element_values[2]
        id_categorie = element_values[1]
        categorie_query = select(CategorieElement).where(CategorieElement.id == id_categorie)
        categorie_values = db.session.execute(categorie_query.select()).first()
        categorie = categorie_values[1]
        if categorie not in Valeurs.keys():
            Valeurs[categorie] = {element : [val, observation, str(id)]}
        else:
            Valeurs[categorie][element] = [val, observation, str(id)]
    return Valeurs
    #db.session.add(new_user)
    #db.session.commit()

