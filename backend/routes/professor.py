from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, or_
from backend.models import db, User, Course, Lesson
from sqlalchemy import func

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@courses_bp.route('', methods=['GET'])
def get_courses():
    """Listar cursos com filtros e paginação"""
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        category = request.args.get('category')
        level = request.args.get('level')
        search = request.args.get('search')
        featured = request.args.get('featured', type=bool)
        creator_uuid = request.args.get('creator')
        
        # Query base
        query = Course.query.filter_by(is_published=True)
        
        # Filtros
        if category:
            query = query.filter_by(category=category)
        if level:
            query = query.filter_by(level=level)
        if search:
            query = query.filter(
                or_(
                    Course.title.contains(search),
                    Course.description.contains(search)
                )
            )
        if featured:
            query = query.filter_by(is_featured=True)
        if creator_uuid:
            creator = User.query.filter_by(uuid=creator_uuid).first()
            if creator:
                query = query.filter_by(creator_id=creator.id)
        
        # Ordenação
        query = query.order_by(desc(Course.created_at))
        
        # Paginação
        courses = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'courses': [course.to_dict(include_stats=True) for course in courses.items],
            'pagination': {
                'page': page,
                'pages': courses.pages,
                'per_page': per_page,
                'total': courses.total,
                'has_next': courses.has_next,
                'has_prev': courses.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_uuid>', methods=['GET'])
def get_course(course_uuid):
    """Obter detalhes de um curso específico"""
    try:
        course = Course.query.filter_by(uuid=course_uuid, is_published=True).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        return jsonify({'course': course.to_dict(include_lessons=True, include_stats=True)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('', methods=['POST'])
@jwt_required()
def create_course():
    """Criar novo curso"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Sem permissão para criar cursos'}), 403
        
        data = request.get_json()
        
        # Validações
        if not data.get('title'):
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        course = Course(
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category'),
            level=data.get('level', 'beginner'),
            price=data.get('price', 0.0),
            creator_id=user.id
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Curso criado com sucesso',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_uuid>', methods=['PUT'])
@jwt_required()
def update_course(course_uuid):
    """Atualizar curso"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Verificar permissão
        if course.creator_id != user.id and user.role != 'admin':
            return jsonify({'error': 'Sem permissão para editar este curso'}), 403
        
        data = request.get_json()
        
        # Atualizar campos
        if data.get('title'):
            course.title = data['title']
        if data.get('description'):
            course.description = data['description']
        if data.get('category'):
            course.category = data['category']
        if data.get('level'):
            course.level = data['level']
        if 'price' in data:
            course.price = data['price']
        if 'thumbnail_url' in data:
            course.thumbnail_url = data['thumbnail_url']
        if 'is_published' in data:
            course.is_published = data['is_published']
        if 'is_featured' in data and user.role == 'admin':
            course.is_featured = data['is_featured']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Curso atualizado com sucesso',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_uuid>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(course_uuid):
    """Matricular usuário em um curso"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        course = Course.query.filter_by(uuid=course_uuid, is_published=True).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Verificar se já está matriculado
        if course in user.enrolled_courses:
            return jsonify({'error': 'Usuário já matriculado neste curso'}), 409
        
        # Matricular usuário
        user.enrolled_courses.append(course)
        db.session.commit()
        
        return jsonify({'message': 'Matrícula realizada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_uuid>/lessons', methods=['GET'])
def get_lessons(course_uuid):
    """Listar aulas de um curso"""
    try:
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Ordenar por order_index
        lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order_index).all()
        
        return jsonify({
            'lessons': [lesson.to_dict() for lesson in lessons]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_uuid>/lessons', methods=['POST'])
@jwt_required()
def create_lesson(course_uuid):
    """Criar nova aula em um curso"""
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Verificar permissão
        if course.creator_id != user.id and user.role != 'admin':
            return jsonify({'error': 'Sem permissão para criar aulas neste curso'}), 403
        
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        # Calcular próximo order_index
        max_order = db.session.query(func.max(Lesson.order_index)).filter_by(course_id=course.id).scalar() or 0
        
        lesson = Lesson(
            title=data['title'],
            description=data.get('description', ''),
            content=data.get('content', ''),
            video_url=data.get('video_url'),
            video_duration=data.get('video_duration', 0),
            order_index=max_order + 1,
            course_id=course.id,
            is_free=data.get('is_free', False)
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        return jsonify({
            'message': 'Aula criada com sucesso',
            'lesson': lesson.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500