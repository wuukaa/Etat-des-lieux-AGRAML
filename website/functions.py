from flask import request, flash
from sqlalchemy import select, delete, desc
from .models import *
from . import db
import time
import math
from datetime import datetime
import os
from .pdf_generation import *
# from xhtml2pdf import pisa

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

# def convert_html_file_to_pdf(html_content, output_path):
#     with open(output_path, 'wb') as pdf_file:
#         pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    
#     if pisa_status.err:
#         print("An error occurred while creating the PDF.")
#     else:
#         print(f"PDF successfully created at {output_path}")

# Fonction qui convertie la date HTML en format illisible pour un français
def tempsHTMLVersSeconde(temps_html: str) -> float:
    print(temps_html)
    Date = temps_html.split('T')[0].split('-')
    Heure = temps_html.split('T')[1].split(':')
    annee = int(Date[0])
    mois = int(Date[1])
    jour = int(Date[2])
    heure = int(Heure[0])
    minute = int(Heure[1])
    temps_en_seconde = datetime(annee, mois, jour, heure, minute).timestamp()
    return(temps_en_seconde)

# Fonction qui convertie la date en format illisible pour un français vers un format HTML 
def tempsSecondeVersHTML(temps_seconde: float) -> str:
    temps_string_brut = datetime.fromtimestamp(temps_seconde)
    temps_string = temps_string_brut.strftime('%Y-%m-%dT%H:%M')
    return temps_string

def tempsHTMLVersHumain(temps_html: str) -> str:
    Date = temps_html.split('T')[0].split('-')
    Heure = temps_html.split('T')[1].split(':')
    annee = Date[0]
    mois = Date[1]
    jour = Date[2]
    heure = Heure[0]
    minute = Heure[1]
    return f'{jour}/{mois}/{annee} à {heure}:{minute}'

def passWdCheck(string: str) -> bool:
    respect = [False, False, False]
    for character in string:
        for i, rulesList in enumerate(Rules):
            if character in rulesList:
                respect[i] = True
    if respect == [True, True, True]:
        return True
    return False

nonAllowed = [' ', '-', 'é', 'à', 'ç', ',', ';', '=', ':']

def userNmCheck(string: str) -> bool:
    if len(string) < 6:
        return False
    for character in string:
        if character in (nonAllowed + upperCaseList + specialList):
            return False
    return True

# Fonction qui récupère la liste de tous les logement selon le filtre
def searchLogements(form: dict) -> list[dict]:
    Logements = []
    batiment = form['batiment']
    if batiment != '-':
        Logements = db.session.query(Logement, TypeLogement).filter(Logement.batiment == batiment)
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
    # Mise en forme de la liste des logements
    ListeLogements = []
    for logement in Logements:
        nom_logement = logement.Logement.batiment + '.' + str(logement.Logement.etage) + '.' + logement.Logement.numero
        type_logement = logement.TypeLogement.type
        id_logement = logement.Logement.id
        try:
            etat_logement = db.session.query(EDL).filter(EDL.id_logement == logement.Logement.id).order_by(desc(EDL.date)).first().occupation
        except:
            etat_logement = None
        ListeLogements.append({'id_logement': id_logement,
                               'nom_logement' : nom_logement,
                               'type_logement' : type_logement,
                               'etat_logement' : etat_logement})
    return ListeLogements

# Fonction qui récupère les information d'un utilisateur (user) en fonction de son id
def getUser(id_user: int) -> dict:
    QueryUser = db.session.query(User).where(User.id == id_user).first()
    user = {'nom': QueryUser.nom, 'prenom': QueryUser.prenom}
    return user

# Fonction qui récupère la liste des EDL par logement spécifique
def getListeEtatDesLieux(id_logement: int) -> dict:
    QueryEDL = db.session.query(EDL).filter(EDL.id_logement == id_logement).order_by(desc(EDL.date)).first()
    user = getUser(QueryEDL.effectue_par)
    edl = {'id_edl' : QueryEDL.id,
            'occupation' : QueryEDL.occupation,
            'date' : tempsHTMLVersHumain(tempsSecondeVersHTML(float(QueryEDL.date))),
            'nom' : QueryEDL.nom,
            'prenom' : QueryEDL.prenom,
            'agraml_nom': user['nom'],
            'agraml_prenom': user['prenom']}
    return edl

