from flask import Blueprint, render_template, request, flash, redirect, send_file
from flask_login import login_required, current_user
from ..models import CategorieElement, Element, TypeLogement, TypeEDL, Logement, User, EDL, Historique
from .. import db
from sqlalchemy import select
from ..functions import *

views = Blueprint('views', __name__, template_folder='../templates/views')

# Redirection vers la page d'accueil depuis la racine
@views.route('/accueil', methods = ['GET'])
@login_required
def accueil():
    return render_template('accueil.html', user=current_user, active=activePage(0))

# Redirection vers la page à propos depuis la racine
@views.route('/', methods = ['GET'])
def home():
    return render_template('about.html', user=current_user, active=activePage(14))

# Redirection vers la page à propos
@views.route('/about', methods = ['GET'])
def home_bis():
    return render_template('about.html', user=current_user, active=activePage(14))

@views.route('historique', methods = ['GET', 'POST'])
@login_required
def historique():
    i_page_pagination = request.args.get('pagination')
    if i_page_pagination is None:
        i_page_pagination = 0
    else:
        i_page_pagination = int(i_page_pagination)
    ListeEDL, ListeBoutton = pagination(getHistoriqueEDL(), i_page_pagination, current_user.max_item_par_page)
    return render_template('historique.html', active=activePage(2),  user=current_user, ListeEDL=ListeEDL, convertDateFormat=tempsHTMLVersHumain, ListeBoutton=ListeBoutton)  

@views.route('/interventions/')
@login_required
def intervention():
    i_page_pagination = request.args.get('pagination')
    if i_page_pagination is None:
        i_page_pagination = 0
    else:
        i_page_pagination = int(i_page_pagination)
    ListeInterventions, ListeBoutton = pagination(getListeInterventions(False), i_page_pagination, current_user.max_item_par_page)
    return render_template('intervention.html', active=activePage(13), user=current_user, ListeInterventions=ListeInterventions, ListeBoutton=ListeBoutton)

@views.route('/interventions/<option>/<intervention>/')
@login_required
def operationIntervention(option: str, intervention: str):
    id_intervention = intervention.split('-')[1]
    if option == 'repare':
        interventiondb = db.session.query(Intervention).filter(Intervention.id == id_intervention).first()
        interventiondb.etat = 1
        db.session.commit()
    return redirect('/interventions/', code=302)

@views.route('/interventions/journal/')
@login_required
def journalIntervention():
    i_page_pagination = request.args.get('pagination')
    if i_page_pagination is None:
        i_page_pagination = 0
    else:
        i_page_pagination = int(i_page_pagination)
    JournalIntervention, ListeBoutton = pagination(getListeInterventions(True), i_page_pagination, current_user.max_item_par_page)
    return render_template('journal_intervention.html', active=activePage(13), user=current_user, JournalIntervention=JournalIntervention, ListeBoutton=ListeBoutton)