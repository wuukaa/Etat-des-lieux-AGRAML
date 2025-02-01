from . import db
from flask_login import UserMixin
from sqlalchemy import func, select

class Logement(db.Model):
    __tablename__ = "logement"
    numero = db.Column(db.String(10), unique=True, primary_key=True)
    type_logement = db.Column(db.Integer)

class SALLE_DE_VIE(db.Model):
    __tablename__ = "salle_de_vie"
    id = db.Column(db.Integer, primary_key=True)
    niveau = db.Column(db.Integer)

class KITCHENETTE(db.Model):
    __tablename__ = "kitchenette"
    id = db.Column(db.Integer, primary_key=True)
    niveau = db.Column(db.Integer)

class CHAMBRE(db.Model):
    __tablename__ = "chambre"
    id = db.Column(db.Integer, primary_key=True)
    lit = db.Column(db.Integer)
    table = db.Column(db.Integer)
    mur = db.Column(db.Integer)
    matelat = db.Column(db.Integer)

class SALLE_DE_BAIN(db.Model):
    __tablename__ = "salle_de_bain"
    id = db.Column(db.Integer, primary_key=True)
    niveau = db.Column(db.Integer)

class WC(db.Model):
    __tablename__ = "wc"
    id = db.Column(db.Integer, primary_key=True)
    niveau = db.Column(db.Integer)

class AUTRE(db.Model):
    __tablename__ = "autre"
    id = db.Column(db.Integer, primary_key=True)
    niveau = db.Column(db.Integer)

class EDL(db.Model):
    __tablename__ = "edl"
    id = db.Column(db.Integer, primary_key=True)
    entree_sortie = db.Column(db.Boolean)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    mail = db.Column(db.String(200))
    date = db.Column(db.String(100))
    id_logement = db.Column(db.String(50), db.ForeignKey('logement.numero'))
    id_sdv = db.Column(db.Integer, db.ForeignKey('salle_de_vie.id'))
    id_k = db.Column(db.Integer, db.ForeignKey('kitchenette.id'))
    id_c = db.Column(db.Integer, db.ForeignKey('chambre.id'))
    id_wc = db.Column(db.Integer, db.ForeignKey('wc.id'))
    id_sdb = db.Column(db.Integer, db.ForeignKey('salle_de_bain.id'))
    id_a = db.Column(db.Integer, db.ForeignKey('autre.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150))
    prenom = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(2000))