from flask import request, jsonify
from functools import wraps
from repositories import UserRepository, BookRepository, BorrowRepository, UnitRepository
from services import AuthService, BookService, BorrowService, UnitService

# -------------------------------------------------------------------
# INVERSÃO DE DEPENDÊNCIA
# -------------------------------------------------------------------
user_repo = UserRepository()
book_repo = BookRepository()
borrow_repo = BorrowRepository()
unit_repo = UnitRepository()

auth_service = AuthService(user_repo)
book_service = BookService(book_repo, borrow_repo)
borrow_service = BorrowService(book_repo, borrow_repo)
unit_service = UnitService(unit_repo)
# -------------------------------------------------------------------

def check_auth(username, password):
    """Verifica se a combinação usuário/senha é válida via Service."""
    return auth_service.authenticate(username, password)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify({"message": "Autenticação Necessária"}), 401
        user = check_auth(auth.username, auth.password)
        if not user:
            return jsonify({"message": "Autenticação Inválida"}), 401
        
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated

def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify({"message": "Autenticação Necessária"}), 401
        user = check_auth(auth.username, auth.password)
        if not user or not user.is_admin:
            return jsonify({"message": "Permissão de Administrador Necessária"}), 401
            
        return f(*args, **kwargs)
    return decorated

