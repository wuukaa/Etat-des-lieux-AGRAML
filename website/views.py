from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Logement
from . import db
from .functions import getLogements, getEtat_des_lieux, getValeurs

views = Blueprint('views', __name__)

# Redirection vers la page d'accueil depuis la racine
@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    return render_template('accueil.html', user=current_user)

# Redirection vers la page d'accueil
@views.route('/accueil', methods = ['GET'])
def accueil():
    return render_template('accueil.html', user=current_user)

# Redirection vers la page d'état des lieux
@views.route('/etat_des_lieux', methods = ['GET'])
@login_required
def etat_des_lieux():
    # On récupère l'identifiant associé au bouton du menu
    # 0 -> Chambre , 1 -> Studio, 2 -> Collocation
    type_logement = request.args.get('id')
    Dict_logements = dict()
    if type_logement is not None:
        print(id)
        Dict_logements = getLogements(int(type_logement))
    else:
        flash('Il y a une erreur de redirection, utilise la barre de navigation!', category='error')
    return render_template('liste_logements.html', user=current_user, Dict_logements = Dict_logements)

# Redirection vers la page de la liste des états des lieux pour un logement
@views.route('/liste_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def liste_etat_des_lieux():
    # On récupère l'identifiant associé au logement
    id_logement = request.form.get('id_logement')
    Dict_edl = dict()
    if id_logement is not None:
        Dict_edl = getEtat_des_lieux(id_logement)
    else:
        flash('Il y a une erreur de redirection, utilise la barre de navigation!', category='error')
    return render_template('liste_etat_des_lieux.html', user=current_user, Dict_edl = Dict_edl)

# Redirection vers la page de modification d'état des lieux
@views.route('/modification_etat_des_lieux', methods = ['GET', 'POST'])
@login_required
def modification_etat_des_lieux():
    id_edl = request.form.get('id_edl')
    Valeurs = getValeurs(id_edl)
    return render_template('modification_etat_des_lieux.html', user=current_user, Valeurs = Valeurs, id_edl = id_edl)

@views.route('requete_etat_des_lieux', methods = ['POST', 'GET'])
@login_required
def requete_etat_des_lieux():
    if request.method == 'POST':
        id_edl = request.args.get('id_edl')
        if request.form.get('0.action') == 'modification':
            print(request.form)
            print(id_edl)
            flash('Les données ont été modifiés dans la base de données', category='success')
        return render_template('accueil.html', user=current_user)

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