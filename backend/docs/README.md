# CursoHub - Plataforma de Cursos Online

Uma plataforma completa para criação e gerenciamento de cursos online, desenvolvida com Flask (backend) e HTML/CSS/JavaScript (frontend).

## 🚀 Funcionalidades

### Para Professores
- ✅ Criação e gerenciamento de cursos
- ✅ Upload de vídeos e materiais
- ✅ Organização de aulas em sequência
- ✅ Publicação de cursos
- ✅ Acompanhamento de progresso dos alunos

### Para Alunos
- ✅ Navegação e busca de cursos
- ✅ Matrícula em cursos
- ✅ Assistir aulas online
- ✅ Acompanhamento de progresso
- ✅ Sistema de comentários

### Para Administradores
- ✅ Gerenciamento completo de usuários
- ✅ Moderação de cursos
- ✅ Analytics e relatórios
- ✅ Configurações da plataforma

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Navegador web moderno

### Passo a Passo

1. **Configure o Python e dependências**:
   ```bash
   python setup.py
   ```

2. **Inicie o backend**:
   ```bash
   python backend_complete.py
   ```

3. **Abra o frontend**:
   - Abra `index.html` no navegador
   - Ou use um servidor local: `python -m http.server 8080`

## 🔑 Usuários de Teste

O sistema já vem com usuários pré-configurados para testes:

| Tipo | Email | Senha | Descrição |
|------|--------|--------|------------|
| **Professor** | professor@cursohub.com | 123456 | Pode criar e gerenciar cursos |
| **Aluno** | aluno@cursohub.com | 123456 | Pode se matricular e assistir cursos |
| **Admin** | admin@cursohub.com | admin123 | Acesso completo ao sistema |

## 🌐 Endpoints da API

### Autenticação
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/register` - Cadastro de usuário
- `GET /api/auth/profile` - Obter perfil do usuário

### Cursos
- `GET /api/courses` - Listar cursos públicos
- `GET /api/courses/{uuid}` - Obter curso específico
- `POST /api/courses` - Criar novo curso (professor)
- `POST /api/courses/{uuid}/enroll` - Matricular-se em curso

### Aulas
- `GET /api/courses/{uuid}/lessons` - Listar aulas do curso
- `POST /api/courses/{uuid}/lessons` - Criar aula (professor)

### Upload
- `POST /api/upload` - Upload de arquivos (vídeos, materiais)

## 🎯 Como Usar

### 1. Acesso inicial
1. Abra `index.html` no navegador
2. Clique em "Começar Gratuitamente" ou acesse `/telas/index.html`
3. Use as credenciais de teste para fazer login

### 2. Como Professor
1. Faça login com `professor@cursohub.com / 123456`
2. Acesse o painel do professor
3. Crie um novo curso preenchendo título, descrição, categoria
4. Adicione aulas com vídeos e materiais
5. Publique o curso quando estiver pronto

### 3. Como Aluno
1. Faça login com `aluno@cursohub.com / 123456`
2. Navegue pelos cursos disponíveis
3. Clique em "Matricular-se" em um curso de interesse
4. Acesse as aulas e acompanhe seu progresso

### 4. Testando a API
```bash
# Teste básico da API
curl http://localhost:5000/

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"professor@cursohub.com","password":"123456"}'

# Listar cursos
curl http://localhost:5000/api/courses
```

## 🗂️ Estrutura de Arquivos

```
salinhaprof/
├── backend_complete.py      # Backend Flask completo
├── requirements.txt         # Dependências Python
├── setup.py                # Script de configuração
├── frontend-integration.js # Integração frontend/backend
├── index.html              # Página principal
├── telas/                  # Páginas da aplicação
│   ├── index.html          # Login
│   ├── professor/          # Painel do professor
│   └── aluno/              # Painel do aluno
├── styles/                 # Arquivos CSS
├── uploads/                # Arquivos enviados (criado automaticamente)
└── cursohub.db            # Banco SQLite (criado automaticamente)
```

## 🔧 Desenvolvimento

### Banco de Dados
- **SQLite** para desenvolvimento (arquivo `cursohub.db`)
- **Modelos**: User, Course, Lesson
- **Relacionamentos**: Many-to-many entre Users e Courses

### Frontend
- **HTML/CSS/JavaScript** puro
- **Design responsivo** com Tailwind-like classes
- **Integração via API** REST

### Backend
- **Flask** com extensões essenciais
- **JWT** para autenticação
- **SQLAlchemy** para ORM
- **CORS** habilitado para desenvolvimento

## 🚀 Deploy (Produção)

Para colocar em produção:

1. **Configure variáveis de ambiente**:
   ```bash
   export SECRET_KEY="sua-chave-super-secreta"
   export DATABASE_URL="postgresql://user:pass@host/db"
   ```

2. **Use um servidor WSGI**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend_complete:app
   ```

3. **Configure um proxy reverso** (Nginx)

## 🐛 Solução de Problemas

### Backend não inicia
- Verifique se as dependências estão instaladas: `pip install -r requirements.txt`
- Verifique se a porta 5000 está livre

### Frontend não conecta com backend
- Verifique se o backend está rodando em `http://localhost:5000`
- Abra o console do navegador para ver erros de CORS

### Erro de banco de dados
- Delete o arquivo `cursohub.db` e reinicie o backend
- O banco será recriado automaticamente

## 📝 Próximos Passos

- [ ] Sistema de pagamentos
- [ ] Notificações por email
- [ ] Chat em tempo real
- [ ] Sistema de certificados
- [ ] App mobile
- [ ] Analytics avançados

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ para educação online**
