from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Tabela de associação para cursos e estudantes
course_students = db.Table('course_students',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow),
    db.Column('progress', db.Float, default=0.0),
    db.Column('completed_at', db.DateTime, nullable=True)
)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student
    avatar = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    created_courses = db.relationship('Course', backref='creator', lazy=True, foreign_keys='Course.creator_id')
    enrolled_courses = db.relationship('Course', secondary=course_students, lazy='subquery',
                                     backref=db.backref('students', lazy=True))
    comments = db.relationship('Comment', backref='author', lazy=True)
    ratings = db.relationship('Rating', backref='author', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

# Modelo de Curso
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    level = db.Column(db.String(20), nullable=False, default='beginner')  # beginner, intermediate, advanced
    price = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Integer, default=0)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan')
    materials = db.relationship('Material', backref='course', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='course', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_lessons=False, include_stats=False):
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'category': self.category,
            'level': self.level,
            'price': self.price,
            'duration_hours': self.duration_hours,
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'is_published': self.is_published,
            'is_featured': self.is_featured
        }
        
        if include_lessons:
            data['lessons'] = [lesson.to_dict() for lesson in self.lessons]
        
        if include_stats:
            data['stats'] = {
                'total_students': len(self.students),
                'total_lessons': len(self.lessons),
                'avg_rating': self.get_average_rating(),
                'total_ratings': len(self.ratings)
            }
        
        return data
    
    def get_average_rating(self):
        if not self.ratings:
            return 0
        return sum(rating.rating for rating in self.ratings) / len(self.ratings)

# Modelo de Aula/Lição
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)  # Conteúdo texto da aula
    video_url = db.Column(db.String(500), nullable=True)
    video_duration = db.Column(db.Integer, default=0)  # em segundos
    order_index = db.Column(db.Integer, nullable=False, default=0)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_free = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    materials = db.relationship('Material', backref='lesson', lazy=True, cascade='all, delete-orphan')
    exercises = db.relationship('Exercise', backref='lesson', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'video_url': self.video_url,
            'video_duration': self.video_duration,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'is_free': self.is_free,
            'materials': [material.to_dict() for material in self.materials],
            'exercises': [exercise.to_dict() for exercise in self.exercises]
        }

# Modelo de Material
class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, doc, video, image, etc
    file_size = db.Column(db.Integer, default=0)  # em bytes
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat()
        }

# Modelo de Exercício
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=True)  # Para questões de múltipla escolha
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'question': self.question,
            'options': self.options,
            'explanation': self.explanation,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat()
        }
        
        if include_answer:
            data['correct_answer'] = self.correct_answer
        
        return data

# Modelo de Comentário
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # Para respostas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento para respostas
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'content': self.content,
            'author': self.author.to_dict(),
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'replies': [reply.to_dict() for reply in self.replies]
        }

# Modelo de Avaliação
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comment = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint para evitar múltiplas avaliações do mesmo usuário no mesmo curso
    __table_args__ = (db.UniqueConstraint('course_id', 'author_id', name='unique_user_course_rating'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'author': self.author.to_dict(),
            'created_at': self.created_at.isoformat()
        }

# Modelo de Progresso do Estudante
class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    watch_time = db.Column(db.Integer, default=0)  # tempo assistido em segundos
    
    # Constraint para evitar duplicatas
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_progress'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'watch_time': self.watch_time
        }

# Modelo de Analytics/Estatísticas
class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # view, enrollment, completion, etc
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    metadata = db.Column(db.JSON, nullable=True)  # dados adicionais do evento
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'lesson_id': self.lesson_id,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }