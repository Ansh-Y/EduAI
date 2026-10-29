import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.models import User, Course, Section, Artifact, Enrollment, QuizQuestion, Notification, LearningProgress
from app.schemas.schemas import CourseOut, CourseDetailOut, CourseCreate, CourseUpdate, CourseGenerateRequest, SectionOut, ArtifactOut
from app.ai.generator import generate_course_content, generate_quiz_for_section, is_ai_configured
from app.services.pdf_generator import generate_smart_notes_pdf
from app.services.docx_generator import generate_smart_notes_docx

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("", response_model=List[CourseOut])
def list_courses(
    search: Optional[str] = None,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    mine_only: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Course)
    
    # If teacher asks for "mine_only", restrict to teacher's courses
    if mine_only and current_user.role in ["teacher", "admin"]:
        query = query.filter(Course.teacher_id == current_user.id)
    elif current_user.role == "student":
        # Students should only discover published courses
        query = query.filter(Course.is_published == True)
        
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Course.title.ilike(term)) | (Course.description.ilike(term)) | (Course.subject.ilike(term)))
    if subject and subject != "all":
        query = query.filter(Course.subject.ilike(f"%{subject}%"))
    if difficulty and difficulty != "all":
        query = query.filter(Course.difficulty == difficulty)
        
    courses = query.order_by(Course.created_at.desc()).all()
    
    result = []
    for c in courses:
        enrolled_count = db.query(Enrollment).filter(Enrollment.course_id == c.id).count()
        sections_count = db.query(Section).filter(Section.course_id == c.id).count()
        teacher = db.query(User).filter(User.id == c.teacher_id).first()
        result.append(CourseOut(
            id=c.id,
            title=c.title,
            description=c.description,
            subject=c.subject,
            difficulty=c.difficulty,
            teacher_id=c.teacher_id,
            teacher_name=teacher.name if teacher else "Faculty Member",
            is_published=c.is_published,
            passing_threshold=c.passing_threshold,
            max_quiz_attempts=c.max_quiz_attempts,
            sections_count=sections_count,
            enrolled_count=enrolled_count,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))
    return result


