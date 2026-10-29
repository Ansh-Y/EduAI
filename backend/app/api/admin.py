from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.models import User, Course, Section, Enrollment, QuizAttempt, LearningProgress
from app.schemas.schemas import UserOut, UserUpdate, AdminOverviewOut

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/overview", response_model=AdminOverviewOut)
def get_admin_overview(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    
    total_courses = db.query(Course).count()
    published_courses = db.query(Course).filter(Course.is_published == True).count()
    
    total_enrollments = db.query(Enrollment).count()
    total_quiz_submissions = db.query(QuizAttempt).count()
    
    # Calculate global completion rate
    if total_enrollments > 0:
        completed_enrollments = db.query(Enrollment).filter(Enrollment.progress_percentage >= 100.0).count()
        completion_rate = round((completed_enrollments / total_enrollments) * 100.0, 1)
    else:
        completion_rate = 0.0
        
    user_distribution = [
        {"role": "Students", "count": total_students, "fill": "#4F46E5"},
        {"role": "Faculty / Teachers", "count": total_teachers, "fill": "#0EA5E9"},
        {"role": "Administrators", "count": total_users - total_students - total_teachers, "fill": "#F59E0B"}
    ]
    
    # Enrollments by Course
    courses = db.query(Course).all()
    enrollment_trends = []
    for c in courses:
        cnt = db.query(Enrollment).filter(Enrollment.course_id == c.id).count()
        enrollment_trends.append({
            "course": c.title[:25] + ("..." if len(c.title) > 25 else ""),
            "enrollments": cnt,
            "status": "Published" if c.is_published else "Draft"
        })
        
    # Recent activity
    recent_attempts = db.query(QuizAttempt).order_by(QuizAttempt.completed_at.desc()).limit(6).all()
    recent_activity = []
    for a in recent_attempts:
        st = a.student
        sec = a.section
        recent_activity.append({
            "type": "quiz_submission",
            "description": f"{st.name if st else 'Student'} scored {a.score}% on '{sec.title if sec else 'Quiz'}'",
            "status": "Passed" if a.passed else "Needs Review",
            "timestamp": a.completed_at.strftime("%Y-%m-%d %H:%M")
        })
        
    return AdminOverviewOut(
        total_users=total_users,
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        published_courses=published_courses,
        total_enrollments=total_enrollments,
        total_quiz_submissions=total_quiz_submissions,
        course_completion_rate=completion_rate,
        user_distribution=user_distribution,
        enrollment_trends=enrollment_trends,
        recent_activity=recent_activity
    )


@router.get("/users", response_model=List[UserOut])
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((User.name.ilike(term)) | (User.email.ilike(term)))
    if role and role != "all":
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
        
    return query.order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user_status(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Safeguard: prevent admin from deactivating or demoting themselves
    if target_user.id == current_user.id:
        if user_in.is_active is False:
            raise HTTPException(status_code=400, detail="Cannot deactivate your own administrator account.")
        if user_in.role and user_in.role != "admin":
            raise HTTPException(status_code=400, detail="Cannot demote your own administrator account.")
            
    if user_in.name is not None:
        target_user.name = user_in.name
    if user_in.role is not None:
        if user_in.role in ["teacher", "student", "admin"]:
            target_user.role = user_in.role
    if user_in.is_active is not None:
        target_user.is_active = user_in.is_active
        
    db.commit()
    db.refresh(target_user)
    return target_user
