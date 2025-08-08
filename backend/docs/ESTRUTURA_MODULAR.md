# Estrutura Modular do Backend CursoHub

## Resumo da Separação

O arquivo `backend_complete.py` foi separado em uma estrutura modular organizada da seguinte forma:

## Estrutura de Arquivos

```
├── app.py                  # Fábrica de aplicação Flask principal
├── config.py               # Configurações da aplicação
├── models.py               # Modelos de banco de dados SQLAlchemy
├── utils.py                # Funções utilitárias
├── run_modular.py          # Script de execução com estrutura modular
├── routes/                 # Módulo de rotas organizadas por funcionalidade
│   ├── __init__.py         # Inicialização do pacote
│   ├── login.py            # Rotas de autenticação (/api/auth)
│   ├── professor.py        # Rotas de cursos (/api/courses)  
│   ├── aluno.py           # Rotas de alunos (/api/students)
│   ├── material.py        # Rotas de upload (/api/upload)
│   └── meus_cursos.py     # Rotas de gerenciamento (/api/my-courses)
```

## Principais Mudanças

### 1. **app.py** - Fábrica de Aplicação
- Implementa o padrão Factory para criar a aplicação Flask
- Configuração centralizada usando blueprints
- Inicialização automática de dados padrão
- Configuração modular de extensões

### 2. **config.py** - Configurações
- Classes de configuração para desenvolvimento e produção
- Centralização de todas as configurações da aplicação
- Configurações de segurança e banco de dados

### 3. **models.py** - Modelos Atualizados
- Todos os modelos SQLAlchemy organizados
- Correção do problema com `metadata` (renomeado para `event_data`)
- Relacionamentos e métodos auxiliares mantidos

### 4. **utils.py** - Utilitários
- Funções auxiliares como `allowed_file()`
- Configurações de tipos de arquivo permitidos

### 5. **routes/** - Rotas Modulares

#### **login.py** - Autenticação
- `POST /api/auth/register` - Registro de usuários
- `POST /api/auth/login` - Login de usuários  
- `GET /api/auth/profile` - Perfil do usuário
- `PUT /api/auth/profile` - Atualizar perfil

#### **professor.py** - Gestão de Cursos
- `GET /api/courses` - Listar cursos com filtros
- `POST /api/courses` - Criar curso
- `GET /api/courses/{uuid}` - Detalhes do curso
- `PUT /api/courses/{uuid}` - Atualizar curso
- `POST /api/courses/{uuid}/enroll` - Matricular no curso
- `GET /api/courses/{uuid}/lessons` - Listar aulas
- `POST /api/courses/{uuid}/lessons` - Criar aula

#### **aluno.py** - Funcionalidades do Aluno
- `GET /api/students/my-courses` - Cursos matriculados
- `POST /api/students/lesson-progress` - Atualizar progresso
- `GET /api/students/course-progress/{uuid}` - Progresso detalhado

#### **material.py** - Upload de Arquivos
- `POST /api/upload` - Upload de arquivos
- `GET /uploads/{filename}` - Servir arquivos estáticos

#### **meus_cursos.py** - Gerenciamento de Cursos
- `GET /api/my-courses` - Meus cursos (professor/aluno)
- `GET /api/my-courses/{uuid}/students` - Alunos do curso
- `POST /api/my-courses/{uuid}/rate` - Avaliar curso
- `GET /api/my-courses/{uuid}/comments` - Comentários
- `POST /api/my-courses/{uuid}/comments` - Adicionar comentário

## Vantagens da Nova Estrutura

### ✅ **Organização**
- Código separado por responsabilidade
- Fácil manutenção e localização de funcionalidades
- Estrutura escalável para novos recursos

### ✅ **Reutilização**
- Blueprints podem ser reutilizados em diferentes aplicações
- Configurações centralizadas
- Modelos independentes da aplicação

### ✅ **Testabilidade**
- Cada módulo pode ser testado independentemente
- Fábrica de aplicação facilita testes unitários
- Mocks e stubs mais fáceis de implementar

### ✅ **Escalabilidade**
- Novos blueprints podem ser adicionados facilmente
- Configurações por ambiente (dev/prod)
- Suporte a microsserviços futuro

## Como Executar

### Opção 1: Usando a nova estrutura modular
```bash
python run_modular.py
```

### Opção 2: Usando o app.py diretamente
```bash
python app.py
```

### Opção 3: Para produção
```python
from app import create_app
app = create_app('production')
app.run()
```

## Dependências Adicionais

O projeto agora requer:
```bash
pip install flask-migrate
```

## Usuários Padrão Criados

- **Admin**: admin@cursohub.com / admin123
- **Professor**: professor@cursohub.com / 123456  
- **Aluno**: aluno@cursohub.com / 123456

## Próximos Passos Recomendados

1. **Testes Unitários**: Criar testes para cada blueprint
2. **Documentação da API**: Implementar Swagger/OpenAPI
3. **Logging Avançado**: Configurar logs estruturados
4. **Cache**: Implementar Redis para performance
5. **Validação**: Adicionar Marshmallow para validação de dados

A nova estrutura mantém toda a funcionalidade original do `backend_complete.py` mas organizada de forma mais profissional e escalável.
