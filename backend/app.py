from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-muito-segura-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cursohub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Extensões
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app)

# Criar diretório de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'materials'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)

# Importar modelos
from models import *

# Importar rotas
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar usuário admin padrão se não existir
        admin = User.query.filter_by(email='admin@cursohub.com').first()
        if not admin:
            admin = User(
                name='Administrador',
                email='admin@cursohub.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado: admin@cursohub.com / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)