from flask import request
from sqlalchemy import select, delete
from .models import Logement, EDL, User, Valeur, Element, CategorieElement, TypeEDL, TypeLogement
from . import db
import time

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        if col != 'password':
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
    print(Valeurs)
    return Valeurs

# Fonction qui met à jour un EDL
def editEDL(form, id_edl):
    edl_line = db.session.query(EDL).filter(EDL.id == id_edl).first()
    for line in form.keys():
        split = line.split('.')
        if split[0] == 'Information':
            if split[1] == 'nom':
                edl_line.nom = form[line]
                continue
            elif split[1] == 'prenom':
                edl_line.prenom = form[line]
                continue
            elif split[1] == 'mail':
                edl_line.mail = form[line]
                continue
            elif split[1] == 'date':
                edl_line.date = form[line]
                continue
            continue
        id_valeur = int(split[0])
        if id_valeur != 0:
            champ = split[-1]
            if champ == 'valeur':
                valeur = form[line]
            else:
                line_db = db.session.query(Valeur).filter(Valeur.id == id_valeur).first()
                line_db.valeur = valeur
                line_db.observation = form[line]
                db.session.commit()
                print(f"{color.WARNING}Information: {color.OKBLUE}Ligne {id_valeur} modifié dans la table Valeurs{color.ENDC}")

# Fonction qui met à jour le prix et l'intitulé d'un élément
def updateElement(form):
    for elm in form.keys():
        split = elm.split('.')
        id_element = split[0]
        champ = split[1]
        valeur = form[elm]
        if champ == 'intitule':
            intitule = valeur
        else:
            line_db = db.session.query(Element).filter(Element.id == id_element).first()
            line_db.intitule = intitule
            line_db.prix = valeur
            db.session.commit()
            print(f"{color.WARNING}Information: {color.OKBLUE}Ligne {id_element} modifié dans la table Element{color.ENDC}")

# Fonction qui récupère les éléments présent dans un EDL pour un certain type de logement
def getStructure(type_logement):
    element_query = select(Element)
    element_values = db.session.execute(element_query.select()).fetchall()
    Checks = dict()
    for elm in element_values:
        check_query = select(TypeEDL).where(TypeEDL.id_element == elm[0]).where(TypeEDL.id_type_logement == type_logement)
        check_values = db.session.execute(check_query.select()).first()
        Checks[check_values[2]] = check_values[3]
    return Checks

# Fonction qui modifie les élements qui constitue un EDL par type de logement
def updateStructure(type_logement, form):
    def append_or_edit(type_logement, id_element, actif):
        line = db.session.query(TypeEDL).where(TypeEDL.id_element == id_element).where(TypeEDL.id_type_logement == type_logement).first()
        if line == None:
            new_line = TypeEDL(id_element=id_element, id_type_logement=type_logement, actif=actif)
            db.session.add(new_line)
            db.session.commit()
            print(f"{color.WARNING}Information: {color.OKBLUE}Ligne ajouté dans la table TypeEDL{color.ENDC}")
        else:
            line.actif = actif
            db.session.commit()
            print(f"{color.WARNING}Information: {color.OKBLUE}Ligne {line.id} modifié dans la table TypeEDL{color.ENDC}")
    element_query = select(Element)
    element_values = db.session.execute(element_query.select()).fetchall()
    element_dans_type = []
    for f in form:
        element_dans_type.append(int(f[0]))
    for elm in element_values:
        if elm[0] in element_dans_type:
            append_or_edit(type_logement, elm[0], True)
        else:
            append_or_edit(type_logement, elm[0], False)

# Création d'état des lieux vièrge selon le modele associé à un type de logement
def createEtat_des_lieux(type_logement):
    element_actif_query = select(TypeEDL).where(TypeEDL.id_type_logement == type_logement)
    element_actif_values = db.session.execute(element_actif_query.select()).fetchall()
    element_query = select(Element)
    element_values = db.session.execute(element_query.select()).fetchall()
    Elements = dict()
    for act in element_actif_values:
        if act[3]:
            cat_query = select(CategorieElement).where(CategorieElement.id == element_values[act[2]-1][1])
            cat = db.session.execute(cat_query.select()).first().intitule
            if cat not in Elements.keys():
                Elements[cat] = dict()
            Elements[cat][element_values[act[2]-1][2]] = [3, None, str(act[2])] # Etat, Observation, ID element
    return Elements

