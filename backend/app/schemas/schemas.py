from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# --- Auth & User ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "student"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


# --- Artifacts ---
class ArtifactOut(BaseModel):
    id: int
    section_id: int
    artifact_type: str
    status: str
    file_path: Optional[str] = None
    error_details: Optional[str] = None
    updated_at: datetime
    class Config:
        from_attributes = True


# --- Quiz Questions & Attempts ---
class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    options: List[str] = []
    correct_answer: str
    explanation: str
    associated_concept: str

class QuizQuestionCreate(QuizQuestionBase):
    pass

class QuizQuestionOut(BaseModel):
    id: int
    section_id: int
    question_text: str
    question_type: str
    options: List[str]
    # For student player, correct_answer & explanation may be hidden until submission, but let's allow teacher view
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    associated_concept: str
    class Config:
        from_attributes = True

class QuizSubmitRequest(BaseModel):
    answers: Dict[str, str]  # question_id string -> user answer string

class QuizAttemptOut(BaseModel):
    id: int
    student_id: int
    section_id: int
    attempt_num: int
    submitted_answers: Dict[str, str]
    score: float
    total_questions: int
    correct_count: int
    passed: bool
    weak_concepts: List[str]
    strong_concepts: List[str]
    feedback_plan: Optional[str]
    completed_at: datetime
    class Config:
        from_attributes = True


# --- Sections ---
class SectionBase(BaseModel):
    title: str
    order_num: int = 1
    content: str
    objectives: List[str] = []
    summary: Optional[str] = None
    is_published: bool = True

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    order_num: Optional[int] = None
    content: Optional[str] = None
    objectives: Optional[List[str]] = None
    summary: Optional[str] = None
    is_published: Optional[bool] = None

class SectionOut(BaseModel):
    id: int
    course_id: int
    title: str
    order_num: int
    content: str
    objectives: List[str]
    summary: Optional[str] = None
    video_url: Optional[str] = None
    summary_video_url: Optional[str] = None
    is_published: bool
    artifacts: List[ArtifactOut] = []
    is_completed: Optional[bool] = False
    is_unlocked: Optional[bool] = True
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# --- Courses ---
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    difficulty: str = "Beginner"

class CourseCreate(CourseBase):
    pass

class CourseGenerateRequest(BaseModel):
    title: str
    subject: str
    description: Optional[str] = ""
    prompt: Optional[str] = ""
    target_audience: Optional[str] = "Undergraduate Students"
    difficulty: str = "Beginner"
    section_count: int = Field(default=5, ge=1, le=10)
    reference_text: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    is_published: Optional[bool] = None
    passing_threshold: Optional[float] = None
    max_quiz_attempts: Optional[int] = None

class CourseOut(CourseBase):
    id: int
    teacher_id: int
    teacher_name: Optional[str] = None
    is_published: bool
    passing_threshold: float
    max_quiz_attempts: int
    sections_count: int = 0
    enrolled_count: int = 0
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class CourseDetailOut(CourseOut):
    sections: List[SectionOut] = []
    is_enrolled: Optional[bool] = False
    student_progress: Optional[float] = 0.0


# --- Progress & Enrollment ---
class ProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    video_progress: Optional[float] = None

class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    course_title: Optional[str] = None
    course_subject: Optional[str] = None
    enrolled_at: datetime
    progress_percentage: float
    class Config:
        from_attributes = True


# --- Chat ---
class ChatRequest(BaseModel):
    message: str

class ChatMessageOut(BaseModel):
    id: int
    role: str
    message_content: str
    sources_cited: Optional[str] = None
    timestamp: datetime
    class Config:
        from_attributes = True


# --- Notifications ---
class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    link: Optional[str] = None
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True


# --- Certificates ---
class CertificateOut(BaseModel):
    id: int
    certificate_uid: str
    course_id: int
    course_title: str
    student_name: str
    completion_date: datetime
    download_url: str
    class Config:
        from_attributes = True


# --- Analytics ---
class TeacherAnalyticsOut(BaseModel):
    total_courses: int
    published_courses: int
    total_students: int
    average_quiz_score: float
    course_completion_rate: float
    enrollment_by_course: List[Dict[str, Any]]
    quiz_scores_by_course: List[Dict[str, Any]]
    frequently_missed_concepts: List[Dict[str, Any]]

class StudentAnalyticsOut(BaseModel):
    enrolled_courses_count: int
    completed_courses_count: int
    completed_sections_count: int
    average_quiz_score: float
    study_streak_days: int
    quiz_score_trend: List[Dict[str, Any]]
    weak_concepts: List[str]
    strong_concepts: List[str]
    recent_attempts: List[Dict[str, Any]]

class AdminOverviewOut(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_courses: int
    published_courses: int
    total_enrollments: int
    total_quiz_submissions: int
    course_completion_rate: float
    user_distribution: List[Dict[str, Any]]
    enrollment_trends: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
