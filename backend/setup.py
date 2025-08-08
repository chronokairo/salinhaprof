#!/usr/bin/env python3
"""
Script de inicialização para o CursoHub Backend
Instala dependências e configura o ambiente
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e.stderr.strip()}")
        return False

def main():
    """Função principal de inicialização"""
    print("🎓 CursoHub Backend - Configuração do Ambiente")
    print("=" * 50)
    
    # Verificar se Python está instalado
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python {python_version} detectado")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        sys.exit(1)
    
    # Instalar dependências
    if not run_command("pip install -r requirements.txt", "Instalando dependências"):
        print("❌ Falha ao instalar dependências")
        sys.exit(1)
    
    # Criar diretórios necessários
    directories = ['uploads', 'uploads/videos', 'uploads/materials', 'uploads/avatars']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Diretório criado: {directory}")
    
    print("\n🎉 Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute o backend: python backend_complete.py")
    print("2. Acesse http://localhost:5000 para verificar a API")
    print("3. Use as credenciais de teste:")
    print("   - Professor: professor@cursohub.com / 123456")
    print("   - Aluno: aluno@cursohub.com / 123456")
    print("   - Admin: admin@cursohub.com / admin123")

if __name__ == "__main__":
    main()
