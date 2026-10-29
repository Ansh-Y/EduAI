import os
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine, Base
from app.models.models import (
    User, Course, Section, Artifact, Enrollment, QuizQuestion, QuizAttempt,
    LearningProgress, ChatMessage, Notification, Certificate
)
from app.core.security import get_password_hash
from app.ai.generator import SUBJECT_CURRICULA, MACHINE_LEARNING_QUESTIONS
from app.services.pdf_generator import generate_smart_notes_pdf, generate_course_certificate_pdf
from app.services.docx_generator import generate_smart_notes_docx

def init_and_seed_db(db: Session):
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == "admin@eduai.demo").first()
    if existing_admin:
        print("Database already initialized with seed data. Skipping seed.")
        return

    print("Seeding database with university demo data...")
    password_hash = get_password_hash("password123")
    
    # 1. Users
    admin_user = User(
        name="Dean Marcus Vance (Admin)",
        email="admin@eduai.demo",
        hashed_password=password_hash,
        role="admin",
        is_active=True
    )
    teacher_user = User(
        name="Prof. Sarah Jenkins",
        email="teacher@eduai.demo",
        hashed_password=password_hash,
        role="teacher",
        is_active=True
    )
    student1 = User(
        name="Alex Rivera",
        email="student@eduai.demo",
        hashed_password=password_hash,
        role="student",
        is_active=True
    )
    student2 = User(
        name="Jordan Chen",
        email="student2@eduai.demo",
        hashed_password=password_hash,
        role="student",
        is_active=True
    )
    student3 = User(
        name="Maya Patel",
        email="student3@eduai.demo",
        hashed_password=password_hash,
        role="student",
        is_active=True
    )
    db.add_all([admin_user, teacher_user, student1, student2, student3])
    db.commit()
    db.refresh(teacher_user)
    db.refresh(student1)
    db.refresh(student2)
    db.refresh(student3)

    # 2. Courses
    # Course 1: Introduction to Machine Learning (Published)
    ml_course = Course(
        title="Introduction to Machine Learning",
        description="Comprehensive university curriculum on predictive modeling, optimization, supervised and unsupervised learning, model validation, and regularization techniques.",
        subject="Computer Science & AI",
        difficulty="Intermediate",
        teacher_id=teacher_user.id,
        is_published=True,
        passing_threshold=70.0,
        max_quiz_attempts=3
    )
    
    # Course 2: Modern Web Engineering (Published)
    web_course = Course(
        title="Full-Stack Web Engineering with React & FastAPI",
        description="Master modern reactive UI architectures, asynchronous REST endpoints, database modeling, and state management systems.",
        subject="Software Engineering",
        difficulty="Beginner",
        teacher_id=teacher_user.id,
        is_published=True,
        passing_threshold=75.0,
        max_quiz_attempts=3
    )

    # Course 3: Advanced Cloud Infrastructure (Draft)
    cloud_course = Course(
        title="Cloud Architecture & Microservices (Draft)",
        description="Designing scalable containerized microservices, distributed consensus protocols, and continuous deployment pipelines.",
        subject="Distributed Systems",
        difficulty="Advanced",
        teacher_id=teacher_user.id,
        is_published=False,
        passing_threshold=80.0,
        max_quiz_attempts=2
    )
    db.add_all([ml_course, web_course, cloud_course])
    db.commit()
    db.refresh(ml_course)
    db.refresh(web_course)
    db.refresh(cloud_course)

    # Educational Sample Videos (Standard educational videos)
    sample_videos = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    ]

    # 3. Sections for Course 1 (Machine Learning)
    ml_curriculum = SUBJECT_CURRICULA["machine learning"]
    ml_sections = []
    
    for idx, sec_data in enumerate(ml_curriculum):
        sec = Section(
            course_id=ml_course.id,
            title=sec_data["title"],
            order_num=idx + 1,
            content=sec_data["content"],
            objectives=json.dumps(sec_data["objectives"]),
            summary=sec_data["summary"],
            video_url=sample_videos[idx % len(sample_videos)],
            summary_video_url=sample_videos[(idx + 1) % len(sample_videos)],
            is_published=True
        )
        db.add(sec)
        db.commit()
        db.refresh(sec)
        ml_sections.append(sec)

        # Generate Real PDF and DOCX Smart Notes files on disk!
        pdf_name = f"notes_ml_sec_{sec.id}.pdf"
        docx_name = f"notes_ml_sec_{sec.id}.docx"
        try:
            generate_smart_notes_pdf(
                course_title=ml_course.title,
                section_title=sec.title,
                objectives=sec_data["objectives"],
                content=sec.content,
                summary=sec.summary,
                output_filename=pdf_name
            )
            generate_smart_notes_docx(
                course_title=ml_course.title,
                section_title=sec.title,
                objectives=sec_data["objectives"],
                content=sec.content,
                summary=sec.summary,
                output_filename=docx_name
            )
        except Exception as e:
            print(f"Error pre-generating notes files: {e}")

        # Six Artifacts for each section
        artifacts = [
            Artifact(section_id=sec.id, artifact_type="script", status="completed", file_path=None),
            Artifact(section_id=sec.id, artifact_type="main_video", status="completed", file_path=sec.video_url),
            Artifact(section_id=sec.id, artifact_type="summary_video", status="completed", file_path=sec.summary_video_url),
            Artifact(section_id=sec.id, artifact_type="notes_pdf", status="completed", file_path=f"storage/notes/{pdf_name}"),
            Artifact(section_id=sec.id, artifact_type="notes_docx", status="completed", file_path=f"storage/notes/{docx_name}"),
            Artifact(section_id=sec.id, artifact_type="quiz", status="completed", file_path=None),
        ]
        db.add_all(artifacts)

        # Quiz questions for this section
        if idx < len(MACHINE_LEARNING_QUESTIONS):
            for q_data in MACHINE_LEARNING_QUESTIONS[idx]:
                q = QuizQuestion(
                    section_id=sec.id,
                    question_text=q_data["question_text"],
                    question_type=q_data["question_type"],
                    options=json.dumps(q_data.get("options", [])),
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    associated_concept=q_data["associated_concept"]
                )
                db.add(q)
        db.commit()

    # 4. Sections for Web Course
    web_sections_data = [
        ("Modern Component Architecture & Hooks", ["Understand React fiber reconciliation", "Master useState and useEffect patterns", "State colocation principles"]),
        ("Backend Services with FastAPI & Pydantic", ["Asynchronous route handlers", "Data contract validation", "Dependency injection mechanics"]),
        ("State Management & Global Context Providers", ["Context API optimization", "Tailwind theme integration", "Custom storage persistence hooks"])
    ]
    for idx, (w_title, w_objs) in enumerate(web_sections_data):
        w_sec = Section(
            course_id=web_course.id,
            title=w_title,
            order_num=idx + 1,
            content=f"# {w_title}\n\nComprehensive engineering principles and code patterns for {w_title}.\n\n## 1. Technical Framework\nDetailed exploration of core patterns.\n\n## 2. Practical Code\n```javascript\n// Sample implementation\nconst [data, setData] = useState([]);\n```",
            objectives=json.dumps(w_objs),
            summary=f"Foundational review of {w_title} in full-stack web applications.",
            video_url=sample_videos[idx % len(sample_videos)],
            summary_video_url=sample_videos[(idx + 1) % len(sample_videos)],
            is_published=True
        )
        db.add(w_sec)
        db.commit()
        db.refresh(w_sec)

        pdf_name = f"notes_web_sec_{w_sec.id}.pdf"
        docx_name = f"notes_web_sec_{w_sec.id}.docx"
        try:
            generate_smart_notes_pdf(web_course.title, w_sec.title, w_objs, w_sec.content, w_sec.summary, pdf_name)
            generate_smart_notes_docx(web_course.title, w_sec.title, w_objs, w_sec.content, w_sec.summary, docx_name)
        except Exception:
            pass

        db.add_all([
            Artifact(section_id=w_sec.id, artifact_type="script", status="completed"),
            Artifact(section_id=w_sec.id, artifact_type="main_video", status="completed", file_path=w_sec.video_url),
            Artifact(section_id=w_sec.id, artifact_type="summary_video", status="completed", file_path=w_sec.summary_video_url),
            Artifact(section_id=w_sec.id, artifact_type="notes_pdf", status="completed", file_path=f"storage/notes/{pdf_name}"),
            Artifact(section_id=w_sec.id, artifact_type="notes_docx", status="completed", file_path=f"storage/notes/{docx_name}"),
            Artifact(section_id=w_sec.id, artifact_type="quiz", status="completed")
        ])
        # Add basic quiz question
        db.add(QuizQuestion(
            section_id=w_sec.id,
            question_text=f"What is the key benefit of {w_title}?",
            question_type="multiple_choice",
            options=json.dumps(["Modularity and scalability", "Eliminates network latency", "Replaces hardware RAM", "Disables browser caching"]),
            correct_answer="Modularity and scalability",
            explanation="Modern architectures prioritize modularity, predictability, and maintainability.",
            associated_concept="Architecture Fundamentals"
        ))
        db.commit()

    # 5. Enrollments & Progress for Student 1 (Alex Rivera)
    # Alex is enrolled in ML course and completed sections 1, 2, 3 (progress 60%)
    enr1 = Enrollment(
        student_id=student1.id,
        course_id=ml_course.id,
        enrolled_at=datetime.utcnow() - timedelta(days=7),
        progress_percentage=60.0
    )
    # Alex also enrolled in Web course (progress 33%)
    enr2 = Enrollment(
        student_id=student1.id,
        course_id=web_course.id,
        enrolled_at=datetime.utcnow() - timedelta(days=3),
        progress_percentage=33.3
    )
    # Student 2 & 3 enrollments
    enr3 = Enrollment(student_id=student2.id, course_id=ml_course.id, progress_percentage=80.0)
    enr4 = Enrollment(student_id=student3.id, course_id=ml_course.id, progress_percentage=40.0)
    db.add_all([enr1, enr2, enr3, enr4])
    db.commit()

    # Learning progress records for student1 on ML course
    for i in range(3):
        db.add(LearningProgress(
            student_id=student1.id,
            section_id=ml_sections[i].id,
            is_completed=True,
            video_progress=100.0,
            last_accessed=datetime.utcnow() - timedelta(days=2-i)
        ))
    db.commit()

    # Pre-seeded Quiz Attempts for student1 (demonstrating diagnostic feedback & weak concepts!)
    # Attempt 1: Section 1 - Scored 100% (Passed)
    attempt1 = QuizAttempt(
        student_id=student1.id,
        section_id=ml_sections[0].id,
        attempt_num=1,
        submitted_answers=json.dumps({
            "1": "Data and Answers (Ground Truth)",
            "2": "False",
            "3": "Regression",
            "4": "Leakage",
            "5": "Parametric models have fixed parameters whereas non-parametric parameters grow with dataset size."
        }),
        score=100.0,
        total_questions=5,
        correct_count=5,
        passed=True,
        weak_concepts=json.dumps([]),
        strong_concepts=json.dumps(["ML Fundamentals", "Unsupervised Learning Taxonomy", "Supervised Learning Taxonomy", "Data Preprocessing & Validation"]),
        feedback_plan="Outstanding mastery of core machine learning taxonomy and pipeline principles! You are well prepared for advanced optimization.",
        completed_at=datetime.utcnow() - timedelta(days=5)
    )
    # Attempt 2: Section 2 - Scored 60% (Failed threshold 70% - Shows weak concepts!)
    attempt2 = QuizAttempt(
        student_id=student1.id,
        section_id=ml_sections[1].id,
        attempt_num=1,
        submitted_answers=json.dumps({
            "1": "Logistic Sigmoid Function",
            "2": "Accuracy", # Wrong! Should be Recall
            "3": "True",
            "4": "ROC-AUC", # Wrong! Should be F1-Score
            "5": "Random forest uses bagging and gradient boosting is sequential."
        }),
        score=60.0,
        total_questions=5,
        correct_count=3,
        passed=False,
        weak_concepts=json.dumps(["Evaluation Metrics", "Imbalanced Classification Diagnostics"]),
        strong_concepts=json.dumps(["Logistic Regression", "Ensemble Methods"]),
        feedback_plan="Focus on medical and fraud evaluation criteria: review when Recall takes precedence over Accuracy, and re-examine the harmonic mean formula for F1-Score in Section 2 Smart Notes.",
        completed_at=datetime.utcnow() - timedelta(days=3)
    )
    # Attempt 3: Section 2 - Retake scored 100% (Passed after reviewing notes!)
    attempt3 = QuizAttempt(
        student_id=student1.id,
        section_id=ml_sections[1].id,
        attempt_num=2,
        submitted_answers=json.dumps({
            "1": "Logistic Sigmoid Function",
            "2": "Recall (Sensitivity)",
            "3": "True",
            "4": "F1-Score",
            "5": "Random forest uses bagging and gradient boosting is sequential."
        }),
        score=100.0,
        total_questions=5,
        correct_count=5,
        passed=True,
        weak_concepts=json.dumps([]),
        strong_concepts=json.dumps(["Evaluation Metrics", "Logistic Regression", "Ensemble Methods"]),
        feedback_plan="Excellent revision! You conquered the evaluation metrics gap and demonstrated full mastery.",
        completed_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add_all([attempt1, attempt2, attempt3])
    db.commit()

    # Pre-generate Certificate for student2 (Jordan Chen has completed ML course!)
    cert_uid = f"EDUAI-{uuid.uuid4().hex[:8].upper()}"
    cert_filename = f"certificate_{cert_uid}.pdf"
    try:
        generate_course_certificate_pdf(
            student_name=student2.name,
            course_title=ml_course.title,
            certificate_uid=cert_uid,
            completion_date="October 25, 2025",
            output_filename=cert_filename
        )
        cert = Certificate(
            student_id=student2.id,
            course_id=ml_course.id,
            certificate_uid=cert_uid,
            completion_date=datetime.utcnow() - timedelta(days=2),
            file_path=f"storage/certificates/{cert_filename}"
        )
        db.add(cert)
        db.commit()
    except Exception as e:
        print(f"Error creating demo certificate: {e}")

    # Notifications
    notifications = [
        Notification(
            recipient_id=student1.id,
            title="Welcome to EduAI Platform",
            message="Your student account has been activated. Explore published university courses and start learning!",
            notification_type="system",
            link="/courses",
            is_read=False
        ),
        Notification(
            recipient_id=student1.id,
            title="Quiz Retake Graded: 100% Passed",
            message="Congratulations! Your retake of Section 2 Quiz achieved 100%. Section 3 is now unlocked.",
            notification_type="quiz_graded",
            link=f"/learn/{ml_course.id}",
            is_read=True
        ),
        Notification(
            recipient_id=teacher_user.id,
            title="Course Enrollment Spike",
            message="3 students recently enrolled in 'Introduction to Machine Learning'.",
            notification_type="system",
            link="/teacher/analytics",
            is_read=False
        ),
        Notification(
            recipient_id=admin_user.id,
            title="Platform Health & Activity",
            message="All database indexes, background generators, and academic engines are functioning normally.",
            notification_type="system",
            link="/admin",
            is_read=False
        )
    ]
    db.add_all(notifications)

    # Initial Chat message in Section 1
    db.add(ChatMessage(
        student_id=student1.id,
        section_id=ml_sections[0].id,
        role="user",
        message_content="Explain the difference between supervised and unsupervised learning in simple terms."
    ))
    db.add(ChatMessage(
        student_id=student1.id,
        section_id=ml_sections[0].id,
        role="assistant",
        message_content="In Supervised Learning, you train the algorithm with both input questions and correct answers (labels), like a teacher grading flashcards. In Unsupervised Learning, you only provide raw data without any answers, and the algorithm must detect natural groupings or patterns on its own!",
        sources_cited="Chapter 1: Taxonomy of Machine Learning"
    ))
    db.commit()
    print("Database seeding completed successfully!")
