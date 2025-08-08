# CursoHub Auto Start Script
# PowerShell version for better process management

param(
    [switch]$SkipBrowser,
    [switch]$TestOnly
)

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "  🎓 CursoHub - Auto Start System" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Function to check if Python is available
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Python não encontrado. Instale Python 3.8+ e tente novamente." -ForegroundColor Red
        return $false
    }
}

# Function to check if port is free
function Test-Port {
    param($Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    }
    catch {
        return $false
    }
}

# Function to wait for server to be online
function Wait-ForServer {
    param($Url, $MaxAttempts = 10)
    
    Write-Host "⏳ Aguardando servidor ficar online..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Servidor online! Status: $($response.StatusCode)" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "." -NoNewline -ForegroundColor Gray
            Start-Sleep -Seconds 1
        }
    }
    
    Write-Host ""
    Write-Host "❌ Servidor não respondeu após $MaxAttempts tentativas" -ForegroundColor Red
    return $false
}

# Check Python
if (-not (Test-Python)) {
    Read-Host "Pressione Enter para sair"
    exit 1
}

$process = $null

# Check if port 5000 is free
if (-not (Test-Port -Port 5000)) {
    Write-Host "⚠️ Porta 5000 já está em uso. Tentando conectar ao servidor existente..." -ForegroundColor Yellow
    
    if (Wait-ForServer -Url "http://localhost:5000" -MaxAttempts 3) {
        Write-Host "✅ Servidor já está rodando!" -ForegroundColor Green
    } else {
        Write-Host "❌ Não foi possível conectar ao servidor na porta 5000" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
} else {
    # Start Flask server
    Write-Host "🚀 Iniciando servidor Flask..." -ForegroundColor Cyan
    
    $backendPath = Join-Path $PSScriptRoot "backend"
    
    # Check if backend folder exists
    if (-not (Test-Path $backendPath)) {
        Write-Host "❌ Pasta backend não encontrada: $backendPath" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    
    # Start Python process in background
    $process = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $backendPath -WindowStyle Hidden -PassThru
    
    Write-Host "📊 Processo Flask iniciado (PID: $($process.Id))" -ForegroundColor Green
    
    # Wait for server to be online
    if (-not (Wait-ForServer -Url "http://localhost:5000")) {
        Write-Host "❌ Falha ao iniciar o servidor" -ForegroundColor Red
        if ($process) { $process.Kill() }
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Backend iniciado com sucesso!" -ForegroundColor Green
Write-Host "   API: http://localhost:5000" -ForegroundColor Cyan

# Open pages in browser (if not disabled)
if (-not $SkipBrowser) {
    Write-Host ""
    Write-Host "🌐 Abrindo páginas no navegador..." -ForegroundColor Cyan
    
    # File paths
    $testIntegrationPath = Join-Path $PSScriptRoot "test-integration.html"
    $loginPath = Join-Path $PSScriptRoot "frontend\telas\index.html"
    
    if ($TestOnly) {
        # Open only test page
        if (Test-Path $testIntegrationPath) {
            Start-Process $testIntegrationPath
            Write-Host "📄 Página de teste aberta: test-integration.html" -ForegroundColor Green
        }
    } else {
        # Open test page first
        if (Test-Path $testIntegrationPath) {
            Start-Process $testIntegrationPath
            Write-Host "📄 Teste de integração: test-integration.html" -ForegroundColor Green
            Start-Sleep -Seconds 1
        }
        
        # Open login page
        if (Test-Path $loginPath) {
            Start-Process $loginPath
            Write-Host "📄 Interface de login: frontend/telas/index.html" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host "  🎉 CursoHub iniciado com sucesso!" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Informações de acesso:" -ForegroundColor White
Write-Host "   🌐 API Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   📄 Teste: test-integration.html" -ForegroundColor Cyan
Write-Host "   🔑 Login: frontend/telas/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Credenciais de teste:" -ForegroundColor White
Write-Host "   👨‍🏫 Professor: professor@cursohub.com / 123456" -ForegroundColor Yellow
Write-Host "   👨‍🎓 Aluno:     aluno@cursohub.com / 123456" -ForegroundColor Yellow
Write-Host "   👑 Admin:     admin@cursohub.com / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Para parar o servidor, feche esta janela ou pressione Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Keep script running to monitor
try {
    Write-Host "🔄 Monitorando servidor... (Pressione Ctrl+C para parar)" -ForegroundColor Green
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if server is still responding
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 3 -UseBasicParsing
            # Server OK, continue
        }
        catch {
            Write-Host "⚠️ Servidor não está respondendo..." -ForegroundColor Yellow
            break
        }
    }
}
catch {
    Write-Host ""
    Write-Host "🛑 Parando servidor..." -ForegroundColor Yellow
}
finally {
    if ($process) {
        try {
            $process.Kill()
            Write-Host "👋 Servidor parado (PID: $($process.Id))" -ForegroundColor Green
        }
        catch {
            # Process already stopped
        }
    }
}

Write-Host "👋 CursoHub encerrado." -ForegroundColor Green
