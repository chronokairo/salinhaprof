@echo off
title CursoHub - Launcher
cls
echo.
echo  ==========================================
echo   🎓 CursoHub - Sistema de Inicialização
echo  ==========================================
echo.
echo  Escolha como deseja iniciar o CursoHub:
echo.
echo  [1] Auto Start Simples (Batch)
echo  [2] Auto Start Avançado (PowerShell)
echo  [3] Auto Start Cross-Platform (Python)
echo  [4] Apenas Backend
echo  [5] Apenas Teste de Integração
echo.
set /p choice="Digite sua escolha (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Iniciando com Batch Script...
    call auto-start.bat
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Iniciando com PowerShell...
    powershell -ExecutionPolicy Bypass -File auto-start.ps1
) else if "%choice%"=="3" (
    echo.
    echo 🚀 Iniciando com Python...
    python auto-start.py
) else if "%choice%"=="4" (
    echo.
    echo 🚀 Iniciando apenas o Backend...
    cd backend
    python app.py
) else if "%choice%"=="5" (
    echo.
    echo 🚀 Apenas teste de integração...
    powershell -ExecutionPolicy Bypass -File auto-start.ps1 -TestOnly
) else (
    echo.
    echo ❌ Opção inválida. Tente novamente.
    pause
    goto :eof
)

pause