# Fonction qui récupère les données d'un état des lieux en fonction de son id
def getEtat(id_edl: int) -> dict[list[dict[int, str, list[dict[int, str, str]], str],],]:
    # Fonction qui retourne un dictionnaire utile à l'affichage d'un etat pour le front end
    def attributionEtat(valeur: int) -> list[dict[int, str, str]]:
        EtatList = [{"valeur": 1, "attribut": 'Mauvais état', "couleur": 'danger', "actif": False},
                    {"valeur": 2, "attribut": "Etat d'usage", "couleur": 'warning', "actif": False},
                    {"valeur": 3, "attribut": 'Bon état', "couleur": 'secondary', "actif": False},
                    {"valeur": 4, "attribut": 'Très bon état', "couleur": 'success', "actif": False},
                    {"valeur": 5, "attribut": 'Neuf', "couleur": 'primary', "actif": False}]
        EtatList[int(valeur)-1]["actif"] = True
        return EtatList

    QueryValeur = db.session.query(Valeur, Element, CategorieElement).where(Valeur.id_element == Element.id).where(Element.id_categorie == CategorieElement.id).filter(Valeur.id_edl == id_edl).all()
    Etat = dict()
    for Item in QueryValeur:
        attributionEtatRelatif = attributionEtat(Item.Valeur.valeur)
        intituleCategorie = Item.CategorieElement.intitule
        EtatRelatif = {"id": Item.Element.id,
                       "intitule": Item.Element.intitule,
                       "etat": attributionEtatRelatif,
                       "observation": Item.Valeur.observation,
                       "facturation": Item.Valeur.facturation}
        if intituleCategorie not in Etat.keys():
            Etat[intituleCategorie] = [EtatRelatif]
        else:
            Etat[intituleCategorie].append(EtatRelatif)
    return Etat

# Fonction qui met à jour un EDL
def editEDL(form, id_edl):
    edl_line = db.session.query(EDL).filter(EDL.id == id_edl).first()
    for line in form.keys():
        split = line.split('.')

        match split[0]:
            case 'Information':
                match split[1]:
                    case 'nom':
                        edl_line.nom = form[line]
                        continue
                    case 'prenom':
                        edl_line.prenom = form[line]
                        continue
                    case 'mail':
                        edl_line.mail = form[line]
                        continue
                    case 'date':
                        edl_line.date = form[line]
                        continue
                    case _:
                        raise(KeyError)
            case 'signature':
                edl_line.signature = form[line]
                continue
            case 'image':
                #print(form[line])
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

# Fonction qui donne la liste des éléments pour un type d'edl selon le modèle, est utilisée lorsque qu'on fait un nouveau edl
def getTemplateEtatDesLieux(id_type_logement: int) -> dict[list[dict[int, str, list[dict[int, str, str]], str],],]:
    EtatListParDefault = [{"valeur": 1, "attribut": 'Mauvais état', "couleur": 'danger', "actif": False},
                {"valeur": 2, "attribut": "Etat d'usage", "couleur": 'warning', "actif": False},
                {"valeur": 3, "attribut": 'Bon état', "couleur": 'secondary', "actif": True},
                {"valeur": 4, "attribut": 'Très bon état', "couleur": 'success', "actif": False},
                {"valeur": 5, "attribut": 'Neuf', "couleur": 'primary', "actif": False}]
    QueryTypeEDL = db.session.query(TypeEDL).filter(TypeEDL.actif == True).filter(TypeEDL.id_type_logement == id_type_logement).all()
    StructureEtatDesLieux = dict()
    for Item in QueryTypeEDL:
        ElementRelatif = db.session.query(Element).filter(Element.id == Item.id_element).first()
        CategorieRelative = db.session.query(CategorieElement).filter(CategorieElement.id == ElementRelatif.id_categorie).first()
        element_id = ElementRelatif.id
        element_intitule = ElementRelatif.intitule
        categorie_intitule = CategorieRelative.intitule
        EtatRelatif = {"id": element_id,
                       "intitule": element_intitule,
                       "etat": EtatListParDefault,
                       "observation": '',
                       "facturation": False}
        if categorie_intitule not in StructureEtatDesLieux.keys():
            StructureEtatDesLieux[categorie_intitule] = [EtatRelatif]
        else:
            StructureEtatDesLieux[categorie_intitule].append(EtatRelatif)
    return StructureEtatDesLieux

