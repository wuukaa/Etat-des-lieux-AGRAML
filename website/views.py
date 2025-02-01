from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Logement
from sqlalchemy import select
from . import db
from .functions import listCritere

views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', user=current_user, logement = Logement.query.all())

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
        
@views.route('/chambre', methods=['GET'])
@login_required
def redirect_cambre():
    return render_template('chambre.html', user=current_user, chambres = Logement.query.all())

@views.route('/edl', methods=['GET', 'POST'])
@login_required
def edl():
    chambre = request.args.get('id')
    if request.method == 'POST':
        print(request.form)
        flash('Tout est OK!', category="success")
        return render_template('home.html', user=current_user, logement = Logement.query.all())
    if chambre != None:
        listeCritere = listCritere(chambre)[0]
        Data = listCritere(chambre)[1]
        return render_template('edl.html', user=current_user, chambre=chambre, type = listeCritere, Data = Data)        