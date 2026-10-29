from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.models import User, Course, Section, Enrollment, LearningProgress, QuizAttempt, Certificate, Notification
from app.schemas.schemas import EnrollmentOut, CourseOut

router = APIRouter(prefix="/student", tags=["Student Portal"])

@router.post("/enroll/{course_id}")
def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published and current_user.role == "student":
        raise HTTPException(status_code=400, detail="Cannot enroll in an unpublished draft course.")
        
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    if existing:
        return {"message": "Already enrolled in this course.", "enrollment_id": existing.id}
        
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id,
        progress_percentage=0.0,
        enrolled_at=datetime.utcnow()
    )
    db.add(enrollment)
    
    # Notify student
    db.add(Notification(
        recipient_id=current_user.id,
        title=f"Enrolled in {course.title}",
        message=f"You have successfully enrolled in '{course.title}'. Section 1 is unlocked and ready!",
        notification_type="system",
        link=f"/learn/{course.id}"
    ))
    db.commit()
    db.refresh(enrollment)
    
    return {
        "message": f"Successfully enrolled in '{course.title}'!",
        "enrollment_id": enrollment.id,
        "course_id": course.id
    }


@router.get("/courses")
def get_enrolled_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    results = []
    for enr in enrollments:
        c = enr.course
        if not c:
            continue
        total_sections = db.query(Section).filter(Section.course_id == c.id).count()
        completed_sections = db.query(LearningProgress).join(Section).filter(
            Section.course_id == c.id,
            LearningProgress.student_id == current_user.id,
            LearningProgress.is_completed == True
        ).count()
        
        results.append({
            "enrollment_id": enr.id,
            "course_id": c.id,
            "title": c.title,
            "description": c.description,
            "subject": c.subject,
            "difficulty": c.difficulty,
            "progress_percentage": enr.progress_percentage,
            "enrolled_at": enr.enrolled_at,
            "total_sections": total_sections,
            "completed_sections": completed_sections,
            "is_completed": enr.progress_percentage >= 100.0
        })
    return results


@router.get("/dashboard")
def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    enrolled_count = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e.progress_percentage >= 100.0)
    
    completed_sections_count = db.query(LearningProgress).filter(
        LearningProgress.student_id == current_user.id,
        LearningProgress.is_completed == True
    ).count()
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == current_user.id).all()
    if attempts:
        avg_score = round(sum(a.score for a in attempts) / len(attempts), 1)
    else:
        avg_score = 0.0
        
    certificates_count = db.query(Certificate).filter(Certificate.student_id == current_user.id).count()
    
    # Collect weak concepts from past quiz attempts to form recommended revision topics
    weak_concepts = []
    strong_concepts = []
    import json
    for a in attempts:
        try:
            w = json.loads(a.weak_concepts) if a.weak_concepts else []
            weak_concepts.extend(w)
            s = json.loads(a.strong_concepts) if a.strong_concepts else []
            strong_concepts.extend(s)
        except Exception:
            pass
            
    # Deduplicate while preserving order
    unique_weak = list(dict.fromkeys(weak_concepts))
    unique_strong = list(dict.fromkeys(strong_concepts))
    
    # Recent activity
    recent_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    
    recent_activity = []
    for a in recent_attempts:
        sec = a.section
        recent_activity.append({
            "id": a.id,
            "section_title": sec.title if sec else "Quiz Assessment",
            "score": a.score,
            "passed": a.passed,
            "completed_at": a.completed_at
        })

    return {
        "enrolled_courses_count": enrolled_count,
        "completed_courses_count": completed_courses,
        "completed_sections_count": completed_sections_count,
        "average_quiz_score": avg_score,
        "study_streak_days": 5,  # active consistent demo streak
        "certificates_count": certificates_count,
        "recommended_revision_topics": unique_weak[:5] if unique_weak else ["Supervised Learning Loss Functions", "Evaluation Metrics & ROC Curves"],
        "strong_topics": unique_strong[:5],
        "recent_activity": recent_activity
    }
