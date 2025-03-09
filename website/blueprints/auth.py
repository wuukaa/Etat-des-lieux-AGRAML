from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..functions import passWdCheck, userNmCheck, activePage, getActivationCodeNewUser
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if user and user.active:
            if check_password_hash(user.password, password):
                flash('Connexion réussite!', category = 'success')
                login_user(user, remember = True)
                return redirect(url_for('views.home'))
            else:
                flash('Mauvais identifiants ou compte pas activé', category = 'error')
        else:
            flash('''Tu n'es pas dans la base de donnée''', category = 'error')


    return render_template('login.html', active=activePage(11), user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        username = request.form.get('user')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        signature = request.form.get('signature')
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
        elif len(nom) == 0 or len(prenom) == 0:
            flash('Veuillez renseigner ton nom et/ou ton prénom.', category='error')
        else:
            new_user = User(mode='dark',
                            accent_color='rgb(6, 159, 47)',
                            signature=signature,
                            email = email,
                            username = username,
                            password = generate_password_hash(password1),
                            nom = nom,
                            prenom = prenom,
                            active=False,
                            max_item_par_page = 10)
            db.session.add(new_user)
            db.session.commit()
            flash('Demande envoyée', category = 'info')
            return redirect(url_for('auth.login'))
    return render_template('sign_up.html', active=activePage(12), user = current_user)

@auth.route('/confirmation', methods=['GET', 'POST'])
@login_required
def confirmation():
    action = request.args.get('action')
    id = request.args.get('id_user')
    print(action, id)
    if action == 'accepte':
        user = db.session.query(User).filter(User.id == id).first()
        user.active = True
        flash("Demande d'inscription confirmée", category='info')
    elif action == 'rejet':
        user = db.session.query(User).filter(User.id == id).first()
        db.session.delete(user)
        flash("Demande d'inscription rejetée", category='info')
    db.session.commit()
    return redirect('confirmation.html')

@auth.route('gestion_utilisateurs', methods=['GET', 'POST'])
@login_required
def gestion_utilisateur():
    ActivationCodeNewUser = getActivationCodeNewUser()
    return render_template('gestion_utilisateurs.html', user=current_user, active=activePage(9), ActivationCodeNewUser=ActivationCodeNewUser)

@auth.route('parametres', methods=['GET','POST'])
@login_required
def parametres():
    if current_user.mode == 'dark':
        ListeThemes = ['rgb(28, 70, 107)', 'rgb(129, 22, 182)', 'rgb(161, 18, 32)', 'rgb(181, 115, 3)', 'rgb(6, 159, 47)']
    else:
        ListeThemes = ['rgb(140, 192, 239)', 'rgb(201, 141, 232)', 'rgb(239, 121, 133)', 'rgb(245, 204, 134)', 'rgb(135, 248, 165)']
    if request.method == 'POST':
        arg = request.args.get('type')
        form = request.form
        if arg == 'par':
            current_user.mode = form['mode']
            if current_user.mode == 'dark':
                ListeThemes = ['rgb(28, 70, 107)', 'rgb(129, 22, 182)', 'rgb(161, 18, 32)', 'rgb(181, 115, 3)', 'rgb(6, 159, 47)']
            else:
                ListeThemes = ['rgb(140, 192, 239)', 'rgb(201, 141, 232)', 'rgb(239, 121, 133)', 'rgb(245, 204, 134)', 'rgb(135, 248, 165)']
            current_user.accent_color = ListeThemes[int(form['accent-color'])]
            db.session.commit()
        if arg == 'compte':
            current_user.email = form['email']
            current_user.nom = form['nom']
            current_user.prenom = form['prenom']
            current_user.signature = form['signature']
            current_user.max_item_par_page = form['max_item_par_page']
            db.session.commit()
    i_accent = 0
    for color in ListeThemes:
        if color == current_user.accent_color:
            break
        i_accent += 1
    return render_template('parametres.html', user=current_user, active=activePage(8), ListeThemes=ListeThemes, i_accent=i_accent)
