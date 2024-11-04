from . import db
from datetime import datetime
from flask_login import UserMixin
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash

# Table d'association pour la relation many-to-many entre Commande et Plat
commande_plat = db.Table('commande_plat',
    db.Column('commande_id', db.Integer, db.ForeignKey('commande.id'), primary_key=True),
    db.Column('plat_id', db.Integer, db.ForeignKey('plat.id'), primary_key=True)
)

class Plat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    items = db.Column(db.Text, nullable=False)  # Vous pouvez utiliser JSON pour stocker les articles
    archived = db.Column(db.Boolean, default=False)
    plats = db.relationship('Plat', secondary=commande_plat, lazy='subquery',
        backref=db.backref('commandes', lazy=True))
    
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        # Utilisez le hachage par défaut (PBKDF2 avec SHA-256)
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))