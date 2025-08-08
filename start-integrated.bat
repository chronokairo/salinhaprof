@echo off
title CursoHub - Servidor Integrado
echo.
echo  ========================================
echo   🎓 CursoHub - Plataforma de Cursos
echo  ========================================
echo.
echo  🚀 Iniciando servidor Flask...
echo     API: http://localhost:5000
echo.
echo  🔐 Credenciais de teste:
echo     Professor: professor@cursohub.com / 123456
echo     Aluno:     aluno@cursohub.com / 123456
echo     Admin:     admin@cursohub.com / admin123
echo.
echo  🌐 Páginas para testar:
echo     1. Login: frontend/telas/index.html
echo     2. Teste: test-integration.html
echo     3. Professor: frontend/telas/professor/painel.html
echo.
echo  💡 Pressione Ctrl+C para parar
echo  ========================================
echo.

cd backend
python app.py
