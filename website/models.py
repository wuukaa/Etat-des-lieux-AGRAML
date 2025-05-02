from . import db
from flask_login import UserMixin
from sqlalchemy import func, select

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)
    nom = db.Column(db.String(150))
    prenom = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(2000))
    mode = db.Column(db.String(10))
    accent_color = db.Column(db.String(10))
    signature = db.Column(db.Text)
    max_item_par_page = db.Column(db.Integer)

class Logement(db.Model):
    __tablename__ = "logement"
    id = db.Column(db.Integer, primary_key=True)
    batiment = db.Column(db.String(3))
    etage = db.Column(db.Integer)
    numero = db.Column(db.String(4))
    type_logement = db.Column(db.Integer)

class TypeLogement(db.Model):
    __tablename__ = "type_logement"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))

class CategorieElement(db.Model):
    __tablename__ = "categorie_element"
    id = db.Column(db.Integer, primary_key=True)
    intitule = db.Column(db.String(100))

class Element(db.Model):
    __tablename__ = "element"
    id = db.Column(db.Integer, primary_key=True)
    id_categorie = db.Column(db.Integer, db.ForeignKey('categorie_element.id'))
    intitule = db.Column(db.String(100))

class EDL(db.Model):
    __tablename__ = "edl"
    id = db.Column(db.Integer, primary_key=True)
    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id'))
    effectue_par = db.Column(db.Integer, db.ForeignKey('user.id'))
    etat = db.Column(db.String(20))
    date = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    mail = db.Column(db.String(200))
    signature = db.Column(db.Text)

class Valeur(db.Model):
    __tablename__ = "valeur"
    id = db.Column(db.Integer, primary_key=True)
    id_edl = db.Column(db.Integer, db.ForeignKey('edl.id'))
    id_element = db.Column(db.Integer, db.ForeignKey('element.id'))
    valeur = db.Column(db.Integer, default=2)
    observation = db.Column(db.String(1000))
    facturation = db.Column(db.Boolean)

class TypeEDL(db.Model):
    __tablename__ = "type_edl"
    id = db.Column(db.Integer, primary_key=True)
    id_type_logement = db.Column(db.String(50))
    id_element = db.Column(db.Integer, db.ForeignKey('element.id'))
    actif = db.Column(db.Boolean)

class Historique(db.Model):
    __tablename__ = "historique"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    id_edl = db.Column(db.Integer, db.ForeignKey('edl.id'))
    action = db.Column(db.Integer)

class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    nom_image = db.Column(db.String)
    id_edl = db.Column(db.Integer, db.ForeignKey('edl.id'))

class Intervention(db.Model):
    __tablename__ = "intervention"
    id = db.Column(db.Integer, primary_key=True)
    id_valeur = db.Column(db.Integer, db.ForeignKey('valeur.id'), unique=True)
    etat = db.Column(db.Integer)