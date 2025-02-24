from flask import request, flash
from sqlalchemy import select, delete
from .models import *
from . import db
import time
from datetime import datetime
import random as rd
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

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

def getTypeLogements():
    typeLogements_query = select(TypeLogement)
    typeLogements = db.session.execute(typeLogements_query.select()).fetchall()
    return typeLogements

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

# Fonction qui récupère la liste de tous les logement selon le filtre
def getLogements(form):
    Logements = []
    batiment = form['batiment']
    if batiment != '-':
        Logements = db.session.query(Logement, TypeLogement).filter(Logement.batiment == batiment)
        print(Logements)
    etage = form['etage']
    if etage != '-':
        if Logements != []:
            Logements = Logements.filter(Logement.etage == etage)
        else:
            Logements = db.session.query(Logement, TypeLogement).filter(Logement.etage == etage)
    type = form['type']
    if type != '-':
        if Logements != []:
            Logements = Logements.filter(Logement.type_logement == type)
        else:
            Logements = db.session.query(Logement, TypeLogement).filter(Logement.type_logement == type)
    prenom = form['prenom']
    if prenom != '':
        if Logements != []:
            Logements = Logements.where(EDL.id_logement == Logement.id).filter(EDL.prenom == prenom)
        else:
            Logements = db.session.query(Logement, TypeLogement).where(EDL.id_logement == Logement.id).filter(EDL.prenom == prenom)
    nom = form['nom']
    if nom != '':
        if Logements != []:
            Logements = Logements.where(EDL.id_logement == Logement.id).filter(EDL.nom == nom)
        else:
            Logements = db.session.query(Logement, TypeLogement).where(EDL.id_logement == Logement.id).filter(EDL.nom == nom)
    if Logements != []:
        Logements = Logements.where(Logement.type_logement == TypeLogement.id).all()
    else:
        Logements = db.session.query(Logement, TypeLogement).where(Logement.type_logement == TypeLogement.id).all()
    InfoLogements = dict()
    for logement in Logements:
        id_logement = logement.Logement.id
        nb_edl = db.session.query(EDL).where(EDL.id_logement == id_logement).where(EDL.supprime == False).count()
        InfoLogements[id_logement] = nb_edl
    return Logements, InfoLogements

# Fonction qui récupère les information d'un utilisateur (user) en fonction de son id
def getUser(id_user):
    user_query = select(User).where(User.id == id_user)
    user_keys = db.session.execute(user_query.select()).keys()
    user_values = db.session.execute(user_query.select()).first()
    User_information = dict()
    for i, col in enumerate(user_keys):
        if col != 'password':
            if user_values:
                User_information[col] = user_values[i]
            else:
                User_information[col] = 'Inexistant'
    return User_information

# Fonction qui récupère la liste des EDL par logement spécifique
def getEtat_des_lieux(id_logement):
    edl_query = select(EDL).where(EDL.id_logement == id_logement).where(EDL.supprime == False)
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
        if element_values != None:
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
        elif split[0] == 'signature':
            edl_line.signature = form[line]
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
def updateElement(form, id_cat):
    for elm in form.keys():
        split = elm.split('.')
        id_element = split[0]
        if id_element != 'newitem':
            champ = split[1]
            valeur = form[elm]
            if champ == 'intitule':
                intitule = valeur
            else:
                if intitule == '' and valeur == '':
                    typeEDLtable = db.session.query(TypeEDL).where(TypeEDL.id_element == id_element).first()
                    valeurTable = db.session.query(Valeur).where(Valeur.id_element == id_element).first()
                    if typeEDLtable == None and valeurTable == None:
                        element_del = db.session.query(Element).where(Element.id == id_element).first()
                        db.session.delete(element_del)
                        db.session.commit()
                    else:
                        flash("L'élement est utilisé ailleurs (structure d'EDL et dans les EDL).", category="error")
                else:
                    line_db = db.session.query(Element).where(Element.id == id_element).first()
                    line_db.intitule = intitule
                    line_db.prix = valeur
                    db.session.commit()
                    print(f"{color.WARNING}Information: {color.OKBLUE}Ligne {id_element} modifié dans la table Element{color.ENDC}")
        else:
            if split[1] == 'intitule':
                new_intitule = form[elm]
            else:
                new_prix = form[elm]
    if new_intitule != '' and new_prix != '':
        new_element = Element(id_categorie=id_cat,
                intitule=new_intitule,
                prix=new_prix)
        db.session.add(new_element)
        db.session.commit()
        print(f"{color.WARNING}Information: {color.OKBLUE}Ligne ajoutée dans la table Element{color.ENDC}")


