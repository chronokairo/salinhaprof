from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Course, Lesson, StudentProgress
from datetime import datetime

students_bp = Blueprint('students', __name__, url_prefix='/api/students')

@students_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """Obter cursos do aluno logado"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Obter cursos matriculados
        enrolled_courses = user.enrolled_courses
        
        courses_data = []
        for course in enrolled_courses:
            # Calcular progresso do curso
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

@students_bp.route('/lesson-progress', methods=['POST'])
@jwt_required()
def update_lesson_progress():
    """Atualizar progresso de uma aula"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        lesson_uuid = data.get('lesson_uuid')
        watch_time = data.get('watch_time', 0)
        is_completed = data.get('is_completed', False)
        
        if not lesson_uuid:
            return jsonify({'error': 'UUID da aula é obrigatório'}), 400
        
        lesson = Lesson.query.filter_by(uuid=lesson_uuid).first()
        if not lesson:
            return jsonify({'error': 'Aula não encontrada'}), 404
        
        # Verificar se o usuário está matriculado no curso
        if lesson.course not in user.enrolled_courses:
            return jsonify({'error': 'Usuário não matriculado neste curso'}), 403
        
        # Buscar ou criar progresso
        progress = StudentProgress.query.filter_by(
            user_id=user.id,
            lesson_id=lesson.id
        ).first()
        
        if not progress:
            progress = StudentProgress(
                user_id=user.id,
                lesson_id=lesson.id
            )
            db.session.add(progress)
        
        # Atualizar progresso
        progress.watch_time = watch_time
        if is_completed and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progresso atualizado com sucesso',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/course-progress/<course_uuid>', methods=['GET'])
@jwt_required()
def get_course_progress(course_uuid):
    """Obter progresso detalhado de um curso"""
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
        
        # Obter progresso de todas as aulas
        lessons_progress = []
        for lesson in course.lessons:
            progress = StudentProgress.query.filter_by(
                user_id=user.id,
                lesson_id=lesson.id
            ).first()
            
            lesson_dict = lesson.to_dict()
            if progress:
                lesson_dict['progress'] = progress.to_dict()
            else:
                lesson_dict['progress'] = {
                    'is_completed': False,
                    'watch_time': 0,
                    'completed_at': None
                }
            
            lessons_progress.append(lesson_dict)
        
        return jsonify({
            'course': course.to_dict(),
            'lessons': lessons_progress
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500