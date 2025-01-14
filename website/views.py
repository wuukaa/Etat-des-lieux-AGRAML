from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    notes = Note.query.filter_by(user_id=current_user.id)
    if request.method == 'POST':
        note = request.form.get('note')
        if len(note) <= 1:
            flash('Note trop courte!', category='error')
        else:
            flash('Note ajoutée', category='success')
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
    return render_template('home.html', user=current_user, notes=notes)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note= json.loads(request.data)
    note_id = note['noteId']
    note = Note.query.get(note_id)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            return jsonify({})