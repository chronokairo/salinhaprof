@echo off
title CursoHub - Auto Start (Backend + Frontend)
color 0A
echo.
echo  ==========================================
echo   🎓 CursoHub - Auto Start System
echo  ==========================================
echo.
echo  🚀 Iniciando Backend Flask...
echo  📱 Abrindo Frontend no navegador...
echo.
echo  ⏳ Aguarde alguns segundos...
echo.

REM Verifica se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

REM Navega para a pasta backend
cd /d "%~dp0backend"

REM Inicia o servidor Flask em background
echo  🔧 Iniciando servidor Flask em segundo plano...
start /B python app.py

REM Aguarda 3 segundos para o servidor inicializar
timeout /t 3 /nobreak >nul

REM Abre as páginas no navegador padrão
echo  🌐 Abrindo páginas no navegador...

REM Página de teste de integração
start "" "%~dp0test-integration.html"

REM Aguarda 1 segundo
timeout /t 1 /nobreak >nul

REM Página de login
start "" "%~dp0frontend\telas\index.html"

echo.
echo  ✅ Sistema iniciado com sucesso!
echo.
echo  📋 Informações importantes:
echo     - API Backend: http://localhost:5000
echo     - Teste de Integração: test-integration.html
echo     - Login do Frontend: frontend/telas/index.html
echo.
echo  🔐 Credenciais de teste:
echo     Professor: professor@cursohub.com / 123456
echo     Aluno:     aluno@cursohub.com / 123456
echo     Admin:     admin@cursohub.com / admin123
echo.
echo  💡 Para parar o servidor, feche esta janela ou pressione Ctrl+C
echo  ==========================================
echo.

REM Mantém a janela aberta para monitorar logs
pause