@router.post("/generate", response_model=CourseDetailOut)
def generate_course(
    request: CourseGenerateRequest,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    # 1. Create Course Record
    course = Course(
        title=request.title.strip(),
        description=request.description or f"AI-generated university course on {request.subject}.",
        subject=request.subject.strip(),
        difficulty=request.difficulty,
        teacher_id=current_user.id,
        is_published=False,  # Defaults to draft so teacher can review
        passing_threshold=70.0,
        max_quiz_attempts=3
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # 2. Call AI Content Generator
    generated_sections = generate_course_content(
        title=request.title,
        subject=request.subject,
        description=request.description or "",
        prompt=request.prompt or "",
        difficulty=request.difficulty,
        section_count=request.section_count
    )
    
    sample_videos = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    ]
    
    created_sections = []
    for idx, sec_info in enumerate(generated_sections):
        sec = Section(
            course_id=course.id,
            title=sec_info.get("title", f"Section {idx+1}"),
            order_num=idx + 1,
            content=sec_info.get("content", ""),
            objectives=json.dumps(sec_info.get("objectives", [])),
            summary=sec_info.get("summary", ""),
            video_url=sample_videos[idx % len(sample_videos)],
            summary_video_url=sample_videos[(idx + 1) % len(sample_videos)],
            is_published=True
        )
        db.add(sec)
        db.commit()
        db.refresh(sec)
        
        # Pre-generate Real PDF & DOCX notes
        pdf_name = f"notes_course_{course.id}_sec_{sec.id}.pdf"
        docx_name = f"notes_course_{course.id}_sec_{sec.id}.docx"
        try:
            generate_smart_notes_pdf(
                course_title=course.title,
                section_title=sec.title,
                objectives=sec_info.get("objectives", []),
                content=sec.content,
                summary=sec.summary or "",
                output_filename=pdf_name
            )
            generate_smart_notes_docx(
                course_title=course.title,
                section_title=sec.title,
                objectives=sec_info.get("objectives", []),
                content=sec.content,
                summary=sec.summary or "",
                output_filename=docx_name
            )
        except Exception:
            pass
            
        # Create Six Artifacts
        artifacts = [
            Artifact(section_id=sec.id, artifact_type="script", status="completed"),
            Artifact(section_id=sec.id, artifact_type="main_video", status="completed", file_path=sec.video_url),
            Artifact(section_id=sec.id, artifact_type="summary_video", status="completed", file_path=sec.summary_video_url),
            Artifact(section_id=sec.id, artifact_type="notes_pdf", status="completed", file_path=f"storage/notes/{pdf_name}"),
            Artifact(section_id=sec.id, artifact_type="notes_docx", status="completed", file_path=f"storage/notes/{docx_name}"),
            Artifact(section_id=sec.id, artifact_type="quiz", status="completed")
        ]
        db.add_all(artifacts)
        
        # Generate Quiz Questions
        quiz_questions = generate_quiz_for_section(
            course_title=course.title,
            section_title=sec.title,
            section_content=sec.content,
            section_index=idx
        )
        for q in quiz_questions:
            db.add(QuizQuestion(
                section_id=sec.id,
                question_text=q["question_text"],
                question_type=q.get("question_type", "multiple_choice"),
                options=json.dumps(q.get("options", [])),
                correct_answer=q["correct_answer"],
                explanation=q["explanation"],
                associated_concept=q.get("associated_concept", sec.title)
            ))
        db.commit()
        created_sections.append(sec)

    # In-app notification for teacher
    db.add(Notification(
        recipient_id=current_user.id,
        title="Course Generation Completed",
        message=f"Course '{course.title}' has been generated with {len(created_sections)} sections and smart study materials.",
        notification_type="course_created",
        link=f"/teacher/courses/{course.id}"
    ))
    db.commit()

    return get_course_detail_internal(course.id, current_user, db)


@router.post("", response_model=CourseOut)
def create_course_manual(
    course_in: CourseCreate,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    course = Course(
        title=course_in.title,
        description=course_in.description,
        subject=course_in.subject,
        difficulty=course_in.difficulty,
        teacher_id=current_user.id,
        is_published=False
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        subject=course.subject,
        difficulty=course.difficulty,
        teacher_id=course.teacher_id,
        teacher_name=current_user.name,
        is_published=course.is_published,
        passing_threshold=course.passing_threshold,
        max_quiz_attempts=course.max_quiz_attempts,
        sections_count=0,
        enrolled_count=0,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.get("/{course_id}", response_model=CourseDetailOut)
def get_course_detail(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_course_detail_internal(course_id, current_user, db)


def get_course_detail_internal(course_id: int, current_user: User, db: Session) -> CourseDetailOut:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Check permissions: if unpublished, only teacher/owner or admin can access
    if not course.is_published and current_user.role == "student" and current_user.id != course.teacher_id:
        raise HTTPException(status_code=403, detail="This course is in draft mode and not yet published.")
        
    sections = db.query(Section).filter(Section.course_id == course.id).order_by(Section.order_num).all()
    enrollment = db.query(Enrollment).filter(
        Enrollment.course_id == course.id,
        Enrollment.student_id == current_user.id
    ).first()
    
    sections_out = []
    prev_completed_or_unlocked = True  # Section 1 is unlocked by default
    
    for s in sections:
        # Check progress for this section
        progress = db.query(LearningProgress).filter(
            LearningProgress.student_id == current_user.id,
            LearningProgress.section_id == s.id
        ).first()
        is_completed = progress.is_completed if progress else False
        
        # Section unlocking rule:
        # Teachers and Admins have everything unlocked
        # Students have Section 1 unlocked; Section N is unlocked if Section N-1 was completed
        is_unlocked = True if current_user.role in ["teacher", "admin"] else prev_completed_or_unlocked
        
        # Prepare for next section
        prev_completed_or_unlocked = is_completed
        
        # Parse objectives
        try:
            objs = json.loads(s.objectives) if s.objectives else []
        except Exception:
            objs = []
            
        artifacts_out = [
            ArtifactOut(
                id=a.id,
                section_id=a.section_id,
                artifact_type=a.artifact_type,
                status=a.status,
                file_path=a.file_path,
                error_details=a.error_details,
                updated_at=a.updated_at
            ) for a in s.artifacts
        ]
        
        sections_out.append(SectionOut(
            id=s.id,
            course_id=s.course_id,
            title=s.title,
            order_num=s.order_num,
            content=s.content,
            objectives=objs,
            summary=s.summary,
            video_url=s.video_url,
            summary_video_url=s.summary_video_url,
            is_published=s.is_published,
            artifacts=artifacts_out,
            is_completed=is_completed,
            is_unlocked=is_unlocked,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
        
    teacher = db.query(User).filter(User.id == course.teacher_id).first()
    enrolled_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
    
    return CourseDetailOut(
        id=course.id,
        title=course.title,
        description=course.description,
        subject=course.subject,
        difficulty=course.difficulty,
        teacher_id=course.teacher_id,
        teacher_name=teacher.name if teacher else "Faculty Member",
        is_published=course.is_published,
        passing_threshold=course.passing_threshold,
        max_quiz_attempts=course.max_quiz_attempts,
        sections_count=len(sections),
        enrolled_count=enrolled_count,
        created_at=course.created_at,
        updated_at=course.updated_at,
        sections=sections_out,
        is_enrolled=bool(enrollment),
        student_progress=enrollment.progress_percentage if enrollment else 0.0
    )


@router.put("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this course.")
        
    for field, val in course_in.dict(exclude_unset=True).items():
        setattr(course, field, val)
    db.commit()
    db.refresh(course)
    
    teacher = db.query(User).filter(User.id == course.teacher_id).first()
    enrolled_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
    sections_count = db.query(Section).filter(Section.course_id == course.id).count()
    
    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        subject=course.subject,
        difficulty=course.difficulty,
        teacher_id=course.teacher_id,
        teacher_name=teacher.name if teacher else "Faculty Member",
        is_published=course.is_published,
        passing_threshold=course.passing_threshold,
        max_quiz_attempts=course.max_quiz_attempts,
        sections_count=sections_count,
        enrolled_count=enrolled_count,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this course.")
        
    db.delete(course)
    db.commit()
    return {"message": "Course and all associated materials deleted successfully."}


@router.post("/{course_id}/publish")
def toggle_publish_course(
    course_id: int,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to publish this course.")
        
    course.is_published = not course.is_published
    db.commit()
    
    if course.is_published:
        # Notify enrolled students or broad notification
        db.add(Notification(
            recipient_id=current_user.id,
            title="Course Published to Catalog",
            message=f"Course '{course.title}' is now live and accessible to enrolled students.",
            notification_type="course_published",
            link=f"/courses"
        ))
        db.commit()
        
    return {"is_published": course.is_published, "message": f"Course is now {'published' if course.is_published else 'saved as draft'}."}
