from flask import Blueprint, render_template, request, flash, redirect, make_response
from flask_login import login_required, current_user
from .models import CategorieElement, Element, TypeLogement, TypeEDL, Logement, User, EDL, Historique
from . import db
from sqlalchemy import select
from .functions import *

views = Blueprint('views', __name__)


# Redirection vers la page d'accueil depuis la racine
@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    return render_template('accueil.html', user=current_user, active=activePage(0))

# Redirection vers la page d'accueil
@views.route('/accueil', methods = ['GET'])
def accueil():
    return render_template('accueil.html', user=current_user, active=activePage(0))

# Redirection vers la page d'état des lieux
@views.route('/etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def etat_des_lieux():
    # On récupère l'identifiant associé au bouton du menu
    TypesLogements = db.session.query(TypeLogement).all()
    form = {'batiment':'-',
            'etage':'-',
            'type':'-',
            'prenom': '',
            'nom': ''}
    # Si on a une requete de filtre
    if request.method == 'POST':
        form = request.form
        ListeLogements = searchLogements(form)
    else:
        ListeLogements = searchLogements(form)
    return render_template('liste_logements.html', form=form, active=activePage(1), len=len, str=str, user=current_user, TypesLogements=TypesLogements, ListeLogements=ListeLogements)

# Redirection vers la page de la liste des états des lieux pour un logement
@views.route('/liste_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def liste_etat_des_lieux():
    # On récupère l'identifiant associé au logement
    id_logement = request.form.get('id_logement')
    ListeEtatDesLieux = getListeEtatDesLieux(id_logement)
    return render_template('liste_etat_des_lieux.html', active=activePage(1),  id_logement=id_logement, user=current_user, ListeEtatDesLieux=ListeEtatDesLieux)

# Redirection vers la page de modification d'état des lieux
@views.route('/modification_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def modification_etat_des_lieux():
    id_edl = request.form.get('id_edl')
    id_logement = request.args.get('id_logement')
    Valeurs = dict()
    if id_edl == 'nouveau':
        type_logement = db.session.query(Logement).filter(Logement.id == id_logement).first().type_logement
        Valeurs = createEtatDesLieux(type_logement)
        EDLInformation = getEDLNewInformation(id_logement, current_user)
        # Variable qui sert à afficher ou non les boutons modifier et supprimer
        creation = True
    else:
        Valeurs = getValeurs(id_edl)
        EDLInformation = getEDLInformation(id_edl)
        creation = False
    return render_template('modification_etat_des_lieux.html', active=activePage(1),  user=current_user,  Valeurs = Valeurs, id_edl = id_edl, creation=creation, EDLInformation=EDLInformation)

# Pour récupérer les détails des états des lieux
@views.route('requete_etat_des_lieux', methods = ['POST', 'GET'])
@login_required
def requete_etat_des_lieux():
    if request.method == 'POST':
        id_logement = request.args.get('id_logement')
        id_edl = request.args.get('id_edl')
        form = request.form
        action = request.form.get('0.action')
        if action == 'modification':
            appendHistorique(id_edl, '1')
            editEDL(form, id_edl)
            flash('Les données ont été modifiés dans la base de données', category='warning')
        elif action == 'supprimer':
            appendHistorique(id_edl, '0')
            hideEDL(id_edl)
            flash("L'état des lieux à bien été supprimé", category='warning')
        elif action == 'defsupp':
            deleteEDL(id_edl)
            flash("L'état des lieux a été supprimé difinitevement", category='success')
        elif action == 'depart' or action == 'arrivee':
            if action == 'depart':
                occupe = False
            else:
                occupe = True
            id_new_edl = createEDL(form, occupe, id_logement, current_user.id)
            if action == "arrivee":
                appendHistorique(id_new_edl, '2')
            else:
                appendHistorique(id_new_edl, '3')
            flash("L'état des lieux à bien été pris en compte!", category="info")
    return redirect('etat_des_lieux', code=302)

# Redirection vers la page de modification des éléments
@views.route('modifier_elements', methods = ['GET', 'POST'])
@login_required
def modifier_elements():
    action = request.args.get('action')
    cat_query = select(CategorieElement)
    cat_keys = db.session.execute(cat_query.select()).fetchall()
    id_cat = 0
    element_query = select(Element).where(Element.id_categorie == id_cat)
    element_values = db.session.execute(element_query.select()).fetchall()
    if request.method == 'POST':
        form = request.form
        if action == 'reload':
            id_cat = request.form.get('id_categorie')
            element_query = select(Element).where(Element.id_categorie == id_cat)
            element_values = db.session.execute(element_query.select()).fetchall()
            return render_template('modifier_elements.html', active=activePage(3), id_cat = int(id_cat), user=current_user, cat_keys=cat_keys, Elements = element_values)
        if action == 'save':
            id_cat = request.args.get('id_categorie')
            updateElement(form, id_cat)
            element_query = select(Element).where(Element.id_categorie == id_cat)
            element_values = db.session.execute(element_query.select()).fetchall()
    return render_template('modifier_elements.html', active=activePage(3),  user=current_user, cat_keys=cat_keys, id_cat=int(id_cat), Elements = element_values)

# Redirection vers la page de modification des catégories
@views.route('modifier_categories', methods = ['GET', 'POST'])
@login_required
def modifier_categories():
    if request.method == 'POST':
        form = request.form
        updateCategorie(form)
    Categories = db.session.query(CategorieElement).all()
    return render_template('modifier_categories.html', active=activePage(4),  user=current_user, Categories=Categories)

# Redirection vers la page de modification des logements
@views.route('modifier_logements', methods = ['GET', 'POST'])
@login_required
def modifier_logements():
    if request.method == 'POST':
        form = request.form
        updateLogements(form)
    Logements = db.session.query(Logement, TypeLogement).where(Logement.type_logement == TypeLogement.id).all()
    TypesLogements = db.session.query(TypeLogement).all()
    return render_template('modifier_logements.html', active=activePage(5), TypesLogements=TypesLogements,  user=current_user, Logements=Logements)

# Redirection vers la page de modification des types de logement
@views.route('modification_types_logement', methods = ['GET', 'POST'])
@login_required
def modification_types_logement():
    if request.method == 'POST':
        form = request.form
        updateTypeLogement(form)
    Types = db.session.query(TypeLogement).all()
    return render_template('modification_types_logement.html', active=activePage(6),  user=current_user, Types=Types)

# Redirection vers la page de strucuration d'état des lieux
@views.route('structure_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def structure_etat_des_lieux():
    type_logement_query = select(TypeLogement)
    type_logement = db.session.execute(type_logement_query.select()).fetchall()
    type_edl, elements, Checks, Elements = [], [], dict(), dict()
    action = request.args.get('action')
    id_type = -1
    if request.method == 'POST':
        if action == 'reload':
            id_type = request.form.get('id_type_logement')
            element_query = select(CategorieElement, Element).where(Element.id_categorie == CategorieElement.id)
            elements = db.session.execute(element_query.select()).fetchall()
            type_edl_query = select(TypeEDL).where(TypeEDL.id_type_logement == id_type)
            type_edl = db.session.execute(type_edl_query.select()).fetchall()
            Checks = getStructure(id_type)
            for elm in elements:
                categorie = elm[1]
                if categorie not in Elements.keys():
                    Elements[categorie] = [elm[2:]]
                else:
                    Elements[categorie].append(elm[2:])
        elif action == 'save':
            id_type = request.args.get('id_type')
            element_query = select(CategorieElement, Element).where(Element.id_categorie == CategorieElement.id)
            elements = db.session.execute(element_query.select()).fetchall()
            type_edl_query = select(TypeEDL).where(TypeEDL.id_type_logement == id_type)
            type_edl = db.session.execute(type_edl_query.select()).fetchall()
            for elm in elements:
                categorie = elm[1]
                if categorie not in Elements.keys():
                    Elements[categorie] = [elm[2:]]
                else:
                    Elements[categorie].append(elm[2:])
            if 'save' in request.form.keys():
                updateStructure(id_type, request.form)
                Checks = getStructure(id_type)
            else:
                deleteStructure(id_type)
            flash('Modification enregistrée pour les prochains états des lieux!', category='success')
    elif id_type == -1:
        id_type = 0
        element_query = select(CategorieElement, Element).where(Element.id_categorie == CategorieElement.id)
        elements = db.session.execute(element_query.select()).fetchall()
        type_edl_query = select(TypeEDL).where(TypeEDL.id_type_logement == 0)
        type_edl = db.session.execute(type_edl_query.select()).fetchall()
        Checks = getStructure(0)
        for elm in elements:
            categorie = elm[1]
            if categorie not in Elements.keys():
                Elements[categorie] = [elm[2:]]
            else:
                Elements[categorie].append(elm[2:])
    return render_template('structure_etat_des_lieux.html', active=activePage(7),  user=current_user, type_logement=type_logement, Elements=Elements, type_edl=type_edl, id_type=int(id_type), Checks=Checks)

@views.route('historique', methods = ['GET', 'POST'])
@login_required
def historique():
    ListeEDL = sortEDLbyDate()
    return render_template('historique.html', active=activePage(2),  user=current_user, ListeEDL=ListeEDL, convertDateFormat=convertDateFormat)
# @views.route('/delete-note', methods=['POST'])
# def delete_note():
#     note= json.loads(request.data)
#     note_id = note['noteId']
#     note = Note.query.get(note_id)
#     if note:
#         if note.user_id == current_user.id:
#             db.session.delete(note)
#             db.session.commit()
#             return jsonify({})
        
# @views.route('/chambre', methods=['GET'])
# @login_required
# def redirect_cambre():
#     return render_template('chambre.html', user=current_user, chambres = Logement.query.all())

# @views.route('/liste_edl', methods=['GET', 'POST'])
# @login_required
# def liste_edl():
#     logement = request.args.get('id')
#     return render_template('liste_edl.html', user=current_user, edl = listeEDL(logement))

# @views.route('/edl', methods=['GET', 'POST'])
# @login_required
# def edl():
#     id_edl = request.args.get('id')
#     if request.method == 'POST':
#         modifEDL(id_edl, request.form)
#         flash('Tout est OK!', category="success")
#         return render_template('home.html', user=current_user, logement = Logement.query.all())
#     return render_template('edl.html', user=current_user,type = listCritere(id_edl)[0], Data = listCritere(id_edl)[1])        