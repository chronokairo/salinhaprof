# CursoHub Backend API

API REST para a plataforma de cursos online CursoHub, desenvolvida em Python com Flask.

## 🚀 Tecnologias

- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **Flask-JWT-Extended** - Autenticação JWT
- **Flask-CORS** - Configuração de CORS
- **SQLite/PostgreSQL** - Banco de dados
- **Werkzeug** - Utilitários web

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Configuração

1. **Clone o repositório** (se ainda não fez):
```bash
git clone <repository-url>
cd salinhaprof2/backend
```

2. **Crie um ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente** (opcional):
```bash
export SECRET_KEY="sua-chave-secreta-super-segura"
export JWT_SECRET_KEY="jwt-chave-secreta"
export DATABASE_URL="sqlite:///cursohub.db"
```

5. **Execute a aplicação**:
```bash
python app.py
```

O servidor estará rodando em `http://localhost:5000`

## 🗄️ Banco de Dados

### Inicialização
O banco de dados SQLite será criado automaticamente quando você executar a aplicação pela primeira vez.

### Popular com dados de exemplo
```bash
python seed_data.py
```

Este comando criará usuários, cursos, aulas e outros dados de exemplo para testar a API.

## 👤 Usuários de Teste

Após executar o `seed_data.py`, você terá os seguintes usuários:

| Tipo | Email | Senha | Descrição |
|------|-------|-------|-----------|
| Admin | admin@cursohub.com | admin123 | Administrador |
| Professor | joao@cursohub.com | professor123 | Prof. de Matemática |
| Professor | maria@cursohub.com | professor123 | Prof. de Física/Química |
| Professor | carlos@cursohub.com | professor123 | Prof. de Programação |
| Aluno | ana@email.com | aluno123 | Estudante |
| Aluno | pedro@email.com | aluno123 | Estudante |
| Aluno | julia@email.com | aluno123 | Estudante |

## 📋 Endpoints da API

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Obter perfil (autenticado)
- `PUT /api/auth/profile` - Atualizar perfil (autenticado)

### Cursos
- `GET /api/courses` - Listar cursos
- `GET /api/courses/<uuid>` - Obter curso específico
- `POST /api/courses` - Criar curso (professor/admin)
- `PUT /api/courses/<uuid>` - Atualizar curso (criador/admin)
- `POST /api/courses/<uuid>/publish` - Publicar curso
- `POST /api/courses/<uuid>/enroll` - Matricular-se (autenticado)

### Aulas
- `GET /api/courses/<uuid>/lessons` - Listar aulas do curso
- `POST /api/courses/<uuid>/lessons` - Criar aula (criador/admin)
- `GET /api/lessons/<uuid>` - Obter aula específica (autenticado)
- `POST /api/lessons/<uuid>/complete` - Marcar aula como concluída

### Comentários
- `GET /api/courses/<uuid>/comments` - Obter comentários do curso
- `POST /api/courses/<uuid>/comments` - Criar comentário (autenticado)

### Avaliações
- `POST /api/courses/<uuid>/rating` - Avaliar curso (autenticado)

### Progresso
- `GET /api/courses/<uuid>/progress` - Obter progresso no curso (autenticado)

### Analytics
- `GET /api/analytics/dashboard` - Dashboard de analytics (professor/admin)

### Upload
- `POST /api/upload` - Upload de arquivos (autenticado)

### Utilitários
- `GET /api/health` - Health check
- `GET /api/stats` - Estatísticas gerais

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação. Para acessar endpoints protegidos:

1. Faça login em `/api/auth/login`
2. Use o `access_token` retornado no header `Authorization: Bearer <token>`

### Exemplo de uso:

```javascript
// Login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'joao@cursohub.com',
    password: 'professor123'
  })
});

const { access_token } = await loginResponse.json();

// Usar token em requisições protegidas
const profileResponse = await fetch('/api/auth/profile', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 📊 Modelos de Dados

### User
- Informações do usuário (aluno, professor, admin)
- Autenticação e autorização
- Cursos criados e matriculados

### Course
- Informações do curso
- Relacionamento com criador e alunos
- Status de publicação

### Lesson
- Aulas dentro dos cursos
- Conteúdo, vídeos e materiais
- Ordem sequencial

### Comment
- Comentários em cursos
- Sistema de respostas (threading)

### Rating
- Avaliações de cursos (1-5 estrelas)
- Comentários opcionais

### StudentProgress
- Progresso individual do aluno
- Aulas completadas e tempo assistido

### Analytics
- Eventos de uso da plataforma
- Métricas para relatórios

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Segurança
SECRET_KEY=sua-chave-secreta-super-segura
JWT_SECRET_KEY=jwt-chave-secreta

# Banco de dados
DATABASE_URL=sqlite:///cursohub.db
# ou para PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/cursohub

# Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Configurações por Ambiente

O arquivo `config.py` contém configurações para:
- **Development** - Desenvolvimento local
- **Production** - Produção
- **Testing** - Testes automatizados

## 🚀 Deploy em Produção

### Usando Gunicorn

```bash
# Instalar Gunicorn
pip install gunicorn

# Executar aplicação
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (opcional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📈 Monitoramento

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Estatísticas
```bash
curl http://localhost:5000/api/stats
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
backend/
├── app.py              # Aplicação principal
├── models.py           # Modelos de dados
├── routes.py           # Endpoints da API
├── config.py           # Configurações
├── seed_data.py        # Dados de exemplo
├── requirements.txt    # Dependências
├── uploads/            # Arquivos enviados
│   ├── videos/
│   ├── materials/
│   └── avatars/
└── README.md          # Esta documentação
```

### Comandos Úteis

```bash
# Executar em modo debug
python app.py

# Popular banco com dados de exemplo
python seed_data.py

# Instalar nova dependência
pip install <package>
pip freeze > requirements.txt
```

## 🐛 Resolução de Problemas

### Erro de CORS
- Certifique-se de que o frontend está na lista `CORS_ORIGINS`
- Verifique se o Flask-CORS está configurado corretamente

### Erro de Banco de Dados
- Verifique se o arquivo do banco SQLite tem permissões corretas
- Para PostgreSQL, confirme a string de conexão

### Token JWT Inválido
- Verifique se o token não expirou (24h por padrão)
- Confirme se está enviando o header `Authorization: Bearer <token>`

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ para o CursoHub**