from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from app import app, db
from models import *
import os
from datetime import datetime

# Utilitários
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_analytics(event_type, user_id=None, course_id=None, lesson_id=None, metadata=None):
    """Log analytics events"""
    analytics = Analytics(
        event_type=event_type,
        user_id=user_id,
        course_id=course_id,
        lesson_id=lesson_id,
        metadata=metadata
    )
    db.session.add(analytics)
    db.session.commit()

# ==================== AUTENTICAÇÃO ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
        
        # Verificar se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Criar usuário
        user = User(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=data.get('role', 'student'),
            bio=data.get('bio', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Gerar token
        access_token = create_access_token(identity=user.uuid)
        
        # Log analytics
        log_analytics('user_registered', user_id=user.id)
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Conta desativada'}), 401
        
        access_token = create_access_token(identity=user.uuid)
        
        # Log analytics
        log_analytics('user_login', user_id=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'name' in data:
            user.name = data['name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'avatar' in data:
            user.avatar = data['avatar']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CURSOS ====================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        level = request.args.get('level')
        search = request.args.get('search')
        featured = request.args.get('featured', type=bool)
        
        # Query base
        query = Course.query.filter_by(is_published=True)
        
        # Filtros
        if category:
            query = query.filter_by(category=category)
        if level:
            query = query.filter_by(level=level)
        if search:
            query = query.filter(Course.title.contains(search) | Course.description.contains(search))
        if featured:
            query = query.filter_by(is_featured=True)
        
        # Ordenação
        query = query.order_by(desc(Course.created_at))
        
        # Paginação
        courses = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Log analytics
        log_analytics('courses_viewed', metadata={'page': page, 'filters': request.args.to_dict()})
        
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

@app.route('/api/courses/<course_uuid>', methods=['GET'])
def get_course(course_uuid):
    try:
        course = Course.query.filter_by(uuid=course_uuid, is_published=True).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Log analytics
        log_analytics('course_viewed', course_id=course.id)
        
        return jsonify({'course': course.to_dict(include_lessons=True, include_stats=True)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses', methods=['POST'])
@jwt_required()
def create_course():
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
        
        # Log analytics
        log_analytics('course_created', user_id=user.id, course_id=course.id)
        
        return jsonify({
            'message': 'Curso criado com sucesso',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_uuid>', methods=['PUT'])
@jwt_required()
def update_course(course_uuid):
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
            return jsonify({'error': 'Sem permissão para editar este curso'}), 403
        
        data = request.get_json()
        
        # Atualizar campos
        if 'title' in data:
            course.title = data['title']
        if 'description' in data:
            course.description = data['description']
        if 'category' in data:
            course.category = data['category']
        if 'level' in data:
            course.level = data['level']
        if 'price' in data:
            course.price = data['price']
        if 'thumbnail' in data:
            course.thumbnail = data['thumbnail']
        
        course.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Curso atualizado com sucesso',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_uuid>/publish', methods=['POST'])
@jwt_required()
def publish_course(course_uuid):
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Verificar permissão
        if course.creator_id != user.id and user.role != 'admin':
            return jsonify({'error': 'Sem permissão para publicar este curso'}), 403
        
        course.is_published = True
        course.published_at = datetime.utcnow()
        db.session.commit()
        
        # Log analytics
        log_analytics('course_published', user_id=user.id, course_id=course.id)
        
        return jsonify({'message': 'Curso publicado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_uuid>/enroll', methods=['POST'])
@jwt_required()
def enroll_course(course_uuid):
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
        
        # Log analytics
        log_analytics('course_enrolled', user_id=user.id, course_id=course.id)
        
        return jsonify({'message': 'Matrícula realizada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== AULAS ====================

@app.route('/api/courses/<course_uuid>/lessons', methods=['GET'])
def get_lessons(course_uuid):
    try:
        course = Course.query.filter_by(uuid=course_uuid, is_published=True).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order_index).all()
        
        return jsonify({
            'lessons': [lesson.to_dict() for lesson in lessons]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_uuid>/lessons', methods=['POST'])
@jwt_required()
def create_lesson(course_uuid):
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
        
        # Log analytics
        log_analytics('lesson_created', user_id=user.id, course_id=course.id, lesson_id=lesson.id)
        
        return jsonify({
            'message': 'Aula criada com sucesso',
            'lesson': lesson.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lessons/<lesson_uuid>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_uuid):
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        lesson = Lesson.query.filter_by(uuid=lesson_uuid).first()
        
        if not lesson:
            return jsonify({'error': 'Aula não encontrada'}), 404
        
        course = lesson.course
        
        # Verificar se o usuário tem acesso
        if not lesson.is_free:
            if course not in user.enrolled_courses and course.creator_id != user.id and user.role != 'admin':
                return jsonify({'error': 'Acesso negado. Matricule-se no curso'}), 403
        
        # Log analytics
        log_analytics('lesson_viewed', user_id=user.id, course_id=course.id, lesson_id=lesson.id)
        
        return jsonify({'lesson': lesson.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== COMENTÁRIOS ====================

@app.route('/api/courses/<course_uuid>/comments', methods=['GET'])
def get_comments(course_uuid):
    try:
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        comments = Comment.query.filter_by(course_id=course.id, parent_id=None).order_by(desc(Comment.created_at)).all()
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_uuid>/comments', methods=['POST'])
@jwt_required()
def create_comment(course_uuid):
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': 'Conteúdo é obrigatório'}), 400
        
        comment = Comment(
            content=data['content'],
            course_id=course.id,
            author_id=user.id,
            parent_id=data.get('parent_id')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Log analytics
        log_analytics('comment_created', user_id=user.id, course_id=course.id)
        
        return jsonify({
            'message': 'Comentário criado com sucesso',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== AVALIAÇÕES ====================

@app.route('/api/courses/<course_uuid>/rating', methods=['POST'])
@jwt_required()
def rate_course(course_uuid):
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        data = request.get_json()
        
        if not data.get('rating') or not 1 <= int(data['rating']) <= 5:
            return jsonify({'error': 'Avaliação deve ser entre 1 e 5'}), 400
        
        # Verificar se já avaliou
        existing_rating = Rating.query.filter_by(course_id=course.id, author_id=user.id).first()
        
        if existing_rating:
            # Atualizar avaliação existente
            existing_rating.rating = data['rating']
            existing_rating.comment = data.get('comment', '')
        else:
            # Criar nova avaliação
            rating = Rating(
                rating=data['rating'],
                comment=data.get('comment', ''),
                course_id=course.id,
                author_id=user.id
            )
            db.session.add(rating)
        
        db.session.commit()
        
        # Log analytics
        log_analytics('course_rated', user_id=user.id, course_id=course.id, metadata={'rating': data['rating']})
        
        return jsonify({'message': 'Avaliação registrada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PROGRESSO ====================

@app.route('/api/lessons/<lesson_uuid>/complete', methods=['POST'])
@jwt_required()
def complete_lesson(lesson_uuid):
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        lesson = Lesson.query.filter_by(uuid=lesson_uuid).first()
        
        if not lesson:
            return jsonify({'error': 'Aula não encontrada'}), 404
        
        # Verificar ou criar progresso
        progress = StudentProgress.query.filter_by(user_id=user.id, lesson_id=lesson.id).first()
        
        if not progress:
            progress = StudentProgress(user_id=user.id, lesson_id=lesson.id)
            db.session.add(progress)
        
        progress.completed = True
        progress.completion_date = datetime.utcnow()
        
        db.session.commit()
        
        # Log analytics
        log_analytics('lesson_completed', user_id=user.id, course_id=lesson.course_id, lesson_id=lesson.id)
        
        return jsonify({'message': 'Aula marcada como concluída'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_uuid>/progress', methods=['GET'])
@jwt_required()
def get_course_progress(course_uuid):
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Buscar progresso do usuário
        progress_query = db.session.query(StudentProgress, Lesson).join(
            Lesson, StudentProgress.lesson_id == Lesson.id
        ).filter(
            Lesson.course_id == course.id,
            StudentProgress.user_id == user.id
        )
        
        progress_data = []
        total_lessons = len(course.lessons)
        completed_lessons = 0
        
        for progress, lesson in progress_query:
            progress_data.append({
                'lesson': lesson.to_dict(),
                'progress': progress.to_dict()
            })
            if progress.completed:
                completed_lessons += 1
        
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return jsonify({
            'course_progress': {
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'progress_percentage': round(progress_percentage, 2),
                'lessons': progress_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ANALYTICS ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_analytics_dashboard():
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Sem permissão para acessar analytics'}), 403
        
        # Estatísticas dos cursos do professor
        if user.role == 'teacher':
            courses = Course.query.filter_by(creator_id=user.id).all()
        else:
            courses = Course.query.all()
        
        course_ids = [course.id for course in courses]
        
        # Estatísticas gerais
        total_courses = len(courses)
        total_students = db.session.query(course_students).filter(
            course_students.c.course_id.in_(course_ids)
        ).count() if course_ids else 0
        
        # Cursos mais populares
        popular_courses = db.session.query(
            Course,
            func.count(course_students.c.user_id).label('student_count')
        ).outerjoin(course_students).filter(
            Course.id.in_(course_ids) if course_ids else False
        ).group_by(Course.id).order_by(desc('student_count')).limit(5).all()
        
        return jsonify({
            'analytics': {
                'total_courses': total_courses,
                'total_students': total_students,
                'published_courses': len([c for c in courses if c.is_published]),
                'popular_courses': [
                    {
                        'course': course.to_dict(),
                        'student_count': count
                    } for course, count in popular_courses
                ]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== UPLOAD DE ARQUIVOS ====================

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Adicionar timestamp para evitar conflitos
            filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
            
            # Determinar pasta de destino
            file_type = request.form.get('type', 'materials')
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file_type)
            os.makedirs(upload_path, exist_ok=True)
            
            filepath = os.path.join(upload_path, filename)
            file.save(filepath)
            
            return jsonify({
                'message': 'Arquivo enviado com sucesso',
                'file_path': f"/uploads/{file_type}/{filename}",
                'filename': filename
            }), 200
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ROTAS DE TESTE ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'CursoHub API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = {
            'total_users': User.query.count(),
            'total_courses': Course.query.count(),
            'published_courses': Course.query.filter_by(is_published=True).count(),
            'total_lessons': Lesson.query.count(),
            'total_comments': Comment.query.count(),
            'total_ratings': Rating.query.count()
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HANDLERS DE ERRO ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Token não fornecido ou inválido'}), 401