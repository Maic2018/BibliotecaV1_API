import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from models import db, User
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configurações do banco de dados
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'biblioteca_v3.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração do Swagger
    app.config['SWAGGER'] = {
        'title': 'API da Biblioteca MVP',
        'uiversion': 3,
        'description': 'Documentação da API para o sistema de biblioteca MVP',
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/apidocs/',
        'securityDefinitions': {
            'basicAuth': {
                'type': 'basic'
            }
        }
    }

    db.init_app(app)
    Swagger(app)

    # Importar e registrar as rotas
    from routes import register_routes
    register_routes(app)

    with app.app_context():
        db.create_all()
        # Criar admin padrão se não existir
        if not User.query.filter_by(username='admin').first():
            default_admin = User(
                username='admin', 
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(default_admin)
            
        # Criar usuário padrão se não existir
        if not User.query.filter_by(username='user').first():
            default_user = User(
                username='user', 
                password_hash=generate_password_hash('user123'),
                is_admin=False
            )
            db.session.add(default_user)
            
        db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
