# CursoHub Auto Start Script - PowerShell
param(
    [switch]$SkipBrowser,
    [switch]$TestOnly
)

# Colors and output functions
function Write-ColoredOutput {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header {
    Write-Host ""
    Write-ColoredOutput "===========================================" "Green"
    Write-ColoredOutput "  🎓 CursoHub - Auto Start System" "Yellow"
    Write-ColoredOutput "===========================================" "Green"
    Write-Host ""
}

function Test-Python {
    try {
        $version = python --version 2>&1
        Write-ColoredOutput "✅ Python encontrado: $version" "Green"
        return $true
    }
    catch {
        Write-ColoredOutput "❌ Python não encontrado. Instale Python 3.8+ e tente novamente." "Red"
        return $false
    }
}

function Test-PortAvailable {
    param([int]$Port)
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

function Wait-ServerOnline {
    param([string]$Url, [int]$MaxAttempts = 10)
    
    Write-ColoredOutput "⏳ Aguardando servidor ficar online..." "Yellow"
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-ColoredOutput "✅ Servidor online! Status: $($response.StatusCode)" "Green"
                return $true
            }
        }
        catch {
            Write-Host "." -NoNewline -ForegroundColor Gray
            Start-Sleep -Seconds 1
        }
    }
    
    Write-Host ""
    Write-ColoredOutput "❌ Servidor não respondeu após $MaxAttempts tentativas" "Red"
    return $false
}

function Show-AccessInfo {
    Write-Host ""
    Write-ColoredOutput "===========================================" "Green"
    Write-ColoredOutput "  🎉 CursoHub iniciado com sucesso!" "Yellow"
    Write-ColoredOutput "===========================================" "Green"
    Write-Host ""
    Write-ColoredOutput "📋 Informações de acesso:" "White"
    Write-ColoredOutput "   🌐 API Backend: http://localhost:5000" "Cyan"
    Write-ColoredOutput "   📄 Teste: test-integration.html" "Cyan"
    Write-ColoredOutput "   🔑 Login: frontend/telas/index.html" "Cyan"
    Write-Host ""
    Write-ColoredOutput "🔐 Credenciais de teste:" "White"
    Write-ColoredOutput "   👨‍🏫 Professor: professor@cursohub.com / 123456" "Yellow"
    Write-ColoredOutput "   👨‍🎓 Aluno:     aluno@cursohub.com / 123456" "Yellow"
    Write-ColoredOutput "   👑 Admin:     admin@cursohub.com / admin123" "Yellow"
    Write-Host ""
    Write-ColoredOutput "💡 Para parar o servidor, feche esta janela ou pressione Ctrl+C" "Gray"
    Write-Host ""
}

# Main execution
Write-Header

# Check Python
if (-not (Test-Python)) {
    Read-Host "Pressione Enter para sair"
    exit 1
}

$serverProcess = $null

# Check if port 5000 is available
if (-not (Test-PortAvailable -Port 5000)) {
    Write-ColoredOutput "⚠️ Porta 5000 já está em uso. Tentando conectar ao servidor existente..." "Yellow"
    
    if (Wait-ServerOnline -Url "http://localhost:5000" -MaxAttempts 3) {
        Write-ColoredOutput "✅ Servidor já está rodando!" "Green"
    } else {
        Write-ColoredOutput "❌ Não foi possível conectar ao servidor na porta 5000" "Red"
        Read-Host "Pressione Enter para sair"
        exit 1
    }
} else {
    # Start Flask server
    Write-ColoredOutput "🚀 Iniciando servidor Flask..." "Cyan"
    
    $backendPath = Join-Path $PSScriptRoot "backend"
    
    if (-not (Test-Path $backendPath)) {
        Write-ColoredOutput "❌ Pasta backend não encontrada: $backendPath" "Red"
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    
    # Start the server process
    $serverProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $backendPath -WindowStyle Hidden -PassThru
    
    Write-ColoredOutput "📊 Processo Flask iniciado (PID: $($serverProcess.Id))" "Green"
    
    # Wait for server to respond
    if (-not (Wait-ServerOnline -Url "http://localhost:5000")) {
        Write-ColoredOutput "❌ Falha ao iniciar o servidor" "Red"
        if ($serverProcess) { $serverProcess.Kill() }
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

Write-Host ""
Write-ColoredOutput "✅ Backend iniciado com sucesso!" "Green"
Write-ColoredOutput "   API: http://localhost:5000" "Cyan"

# Open browser pages
if (-not $SkipBrowser) {
    Write-Host ""
    Write-ColoredOutput "🌐 Abrindo páginas no navegador..." "Cyan"
    
    $testFile = Join-Path $PSScriptRoot "test-integration.html"
    $loginFile = Join-Path $PSScriptRoot "frontend\telas\index.html"
    
    if ($TestOnly) {
        if (Test-Path $testFile) {
            Start-Process $testFile
            Write-ColoredOutput "📄 Página de teste aberta: test-integration.html" "Green"
        }
    } else {
        if (Test-Path $testFile) {
            Start-Process $testFile
            Write-ColoredOutput "📄 Teste de integração: test-integration.html" "Green"
            Start-Sleep -Seconds 1
        }
        
        if (Test-Path $loginFile) {
            Start-Process $loginFile
            Write-ColoredOutput "📄 Interface de login: frontend/telas/index.html" "Green"
        }
    }
}

Show-AccessInfo

# Monitor server
try {
    Write-ColoredOutput "🔄 Monitorando servidor... (Pressione Ctrl+C para parar)" "Green"
    while ($true) {
        Start-Sleep -Seconds 5
        
        try {
            $null = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        }
        catch {
            Write-ColoredOutput "⚠️ Servidor não está respondendo..." "Yellow"
            break
        }
    }
}
catch [System.Management.Automation.PipelineStoppedException] {
    # Ctrl+C pressed
    Write-Host ""
    Write-ColoredOutput "🛑 Parando servidor..." "Yellow"
}
catch {
    Write-Host ""
    Write-ColoredOutput "🛑 Erro no monitoramento: $($_.Exception.Message)" "Yellow"
}
finally {
    if ($serverProcess) {
        try {
            if (-not $serverProcess.HasExited) {
                $serverProcess.Kill()
                Write-ColoredOutput "👋 Servidor parado (PID: $($serverProcess.Id))" "Green"
            }
        }
        catch {
            # Process may have already exited
        }
    }
}

Write-ColoredOutput "👋 CursoHub encerrado." "Green"