# Fonction qui donne les information pour un edl, est utilisée lorsque qu'on fait un nouveau edl
def getTemplateEtatDesLieuxInformation(id_logement: int, current_user: User) -> dict:
    QueryLogement = db.session.query(Logement).filter(Logement.id == id_logement).first()
    QueryTypeLogement = db.session.query(TypeLogement).filter(QueryLogement.type_logement == TypeLogement.id).first()
    date = tempsSecondeVersHTML(time.time())
    EDLInformation = {'id_logement': QueryLogement.id,
            'date': date,
            'nom_agraml': current_user.nom,
            'prenom_agraml': current_user.prenom,
            'logement': QueryLogement.batiment + '.' + str(QueryLogement.etage) + '.' + QueryLogement.numero,
            'type_logement': QueryTypeLogement.type}
    return EDLInformation

# Fonction qui récupère les information d'un locataire selon l'id de l'EDL
def getEDLInformation(id_edl: int, edl_existant: bool) -> dict:
    QueryEDL = db.session.query(EDL).filter(EDL.id == id_edl).first()
    QueryUser = db.session.query(User).filter(User.id == QueryEDL.effectue_par).first()
    QueryLogement = db.session.query(Logement).filter(QueryEDL.id_logement == Logement.id).first()
    QueryTypeLogement = db.session.query(TypeLogement).filter(QueryLogement.type_logement == TypeLogement.id).first()
    if QueryUser:
        nom_agraml = QueryUser.nom
        prenom_agraml = QueryUser.prenom
        mail_agraml = QueryUser.email
        signature_agraml = QueryUser.signature
    else:
        nom_agraml = 'Inexistant'
        prenom_agraml = 'Inexsitant'
        signature_agraml = ''
    EDLInformation = {'id_logement' : QueryLogement.id,
            'nom':  '' if edl_existant else QueryEDL.nom,
            'prenom': '' if edl_existant else QueryEDL.prenom,
            'mail': '' if edl_existant else QueryEDL.mail,
            'date': tempsSecondeVersHTML(time.time()),
            'nom_agraml': nom_agraml,
            'prenom_agraml': prenom_agraml,
            'mail_agraml': mail_agraml,
            'signature_agraml' : signature_agraml,
            'logement': QueryLogement.batiment + '.' + str(QueryLogement.etage) + '.' + QueryLogement.numero,
            'type_logement': QueryTypeLogement.type,
            'signature': '' if edl_existant else QueryEDL.signature,
            'type_edl': QueryEDL.occupation}
    return EDLInformation

# Utiliser cette fonction pour supprimer un EDL totalement (valeurs, historique et edl)
def deleteEDL(id_edl: int) -> ...:
    dir = os.path.dirname(__file__)
    QueryValeur = db.session.query(Valeur).filter(Valeur.id_edl == id_edl)
    QueryImage = db.session.query(Image).filter(Image.id_edl == id_edl)
    for image in QueryImage:
        nb_image = db.session.query(Image).filter(Image.nom_image == image.nom_image).count()
        db.session.delete(image)
        if nb_image == 1:
            try:
                os.remove(dir + '/static/storage/img/' + image.nom_image)
            except:
                print("suppression de photo impossible")
    for val in QueryValeur:
        QueryInterventionRelatif = db.session.query(Intervention).filter(val.id == Intervention.id_valeur)
        db.session.delete(QueryInterventionRelatif)
        db.session.delete(val)
    historique = db.session.query(Historique).filter(Historique.id_edl == id_edl).all()
    for edl in historique:
        db.session.delete(edl)
    edl = db.session.query(EDL).where(EDL.id == id_edl).first()
    db.session.delete(edl)
    db.session.commit()

    print(f"{color.WARNING}Information: {color.OKBLUE}L'EDL n°{id_edl} a été supprimé ainsi que ses informations associées{color.ENDC}")