# Fonction qui récupère les éléments présent dans un EDL pour un certain type de logement
def getStructure(type_logement):
    element_query = select(Element)
    element_values = db.session.execute(element_query.select()).fetchall()
    Checks = dict()
    for elm in element_values:
        check_query = select(TypeEDL).where(TypeEDL.id_element == elm[0]).where(TypeEDL.id_type_logement == type_logement)
        check_values = db.session.execute(check_query.select()).first()
        if check_values != None:
            Checks[check_values[2]] = check_values[3]
    return Checks

# Fonction qui modifie les élements qui constitue un EDL par type de logement
def updateStructure(type_logement, form):
    def append_or_edit(type_logement, id_element, actif):
        line = db.session.query(TypeEDL).where(TypeEDL.id_element - id_element == 0).where(TypeEDL.id_type_logement == type_logement).first()
        if line == None:
            new_line = TypeEDL(id_element=id_element, id_type_logement=type_logement, actif=actif)
            db.session.add(new_line)
            db.session.commit()
            print(f"{color.WARNING}Information: {color.OKBLUE}Ligne ajouté dans la table TypeEDL{color.ENDC}")
        else:
            print(id_element)
            line.actif = actif
            db.session.commit()
            print(f"{color.WARNING}Information: {color.OKBLUE}Ligne {line.id} modifié dans la table TypeEDL{color.ENDC}")
    element_query = select(Element)
    element_values = db.session.execute(element_query.select()).fetchall()
    element_dans_type = []
    for f in form:
        if f == 'delete' or f == 'save':
            continue
        print(int(f))
        element_dans_type.append(int(f))
    for elm in element_values:
        if elm[0] in element_dans_type:
            append_or_edit(type_logement, int(elm[0]), True)
        else:
            append_or_edit(type_logement, int(elm[0]), False)

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
    if user:
        nom = user.nom
        prenom = user.prenom
        signature_agraml = user.signature
    else:
        nom = 'Inexistant'
        prenom = 'Inexsitant'
        signature_agraml = ''
    Data = {'nom': edl.nom,
                 'prenom': edl.prenom,
                 'date': edl.date,
                 'mail': edl.mail,
                 'nom_agraml': nom,
                 'signature_agraml' : signature_agraml,
                 'prenom_agraml': prenom,
                 'logement': logement.batiment + '.' + str(logement.etage) + '.' + logement.numero,
                 'type_logement': type_logement.type,
                 'signature': edl.signature}
    
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
             'logement': logement.batiment + '.' + str(logement.etage) + '.' + logement.numero,
             'type_logement': type_logement.type}
    return Data

# Fonction pour cacher un EDL
def hideEDL(id_edl):
    edl = db.session.query(EDL).filter(EDL.id == id_edl).first()
    edl.supprime = True
    db.session.commit()

# Utiliser cette fonction pour supprimer un EDL totalement
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
    new_edl = EDL(supprime = False,
        id_logement=id_logement,
        effectue_par=id_user,
        occupation=occupe,
        date=form['Information.date'],
        nom=form['Information.nom'],
        prenom=form['Information.prenom'],
        mail=form['Information.mail'],
        signature=form['signature'])
    db.session.add(new_edl)
    db.session.commit()
    id_edl = new_edl.id
    Valeurs = dict()
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
    return new_edl.id

# Fonction qui met à jour les types de logement
def updateTypeLogement(form):
    for key in form.keys():
        if key != 'newtypeoflogement':
            if form[key] != '':
                line_db = db.session.query(TypeLogement).filter(TypeLogement.id == key).first()
                line_db.type = form[key]
            else:
                typeEDLtable = db.session.query(TypeEDL).filter(TypeEDL.id_type_logement == key).first()
                valeurTable = db.session.query(Logement).filter(Logement.type_logement == key).first()
                if typeEDLtable == None and valeurTable == None:
                    typeLogement = db.session.query(TypeLogement).where(TypeLogement.id == key).first()
                    db.session.delete(typeLogement)
                    db.session.commit()
                else:
                    flash("Impossible de supprimer, le type est utilisé pour une structure d'EDL ou pour des logements", category="error")
        else:
            if form[key] != '':
                new_type = TypeLogement(type=form[key])
                db.session.add(new_type)
    db.session.commit()

def updateCategorie(form):
    for key in form.keys():
        if key != 'newcatgeorie':
            line_db = db.session.query(CategorieElement).filter(CategorieElement.id == key).first()
            if form[key] != '':
                if form[key] != line_db.intitule:
                    line_db.intitule = form[key]
                    flash(f'La catégorie {line_db.intitule} a bien été renommé', category='success')
            else:
                id_cat = line_db.id
                check = db.session.query(Element).where(Element.id_categorie == id_cat).first()
                if not check:
                    flash(f'La catégorie {line_db.intitule} a été effacé de la base de données', category='success')
                    db.session.delete(line_db)
                else:
                    flash(f'La catégorie {line_db.intitule} ne peut pas être effacé car un ou plusieurs éléments lui sont rattachés', category='error')
        else:
            if form[key] != '':
                new_categorie = CategorieElement(intitule=form[key])
                flash(f'La catégorie {new_categorie.intitule} a été rajouté à la base de données', category='success')
                db.session.add(new_categorie)
                db.session.commit()
    db.session.commit()

