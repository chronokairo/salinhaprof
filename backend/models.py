from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Será inicializado no app.py
db = SQLAlchemy()

# Tabelas de relacionamento many-to-many
course_enrollments = db.Table('course_enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    created_courses = db.relationship('Course', backref='creator', lazy=True)
    enrolled_courses = db.relationship('Course', secondary=course_enrollments, 
                                     backref=db.backref('students', lazy='dynamic'))
    comments = db.relationship('Comment', backref='author', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    progress = db.relationship('StudentProgress', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self, include_email=False):
        data = {
            'uuid': self.uuid,
            'name': self.name,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_email:
            data['email'] = self.email
        return data

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    price = db.Column(db.Float, default=0.0)
    thumbnail_url = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Chave estrangeira
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    lessons = db.relationship('Lesson', backref='course', lazy=True, 
                            cascade='all, delete-orphan', order_by='Lesson.order_index')
    comments = db.relationship('Comment', backref='course', lazy=True)
    ratings = db.relationship('Rating', backref='course', lazy=True)
    
    def get_average_rating(self):
        if not self.ratings:
            return 0
        return sum(rating.value for rating in self.ratings) / len(self.ratings)
    
    def get_total_duration(self):
        return sum(lesson.video_duration for lesson in self.lessons if lesson.video_duration)
    
    def get_lesson_count(self):
        return len(self.lessons)
    
    def get_student_count(self):
        return self.students.count()
    
    def to_dict(self, include_lessons=False, include_stats=False):
        data = {
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'price': self.price,
            'thumbnail_url': self.thumbnail_url,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'creator': self.creator.to_dict() if self.creator else None
        }
        
        if include_lessons:
            data['lessons'] = [lesson.to_dict() for lesson in self.lessons]
        
        if include_stats:
            data['stats'] = {
                'average_rating': round(self.get_average_rating(), 1),
                'total_duration': self.get_total_duration(),
                'lesson_count': self.get_lesson_count(),
                'student_count': self.get_student_count()
            }
        
        return data

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(255))
    video_duration = db.Column(db.Integer, default=0)  # em segundos
    order_index = db.Column(db.Integer, default=0)
    is_free = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chave estrangeira
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Relacionamentos
    progress = db.relationship('StudentProgress', backref='lesson', lazy=True)
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'video_url': self.video_url,
            'video_duration': self.video_duration,
            'order_index': self.order_index,
            'is_free': self.is_free,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'course_uuid': self.course.uuid if self.course else None
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # Para respostas
    
    # Relacionamentos
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self, include_replies=True):
        data = {
            'uuid': self.uuid,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'author': self.author.to_dict() if self.author else None,
            'parent_id': self.parent.uuid if self.parent else None
        }
        
        if include_replies:
            data['replies'] = [reply.to_dict(include_replies=False) for reply in self.replies]
        
        return data

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # Índice único para evitar múltiplas avaliações do mesmo usuário para o mesmo curso
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course_rating'),)
    
    def to_dict(self):
        return {
            'value': self.value,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_dict() if self.user else None
        }

class StudentProgress(db.Model):
    __tablename__ = 'student_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    is_completed = db.Column(db.Boolean, default=False)
    watch_time = db.Column(db.Integer, default=0)  # tempo assistido em segundos
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    # Índice único
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_progress'),)
    
    def to_dict(self):
        return {
            'is_completed': self.is_completed,
            'watch_time': self.watch_time,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'lesson_uuid': self.lesson.uuid if self.lesson else None
        }

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.JSON)  # Renomeado de metadata para event_data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves estrangeiras opcionais
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'event_data': self.event_data,  # Renomeado de metadata para event_data
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'lesson_id': self.lesson_id
        }