# Fonction qui récupère les information d'un locataire selon l'id de l'EDL
def getEDLInformation(id_edl):
    edl_query = select(EDL).where(EDL.id == id_edl)
    edl = db.session.execute(edl_query.select()).first()
    user_query = select(User).where(User.id == edl.effectue_par)
    user = db.session.execute(user_query.select()).first()
    logement_query = select(Logement).where(edl.id_logement == Logement.id)
    logement = db.session.execute(logement_query.select()).first()
    type_logement_query = select(TypeLogement).where(logement.type_logement == TypeLogement.id)
    type_logement = db.session.execute(type_logement_query.select()).first()
    Data = {'nom': edl.nom,
                 'prenom': edl.prenom,
                 'date': edl.date,
                 'mail': edl.mail,
                 'nom_agraml': user.nom,
                 'prenom_agraml': user.prenom,
                 'logement': logement.numero,
                 'type_logement': type_logement.type}
    
    return Data

def getEDLNewInformation(id_logement, current_user):
    def timeFormat(string):
        if len(string) < 2:
            return f'0{string}'
        else:
            return string
    logement_query = select(Logement).where(Logement.id == id_logement)
    logement = db.session.execute(logement_query.select()).first()
    type_logement_query = select(TypeLogement).where(logement.type_logement == TypeLogement.id)
    type_logement = db.session.execute(type_logement_query.select()).first()
    Time = time.localtime()
    mon = timeFormat(str(Time.tm_mon))
    day = timeFormat(str(Time.tm_mday))
    date = f'{Time.tm_year}-{mon}-{day}'
    Data = {'nom': '',
             'prenom': '',
             'date': date,
             'mail': '',
             'nom_agraml': current_user.nom,
             'prenom_agraml': current_user.prenom,
             'logement': logement.numero,
             'type_logement': type_logement.type}
    return Data

def deleteEDL(id_edl):
    print(id_edl)
    p = True
    while p:
        val = db.session.query(Valeur).where(Valeur.id_edl == id_edl).first()
        if val != None:
            db.session.delete(val)
        else:
            p = False
    edl = db.session.query(EDL).where(EDL.id == id_edl).first()
    db.session.delete(edl)
    db.session.commit()

    print(f"{color.WARNING}Information: {color.OKBLUE}L'EDL n°{id_edl} a été supprimé ainsi que ses informations associées{color.ENDC}")

# Fonction qui créer un EDL
def createEDL(form, occupe, id_logement, id_user):
    new_edl = EDL(id_logement=id_logement,
        effectue_par=id_user,
        occupation=occupe,
        date=form['Information.date'],
        nom=form['Information.nom'],
        prenom=form['Information.prenom'],
        mail=form['Information.mail'])
    db.session.add(new_edl)
    db.session.commit()
    id_edl = new_edl.id
    Valeurs = dict()
    print(form)
    for key in form.keys():
        key_split = key.split('.')
        key_id = key_split[0]
        if len(key_split) > 2:
            element = key_split[2]
            element_id = db.session.query(Element).where(Element.intitule == element).first().id
            categorie = key_split[1]
            champ = key_split[3]
            valeur = form[key]
            if categorie not in Valeurs.keys():
                Valeurs[categorie] = dict()
            if champ == 'valeur':
                valtemp = valeur
            else:
                new_valeur = Valeur(id_edl = id_edl,
                       id_element = element_id,
                       valeur = valtemp,
                       observation = valeur)
                db.session.add(new_valeur)
    db.session.commit()            
    print(f"{color.WARNING}Information: {color.OKBLUE}L'EDL n°{id_edl} a été ajouté ainsi que ses informations associées{color.ENDC}")
