#!/bin/bash

# CursoHub Auto Start Script for Linux/Mac
# Cross-platform startup script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${YELLOW}  🎓 CursoHub - Auto Start System${NC}"
    echo -e "${GREEN}===========================================${NC}"
    echo ""
}

print_colored() {
    local color=$1
    local text=$2
    echo -e "${color}${text}${NC}"
}

check_python() {
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version 2>&1)
        print_colored $GREEN "✅ Python encontrado: $version"
        return 0
    elif command -v python &> /dev/null; then
        local version=$(python --version 2>&1)
        print_colored $GREEN "✅ Python encontrado: $version"
        return 0
    else
        print_colored $RED "❌ Python não encontrado. Instale Python 3.8+ e tente novamente."
        return 1
    fi
}

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

wait_for_server() {
    local url=$1
    local max_attempts=${2:-15}
    
    print_colored $YELLOW "⏳ Aguardando servidor ficar online..."
    
    for ((i=1; i<=max_attempts; i++)); do
        if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
            print_colored $GREEN "✅ Servidor online!"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo ""
    print_colored $RED "❌ Servidor não respondeu após $max_attempts tentativas"
    return 1
}

start_backend() {
    local script_dir=$(dirname "$0")
    local backend_dir="$script_dir/backend"
    
    if [ ! -d "$backend_dir" ]; then
        print_colored $RED "❌ Pasta backend não encontrada: $backend_dir"
        return 1
    fi
    
    print_colored $CYAN "🚀 Iniciando servidor Flask..."
    
    # Start Flask server in background
    cd "$backend_dir"
    if command -v python3 &> /dev/null; then
        nohup python3 app.py > /dev/null 2>&1 &
    else
        nohup python app.py > /dev/null 2>&1 &
    fi
    
    local pid=$!
    print_colored $GREEN "📊 Processo Flask iniciado (PID: $pid)"
    
    # Save PID for later cleanup
    echo $pid > /tmp/cursohub_backend.pid
    
    cd - > /dev/null
    return 0
}

open_frontend() {
    local test_only=${1:-false}
    local script_dir=$(dirname "$0")
    
    print_colored $CYAN "🌐 Abrindo páginas no navegador..."
    
    # Test integration page
    local test_page="$script_dir/test-integration.html"
    if [ -f "$test_page" ]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "file://$test_page" 2>/dev/null &
        elif command -v open &> /dev/null; then
            open "file://$test_page" 2>/dev/null &
        fi
        print_colored $GREEN "📄 Teste de integração: test-integration.html"
        
        if [ "$test_only" != "true" ]; then
            sleep 1
        fi
    fi
    
    if [ "$test_only" != "true" ]; then
        # Login page
        local login_page="$script_dir/frontend/telas/index.html"
        if [ -f "$login_page" ]; then
            if command -v xdg-open &> /dev/null; then
                xdg-open "file://$login_page" 2>/dev/null &
            elif command -v open &> /dev/null; then
                open "file://$login_page" 2>/dev/null &
            fi
            print_colored $GREEN "📄 Interface de login: frontend/telas/index.html"
        fi
    fi
}

print_info() {
    echo ""
    print_colored $GREEN "=========================================="
    print_colored "${YELLOW}  🎉 CursoHub iniciado com sucesso!"
    print_colored $GREEN "=========================================="
    echo ""
    print_colored "${WHITE}📋 Informações de acesso:"
    print_colored $CYAN "   🌐 API Backend: http://localhost:5000"
    print_colored $CYAN "   📄 Teste: test-integration.html"
    print_colored $CYAN "   🔑 Login: frontend/telas/index.html"
    echo ""
    print_colored "${WHITE}🔐 Credenciais de teste:"
    print_colored $YELLOW "   👨‍🏫 Professor: professor@cursohub.com / 123456"
    print_colored $YELLOW "   👨‍🎓 Aluno:     aluno@cursohub.com / 123456"
    print_colored $YELLOW "   👑 Admin:     admin@cursohub.com / admin123"
    echo ""
    print_colored $GRAY "💡 Para parar o servidor, pressione Ctrl+C"
    echo ""
}

cleanup() {
    echo ""
    print_colored $YELLOW "🛑 Parando servidor..."
    
    if [ -f /tmp/cursohub_backend.pid ]; then
        local pid=$(cat /tmp/cursohub_backend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_colored $GREEN "👋 Servidor parado (PID: $pid)"
        fi
        rm -f /tmp/cursohub_backend.pid
    fi
    
    print_colored $GREEN "👋 CursoHub encerrado."
    exit 0
}

monitor_server() {
    print_colored $GREEN "🔄 Monitorando servidor... (Pressione Ctrl+C para parar)"
    
    while true; do
        sleep 5
        
        if ! curl -s --max-time 3 "http://localhost:5000" > /dev/null 2>&1; then
            print_colored $YELLOW "⚠️ Servidor não está respondendo..."
            break
        fi
    done
}

# Main execution
main() {
    local skip_browser=false
    local test_only=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-browser)
                skip_browser=true
                shift
                ;;
            --test-only)
                test_only=true
                shift
                ;;
            -h|--help)
                echo "CursoHub Auto Start"
                echo "Uso: $0 [opções]"
                echo ""
                echo "Opções:"
                echo "  --no-browser    Não abrir navegador"
                echo "  --test-only     Abrir apenas página de teste"
                echo "  -h, --help      Mostrar esta ajuda"
                exit 0
                ;;
            *)
                echo "Opção desconhecida: $1"
                exit 1
                ;;
        esac
    done
    
    # Trap Ctrl+C
    trap cleanup SIGINT SIGTERM
    
    print_header
    
    # Check Python
    if ! check_python; then
        read -p "Pressione Enter para sair..."
        exit 1
    fi
    
    # Check if port 5000 is available
    if ! check_port 5000; then
        print_colored $YELLOW "⚠️ Porta 5000 já está em uso. Tentando conectar ao servidor existente..."
        
        if wait_for_server "http://localhost:5000" 3; then
            print_colored $GREEN "✅ Servidor já está rodando!"
        else
            print_colored $RED "❌ Não foi possível conectar ao servidor na porta 5000"
            read -p "Pressione Enter para sair..."
            exit 1
        fi
    else
        # Start backend
        if ! start_backend; then
            read -p "Pressione Enter para sair..."
            exit 1
        fi
        
        # Wait for server to be ready
        if ! wait_for_server "http://localhost:5000"; then
            print_colored $RED "❌ Falha ao iniciar o servidor"
            cleanup
            exit 1
        fi
    fi
    
    print_colored $GREEN "✅ Backend iniciado com sucesso!"
    print_colored $CYAN "   API: http://localhost:5000"
    
    # Open frontend
    if [ "$skip_browser" != "true" ]; then
        open_frontend $test_only
    fi
    
    # Print info
    print_info
    
    # Monitor server
    monitor_server
}

# Run main function
main "$@"