def register_routes(app):
    @app.route('/api/login', methods=['POST'])
    def login(): 
        """
        Endpoint para validar credenciais.
        Requer Basic Auth.
        ---
        tags:
          - Auth
        security:
          - basicAuth: []
        responses:
          200:
            description: Login com sucesso
          401:
            description: Credenciais inválidas
        """
        auth = request.authorization
        if not auth:
            return jsonify({"message": "Credenciais ausentes"}), 401
            
        user = check_auth(auth.username, auth.password)
        if not user:
            return jsonify({"message": "Credenciais inválidas"}), 401
            
        return jsonify({
            "message": "Login com sucesso", 
            "is_admin": user.is_admin,
            "username": user.username
        }), 200

    @app.route('/api/books', methods=['GET'])
    def get_books():
        """
        Lista de todos os livros.
        ---
        tags:
          - Livros
        responses:
          200:
            description: Uma lista de livros
        """
        books = book_service.get_all_books()
        return jsonify(books), 200

    @app.route('/api/books', methods=['POST'])
    @requires_admin
    def add_book():
        """
        Adiciona um novo livro (Apenas Admin).
        Requer Basic Auth.
        ---
        tags:
          - Livros (Admin)
        security:
          - basicAuth: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - title
                - author
              properties:
                title:
                  type: string
                author:
                  type: string
                qtd:
                  type: integer
                image_url:
                  type: string
        responses:
          201:
            description: Livro criado com sucesso
          400:
            description: Dados incompletos
          401:
            description: Não autorizado
        """
        data = request.get_json()
        book_dict, error = book_service.add_book(data)
        
        if error:
            return jsonify({'message': error}), 400
            
        return jsonify(book_dict), 201

    @app.route('/api/books/<int:book_id>', methods=['PUT'])
    @requires_admin
    def edit_book(book_id):
        """
        Edita as informações de um livro (Apenas Admin).
        Requer Basic Auth.
        ---
        tags:
          - Livros (Admin)
        security:
          - basicAuth: []
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                title:
                  type: string
                author:
                  type: string
                qtd:
                  type: integer
                image_url:
                  type: string
        responses:
          200:
            description: Livro atualizado com sucesso
          404:
            description: Livro não encontrado
          401:
            description: Não autorizado
        """
        data = request.get_json()
        book_dict, error = book_service.edit_book(book_id, data)
        return jsonify(book_dict), 200

    @app.route('/api/books/<int:book_id>', methods=['DELETE'])
    @requires_admin
    def delete_book(book_id):
        """
        Remove um livro (Apenas Admin).
        Requer Basic Auth.
        ---
        tags:
          - Livros (Admin)
        security:
          - basicAuth: []
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Livro removido com sucesso
          400:
            description: O livro possui empréstimos ativos e não pode ser removido
          404:
            description: Livro não encontrado
          401:
            description: Não autorizado
        """
        success, error = book_service.delete_book(book_id)
        
        if not success:
            return jsonify({"message": error}), 400
            
        return jsonify({"message": "Livro removido"}), 200

    @app.route('/api/books/<int:book_id>/borrow', methods=['POST'])
    @requires_auth
    def borrow_book(current_user, book_id):
        """
        Pega emprestado um livro.
        Diminui a quantidade e registra o usuário.
        ---
        tags:
          - Livros
        security:
          - basicAuth: []
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Livro emprestado com sucesso
          400:
            description: Livro não está disponível ou limite atingido
          404:
            description: Livro não encontrado
        """
        book_dict, error = borrow_service.borrow_book(current_user, book_id)
        if error:
            return jsonify({"message": error}), 400
            
        return jsonify({"message": "Livro emprestado com sucesso!", "book": book_dict}), 200

    @app.route('/api/books/<int:book_id>/return', methods=['POST'])
    @requires_auth
    def return_book(current_user, book_id):
        """
        Devolve um livro emprestado pelo usuário logado.
        Aumenta a quantidade e encerra o registro.
        ---
        tags:
          - Livros
        security:
          - basicAuth: []
        parameters:
          - name: book_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Livro devolvido com sucesso
          400:
            description: Livro não estava emprestado por este usuário
          404:
            description: Livro não encontrado
        """
        book_dict, error = borrow_service.return_book(current_user, book_id)
        if error:
            return jsonify({"message": error}), 400
            
        return jsonify({"message": "Livro devolvido com sucesso!", "book": book_dict}), 200

    @app.route('/api/my_borrows', methods=['GET'])
    @requires_auth
    def my_borrows(current_user):
        """
        Retorna os IDs dos livros emprestados pelo usuário logado.
        ---
        tags:
          - Livros
        security:
          - basicAuth: []
        """
        book_ids = borrow_service.get_my_borrows(current_user)
        return jsonify(book_ids), 200

    @app.route('/api/borrows', methods=['GET'])
    @requires_admin
    def get_borrows():
        """
        Lista todos os empréstimos ativos (Apenas Admin).
        ---
        tags:
          - Admin
        security:
          - basicAuth: []
        responses:
          200:
            description: Lista de empréstimos
        """
        result = borrow_service.get_all_borrows()
        return jsonify(result), 200

    @app.route('/api/books/external-lookup', methods=['GET'])
    @requires_admin
    def lookup_book_external():
        """
        Busca automaticamente autor e capa de um livro na API externa
        Open Library, a partir do título (Apenas Admin).
        ---
        tags:
          - Livros (Admin)
        security:
          - basicAuth: []
        parameters:
          - name: title
            in: query
            type: string
            required: true
        responses:
          200:
            description: Dados encontrados na Open Library
          400:
            description: Título ausente ou nada encontrado
        """
        title = request.args.get('title', '')
        result, error = book_service.lookup_external_info(title)

        if error:
            return jsonify({"message": error}), 400

        return jsonify(result), 200

    @app.route('/api/units', methods=['GET'])
    def get_units():
        """
        Lista as unidades físicas da biblioteca, com endereço obtido
        via API externa ViaCEP.
        ---
        tags:
          - Unidades
        responses:
          200:
            description: Lista de unidades
        """
        units = unit_service.get_all_units()
        return jsonify(units), 200

    @app.route('/api/units', methods=['POST'])
    @requires_admin
    def add_unit():
        """
        Cadastra uma nova unidade da biblioteca (Apenas Admin).
        O endereço é preenchido automaticamente a partir do CEP
        informado, consultando a API externa ViaCEP.
        ---
        tags:
          - Unidades (Admin)
        security:
          - basicAuth: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - name
                - cep
              properties:
                name:
                  type: string
                cep:
                  type: string
                phone:
                  type: string
        responses:
          201:
            description: Unidade criada com sucesso
          400:
            description: Dados incompletos ou CEP inválido
        """
        data = request.get_json()
        unit_dict, error = unit_service.add_unit(data)

        if error:
            return jsonify({'message': error}), 400

        return jsonify(unit_dict), 201

    @app.route('/api/units/<int:unit_id>', methods=['PUT'])
    @requires_admin
    def edit_unit(unit_id):
        """
        Edita uma unidade da biblioteca (Apenas Admin).
        Se um novo CEP for enviado, o endereço é atualizado via ViaCEP.
        ---
        tags:
          - Unidades (Admin)
        security:
          - basicAuth: []
        parameters:
          - name: unit_id
            in: path
            type: integer
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                name:
                  type: string
                cep:
                  type: string
                phone:
                  type: string
        responses:
          200:
            description: Unidade atualizada com sucesso
          400:
            description: CEP inválido
          404:
            description: Unidade não encontrada
        """
        data = request.get_json()
        unit_dict, error = unit_service.edit_unit(unit_id, data)

        if error:
            return jsonify({'message': error}), 400

        return jsonify(unit_dict), 200

    @app.route('/api/units/<int:unit_id>', methods=['DELETE'])
    @requires_admin
    def delete_unit(unit_id):
        """
        Remove uma unidade da biblioteca (Apenas Admin).
        ---
        tags:
          - Unidades (Admin)
        security:
          - basicAuth: []
        parameters:
          - name: unit_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Unidade removida com sucesso
          404:
            description: Unidade não encontrada
        """
        unit_service.delete_unit(unit_id)
        return jsonify({"message": "Unidade removida"}), 200