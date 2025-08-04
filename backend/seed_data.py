from app import app, db
from models import User, Course, Lesson, Material, Comment, Rating
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_database():
    """Popular o banco de dados com dados de exemplo"""
    
    with app.app_context():
        # Limpar dados existentes (cuidado em produção!)
        db.drop_all()
        db.create_all()
        
        print("🌱 Iniciando população do banco de dados...")
        
        # ==================== USUÁRIOS ====================
        users_data = [
            {
                'name': 'Administrador',
                'email': 'admin@cursohub.com',
                'password': 'admin123',
                'role': 'admin',
                'bio': 'Administrador da plataforma CursoHub'
            },
            {
                'name': 'Prof. João Silva',
                'email': 'joao@cursohub.com',
                'password': 'professor123',
                'role': 'teacher',
                'bio': 'Professor de Matemática com 15 anos de experiência. Especialista em ensino fundamental e médio.'
            },
            {
                'name': 'Prof. Maria Santos',
                'email': 'maria@cursohub.com',
                'password': 'professor123',
                'role': 'teacher',
                'bio': 'Professora de Física e Química. Doutora em Ciências pela USP.'
            },
            {
                'name': 'Prof. Carlos Oliveira',
                'email': 'carlos@cursohub.com',
                'password': 'professor123',
                'role': 'teacher',
                'bio': 'Professor de Programação e Desenvolvimento Web. Full Stack Developer há 10 anos.'
            },
            {
                'name': 'Ana Costa',
                'email': 'ana@email.com',
                'password': 'aluno123',
                'role': 'student',
                'bio': 'Estudante de Engenharia apaixonada por matemática e programação.'
            },
            {
                'name': 'Pedro Mendes',
                'email': 'pedro@email.com',
                'password': 'aluno123',
                'role': 'student',
                'bio': 'Estudante do ensino médio com interesse em ciências exatas.'
            },
            {
                'name': 'Julia Ferreira',
                'email': 'julia@email.com',
                'password': 'aluno123',
                'role': 'student',
                'bio': 'Estudante de Design interessada em desenvolvimento web.'
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                role=user_data['role'],
                bio=user_data['bio']
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ Criados {len(users)} usuários")
        
        # ==================== CURSOS ====================
        # Buscar professores
        joao = User.query.filter_by(email='joao@cursohub.com').first()
        maria = User.query.filter_by(email='maria@cursohub.com').first()
        carlos = User.query.filter_by(email='carlos@cursohub.com').first()
        
        courses_data = [
            {
                'title': 'Matemática Básica - Fundamentos',
                'description': 'Curso completo de matemática básica cobrindo aritmética, álgebra básica, geometria e estatística fundamental. Ideal para estudantes do ensino fundamental e médio que querem reforçar sua base matemática.',
                'category': 'Matemática',
                'level': 'beginner',
                'price': 0.0,
                'creator': joao,
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Física Aplicada - Mecânica',
                'description': 'Estudo completo da mecânica clássica incluindo cinemática, dinâmica, trabalho e energia. Com exercícios práticos e simulações.',
                'category': 'Física',
                'level': 'intermediate',
                'price': 49.90,
                'creator': maria,
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Química Orgânica Essencial',
                'description': 'Introdução à química orgânica com foco em estruturas moleculares, nomenclatura e reações químicas básicas.',
                'category': 'Química',
                'level': 'intermediate',
                'price': 39.90,
                'creator': maria,
                'is_published': True
            },
            {
                'title': 'Desenvolvimento Web Completo',
                'description': 'Aprenda a criar sites e aplicações web do zero usando HTML, CSS, JavaScript, e frameworks modernos como React.',
                'category': 'Programação',
                'level': 'beginner',
                'price': 99.90,
                'creator': carlos,
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Python para Iniciantes',
                'description': 'Curso introdutório de programação em Python cobrindo sintaxe básica, estruturas de dados e programação orientada a objetos.',
                'category': 'Programação',
                'level': 'beginner',
                'price': 79.90,
                'creator': carlos,
                'is_published': True
            },
            {
                'title': 'Álgebra Linear Avançada',
                'description': 'Curso avançado de álgebra linear para estudantes de engenharia e ciências exatas.',
                'category': 'Matemática',
                'level': 'advanced',
                'price': 69.90,
                'creator': joao,
                'is_published': False  # Curso em desenvolvimento
            }
        ]
        
        courses = []
        for course_data in courses_data:
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                category=course_data['category'],
                level=course_data['level'],
                price=course_data['price'],
                creator_id=course_data['creator'].id,
                is_published=course_data['is_published'],
                is_featured=course_data.get('is_featured', False),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            
            if course_data['is_published']:
                course.published_at = course.created_at + timedelta(days=1)
            
            courses.append(course)
            db.session.add(course)
        
        db.session.commit()
        print(f"✅ Criados {len(courses)} cursos")
        
        # ==================== AULAS ====================
        lessons_data = {
            'Matemática Básica - Fundamentos': [
                {'title': 'Introdução aos Números', 'description': 'Conceitos básicos sobre números naturais, inteiros e racionais', 'video_duration': 900, 'is_free': True},
                {'title': 'Operações Básicas', 'description': 'Adição, subtração, multiplicação e divisão', 'video_duration': 1200, 'is_free': True},
                {'title': 'Frações e Números Decimais', 'description': 'Como trabalhar com frações e converter para decimais', 'video_duration': 1500},
                {'title': 'Porcentagem', 'description': 'Cálculos percentuais e aplicações práticas', 'video_duration': 1000},
                {'title': 'Equações do 1º Grau', 'description': 'Resolução de equações lineares', 'video_duration': 1800}
            ],
            'Física Aplicada - Mecânica': [
                {'title': 'Introdução à Mecânica', 'description': 'Conceitos fundamentais de movimento e força', 'video_duration': 1200, 'is_free': True},
                {'title': 'Cinemática Escalar', 'description': 'Estudo do movimento em uma dimensão', 'video_duration': 1800},
                {'title': 'Cinemática Vetorial', 'description': 'Movimento em duas e três dimensões', 'video_duration': 2100},
                {'title': 'Leis de Newton', 'description': 'As três leis fundamentais da mecânica', 'video_duration': 1500},
                {'title': 'Trabalho e Energia', 'description': 'Conceitos de trabalho, energia cinética e potencial', 'video_duration': 1900}
            ],
            'Desenvolvimento Web Completo': [
                {'title': 'Introdução ao Desenvolvimento Web', 'description': 'Visão geral das tecnologias web', 'video_duration': 800, 'is_free': True},
                {'title': 'HTML Fundamentals', 'description': 'Estrutura básica de páginas web', 'video_duration': 1500, 'is_free': True},
                {'title': 'CSS Styling', 'description': 'Estilização e layout com CSS', 'video_duration': 2000},
                {'title': 'JavaScript Basics', 'description': 'Programação client-side com JavaScript', 'video_duration': 2400},
                {'title': 'React Introduction', 'description': 'Introdução ao framework React', 'video_duration': 1800},
                {'title': 'Building Your First App', 'description': 'Criando uma aplicação web completa', 'video_duration': 3000}
            ]
        }
        
        lesson_count = 0
        for course in courses:
            if course.title in lessons_data:
                for i, lesson_data in enumerate(lessons_data[course.title]):
                    lesson = Lesson(
                        title=lesson_data['title'],
                        description=lesson_data['description'],
                        content=f"Conteúdo detalhado da aula: {lesson_data['title']}. Este é um exemplo de conteúdo texto que acompanha o vídeo da aula.",
                        video_url=f"https://www.youtube.com/embed/dQw4w9WgXcQ?t={random.randint(1, 100)}",
                        video_duration=lesson_data['video_duration'],
                        order_index=i + 1,
                        course_id=course.id,
                        is_free=lesson_data.get('is_free', False)
                    )
                    db.session.add(lesson)
                    lesson_count += 1
        
        db.session.commit()
        print(f"✅ Criadas {lesson_count} aulas")
        
        # ==================== MATRÍCULAS ====================
        # Matricular alguns alunos nos cursos
        students = User.query.filter_by(role='student').all()
        published_courses = Course.query.filter_by(is_published=True).all()
        
        enrollments = 0
        for student in students:
            # Cada aluno se matricula em 2-4 cursos aleatórios
            num_courses = random.randint(2, min(4, len(published_courses)))
            selected_courses = random.sample(published_courses, num_courses)
            
            for course in selected_courses:
                if course not in student.enrolled_courses:
                    student.enrolled_courses.append(course)
                    enrollments += 1
        
        db.session.commit()
        print(f"✅ Criadas {enrollments} matrículas")
        
        # ==================== COMENTÁRIOS ====================
        comments_data = [
            "Excelente curso! Muito didático e bem explicado.",
            "Professor, poderia dar mais exemplos práticos?",
            "Ótima qualidade de vídeo e áudio. Parabéns!",
            "Conteúdo muito bom, mas gostaria de exercícios mais desafiadores.",
            "Curso essencial para quem está começando. Recomendo!",
            "As explicações são claras e fáceis de entender.",
            "Poderia ter mais materiais complementares?",
            "Estou aprendendo muito! Obrigado professor.",
        ]
        
        comment_count = 0
        for course in published_courses[:3]:  # Comentários nos primeiros 3 cursos
            for student in students:
                if random.random() < 0.6:  # 60% chance de comentar
                    comment = Comment(
                        content=random.choice(comments_data),
                        course_id=course.id,
                        author_id=student.id,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
                    )
                    db.session.add(comment)
                    comment_count += 1
        
        db.session.commit()
        print(f"✅ Criados {comment_count} comentários")
        
        # ==================== AVALIAÇÕES ====================
        rating_count = 0
        for course in published_courses:
            for student in students:
                if course in student.enrolled_courses and random.random() < 0.7:  # 70% chance de avaliar
                    rating = Rating(
                        rating=random.randint(3, 5),  # Notas entre 3 e 5
                        comment=random.choice([
                            "Curso muito bom!",
                            "Recomendo para todos.",
                            "Excelente conteúdo.",
                            "Professor muito didático.",
                            "Aprendi muito!",
                            ""
                        ]),
                        course_id=course.id,
                        author_id=student.id
                    )
                    db.session.add(rating)
                    rating_count += 1
        
        db.session.commit()
        print(f"✅ Criadas {rating_count} avaliações")
        
        # ==================== RESUMO ====================
        print("\n🎉 Banco de dados populado com sucesso!")
        print(f"📊 Resumo:")
        print(f"   • {len(users)} usuários")
        print(f"   • {len(courses)} cursos")
        print(f"   • {lesson_count} aulas")
        print(f"   • {enrollments} matrículas")
        print(f"   • {comment_count} comentários")
        print(f"   • {rating_count} avaliações")
        
        print("\n👤 Usuários de teste:")
        print("   • Admin: admin@cursohub.com / admin123")
        print("   • Professor: joao@cursohub.com / professor123")
        print("   • Professor: maria@cursohub.com / professor123")
        print("   • Professor: carlos@cursohub.com / professor123")
        print("   • Aluno: ana@email.com / aluno123")
        print("   • Aluno: pedro@email.com / aluno123")
        print("   • Aluno: julia@email.com / aluno123")

if __name__ == '__main__':
    seed_database()