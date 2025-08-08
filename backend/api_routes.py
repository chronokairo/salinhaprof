from flask import request, jsonify, send_file, current_app as app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc, or_
import os
from datetime import datetime

# Importações que serão disponíveis após app.py executar
def get_db_and_models():
    from backend.models import db, User, Course, Lesson, Comment, Rating, StudentProgress, Analytics, course_enrollments
    return db, User, Course, Lesson, Comment, Rating, StudentProgress, Analytics, course_enrollments

# Utilitários
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_analytics(event_type, user_id=None, course_id=None, lesson_id=None, metadata=None):
    """Log analytics events"""
    try:
        analytics = Analytics(
            event_type=event_type,
            user_id=user_id,
            course_id=course_id,
            lesson_id=lesson_id,
            metadata=metadata
        )
        db.session.add(analytics)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Erro ao registrar analytics: {str(e)}")

# ==================== AUTENTICAÇÃO ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('name'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email é obrigatório'}), 400
        if not data.get('password'):
            return jsonify({'error': 'Senha é obrigatória'}), 400
        
        # Verificar se o email já existe
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
        
        # Criar token JWT
        token = create_access_token(identity=user.uuid)
        
        # Log analytics
        log_analytics('user_registered', user_id=user.id)
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'token': token,
            'user': user.to_dict(include_email=True)
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
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Conta desativada'}), 401
        
        # Criar token JWT
        token = create_access_token(identity=user.uuid)
        
        # Log analytics
        log_analytics('user_login', user_id=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': user.to_dict(include_email=True)
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
        
        return jsonify({'user': user.to_dict(include_email=True)}), 200
        
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
        
        # Atualizar campos
        if 'name' in data:
            user.name = data['name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict(include_email=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CURSOS ====================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)  # máximo 50 por página
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
        sort_by = request.args.get('sort', 'recent')
        if sort_by == 'popular':
            # Ordenar por número de estudantes
            query = query.outerjoin(course_enrollments).group_by(Course.id).order_by(
                desc(func.count(course_enrollments.c.user_id))
            )
        elif sort_by == 'rating':
            # Ordenar por avaliação média
            query = query.outerjoin(Rating).group_by(Course.id).order_by(
                desc(func.avg(Rating.value))
            )
        else:  # recent (padrão)
            query = query.order_by(desc(Course.created_at))
        
        # Paginação
        courses = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Log analytics
        log_analytics('courses_viewed', metadata={
            'page': page, 
            'filters': request.args.to_dict()
        })
        
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
        app.logger.error(f"Erro ao buscar cursos: {str(e)}")
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
        if 'thumbnail_url' in data:
            course.thumbnail_url = data['thumbnail_url']
        
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
        
        data = request.get_json() or {}
        
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        progress.watch_time = data.get('watch_time', progress.watch_time)
        progress.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log analytics
        log_analytics('lesson_completed', user_id=user.id, 
                     course_id=lesson.course_id, lesson_id=lesson.id)
        
        return jsonify({
            'message': 'Aula marcada como concluída',
            'progress': progress.to_dict()
        }), 200
        
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
        
        # Buscar progresso de todas as aulas do curso
        lesson_ids = [lesson.id for lesson in course.lessons]
        progress_records = StudentProgress.query.filter(
            StudentProgress.user_id == user.id,
            StudentProgress.lesson_id.in_(lesson_ids)
        ).all()
        
        total_lessons = len(course.lessons)
        completed_lessons = sum(1 for p in progress_records if p.is_completed)
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return jsonify({
            'course_uuid': course_uuid,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': round(progress_percentage, 1),
            'lesson_progress': [p.to_dict() for p in progress_records]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== COMENTÁRIOS ====================

@app.route('/api/courses/<course_uuid>/comments', methods=['GET'])
def get_comments(course_uuid):
    try:
        course = Course.query.filter_by(uuid=course_uuid).first()
        
        if not course:
            return jsonify({'error': 'Curso não encontrado'}), 404
        
        # Buscar comentários principais (sem parent_id)
        comments = Comment.query.filter_by(
            course_id=course.id, 
            parent_id=None
        ).order_by(desc(Comment.created_at)).all()
        
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
            user_id=user.id,
            course_id=course.id
        )
        
        # Se é uma resposta a outro comentário
        if data.get('parent_uuid'):
            parent = Comment.query.filter_by(uuid=data['parent_uuid']).first()
            if parent:
                comment.parent_id = parent.id
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comentário criado com sucesso',
            'comment': comment.to_dict(include_replies=False)
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
        
        if not data.get('value') or data['value'] not in [1, 2, 3, 4, 5]:
            return jsonify({'error': 'Avaliação deve ser entre 1 e 5 estrelas'}), 400
        
        # Verificar se já avaliou
        existing_rating = Rating.query.filter_by(
            user_id=user.id, 
            course_id=course.id
        ).first()
        
        if existing_rating:
            # Atualizar avaliação existente
            existing_rating.value = data['value']
            existing_rating.comment = data.get('comment', '')
        else:
            # Criar nova avaliação
            rating = Rating(
                value=data['value'],
                comment=data.get('comment', ''),
                user_id=user.id,
                course_id=course.id
            )
            db.session.add(rating)
        
        db.session.commit()
        
        return jsonify({'message': 'Avaliação salva com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ANALYTICS ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def analytics_dashboard():
    try:
        user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Sem permissão para acessar analytics'}), 403
        
        # Buscar cursos do professor ou todos se admin
        if user.role == 'admin':
            courses = Course.query.all()
        else:
            courses = Course.query.filter_by(creator_id=user.id).all()
        
        course_ids = [c.id for c in courses]
        
        # Estatísticas básicas
        total_students = db.session.query(course_enrollments).filter(
            course_enrollments.c.course_id.in_(course_ids)
        ).count()
        
        total_lessons = Lesson.query.filter(
            Lesson.course_id.in_(course_ids)
        ).count()
        
        total_ratings = Rating.query.filter(
            Rating.course_id.in_(course_ids)
        ).count()
        
        avg_rating = db.session.query(func.avg(Rating.value)).filter(
            Rating.course_id.in_(course_ids)
        ).scalar() or 0
        
        return jsonify({
            'summary': {
                'total_courses': len(courses),
                'total_students': total_students,
                'total_lessons': total_lessons,
                'total_ratings': total_ratings,
                'average_rating': round(float(avg_rating), 1)
            },
            'courses': [course.to_dict(include_stats=True) for course in courses]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== UPLOAD DE ARQUIVOS ====================

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'material')  # material, video, avatar
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Adicionar timestamp para evitar conflitos
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
            
            # Determinar subdiretório baseado no tipo
            subdir = {
                'video': 'videos',
                'avatar': 'avatars',
                'material': 'materials'
            }.get(file_type, 'materials')
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], subdir, filename)
            file.save(filepath)
            
            # URL relativa para o arquivo
            file_url = f"/uploads/{subdir}/{filename}"
            
            return jsonify({
                'message': 'Arquivo enviado com sucesso',
                'file_url': file_url,
                'filename': filename
            }), 200
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SERVIR ARQUIVOS ESTÁTICOS ====================

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': 'Arquivo não encontrado'}), 404
