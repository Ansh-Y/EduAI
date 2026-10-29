import os
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.models import (
    User, Course, Section, Artifact, Enrollment, QuizQuestion, LearningProgress,
    ChatMessage, Certificate, Notification
)
from app.schemas.schemas import (
    SectionOut, SectionUpdate, ArtifactOut, ProgressUpdate, ChatRequest,
    ChatMessageOut, QuizQuestionOut
)
from app.ai.generator import answer_student_chat, generate_quiz_for_section
from app.services.pdf_generator import generate_smart_notes_pdf, generate_course_certificate_pdf
from app.services.docx_generator import generate_smart_notes_docx
from app.core.config import settings

router = APIRouter(prefix="/sections", tags=["Sections & Artifacts"])

@router.get("/{section_id}", response_model=SectionOut)
def get_section(
    section_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
        
    try:
        objs = json.loads(sec.objectives) if sec.objectives else []
    except Exception:
        objs = []
        
    progress = db.query(LearningProgress).filter(
        LearningProgress.student_id == current_user.id,
        LearningProgress.section_id == sec.id
    ).first()
    
    return SectionOut(
        id=sec.id,
        course_id=sec.course_id,
        title=sec.title,
        order_num=sec.order_num,
        content=sec.content,
        objectives=objs,
        summary=sec.summary,
        video_url=sec.video_url,
        summary_video_url=sec.summary_video_url,
        is_published=sec.is_published,
        artifacts=[ArtifactOut.from_orm(a) for a in sec.artifacts],
        is_completed=progress.is_completed if progress else False,
        is_unlocked=True,
        created_at=sec.created_at,
        updated_at=sec.updated_at
    )


@router.put("/{section_id}", response_model=SectionOut)
def update_section(
    section_id: int,
    sec_in: SectionUpdate,
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
        
    course = db.query(Course).filter(Course.id == sec.course_id).first()
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this section.")
        
    if sec_in.title is not None:
        sec.title = sec_in.title
    if sec_in.order_num is not None:
        sec.order_num = sec_in.order_num
    if sec_in.content is not None:
        sec.content = sec_in.content
    if sec_in.summary is not None:
        sec.summary = sec_in.summary
    if sec_in.is_published is not None:
        sec.is_published = sec_in.is_published
    if sec_in.objectives is not None:
        sec.objectives = json.dumps(sec_in.objectives)
        
    db.commit()
    db.refresh(sec)
    
    # Automatically regenerate notes PDF and DOCX on update
    try:
        objs = json.loads(sec.objectives) if sec.objectives else []
        pdf_name = f"notes_course_{course.id}_sec_{sec.id}.pdf"
        docx_name = f"notes_course_{course.id}_sec_{sec.id}.docx"
        generate_smart_notes_pdf(course.title, sec.title, objs, sec.content, sec.summary or "", pdf_name)
        generate_smart_notes_docx(course.title, sec.title, objs, sec.content, sec.summary or "", docx_name)
    except Exception:
        pass
        
    return SectionOut(
        id=sec.id,
        course_id=sec.course_id,
        title=sec.title,
        order_num=sec.order_num,
        content=sec.content,
        objectives=json.loads(sec.objectives) if sec.objectives else [],
        summary=sec.summary,
        video_url=sec.video_url,
        summary_video_url=sec.summary_video_url,
        is_published=sec.is_published,
        artifacts=[ArtifactOut.from_orm(a) for a in sec.artifacts],
        is_completed=False,
        is_unlocked=True,
        created_at=sec.created_at,
        updated_at=sec.updated_at
    )


@router.post("/{section_id}/generate")
def regenerate_artifacts(
    section_id: int,
    artifact_type: str = "all",  # "all", "notes_pdf", "notes_docx", "quiz"
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
    course = db.query(Course).filter(Course.id == sec.course_id).first()
    
    try:
        objs = json.loads(sec.objectives) if sec.objectives else []
    except Exception:
        objs = []
        
    pdf_name = f"notes_course_{course.id}_sec_{sec.id}.pdf"
    docx_name = f"notes_course_{course.id}_sec_{sec.id}.docx"
    
    if artifact_type in ["all", "notes_pdf"]:
        generate_smart_notes_pdf(course.title, sec.title, objs, sec.content, sec.summary or "", pdf_name)
        art = db.query(Artifact).filter(Artifact.section_id == sec.id, Artifact.artifact_type == "notes_pdf").first()
        if art:
            art.status = "completed"
            art.file_path = f"storage/notes/{pdf_name}"
        else:
            db.add(Artifact(section_id=sec.id, artifact_type="notes_pdf", status="completed", file_path=f"storage/notes/{pdf_name}"))
            
    if artifact_type in ["all", "notes_docx"]:
        generate_smart_notes_docx(course.title, sec.title, objs, sec.content, sec.summary or "", docx_name)
        art = db.query(Artifact).filter(Artifact.section_id == sec.id, Artifact.artifact_type == "notes_docx").first()
        if art:
            art.status = "completed"
            art.file_path = f"storage/notes/{docx_name}"
        else:
            db.add(Artifact(section_id=sec.id, artifact_type="notes_docx", status="completed", file_path=f"storage/notes/{docx_name}"))
            
    if artifact_type in ["all", "quiz"]:
        # Delete old questions and generate fresh ones
        db.query(QuizQuestion).filter(QuizQuestion.section_id == sec.id).delete()
        new_questions = generate_quiz_for_section(course.title, sec.title, sec.content, sec.order_num - 1)
        for q in new_questions:
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
    return {"message": f"Artifacts [{artifact_type}] regenerated successfully for section '{sec.title}'."}


@router.get("/{section_id}/notes/pdf")
def download_notes_pdf(section_id: int, db: Session = Depends(get_db)):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
    course = db.query(Course).filter(Course.id == sec.course_id).first()
    
    pdf_name = f"notes_course_{course.id}_sec_{sec.id}.pdf"
    filepath = os.path.join(settings.NOTES_DIR, pdf_name)
    
    # Generate on demand if missing
    if not os.path.exists(filepath):
        try:
            objs = json.loads(sec.objectives) if sec.objectives else []
        except Exception:
            objs = []
        generate_smart_notes_pdf(course.title, sec.title, objs, sec.content, sec.summary or "", pdf_name)
        
    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="Notes PDF generation failed")
        
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"EduAI_Notes_{sec.title.replace(' ', '_')}.pdf"
    )


@router.get("/{section_id}/notes/docx")
def download_notes_docx(section_id: int, db: Session = Depends(get_db)):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
    course = db.query(Course).filter(Course.id == sec.course_id).first()
    
    docx_name = f"notes_course_{course.id}_sec_{sec.id}.docx"
    filepath = os.path.join(settings.NOTES_DIR, docx_name)
    
    if not os.path.exists(filepath):
        try:
            objs = json.loads(sec.objectives) if sec.objectives else []
        except Exception:
            objs = []
        generate_smart_notes_docx(course.title, sec.title, objs, sec.content, sec.summary or "", docx_name)
        
    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="Notes DOCX generation failed")
        
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"EduAI_Notes_{sec.title.replace(' ', '_')}.docx"
    )


