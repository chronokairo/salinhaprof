@echo off
color 0A
title CursoHub - Auto Start System
cls

echo.
echo  ===========================================
echo   🎓 CursoHub - Auto Start System
echo  ===========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python não encontrado. Instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

echo  ✅ Python encontrado
echo  🚀 Iniciando servidor Flask em segundo plano...

REM Start Flask server in background
cd /d "%~dp0backend"
start /B python app.py

REM Wait for server
timeout /t 4 /nobreak >nul

echo  🌐 Abrindo páginas no navegador...

REM Open test page
start "" "%~dp0test-integration.html"

REM Wait a moment
timeout /t 1 /nobreak >nul

REM Open login page
start "" "%~dp0frontend\telas\index.html"

echo.
echo  ===========================================
echo   🎉 CursoHub iniciado com sucesso!
echo  ===========================================
echo.
echo  📋 Informações de acesso:
echo     🌐 API Backend: http://localhost:5000
echo     📄 Teste: test-integration.html
echo     🔑 Login: frontend/telas/index.html
echo.
echo  🔐 Credenciais de teste:
echo     👨‍🏫 Professor: professor@cursohub.com / 123456
echo     👨‍🎓 Aluno:     aluno@cursohub.com / 123456
echo     👑 Admin:     admin@cursohub.com / admin123
echo.
echo  💡 Para parar o servidor, feche esta janela
echo  ===========================================
echo.

pause
