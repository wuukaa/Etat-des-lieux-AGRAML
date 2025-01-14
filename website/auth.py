from flask import Blueprint, render_template, request, flash, redirect, url_for
from .functions import passWdCheck, userNmCheck
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)
        user = User.query.filter_by(username = username).first()
        print(user)
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category = 'success')
                login_user(user, remember = True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect IDs', category = 'error')
        else:
            flash('''Tu n'es pas dans la base de donnée''', category = 'error')


    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        username = request.form.get('user')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        dbUser = User.query.filter_by(username = username).first()
        dbEmail = User.query.filter_by(email = email).first()
        if dbUser:
            flash('Tu es déjà inscrit', category = 'error')
        elif dbEmail:
            flash('Tu es déjà inscrit', category = 'error')
        elif len(email) < 4:
            flash('Adresse email incorrecte', category = 'error')
        elif not userNmCheck(username):
            flash('''Nom d'utilisateur non accepté''', category = 'error')
        elif password1 != password2:
            flash('Mots de passe différents', category = 'error')
        elif not passWdCheck(password1):
            flash('Non respect des règles de mot de passe', category = 'error')
        else:
            new_user = User(email = email, username = username, password = generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash('Demande envoyée', category = 'success')
            return redirect(url_for('views.home'))
    return render_template('sign_up.html', user = current_user)