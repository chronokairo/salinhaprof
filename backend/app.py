from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import os
import logging
from config import config

def create_app(config_name='default'):
    """Fábrica de aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config.from_object(config[config_name])
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Extensões
    from models import db
    db.init_app(app)
    
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    CORS(app, origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:5500"])
    
    # Criar diretórios de uploads se não existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'materials'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
    
    # Registrar blueprints
    from routes.login import auth_bp
    from routes.professor import courses_bp
    from routes.material import uploads_bp
    from routes.aluno import students_bp
    from routes.meus_cursos import my_courses_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(my_courses_bp)
    
    # Rota principal
    @app.route('/')
    def index():
        return jsonify({
            'message': 'CursoHub API - Plataforma de Cursos Online',
            'version': '2.0.0',
            'status': 'active',
            'endpoints': {
                'auth': '/api/auth',
                'courses': '/api/courses',
                'students': '/api/students',
                'my_courses': '/api/my-courses',
                'upload': '/api/upload'
            }
        })
    
    # Inicializar dados padrão
    def create_default_data():
        """Criar dados padrão da aplicação"""
        from models import User, Course, Lesson
        
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
                
            # Criar usuário professor padrão se não existir
            professor = User.query.filter_by(email='professor@cursohub.com').first()
            if not professor:
                professor = User(
                    name='Professor Demonstração',
                    email='professor@cursohub.com',
                    password=generate_password_hash('123456'),
                    role='teacher'
                )
                db.session.add(professor)
                
            # Criar usuário aluno padrão se não existir
            aluno = User.query.filter_by(email='aluno@cursohub.com').first()
            if not aluno:
                aluno = User(
                    name='Aluno Demonstração',
                    email='aluno@cursohub.com',
                    password=generate_password_hash('123456'),
                    role='student'
                )
                db.session.add(aluno)
                
            # Criar curso de exemplo se não existir
            if not Course.query.first():
                if professor:
                    curso_exemplo = Course(
                        title='Introdução ao Python',
                        description='Aprenda os fundamentos da programação Python de forma prática e objetiva.',
                        category='Programação',
                        level='beginner',
                        price=99.90,
                        creator_id=professor.id,
                        is_published=True,
                        is_featured=True
                    )
                    db.session.add(curso_exemplo)
                    db.session.commit()
                    
                    # Adicionar aulas de exemplo
                    aulas = [
                        {'title': 'Introdução ao Python', 'description': 'Conhecendo a linguagem Python', 'video_duration': 600},
                        {'title': 'Variáveis e Tipos de Dados', 'description': 'Trabalhando com diferentes tipos de dados', 'video_duration': 800},
                        {'title': 'Estruturas de Controle', 'description': 'If, else, loops e mais', 'video_duration': 900},
                    ]
                    
                    for i, aula_data in enumerate(aulas):
                        aula = Lesson(
                            title=aula_data['title'],
                            description=aula_data['description'],
                            content=f"Conteúdo da aula: {aula_data['title']}",
                            video_duration=aula_data['video_duration'],
                            order_index=i + 1,
                            course_id=curso_exemplo.id,
                            is_free=(i == 0)  # Primeira aula gratuita
                        )
                        db.session.add(aula)
                
            db.session.commit()
            app.logger.info("Usuários padrão criados:")
            app.logger.info("Admin: admin@cursohub.com / admin123")
            app.logger.info("Professor: professor@cursohub.com / 123456")
            app.logger.info("Aluno: aluno@cursohub.com / 123456")
    
    # Executar criação de dados padrão se executado diretamente
    if config_name == 'development':
        create_default_data()
    
    return app

# Para desenvolvimento direto
app = create_app('development')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
