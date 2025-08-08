# 🎓 CursoHub - Integração Backend/Frontend

## 📋 Status da Integração

✅ **Backend Flask** configurado e funcionando
✅ **API REST** implementada com JWT
✅ **Frontend** integrado com chamadas AJAX
✅ **Sistema de autenticação** funcional
✅ **Dashboard dinâmico** carregando dados da API
✅ **CORS** configurado para permitir comunicação

## 🚀 Como Iniciar

### 1. Iniciar o Backend (API)
```bash
cd backend
python app.py
```

**Servidor rodará em:** http://localhost:5000

### 2. Abrir o Frontend
Abra qualquer um destes arquivos no navegador:

- **Página de Login:** `frontend/telas/index.html`
- **Teste de Integração:** `test-integration.html`
- **Painel do Professor:** `frontend/telas/professor/painel.html`

## 🔐 Credenciais de Teste

### Professor
- **Email:** professor@cursohub.com
- **Senha:** 123456

### Aluno
- **Email:** aluno@cursohub.com
- **Senha:** 123456

### Admin
- **Email:** admin@cursohub.com
- **Senha:** admin123

## 🛠️ Recursos Integrados

### ✅ Funcionando
- ✅ **Login/Logout** com JWT
- ✅ **Dashboard** com dados dinâmicos
- ✅ **Lista de cursos** do professor
- ✅ **Autenticação** e redirecionamento
- ✅ **Validação de token** automática
- ✅ **CORS** configurado corretamente

### 🔧 Endpoints da API Disponíveis

#### Autenticação
- `POST /api/auth/login` - Login do usuário
- `POST /api/auth/register` - Registro de usuário
- `GET /api/auth/profile` - Perfil do usuário logado
- `PUT /api/auth/profile` - Atualizar perfil

#### Cursos
- `GET /api/courses` - Listar cursos
- `POST /api/courses` - Criar curso
- `GET /api/courses/{uuid}` - Detalhes do curso
- `PUT /api/courses/{uuid}` - Atualizar curso
- `POST /api/courses/{uuid}/publish` - Publicar curso
- `POST /api/courses/{uuid}/enroll` - Matricular no curso

#### Aulas
- `GET /api/courses/{uuid}/lessons` - Listar aulas
- `POST /api/courses/{uuid}/lessons` - Criar aula
- `GET /api/lessons/{uuid}` - Detalhes da aula
- `POST /api/lessons/{uuid}/complete` - Marcar aula como concluída

## 📁 Estrutura de Arquivos Integrados

```
📁 frontend/
  ├── 📄 frontend-integration.js ← API Client JavaScript
  ├── 📁 telas/
  │   ├── 📄 index.html ← Login integrado
  │   └── 📁 professor/
  │       ├── 📄 painel.html ← Dashboard principal
  │       ├── 📄 dashboard.html ← Estatísticas dinâmicas
  │       └── 📄 cursos.html ← Lista de cursos da API

📁 backend/
  ├── 📄 app.py ← Servidor Flask principal
  ├── 📄 models.py ← Modelos do banco de dados
  ├── 📄 config.py ← Configurações
  └── 📁 routes/ ← Endpoints da API
      ├── 📄 login.py ← Autenticação
      ├── 📄 professor.py ← Cursos
      ├── 📄 aluno.py ← Funcionalidades do aluno
      ├── 📄 material.py ← Upload de arquivos
      └── 📄 meus_cursos.py ← Cursos do usuário

📄 test-integration.html ← Página de teste da integração
```

## 🧪 Testando a Integração

### Método 1: Página de Teste
1. Abrir `test-integration.html` no navegador
2. Clicar em "Testar Conexão com API"
3. Fazer login com as credenciais de teste
4. Testar outras funcionalidades

### Método 2: Interface Normal
1. Abrir `frontend/telas/index.html`
2. Fazer login com `professor@cursohub.com` / `123456`
3. Navegar pelo dashboard e ver dados dinâmicos

## 🔄 Como Funciona a Integração

### 1. **Autenticação**
```javascript
// Login retorna JWT token
const response = await api.login(email, password);
localStorage.setItem('cursohub_token', response.token);
```

### 2. **Requisições Autenticadas**
```javascript
// Token é automaticamente incluído nas requisições
headers: {
  'Authorization': `Bearer ${token}`
}
```

### 3. **Carregamento Dinâmico**
```javascript
// Dashboard carrega dados da API
const courses = await api.getCourses();
document.getElementById('total-courses').textContent = courses.length;
```

## 🎯 Próximos Passos

Para expandir a integração:

1. **Página do Aluno** - Integrar `frontend/telas/aluno/`
2. **Upload de Arquivos** - Implementar upload de vídeos/materiais
3. **Analytics** - Gráficos dinâmicos com dados da API
4. **Notificações** - Sistema de feedback visual
5. **Validação** - Melhorar validação de formulários

## 🐛 Resolução de Problemas

### Erro de CORS
✅ **Já resolvido** - CORS configurado no backend

### Token Expirado
- O token expira em 24 horas
- Fazer logout e login novamente

### API não responde
- Verificar se o backend está rodando em localhost:5000
- Verificar console do navegador para erros

### Erro 404 nas rotas
- Certificar que todos os blueprints estão registrados
- Verificar se URLs estão corretas no frontend-integration.js

## 📝 Logs e Debug

- **Backend:** Logs aparecem no terminal onde rodou `python app.py`
- **Frontend:** Logs aparecem no Console do navegador (F12)
- **Rede:** Aba Network do DevTools mostra requisições HTTP

---

**🎉 Integração concluída com sucesso!** 
O CursoHub agora possui um frontend totalmente integrado com o backend Flask.
