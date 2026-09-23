from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    qtd = db.Column(db.Integer, default=1)
    image_url = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'qtd': self.qtd,
            'is_available': self.qtd > 0,
            'image_url': self.image_url
        }

class LibraryUnit(db.Model):
    """Unidade física da biblioteca. O endereço é preenchido
    automaticamente a partir do CEP, consultando a API externa ViaCEP."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(200), nullable=True)
    bairro = db.Column(db.String(120), nullable=True)
    cidade = db.Column(db.String(120), nullable=True)
    uf = db.Column(db.String(2), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'uf': self.uf,
        }


class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    returned = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('borrows', cascade="all, delete-orphan", lazy=True))
    book = db.relationship('Book', backref=db.backref('borrows', cascade="all, delete-orphan", lazy=True))
