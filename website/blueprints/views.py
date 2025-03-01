from flask import Blueprint, render_template, request, flash, redirect, send_file
from flask_login import login_required, current_user
from ..models import CategorieElement, Element, TypeLogement, TypeEDL, Logement, User, EDL, Historique
from .. import db
from sqlalchemy import select
from .functions import *

views = Blueprint('views', __name__, template_folder='../templates/views')

# Redirection vers la page d'accueil depuis la racine
@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    return render_template('accueil.html', user=current_user, active=activePage(0))

# Redirection vers la page d'accueil
@views.route('/accueil', methods = ['GET'])
def accueil():
    return render_template('accueil.html', user=current_user, active=activePage(0))

@views.route('historique', methods = ['GET', 'POST'])
@login_required
def historique():
    i_page_pagination = request.args.get('pagination')
    if i_page_pagination is None:
        i_page_pagination = 0
    else:
        i_page_pagination = int(i_page_pagination)
    ListeEDL, ListeBoutton = pagination(sortEDLbyDate(), i_page_pagination, current_user.max_item_par_page)
    return render_template('historique.html', active=activePage(2),  user=current_user, ListeEDL=ListeEDL, convertDateFormat=convertDateFormat, ListeBoutton=ListeBoutton)  

@views.route('interventions')
@login_required
def intervention():
    return render_template('intervention.html', active=activePage(13), user=current_user)