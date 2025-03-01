from flask import Blueprint, render_template, request, flash, redirect, send_file
from flask_login import login_required, current_user
from ..models import CategorieElement, Element, TypeLogement, TypeEDL, Logement, User, EDL, Historique
from .. import db
from sqlalchemy import select
from .functions import *

edition = Blueprint('edition', __name__, template_folder='../templates/edition')

# Redirection vers la page de modification d'état des lieux
@edition.route('/modification_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def modification_etat_des_lieux():
    id_edl = request.form.get('id_edl')
    id_logement = request.args.get('id_logement')
    if id_edl == 'nouveau':
        type_logement = db.session.query(Logement).filter(Logement.id == id_logement).first().type_logement
        Etats = getTemplateEtatDesLieux(type_logement)
        EDLInformation = getTemplateEtatDesLieuxInformation(id_logement, current_user)
        edl_existant = True
    else:
        # EDL existant
        Etats = getEtat(id_edl)
        EDLInformation = getEDLInformation(id_edl)
        edl_existant = False
    return render_template('modification_etat_des_lieux.html', active=activePage(1),  user=current_user,  Etats = Etats, id_edl = id_edl, edl_existant=edl_existant, EDLInformation=EDLInformation)

# Redirection vers la page de modification des éléments
@edition.route('modifier_elements', methods = ['GET', 'POST'])
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
@edition.route('modifier_categories', methods = ['GET', 'POST'])
@login_required
def modifier_categories():
    if request.method == 'POST':
        form = request.form
        updateCategorie(form)
    Categories = db.session.query(CategorieElement).all()
    return render_template('modifier_categories.html', active=activePage(4),  user=current_user, Categories=Categories)

# Redirection vers la page de modification des logements
@edition.route('modifier_logements', methods = ['GET', 'POST'])
@login_required
def modifier_logements():
    if request.method == 'POST':
        form = request.form
        updateLogements(form)
    Logements = db.session.query(Logement, TypeLogement).where(Logement.type_logement == TypeLogement.id).all()
    TypesLogements = db.session.query(TypeLogement).all()
    return render_template('modifier_logements.html', active=activePage(5), TypesLogements=TypesLogements,  user=current_user, Logements=Logements)

# Redirection vers la page de modification des types de logement
@edition.route('modification_types_logement', methods = ['GET', 'POST'])
@login_required
def modification_types_logement():
    if request.method == 'POST':
        form = request.form
        updateTypeLogement(form)
    Types = db.session.query(TypeLogement).all()
    return render_template('modification_types_logement.html', active=activePage(6),  user=current_user, Types=Types)

# Redirection vers la page de strucuration d'état des lieux
@edition.route('structure_etat_des_lieux', methods = ['GET', 'POST'])
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