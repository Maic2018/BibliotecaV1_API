import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from models import db, User, LibraryUnit
from werkzeug.security import generate_password_hash
from external_services import ViaCepClient

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

        # Criar unidades padrão se ainda não existir nenhuma.
        # O endereço de cada uma é buscado de verdade na API externa
        # ViaCEP, assim a seção "Nossas Unidades" já nasce populada.
        if not LibraryUnit.query.first():
            via_cep = ViaCepClient()
            default_units = [
                {"name": "Biblioteca Central", "phone": "(11) 3000-1000", "cep": "01310-100"},
                {"name": "Unidade Itaim Bibi", "phone": "(11) 3000-2000", "cep": "04538-133"},
            ]
            for unit_data in default_units:
                address = via_cep.lookup(unit_data["cep"])
                if not address:
                    # Se a API externa estiver indisponível no momento do
                    # start (ex: sem internet), pula a semeadura em vez de
                    # derrubar a aplicação. O admin pode cadastrar manualmente.
                    continue
                db.session.add(LibraryUnit(
                    name=unit_data["name"],
                    phone=unit_data["phone"],
                    cep=address["cep"],
                    logradouro=address["logradouro"],
                    bairro=address["bairro"],
                    cidade=address["cidade"],
                    uf=address["uf"],
                ))
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True, port=5000)
