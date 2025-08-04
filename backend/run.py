#!/usr/bin/env python3
"""
Script de inicialização do CursoHub Backend
"""

import sys
import os

# Adicionar o diretório atual ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def initialize_database():
    """Inicializar banco de dados e criar usuário admin"""
    with app.app_context():
        print("🔄 Inicializando banco de dados...")
        db.create_all()
        
        # Verificar se já existe usuário admin
        admin = User.query.filter_by(email='admin@cursohub.com').first()
        if not admin:
            admin = User(
                name='Administrador',
                email='admin@cursohub.com',
                password=generate_password_hash('admin123'),
                role='admin',
                bio='Administrador da plataforma CursoHub'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado: admin@cursohub.com / admin123")
        else:
            print("ℹ️  Usuário admin já existe")
        
        print("✅ Banco de dados inicializado com sucesso!")

def main():
    """Função principal"""
    print("🚀 Iniciando CursoHub API...")
    print("🌍 URL: http://localhost:5000")
    print("📋 Documentação: http://localhost:5000/api/health")
    print("👤 Admin: admin@cursohub.com / admin123")
    print("-" * 50)
    
    # Inicializar banco
    initialize_database()
    
    # Executar aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()