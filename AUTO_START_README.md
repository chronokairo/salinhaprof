# 🚀 CursoHub - Auto Start Scripts

Este repositório inclui múltiplos scripts para iniciar automaticamente o backend e frontend do CursoHub.

## 📋 Scripts Disponíveis

### 🎯 Launcher Principal
```bash
start.bat          # Windows - Menu interativo de opções
```

### 🖥️ Windows
```bash
auto-start.bat     # Script Batch simples
auto-start.ps1     # Script PowerShell avançado com monitoramento
```

### 🐧 Linux/Mac
```bash
./auto-start.sh    # Script Bash cross-platform
```

### 🐍 Cross-Platform
```bash
python auto-start.py    # Script Python (funciona em qualquer OS)
```

## 🚀 Como Usar

### Método 1: Launcher (Recomendado para Windows)
1. **Duplo clique** em `start.bat`
2. **Escolha** uma opção do menu:
   - `[1]` Auto Start Simples (Batch)
   - `[2]` Auto Start Avançado (PowerShell) ⭐ **Recomendado**
   - `[3]` Auto Start Cross-Platform (Python)
   - `[4]` Apenas Backend
   - `[5]` Apenas Teste de Integração

### Método 2: Execução Direta

#### Windows (PowerShell) ⭐ **Recomendado**
```powershell
# Execução normal
powershell -ExecutionPolicy Bypass -File auto-start.ps1

# Apenas teste
powershell -ExecutionPolicy Bypass -File auto-start.ps1 -TestOnly

# Sem abrir navegador
powershell -ExecutionPolicy Bypass -File auto-start.ps1 -SkipBrowser
```

#### Windows (Batch)
```batch
auto-start.bat
```

#### Linux/Mac
```bash
# Tornar executável (primeira vez)
chmod +x auto-start.sh

# Execução normal
./auto-start.sh

# Apenas teste
./auto-start.sh --test-only

# Sem navegador
./auto-start.sh --no-browser
```

#### Python (Qualquer SO)
```bash
# Execução normal
python auto-start.py

# Apenas teste
python auto-start.py --test-only

# Sem navegador
python auto-start.py --no-browser
```

## ⚡ O que os Scripts Fazem

### 1. **Verificações Iniciais**
- ✅ Verifica se Python está instalado
- ✅ Verifica se a porta 5000 está livre
- ✅ Detecta se já existe um servidor rodando

### 2. **Inicialização do Backend**
- 🚀 Inicia o servidor Flask na porta 5000
- 📊 Mostra o PID do processo
- ⏳ Aguarda o servidor ficar online
- 🔄 Monitora se o servidor está respondendo

### 3. **Abertura do Frontend**
- 🌐 Abre automaticamente as páginas no navegador:
  - `test-integration.html` - Página de teste da integração
  - `frontend/telas/index.html` - Interface de login
- 🎯 Opção de abrir apenas a página de teste

### 4. **Monitoramento**
- 👀 Monitora continuamente o servidor
- ⚠️ Detecta se o servidor para de responder
- 🛑 Permite parar graciosamente com Ctrl+C

## 🔧 Opções Avançadas

### PowerShell (auto-start.ps1)
```powershell
# Parâmetros disponíveis
-SkipBrowser    # Não abrir navegador
-TestOnly       # Abrir apenas página de teste
```

### Bash (auto-start.sh)
```bash
# Opções disponíveis
--no-browser    # Não abrir navegador
--test-only     # Abrir apenas página de teste
--help          # Mostrar ajuda
```

### Python (auto-start.py)
```bash
# Argumentos disponíveis
--no-browser    # Não abrir navegador
--test-only     # Abrir apenas página de teste
```

## 📊 Logs e Monitoramento

### Status do Servidor
Todos os scripts mostram:
- ✅ Status de inicialização
- 📊 PID do processo Flask
- 🌐 URL da API (http://localhost:5000)
- 🔄 Status de monitoramento contínuo

### Detecção de Problemas
- 🔍 Verifica se Python está instalado
- 🚪 Detecta conflitos de porta
- ⚡ Testa conectividade com a API
- 🚨 Alerta se o servidor para de responder

## 🛠️ Resolução de Problemas

### ❌ "Python não encontrado"
**Solução:** Instale Python 3.8+ de https://python.org

### ❌ "Porta 5000 já está em uso"
**Solução:** O script tenta conectar ao servidor existente automaticamente

### ❌ "Erro de ExecutionPolicy" (PowerShell)
**Solução:** 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Ou use: `powershell -ExecutionPolicy Bypass -File auto-start.ps1`

### ❌ "Permission denied" (Linux/Mac)
**Solução:**
```bash
chmod +x auto-start.sh
```

### ❌ "Módulo requests não encontrado" (Python)
**Solução:**
```bash
pip install requests
```

## 🎯 Credenciais de Teste

Todos os scripts mostram estas credenciais automaticamente:

- **👨‍🏫 Professor:** professor@cursohub.com / 123456
- **👨‍🎓 Aluno:** aluno@cursohub.com / 123456  
- **👑 Admin:** admin@cursohub.com / admin123

## 📱 URLs de Acesso

Após inicialização, acesse:

- **🔧 API Backend:** http://localhost:5000
- **📄 Teste de Integração:** test-integration.html
- **🔑 Interface de Login:** frontend/telas/index.html
- **👨‍🏫 Painel do Professor:** frontend/telas/professor/painel.html

## 🎉 Recomendação

**Para Windows:** Use `start.bat` e escolha a opção `[2]` (PowerShell avançado)
**Para Linux/Mac:** Use `./auto-start.sh`
**Para qualquer SO:** Use `python auto-start.py`

---

**🚀 Agora você pode iniciar o CursoHub com um duplo clique!**
