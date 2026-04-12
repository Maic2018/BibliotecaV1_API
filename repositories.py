from models import db, User, Book, Borrow

class UserRepository:
    def get_by_username(self, username):
        return User.query.filter_by(username=username).first()

class BookRepository:
    def get_all(self):
        return Book.query.all()
        
    def get_by_id(self, book_id):
        # Utiliza o get_or_404 do Flask-SQLAlchemy para já tratar a ausência
        return Book.query.get_or_404(book_id)
        
    def add(self, book):
        db.session.add(book)
        db.session.commit()
        return book
        
    def update(self):
        db.session.commit()
        
    def delete(self, book):
        db.session.delete(book)
        db.session.commit()

class BorrowRepository:
    def get_active_by_user(self, user_id):
        return Borrow.query.filter_by(user_id=user_id, returned=False).all()
        
    def get_active_by_book(self, book_id):
        return Borrow.query.filter_by(book_id=book_id, returned=False).first()
        
    def get_specific_active_borrow(self, user_id, book_id):
        return Borrow.query.filter_by(user_id=user_id, book_id=book_id, returned=False).first()
        
    def get_all_active(self):
        return Borrow.query.filter_by(returned=False).all()
        
    def add(self, borrow):
        db.session.add(borrow)
        db.session.commit()
        return borrow
        
    def update(self):
        db.session.commit()
