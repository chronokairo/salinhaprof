@echo off
echo 🎓 CursoHub - Iniciando o Backend
echo ================================

REM Verificar se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

REM Verificar se requirements.txt existe
if not exist requirements.txt (
    echo ❌ Arquivo requirements.txt não encontrado.
    pause
    exit /b 1
)

echo 🔧 Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências.
    pause
    exit /b 1
)

echo 🚀 Iniciando o servidor...
echo.
echo 📋 Informações importantes:
echo    - API: http://localhost:5000
echo    - Frontend: Abra index.html no navegador
echo    - Credenciais de teste:
echo      Professor: professor@cursohub.com / 123456
echo      Aluno: aluno@cursohub.com / 123456
echo      Admin: admin@cursohub.com / admin123
echo.
echo 💡 Pressione Ctrl+C para parar o servidor
echo =========================================
echo.

python backend_complete.py
