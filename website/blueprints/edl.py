from flask import Blueprint, render_template, flash, redirect, make_response
from flask_login import login_required, current_user
from ..models import TypeLogement
from .. import db
from ..functions import *
import os

dir = os.path.dirname(__file__)

edl = Blueprint('edl', __name__, template_folder='../templates/edl')

# Redirection vers la page d'état des lieux
@edl.route('recherche', methods = ['GET', 'POST'])
@login_required
def recherche():
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
        form = {'batiment':request.cookies.get('batiment') if request.cookies.get('batiment') else '-',
            'etage':request.cookies.get('etage') if request.cookies.get('etage') else '-',
            'type':request.cookies.get('type') if request.cookies.get('type') else '-',
            'prenom':request.cookies.get('prenom') if request.cookies.get('prenom') else '',
            'nom':request.cookies.get('nom') if request.cookies.get('nom') else ''}
        ListeLogements = searchLogements(form)
    ListeLogements, ListeBoutton = pagination(ListeLogements, i_page, current_user.max_item_par_page)
    resp = make_response(render_template('recherche.html', form=form, active=activePage(1), len=len, str=str, user=current_user, TypesLogements=TypesLogements, ListeLogements=ListeLogements, ListeBoutton=ListeBoutton))
    resp.set_cookie('batiment', form['batiment'])
    resp.set_cookie('etage', form['etage'])
    resp.set_cookie('type', form['type'])
    resp.set_cookie('prenom', form['prenom'])
    resp.set_cookie('nom', form['nom'])
    return resp

# Redirection vers la page de la liste des états des lieux pour un logement
@edl.route('recherche/<logement>/', methods = ['GET', 'POST'])
@login_required
def liste_etat_des_lieux(logement):
    # On récupère l'identifiant associé au logement
    id_logement = logement.split('-')[1]
    try:
        edl = getListeEtatDesLieux(id_logement)
    except:
        edl = None

    return render_template('liste_etat_des_lieux.html', active=activePage(1),  id_logement=id_logement, user=current_user, edl=edl)

# Pour récupérer les détails des états des lieux
@edl.route('requete_etat_des_lieux', methods = ['POST', 'GET'])
@login_required
def requete_etat_des_lieux():
    if request.method == 'POST':
        files = request.files
        form = request.form
        ListeImageNom = sauvegardeImages(files)
        id_logement = request.args.get('id_logement')
        id_edl = request.args.get('id_edl')
        action = request.form.get('0.action')
        if action == 'depart' or action == 'arrivee':
            if action == 'depart':
                occupe = False
            else:
                occupe = True
            id_new_edl = createEDL(form, occupe, id_logement, current_user.id, ListeImageNom)
            rajoutInterventions(id_new_edl)
            if action == "arrivee":
                appendHistorique(id_new_edl, '2')
            else:
                appendHistorique(id_new_edl, '3')
            id_edl = id_new_edl
            EDLInformation = getEDLInformation(id_edl, True)
            Etats = getEtat(id_edl)
            flash("L'état des lieux à bien été pris en compte!", category="info")

    #html = render_template('template_edl_pdf.html', active=activePage(1),  user=current_user,  id_edl = id_edl, Etats=Etats, EDLInformation=EDLInformation)
    #convert_html_file_to_pdf(html, 'pdf.pdf')
    #return webbrowser.open_new_tab(send_file('C:/Users/Lucas/Documents/GitHub/Etat-des-lieux-AGRAML/pdf.pdf'))
    return redirect('recherche', code=302)

@edl.route('/etat_des_lieux/<option>/<edl>/')
@login_required
def requete(option: str, edl: str):
    id_edl = edl.split('-')[1]
    if option == "supprimer":
        deleteEDL(id_edl)
    return redirect('/historique', 302)

@edl.route('/consultation/<edl>/')
@login_required
def consultation(edl: str):
    id_edl = edl.split('-')[1]
    EDLInformation = getEDLInformation(id_edl, False)
    Etats = getEtat(id_edl)
    Images = recuperationImages(id_edl)
    LongueurListeImage = range(len(Images))
    return render_template('template_edl_pdf.html', active=activePage(2),  user=current_user, Etats=Etats, EDLInformation=EDLInformation, Images=Images, id_edl=id_edl, tempsHTMLVersHumain=tempsHTMLVersHumain, I=LongueurListeImage, enumerate=enumerate)