# Fonction qui créer un EDL
def createEDL(form: dict, occupe: bool, id_logement: int, id_user: int, ListeImageNom: list[str,]):
    new_edl = EDL(  id_logement=id_logement,
                    effectue_par=id_user,
                    occupation=occupe,
                    date=tempsHTMLVersSeconde(form['Information.date']),
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
        if key_split[0] == 'image':
            if form[key] == 'garder':
                ListeImageNom.append(key.split('/')[-1])
            continue
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
            elif champ == 'observation':
                obstemp = valeur
            else:
                new_valeur = Valeur(id_edl = id_edl,
                       id_element = element_id,
                       valeur = valtemp,
                       observation = obstemp,
                       facturation = True if valeur == 'on' else False)
                db.session.add(new_valeur)
    db.session.commit()  
    for image in ListeImageNom:
        new_image = Image(nom_image=image, id_edl=id_edl)
        db.session.add(new_image)
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
        logement_select = db.session.query(Logement).filter(Logement.id == edl_select.id_logement).first()
        logement = logement_select.batiment + "." + str(logement_select.etage) + "." + logement_select.numero
        ListEDL.append([edl_select, edl.action, tempsHTMLVersHumain(tempsSecondeVersHTML(int(edl.date))), logement])
    ListEDL.reverse()
    return ListEDL

# Fonction qui determine quelle page est active pour le menu en haut
def activePage(id: int) -> ...:
    len = 14
    active = len * ['']
    active[id] = 'active'
    return active

def deleteStructure(id_type: str) -> ...:
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

def getActivationCodeNewUser() -> list[dict[int, str, str, str, str],]:
    QueryActivation = db.session.query(User).where(User.active == False).all()
    ActivationCodeNewUser = []
    for Item in QueryActivation:
        ActivationCodeNewUserRelatif = {"id": Item.id,
                                        "identifiant": Item.username,
                                        "prenom": Item.prenom,
                                        "nom": Item.nom,
                                        "email": Item.email}
        ActivationCodeNewUser.append(ActivationCodeNewUserRelatif)
    return(ActivationCodeNewUser)

# Fonction pour paginer les pages web, elle prend une liste ou un doctionnaire, la i^eme page et le nombre d'élément par page 
def pagination(Item: list | dict, i_page: int, n_item_max: int) -> list[list | dict]:
    def generateBouton(i_page: int, nom_page: int | str,  active: bool) -> dict[int, int, bool]:
        return {"id_page": i_page, "identifiant": nom_page, "active": active}
    n_page_max = 6
    n_page = math.ceil((len(Item)) /n_item_max)
    if n_page == 1:
        return Item, None
    elif Item == None or Item == [] or Item == dict():
        return Item, None
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
    if i_page > len(Scindage):
        i_page = 0
    # Génération de la liste des boutons de pagination en fonction du nombre de page
    if n_page > n_page_max:
        ListeBoutton = list()
        if i_page < 4: 
            for i in range(5):
                ListeBoutton.append(generateBouton(i, i+1, True if i == i_page else False))
            ListeBoutton.append(generateBouton(-1, '...', False))
            ListeBoutton.append(generateBouton(n_page - 1, n_page, False))
        elif i_page > n_page - 5 and i_page <= n_page:
            ListeBoutton.append(generateBouton(0, 1, False))
            ListeBoutton.append(generateBouton(-1, '...', False))
            for i in range(5):
                ListeBoutton.append(generateBouton(n_page - 5 + i, n_page - 4 + i, True if n_page - 5 + i == i_page else False))
        else:
            ListeBoutton = [generateBouton(0, 1, False),
                            generateBouton(-1, '...', False),
                            generateBouton(i_page - 2, i_page - 1, False),
                            generateBouton(i_page - 1, i_page, False),
                            generateBouton(i_page, i_page + 1, True),
                            generateBouton(i_page + 1, i_page + 2, False),
                            generateBouton(i_page + 2, i_page + 3, False),
                            generateBouton(-1, '...', False),
                            generateBouton(n_page - 1, n_page, False)]
    else:
        ListeBoutton = [generateBouton(i, i + 1, (True if i == i_page else False)) for i in range(n_page)]
    return Scindage[i_page], ListeBoutton

# Pour accepter seulement les extensions de fichier voulues pour les edl
EXTENSIONS_AUTHORISEES = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def fichiersAutorises(extension: str) -> bool:
    if extension in EXTENSIONS_AUTHORISEES:
        return True
    else:
        return False
    
# Fonction qui récupère les photos d'un état des lieux
def recuperationImages(id_edl: str) -> list[str,]:
    QueryImage = db.session.query(Image).filter(Image.id_edl == id_edl).all()
    cheminImage = list()
    for image in QueryImage:
        cheminImage.append('storage/img/' +  image.nom_image)
    return cheminImage

# Fonction qui enregistre les images
def sauvegardeImages(files) -> list[str,]:
    dir = os.path.dirname(__file__)
    ListeImageNom = list()
    for name in files:
        fichier = request.files[name]
        extension = fichier.filename.split('.')[-1]
        if fichiersAutorises(extension):
            nom_du_fichier = name.split('.')[-1] + '.' +  extension
            fichier.save(dir + '/static/storage/img/' + nom_du_fichier)
            ListeImageNom.append(nom_du_fichier)
    return ListeImageNom

# Fonction qui rajoute les interventions si besoin
def rajoutInterventions(id_edl: int) -> ...:
    QueryValeur = db.session.query(Valeur).filter(Valeur.id_edl == id_edl).filter(Valeur.facturation == True).all()
    for valeur in QueryValeur:
        new_intervention = Intervention(id_valeur=valeur.id, etat=0)
        try:
            db.session.add(new_intervention)
        except:
            print("Erreur lors de l'ajout d'une intervention")
    db.session.commit()

# Fonction qui liste les interventions
def getListeInterventions(Journal: bool) -> list[dict,]:
    QueryIntervention = db.session.query(Intervention).filter(Intervention.etat == (1 if Journal else 0)).all()
    ListeInterventions = list()
    for intervention in QueryIntervention:
        interventionRelative = dict()
        ValeurRelative =  db.session.query(Valeur).filter(Valeur.id == intervention.id_valeur).first()
        print(ValeurRelative)
        ElementRelatif = db.session.query(Element).filter(Element.id == ValeurRelative.id_element).first()
        CategorieRelative = db.session.query(CategorieElement).filter(CategorieElement.id == ElementRelatif.id_categorie).first()
        EDLRelatif = db.session.query(EDL).filter(EDL.id == ValeurRelative.id_edl).first()
        id_logement_relatif = EDLRelatif.id_logement
        prenom_responsable, nom_responsable = EDLRelatif.prenom, EDLRelatif.nom
        LogementRelatif = db.session.query(Logement).filter(Logement.id == id_logement_relatif).first()
        logement = LogementRelatif.batiment + "." + str(LogementRelatif.etage) + "." + LogementRelatif.numero
        id = intervention.id
        intitule_element = ElementRelatif.intitule
        intitule_categorie = CategorieRelative.intitule
        observation = ValeurRelative.observation
        interventionRelative = {"id": id, "logement": logement, "intitule_element": intitule_element, "intitule_categorie": intitule_categorie, "prenom_responsable": prenom_responsable, "nom_responsable": nom_responsable, "observation": observation}
        ListeInterventions.append(interventionRelative)
    return ListeInterventions