def updateLogements(form):
    for name in form.keys():
        split = name.split('.')
        id = split[0]
        champ = split[1]
        if id != 'nouveau':
            if champ =='batiment':
                batiment = form[name]
            elif champ =='etage':
                etage = form[name]
            elif champ == 'numero':
                logement = db.session.query(Logement).filter(Logement.id == id).first()
                numero = form[name]
                if numero == '':
                    checkEDL = db.session.query(EDL).filter(EDL.id_logement == id).first()
                    if checkEDL == None:
                        db.session.delete(logement)
                        db.session.commit()
                        continue
                    else:
                        flash(f"Ne peut pas supprimer le logement {logement.numero}, car affilié à un ou plusieurs EDL!", category='error')
                logement.numero == numero
            else:
                type = form[name]
                logement.type_logement = type
                logement.batiment = batiment
                logement.numero = numero
                logement.etage = etage
                db.session.commit()
        else:
            if champ == 'batiment':
                batiment = form[name]
            elif champ == 'etage':
                etage = form[name]
            elif champ == 'numero':
                numero = form[name]
            else:
                if numero != '' and numero != '00':
                    type = form[name]
                    logement = db.session.query(Logement).filter(Logement.batiment == batiment, Logement.etage == etage, Logement.numero == numero, Logement.type_logement == type).first()
                    if logement != None:
                        flash('Le logement existe dejà!', category='error')
                        continue
                    new_logement = Logement(batiment=batiment, etage=etage, numero=numero, type_logement=int(type))
                    db.session.add(new_logement)
                    db.session.commit()

def sortEDLbyDate():
    Histo = db.session.query(Historique).order_by(Historique.date).all()
    ListEDL = []
    for edl in Histo:
        edl_select = db.session.query(EDL).filter(EDL.id == edl.id_edl).first()
        ListEDL.append([edl_select, edl.action, datetime.fromtimestamp(int(edl.date))])
    ListEDL.reverse()
    return ListEDL

# Fonction qui convertie la date en format lisible pour un français
def convertDateFormat(d):
    dateSplit = d.split("-")
    return(dateSplit[2] + '/' + dateSplit[1] + '/' + dateSplit[0])
            
def randomCodeGenerator():
    texte = "azertyuiopqsdfghjklmwxcvbn1234567890"
    lencode = 60
    lentexte = len(texte)
    code = ''
    for i in range(lencode):
        r = rd.randint(0, lentexte - 1)
        code += texte[r]
    return code

# Fonction qui envoie un mail de confirmation à Riz au lait lors d'une inscription
def SendConfirmationMail(code, id, user):
    sender = "inscription@amnet.fr"
    recipients = "lucas1.henry@live.fr"
    password = "tlxm cgep cvfo xmuf"
    msg = MIMEMultipart()
    msg['Subject'] = "Confirmation d'inscription"
    msg['From'] = sender
    msg['To'] = recipients
    prenom = user.prenom
    nom = user.nom
    mail = user.email
    body = f"""
<body>
    <h2>Activation d'un nouveau compte pour <b>agraml.amnet.fr</b></h2>

    <p>Voici le lien d'activation du compte de {prenom} {nom}, asssocié à l'adresse mail {mail}
    <br>
    <a href="http://agraml.amnet.fr/confirmation?code={code}&id={id}">Activation du compte</a>
</body>
"""
    msg.attach(MIMEText(body, 'html'))
   
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print(color.OKGREEN + "Mail de confirmation envoyé!" + color.ENDC)

# Fonction qui determine quelle page est active pour le menu en haut
def activePage(id):
    len = 14
    active = len * ['']
    active[id] = 'active'
    return active

def deleteStructure(id_type):
    Lines = db.session.query(TypeEDL).where(TypeEDL.id_type_logement == id_type).all()
    for line in Lines:
        db.session.delete(line)
    db.session.commit()

# Fonction qui gère l'historique des actions
# 0 -> supprimé ; 1 -> modif ; 2 -> arrivé ; 3 -> départ
def appendHistorique(id_edl, action):
    date = int(time.time())
    new_event = Historique(id_edl=id_edl, action=action, date = date)
    db.session.add(new_event)
    db.session.commit()