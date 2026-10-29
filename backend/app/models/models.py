import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="student")  # teacher, student, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    courses_created = relationship("Course", back_populates="teacher", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")
    progress_records = relationship("LearningProgress", back_populates="student", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="student", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="Beginner")  # Beginner, Intermediate, Advanced
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    passing_threshold = Column(Float, default=70.0)  # default quiz pass mark
    max_quiz_attempts = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="courses_created")
    sections = relationship("Section", back_populates="course", order_by="Section.order_num", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    order_num = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    objectives = Column(Text, default="[]")  # JSON array string
    summary = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)
    summary_video_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="sections")
    artifacts = relationship("Artifact", back_populates="section", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="section", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="section", cascade="all, delete-orphan")
    progress_records = relationship("LearningProgress", back_populates="section", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="section", cascade="all, delete-orphan")


class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # script, main_video, summary_video, notes_pdf, notes_docx, quiz
    status = Column(String(50), default="pending")      # pending, processing, completed, failed
    file_path = Column(String(500), nullable=True)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    section = relationship("Section", back_populates="artifacts")
    
    __table_args__ = (
        UniqueConstraint("section_id", "artifact_type", name="uq_section_artifact"),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow)
    progress_percentage = Column(Float, default=0.0)
    
    # Relationships
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course_enrollment"),
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice")  # multiple_choice, true_false, fill_blank, short_answer
    options = Column(Text, default="[]")  # JSON list
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    associated_concept = Column(String(255), nullable=False)
    
    # Relationships
    section = relationship("Section", back_populates="quiz_questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    attempt_num = Column(Integer, nullable=False, default=1)
    submitted_answers = Column(Text, default="{}")  # JSON string
    score = Column(Float, nullable=False)  # percentage
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    passed = Column(Boolean, default=False)
    weak_concepts = Column(Text, default="[]")  # JSON array
    strong_concepts = Column(Text, default="[]")  # JSON array
    feedback_plan = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="quiz_attempts")
    section = relationship("Section", back_populates="quiz_attempts")


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    video_progress = Column(Float, default=0.0)  # 0 to 100
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="progress_records")
    section = relationship("Section", back_populates="progress_records")
    
    __table_args__ = (
        UniqueConstraint("student_id", "section_id", name="uq_student_section_progress"),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    message_content = Column(Text, nullable=False)
    sources_cited = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="chat_messages")
    section = relationship("Section", back_populates="chat_messages")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="system")
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    recipient = relationship("User", back_populates="notifications")


class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    certificate_uid = Column(String(100), unique=True, index=True, nullable=False)
    completion_date = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String(500), nullable=False)
    
    # Relationships
    student = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
    
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course_certificate"),
    )
