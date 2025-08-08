#!/usr/bin/env python3
"""
CursoHub Auto Start Script
Cross-platform script to start backend and frontend automatically
"""

import os
import sys
import time
import subprocess
import webbrowser
import requests
import threading
from pathlib import Path

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    """Print text with color"""
    print(f"{color}{text}{Colors.END}")

def print_header():
    """Print startup header"""
    print()
    print_colored("=" * 45, Colors.GREEN)
    print_colored("  🎓 CursoHub - Auto Start System", Colors.YELLOW + Colors.BOLD)
    print_colored("=" * 45, Colors.GREEN)
    print()

def check_python():
    """Check if Python is available"""
    try:
        version = sys.version.split()[0]
        print_colored(f"✅ Python encontrado: {version}", Colors.GREEN)
        return True
    except:
        print_colored("❌ Python não encontrado ou versão inválida", Colors.RED)
        return False

def check_port(port):
    """Check if port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except:
        return False

def wait_for_server(url, max_attempts=15):
    """Wait for server to be online"""
    print_colored("⏳ Aguardando servidor ficar online...", Colors.YELLOW)
    
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print_colored(f"✅ Servidor online! Status: {response.status_code}", Colors.GREEN)
                return True
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    
    print()
    print_colored(f"❌ Servidor não respondeu após {max_attempts} tentativas", Colors.RED)
    return False

def start_backend():
    """Start Flask backend server"""
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    
    if not backend_dir.exists():
        print_colored(f"❌ Pasta backend não encontrada: {backend_dir}", Colors.RED)
        return None
    
    print_colored("🚀 Iniciando servidor Flask...", Colors.CYAN)
    
    # Start Flask server
    try:
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=backend_dir,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  # Unix/Linux/Mac
            process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=backend_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print_colored(f"📊 Processo Flask iniciado (PID: {process.pid})", Colors.GREEN)
        return process
        
    except Exception as e:
        print_colored(f"❌ Erro ao iniciar servidor: {e}", Colors.RED)
        return None

def open_frontend(test_only=False):
    """Open frontend pages in browser"""
    script_dir = Path(__file__).parent
    
    print_colored("🌐 Abrindo páginas no navegador...", Colors.CYAN)
    
    # Test integration page
    test_page = script_dir / "test-integration.html"
    if test_page.exists():
        webbrowser.open(f"file://{test_page.absolute()}")
        print_colored("📄 Teste de integração: test-integration.html", Colors.GREEN)
        if not test_only:
            time.sleep(1)
    
    if not test_only:
        # Login page
        login_page = script_dir / "frontend" / "telas" / "index.html"
        if login_page.exists():
            webbrowser.open(f"file://{login_page.absolute()}")
            print_colored("📄 Interface de login: frontend/telas/index.html", Colors.GREEN)

def print_info():
    """Print access information"""
    print()
    print_colored("=" * 45, Colors.GREEN)
    print_colored("  🎉 CursoHub iniciado com sucesso!", Colors.YELLOW + Colors.BOLD)
    print_colored("=" * 45, Colors.GREEN)
    print()
    print_colored("📋 Informações de acesso:", Colors.WHITE + Colors.BOLD)
    print_colored("   🌐 API Backend: http://localhost:5000", Colors.CYAN)
    print_colored("   📄 Teste: test-integration.html", Colors.CYAN)
    print_colored("   🔑 Login: frontend/telas/index.html", Colors.CYAN)
    print()
    print_colored("🔐 Credenciais de teste:", Colors.WHITE + Colors.BOLD)
    print_colored("   👨‍🏫 Professor: professor@cursohub.com / 123456", Colors.YELLOW)
    print_colored("   👨‍🎓 Aluno:     aluno@cursohub.com / 123456", Colors.YELLOW)
    print_colored("   👑 Admin:     admin@cursohub.com / admin123", Colors.YELLOW)
    print()
    print_colored("💡 Para parar o servidor, pressione Ctrl+C", Colors.GRAY)
    print()

def monitor_server(process):
    """Monitor server process"""
    try:
        print_colored("🔄 Monitorando servidor... (Pressione Ctrl+C para parar)", Colors.GREEN)
        
        while True:
            time.sleep(5)
            
            # Check if process is still running
            if process.poll() is not None:
                print_colored("⚠️ Processo do servidor terminou inesperadamente", Colors.YELLOW)
                break
            
            # Check if server is responding
            try:
                response = requests.get("http://localhost:5000", timeout=3)
            except:
                print_colored("⚠️ Servidor não está respondendo...", Colors.YELLOW)
                break
                
    except KeyboardInterrupt:
        print()
        print_colored("🛑 Parando servidor...", Colors.YELLOW)
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print_colored("👋 CursoHub encerrado.", Colors.GREEN)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CursoHub Auto Start")
    parser.add_argument("--no-browser", action="store_true", help="Não abrir navegador")
    parser.add_argument("--test-only", action="store_true", help="Abrir apenas página de teste")
    args = parser.parse_args()
    
    print_header()
    
    # Check Python
    if not check_python():
        input("Pressione Enter para sair...")
        sys.exit(1)
    
    # Check if port 5000 is available
    if not check_port(5000):
        print_colored("⚠️ Porta 5000 já está em uso. Tentando conectar ao servidor existente...", Colors.YELLOW)
        
        if wait_for_server("http://localhost:5000", max_attempts=3):
            print_colored("✅ Servidor já está rodando!", Colors.GREEN)
            process = None
        else:
            print_colored("❌ Não foi possível conectar ao servidor na porta 5000", Colors.RED)
            input("Pressione Enter para sair...")
            sys.exit(1)
    else:
        # Start backend
        process = start_backend()
        if not process:
            input("Pressione Enter para sair...")
            sys.exit(1)
        
        # Wait for server to be ready
        if not wait_for_server("http://localhost:5000"):
            print_colored("❌ Falha ao iniciar o servidor", Colors.RED)
            process.terminate()
            input("Pressione Enter para sair...")
            sys.exit(1)
    
    print_colored("✅ Backend iniciado com sucesso!", Colors.GREEN)
    print_colored("   API: http://localhost:5000", Colors.CYAN)
    
    # Open frontend
    if not args.no_browser:
        open_frontend(test_only=args.test_only)
    
    # Print info
    print_info()
    
    # Monitor server if we started it
    if process:
        monitor_server(process)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_colored("👋 Saindo...", Colors.GREEN)
        sys.exit(0)
    except Exception as e:
        print_colored(f"❌ Erro inesperado: {e}", Colors.RED)
        input("Pressione Enter para sair...")
        sys.exit(1)
