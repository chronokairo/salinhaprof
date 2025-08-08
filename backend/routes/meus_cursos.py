from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Course, Lesson, StudentProgress, Rating, Comment
from sqlalchemy import desc

my_courses_bp = Blueprint('my_courses', __name__, url_prefix='/api/my-courses')

@my_courses_bp.route('', methods=['GET'])
@jwt_required()
def get_my_courses():
    """Obter todos os cursos do usuário (criados se professor, matriculados se aluno)"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.role in ['teacher', 'admin']:
            # Professor: cursos criados
            courses = Course.query.filter_by(creator_id=user.id).order_by(desc(Course.created_at)).all()
            courses_data = [course.to_dict(include_stats=True) for course in courses]
        else:
            # Aluno: cursos matriculados com progresso
            enrolled_courses = user.enrolled_courses
            courses_data = []
            
            for course in enrolled_courses:
                # Calcular progresso
                total_lessons = len(course.lessons)
                completed_lessons = 0
                
                if total_lessons > 0:
                    for lesson in course.lessons:
                        progress = StudentProgress.query.filter_by(
                            user_id=user.id,
                            lesson_id=lesson.id,
                            is_completed=True
                        ).first()
                        if progress:
                            completed_lessons += 1
                    
                    progress_percentage = int((completed_lessons / total_lessons) * 100)
                else:
                    progress_percentage = 0
                
                course_dict = course.to_dict(include_stats=True)
                course_dict['progress'] = {
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'percentage': progress_percentage
                }
                courses_data.append(course_dict)
        
        return jsonify({'courses': courses_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@my_courses_bp.route('/<course_uuid>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_uuid):
    """Obter alunos matriculados em um curso (apenas para professores)"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Verificar permissão
        if course.creator_id != user.id and user.role != 'admin':
            return jsonify({'error': 'Sem permissão para ver alunos deste curso'}), 403
        
        # Obter alunos com progresso
        students_data = []
        for student in course.students:
            # Calcular progresso do aluno
            total_lessons = len(course.lessons)
            completed_lessons = 0
            
            if total_lessons > 0:
                for lesson in course.lessons:
                    progress = StudentProgress.query.filter_by(
                        user_id=student.id,
                        lesson_id=lesson.id,
                        is_completed=True
                    ).first()
                    if progress:
                        completed_lessons += 1
                
                progress_percentage = int((completed_lessons / total_lessons) * 100)
            else:
                progress_percentage = 0
            
            student_dict = student.to_dict()
            student_dict['progress'] = {
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'percentage': progress_percentage
            }
            students_data.append(student_dict)
        
        return jsonify({'students': students_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@my_courses_bp.route('/<course_uuid>/rate', methods=['POST'])
@jwt_required()
def rate_course(course_uuid):
    """Avaliar um curso"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Verificar se está matriculado
        if course not in user.enrolled_courses:
            return jsonify({'error': 'Usuário não matriculado neste curso'}), 403
        
        data = request.get_json()
        rating_value = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating_value or rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'Avaliação deve ser entre 1 e 5 estrelas'}), 400
        
        # Verificar se já avaliou
        existing_rating = Rating.query.filter_by(
            user_id=user.id,
            course_id=course.id
        ).first()
        
        if existing_rating:
            # Atualizar avaliação existente
            existing_rating.value = rating_value
            existing_rating.comment = comment
        else:
            # Criar nova avaliação
            rating = Rating(
                value=rating_value,
                comment=comment,
                user_id=user.id,
                course_id=course.id
            )
            db.session.add(rating)
        
        db.session.commit()
        
        return jsonify({'message': 'Avaliação salva com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@my_courses_bp.route('/<course_uuid>/comments', methods=['GET'])
def get_course_comments(course_uuid):
    """Obter comentários de um curso"""
    try:
        course = Course.query.filter_by(uuid=course_uuid).first()
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        comments = Comment.query.filter_by(
            course_id=course.id,
            parent_id=None  # Apenas comentários principais
        ).order_by(desc(Comment.created_at)).all()
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@my_courses_bp.route('/<course_uuid>/comments', methods=['POST'])
@jwt_required()
def add_course_comment(course_uuid):
    """Adicionar comentário a um curso"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        data = request.get_json()
        content = data.get('content')
        parent_uuid = data.get('parent_uuid')
        
        if not content:
            return jsonify({'error': 'Conteúdo é obrigatório'}), 400
        
        parent_id = None
        if parent_uuid:
            parent_comment = Comment.query.filter_by(uuid=parent_uuid).first()
            if parent_comment:
                parent_id = parent_comment.id
        
        comment = Comment(
            content=content,
            user_id=user.id,
            course_id=course.id,
            parent_id=parent_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comentário adicionado com sucesso',
            'comment': comment.to_dict(include_replies=False)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500