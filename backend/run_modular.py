# Arquivo de exemplo para demonstrar a nova estrutura modular

from backend.app import create_app

# Criar aplicação com configuração de desenvolvimento
app = create_app('development')

if __name__ == '__main__':
    print("Executando CursoHub com nova estrutura modular...")
    print("\nEstrutura de arquivos:")
    print("├── app.py               # Fábrica de aplicação Flask")
    print("├── config.py            # Configurações da aplicação")
    print("├── models.py            # Modelos de banco de dados")
    print("├── utils.py             # Funções utilitárias")
    print("├── routes/")
    print("│   ├── __init__.py      # Pacote de rotas")
    print("│   ├── login.py         # Rotas de autenticação")
    print("│   ├── professor.py     # Rotas de cursos")
    print("│   ├── aluno.py         # Rotas de alunos")
    print("│   ├── material.py      # Rotas de upload")
    print("│   └── meus_cursos.py   # Rotas de gerenciamento de cursos")
    print("\nEndpoints disponíveis:")
    print("• POST /api/auth/register      - Registro de usuários")
    print("• POST /api/auth/login         - Login de usuários")
    print("• GET  /api/auth/profile       - Perfil do usuário")
    print("• GET  /api/courses            - Listar cursos")
    print("• POST /api/courses            - Criar curso")
    print("• GET  /api/courses/{uuid}     - Detalhes do curso")
    print("• POST /api/courses/{uuid}/enroll - Matricular no curso")
    print("• GET  /api/my-courses         - Meus cursos")
    print("• POST /api/upload             - Upload de arquivos")
    print("• GET  /api/students/my-courses - Cursos do aluno")
    print("\n" + "="*50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