@router.get("/{section_id}/quiz", response_model=List[QuizQuestionOut])
def get_section_quiz_questions(
    section_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
        
    questions = db.query(QuizQuestion).filter(QuizQuestion.section_id == section_id).all()
    
    # If no questions exist yet, generate them dynamically!
    if not questions:
        course = db.query(Course).filter(Course.id == sec.course_id).first()
        gen_qs = generate_quiz_for_section(course.title, sec.title, sec.content, sec.order_num - 1)
        for q in gen_qs:
            q_obj = QuizQuestion(
                section_id=sec.id,
                question_text=q["question_text"],
                question_type=q.get("question_type", "multiple_choice"),
                options=json.dumps(q.get("options", [])),
                correct_answer=q["correct_answer"],
                explanation=q["explanation"],
                associated_concept=q.get("associated_concept", sec.title)
            )
            db.add(q_obj)
        db.commit()
        questions = db.query(QuizQuestion).filter(QuizQuestion.section_id == section_id).all()
        
    result = []
    is_teacher_or_admin = current_user.role in ["teacher", "admin"]
    for q in questions:
        try:
            opts = json.loads(q.options) if q.options else []
        except Exception:
            opts = []
            
        result.append(QuizQuestionOut(
            id=q.id,
            section_id=q.section_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=opts,
            correct_answer=q.correct_answer if is_teacher_or_admin else None,
            explanation=q.explanation if is_teacher_or_admin else None,
            associated_concept=q.associated_concept
        ))
    return result


@router.post("/{section_id}/progress")
def update_section_progress(
    section_id: int,
    req: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
        
    progress = db.query(LearningProgress).filter(
        LearningProgress.student_id == current_user.id,
        LearningProgress.section_id == section_id
    ).first()
    
    if not progress:
        progress = LearningProgress(
            student_id=current_user.id,
            section_id=section_id,
            is_completed=req.is_completed if req.is_completed is not None else False,
            video_progress=req.video_progress if req.video_progress is not None else 0.0
        )
        db.add(progress)
    else:
        if req.is_completed is not None:
            progress.is_completed = req.is_completed
        if req.video_progress is not None:
            progress.video_progress = max(progress.video_progress, req.video_progress)
            
    db.commit()
    
    # Recalculate enrollment overall course progress percentage
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == sec.course_id
    ).first()
    
    if enrollment:
        total_sections = db.query(Section).filter(Section.course_id == sec.course_id).count()
        if total_sections > 0:
            completed_sections = db.query(LearningProgress).join(Section).filter(
                Section.course_id == sec.course_id,
                LearningProgress.student_id == current_user.id,
                LearningProgress.is_completed == True
            ).count()
            
            calc_percent = round((completed_sections / total_sections) * 100.0, 1)
            enrollment.progress_percentage = min(100.0, calc_percent)
            db.commit()
            
            # Check for 100% completion & issue certificate automatically!
            if enrollment.progress_percentage >= 100.0:
                existing_cert = db.query(Certificate).filter(
                    Certificate.student_id == current_user.id,
                    Certificate.course_id == sec.course_id
                ).first()
                if not existing_cert:
                    course = db.query(Course).filter(Course.id == sec.course_id).first()
                    import uuid
                    uid = f"EDUAI-{uuid.uuid4().hex[:8].upper()}"
                    cert_file = f"certificate_{uid}.pdf"
                    generate_course_certificate_pdf(
                        student_name=current_user.name,
                        course_title=course.title,
                        certificate_uid=uid,
                        output_filename=cert_file
                    )
                    new_cert = Certificate(
                        student_id=current_user.id,
                        course_id=sec.course_id,
                        certificate_uid=uid,
                        file_path=f"storage/certificates/{cert_file}"
                    )
                    db.add(new_cert)
                    db.add(Notification(
                        recipient_id=current_user.id,
                        title="Course Completed & Certificate Earned!",
                        message=f"Congratulations! You completed '{course.title}' and earned your official certificate.",
                        notification_type="certificate_issued",
                        link="/student/certificates"
                    ))
                    db.commit()

    return {
        "status": "success",
        "is_completed": progress.is_completed,
        "video_progress": progress.video_progress,
        "course_progress": enrollment.progress_percentage if enrollment else 0.0
    }


@router.post("/{section_id}/chat", response_model=ChatMessageOut)
def chat_with_assistant(
    section_id: int,
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
        
    user_msg_text = req.message.strip()
    if not user_msg_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    # Save student user message
    user_msg = ChatMessage(
        student_id=current_user.id,
        section_id=section_id,
        role="user",
        message_content=user_msg_text
    )
    db.add(user_msg)
    db.commit()
    
    # Retrieve past conversation
    past_messages = db.query(ChatMessage).filter(
        ChatMessage.student_id == current_user.id,
        ChatMessage.section_id == section_id
    ).order_by(ChatMessage.timestamp).all()
    
    history_payload = [{"role": m.role, "content": m.message_content} for m in past_messages]
    
    # Generate assistant answer grounded in current section
    ans = answer_student_chat(
        section_title=sec.title,
        section_content=sec.content,
        chat_history=history_payload,
        user_message=user_msg_text
    )
    
    asst_msg = ChatMessage(
        student_id=current_user.id,
        section_id=section_id,
        role="assistant",
        message_content=ans["content"],
        sources_cited=ans.get("sources_cited")
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)
    
    return ChatMessageOut(
        id=asst_msg.id,
        role=asst_msg.role,
        message_content=asst_msg.message_content,
        sources_cited=asst_msg.sources_cited,
        timestamp=asst_msg.timestamp
    )


@router.get("/{section_id}/chat", response_model=List[ChatMessageOut])
def get_chat_history(
    section_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.student_id == current_user.id,
        ChatMessage.section_id == section_id
    ).order_by(ChatMessage.timestamp).all()
    
    return [
        ChatMessageOut(
            id=m.id,
            role=m.role,
            message_content=m.message_content,
            sources_cited=m.sources_cited,
            timestamp=m.timestamp
        ) for m in messages
    ]
