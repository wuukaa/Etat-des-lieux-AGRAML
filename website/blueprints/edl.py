from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
from ..models import TypeLogement
from .. import db
from .functions import *

edl = Blueprint('edl', __name__, template_folder='../templates/edl')

# Redirection vers la page d'état des lieux
@edl.route('etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def etat_des_lieux():
    TypesLogements = db.session.query(TypeLogement).all()
    # Si on a une requete de filtre
    i_page = request.args.get('pagination')
    if i_page is None:
        i_page = 0
    else:
        i_page = int(i_page)
    if request.method == 'POST':
        form = request.form
        ListeLogements = searchLogements(form)
    else:
        form = {'batiment':'-',
            'etage':'-',
            'type':'-',
            'prenom': '',
            'nom': ''}
        ListeLogements = searchLogements(form)
    ListeLogements, ListeBoutton = pagination(ListeLogements, i_page, current_user.max_item_par_page)
    return render_template('liste_logements.html', form=form, active=activePage(1), len=len, str=str, user=current_user, TypesLogements=TypesLogements, ListeLogements=ListeLogements, ListeBoutton=ListeBoutton)

# Redirection vers la page de la liste des états des lieux pour un logement
@edl.route('liste_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def liste_etat_des_lieux():
    # On récupère l'identifiant associé au logement
    id_logement = request.form.get('id_logement')
    i_page = request.args.get('pagination')
    if i_page is None:
        i_page = 0
    else:
        i_page = int(i_page)
        id_logement = request.args.get('id_logement')
    ListeEtatDesLieux, ListeBoutton = pagination(getListeEtatDesLieux(id_logement), i_page, current_user.max_item_par_page)
    return render_template('liste_etat_des_lieux.html', active=activePage(1),  id_logement=id_logement, user=current_user, ListeEtatDesLieux=ListeEtatDesLieux, ListeBoutton=ListeBoutton)

# Pour récupérer les détails des états des lieux
@edl.route('requete_etat_des_lieux', methods = ['POST', 'GET'])
@login_required
def requete_etat_des_lieux():
    if request.method == 'POST':
        id_logement = request.args.get('id_logement')
        id_edl = request.args.get('id_edl')
        form = request.form
        print(form)
        action = request.form.get('0.action')
        if action == 'modification':
            appendHistorique(id_edl, '1')
            editEDL(form, id_edl)
            flash('Les données ont été modifiés dans la base de données', category='warning')
            EDLInformation = getEDLInformation(id_edl)
            Etats = getEtat(id_edl)
        elif action == 'supprimer':
            appendHistorique(id_edl, '0')
            hideEDL(id_edl)
            flash("L'état des lieux à bien été supprimé", category='warning')
            EDLInformation = getEDLInformation(id_edl)
            Etats = getEtat(id_edl)
        elif action == 'defsupp':
            deleteEDL(id_edl)
            flash("L'état des lieux a été supprimé difinitevement", category='success')
            EDLInformation = dict()
            Etats = dict()
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
            id_edl = id_new_edl
            EDLInformation = getEDLInformation(id_edl)
            Etats = getEtat(id_edl)
            flash("L'état des lieux à bien été pris en compte!", category="info")

    #html = render_template('template_edl_pdf.html', active=activePage(1),  user=current_user,  id_edl = id_edl, Etats=Etats, EDLInformation=EDLInformation)
    #convert_html_file_to_pdf(html, 'pdf.pdf')
    #return webbrowser.open_new_tab(send_file('C:/Users/Lucas/Documents/GitHub/Etat-des-lieux-AGRAML/pdf.pdf'))
    return redirect('etat_des_lieux', code=302)
