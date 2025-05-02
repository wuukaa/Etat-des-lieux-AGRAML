from flask import Blueprint, render_template, flash, redirect, make_response, url_for
from flask_login import login_required, current_user
from ..models import TypeLogement
from .. import db
import jinja2
import pdfkit
from ..functions import *
import os

dir = os.path.dirname(__file__)

edl = Blueprint('edl', __name__, template_folder='../templates/edl')


def genererFichierEDL(id_edl):
    template_directory = f"{dir}/../templates/edl/"
    output_directory = f"{dir}/../static/storage/pdf/"

    template_loader = jinja2.FileSystemLoader(template_directory)
    template_env = jinja2.Environment(loader=template_loader)

    EDLInformation = getEDLInformation(id_edl, False)
    Etats = getEtat(id_edl)
    Images = recuperationImages(id_edl)
    LongueurListeImage = range(len(Images))

    image_dir = dir[:-11]
    template = template_env.get_template('template_edl_pdf_wkhtmltopdf.html')
    output_html = template.render(image_dir=image_dir, url_for=url_for, Etats=Etats, EDLInformation=EDLInformation, Images=Images, id_edl=id_edl, tempsHTMLVersHumain=tempsHTMLVersHumain, I=LongueurListeImage, enumerate=enumerate)

    path = "/usr/bin/wkhtmltopdf"

    config = pdfkit.configuration(wkhtmltopdf=path)
    pdfkit.from_string(output_html, output_directory + f'etat_des_lieux_{id_edl}.pdf', configuration=config, options={"enable-local-file-access": None})

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
        etat = request.form.get('0.action')
        id_new_edl = createEDL(form, etat, id_logement, current_user.id, ListeImageNom)
        rajoutInterventions(id_new_edl)
        if etat == "arrivee":
            appendHistorique(id_new_edl, '2')
        elif etat == "depart":
            appendHistorique(id_new_edl, '3')
        id_edl = id_new_edl
        genererFichierEDL(id_edl)
        flash("L'état des lieux à bien été pris en compte!", category="info")
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
    fichier_edl = f'{dir}/../static/storage/pdf/etat_des_lieux_{id_edl}.pdf'
    if not os.path.isfile(fichier_edl):
        genererFichierEDL(id_edl)
    return render_template('template_edl_pdf.html', fichier_edl=f'etat_des_lieux_{id_edl}.pdf', active=activePage(2),  user=current_user, Etats=Etats, EDLInformation=EDLInformation, Images=Images, id_edl=id_edl, tempsHTMLVersHumain=tempsHTMLVersHumain, I=LongueurListeImage, enumerate=enumerate)