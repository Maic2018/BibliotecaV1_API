from werkzeug.security import check_password_hash
from models import Book, Borrow

class AuthService:
    def __init__(self, user_repository):
        self.user_repo = user_repository
        
    def authenticate(self, username, password):
        user = self.user_repo.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

class BookService:
    def __init__(self, book_repository, borrow_repository):
        self.book_repo = book_repository
        self.borrow_repo = borrow_repository
        
    def get_all_books(self):
        books = self.book_repo.get_all()
        return [book.to_dict() for book in books]
        
    def add_book(self, data):
        if not data or not data.get('title') or not data.get('author'):
            return None, "Dados incompletos"
            
        qtd = data.get('qtd', 1)
        image_url = data.get('image_url', '')
        new_book = Book(title=data['title'], author=data['author'], qtd=qtd, image_url=image_url)
        
        self.book_repo.add(new_book)
        return new_book.to_dict(), None
        
    def edit_book(self, book_id, data):
        book = self.book_repo.get_by_id(book_id)
        
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'qtd' in data:
            book.qtd = data['qtd']
        if 'image_url' in data:
            book.image_url = data['image_url']
            
        self.book_repo.update()
        return book.to_dict(), None
        
    def delete_book(self, book_id):
        book = self.book_repo.get_by_id(book_id)
        
        active_borrows = self.borrow_repo.get_active_by_book(book.id)
        if active_borrows:
            return False, "O livro possui empréstimos ativos e não pode ser removido."
            
        self.book_repo.delete(book)
        return True, None

class BorrowService:
    def __init__(self, book_repository, borrow_repository):
        self.book_repo = book_repository
        self.borrow_repo = borrow_repository
        
    def borrow_book(self, user, book_id):
        book = self.book_repo.get_by_id(book_id)
        
        if book.qtd <= 0:
            return None, "Não há exemplares disponíveis deste livro"
        
        if not user.is_admin:
            active_borrows = self.borrow_repo.get_active_by_user(user.id)
            if len(active_borrows) >= 2:
                return None, "Você já atingiu o limite máximo de 2 livros emprestados simultaneamente."
                
        existing_borrow = self.borrow_repo.get_specific_active_borrow(user.id, book_id)
        if existing_borrow:
            return None, "Você já tem uma cópia deste livro emprestada."
            
        new_borrow = Borrow(user_id=user.id, book_id=book.id)
        book.qtd -= 1
        
        self.borrow_repo.add(new_borrow)
        self.book_repo.update()
        
        return book.to_dict(), None
        
    def return_book(self, user, book_id):
        book = self.book_repo.get_by_id(book_id)
        
        borrow = self.borrow_repo.get_specific_active_borrow(user.id, book.id)
        if not borrow:
            return None, "Você não tem este livro pendente de devolução."
            
        borrow.returned = True
        book.qtd += 1
        
        self.borrow_repo.update()
        self.book_repo.update()
        
        return book.to_dict(), None
        
    def get_my_borrows(self, user):
        borrows = self.borrow_repo.get_active_by_user(user.id)
        return [b.book_id for b in borrows]
        
    def get_all_borrows(self):
        borrows = self.borrow_repo.get_all_active()
        return [{
            "id": b.id,
            "user": b.user.username,
            "book": b.book.title,
            "book_id": b.book_id
        } for b in borrows]