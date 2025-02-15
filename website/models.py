from . import db
from flask_login import UserMixin
from sqlalchemy import func, select

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150))
    prenom = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(2000))
    active = db.Column(db.Boolean)

class Activation(db.Model):
    __tablename__ = "activation"
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(100))

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
    prix = db.Column(db.Float())

class EDL(db.Model):
    __tablename__ = "edl"
    id = db.Column(db.Integer, primary_key=True)
    id_logement = db.Column(db.Integer, db.ForeignKey('logement.id'))
    effectue_par = db.Column(db.Integer, db.ForeignKey('user.id'))
    occupation = db.Column(db.Boolean)
    date = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    mail = db.Column(db.String(200))

class Valeur(db.Model):
    __tablename__ = "valeur"
    id = db.Column(db.Integer, primary_key=True)
    id_edl = db.Column(db.Integer, db.ForeignKey('edl.id'))
    id_element = db.Column(db.Integer, db.ForeignKey('element.id'))
    valeur = db.Column(db.Integer, default=2)
    observation = db.Column(db.String(1000))

class TypeEDL(db.Model):
    __tablename__ = "type_edl"
    id = db.Column(db.Integer, primary_key=True)
    id_type_logement = db.Column(db.String(50))
    id_element = db.Column(db.Integer, db.ForeignKey('element.id'))
    actif = db.Column(db.Boolean)