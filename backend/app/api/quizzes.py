import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.models import (
    User, Course, Section, QuizQuestion, QuizAttempt, LearningProgress,
    Enrollment, Notification, Certificate
)
from app.schemas.schemas import QuizSubmitRequest, QuizAttemptOut, QuizQuestionCreate
from app.services.pdf_generator import generate_course_certificate_pdf

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.post("/{section_id}/submit")
def submit_quiz_attempt(
    section_id: int,
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
    course = db.query(Course).filter(Course.id == sec.course_id).first()
    
    # 1. Enforce Attempt Limits
    past_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.section_id == section_id
    ).all()
    
    attempt_count = len(past_attempts)
    max_attempts = course.max_quiz_attempts or 3
    if attempt_count >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum attempt limit ({max_attempts}) reached for this section quiz."
        )
        
    questions = db.query(QuizQuestion).filter(QuizQuestion.section_id == section_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No quiz questions configured for this section.")
        
    # 2. Grade Submitted Answers
    correct_count = 0
    total_count = len(questions)
    weak_concepts_set = set()
    strong_concepts_set = set()
    question_evaluations = []
    
    for q in questions:
        submitted_val = req.answers.get(str(q.id), "").strip()
        correct_val = q.correct_answer.strip()
        
        is_correct = False
        if q.question_type in ["multiple_choice", "true_false"]:
            is_correct = (submitted_val.lower() == correct_val.lower())
        elif q.question_type == "fill_blank":
            is_correct = (submitted_val.lower() == correct_val.lower())
        elif q.question_type == "short_answer":
            # Keyword or containment matching rubric
            key_words = [w.lower() for w in correct_val.split() if len(w) > 4]
            matches = sum(1 for kw in key_words if kw in submitted_val.lower())
            is_correct = (matches >= max(1, len(key_words) // 3)) or (len(submitted_val) > 15)
            
        if is_correct:
            correct_count += 1
            strong_concepts_set.add(q.associated_concept)
        else:
            weak_concepts_set.add(q.associated_concept)
            
        question_evaluations.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "submitted_answer": submitted_val,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "explanation": q.explanation,
            "associated_concept": q.associated_concept
        })
        
    score_percentage = round((correct_count / total_count) * 100.0, 1)
    passing_threshold = course.passing_threshold or 70.0
    passed = (score_percentage >= passing_threshold)
    
    # 3. Generate Personalized Feedback Plan
    weak_list = list(weak_concepts_set)
    strong_list = [c for c in strong_concepts_set if c not in weak_concepts_set]
    
    if passed:
        if weak_list:
            feedback_plan = (
                f"Great job passing with {score_percentage}%! To reach full mastery, "
                f"review the following concepts before the final exam: {', '.join(weak_list)}."
            )
        else:
            feedback_plan = (
                f"Perfect score of {score_percentage}%! You demonstrated flawless comprehension "
                f"across all evaluated learning objectives."
            )
    else:
        feedback_plan = (
            f"You scored {score_percentage}%, which is below the passing threshold of {passing_threshold}%. "
            f"Focus your revision on: {', '.join(weak_list)}. Review the Smart Notes PDF and ask the AI Tutor for clarification before retrying."
        )
        
    # 4. Save Attempt
    attempt = QuizAttempt(
        student_id=current_user.id,
        section_id=section_id,
        attempt_num=attempt_count + 1,
        submitted_answers=json.dumps(req.answers),
        score=score_percentage,
        total_questions=total_count,
        correct_count=correct_count,
        passed=passed,
        weak_concepts=json.dumps(weak_list),
        strong_concepts=json.dumps(strong_list),
        feedback_plan=feedback_plan,
        completed_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    # 5. Update Progress if Passed
    if passed:
        prog = db.query(LearningProgress).filter(
            LearningProgress.student_id == current_user.id,
            LearningProgress.section_id == section_id
        ).first()
        if not prog:
            prog = LearningProgress(
                student_id=current_user.id,
                section_id=section_id,
                is_completed=True,
                video_progress=100.0
            )
            db.add(prog)
        else:
            prog.is_completed = True
        db.commit()
        
        # Update course overall enrollment progress
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course.id
        ).first()
        if enrollment:
            total_sec = db.query(Section).filter(Section.course_id == course.id).count()
            comp_sec = db.query(LearningProgress).join(Section).filter(
                Section.course_id == course.id,
                LearningProgress.student_id == current_user.id,
                LearningProgress.is_completed == True
            ).count()
            enrollment.progress_percentage = min(100.0, round((comp_sec / total_sec) * 100.0, 1))
            db.commit()
            
            # Auto-issue certificate if 100%
            if enrollment.progress_percentage >= 100.0:
                existing_cert = db.query(Certificate).filter(
                    Certificate.student_id == current_user.id,
                    Certificate.course_id == course.id
                ).first()
                if not existing_cert:
                    import uuid
                    uid = f"EDUAI-{uuid.uuid4().hex[:8].upper()}"
                    cert_file = f"certificate_{uid}.pdf"
                    generate_course_certificate_pdf(
                        student_name=current_user.name,
                        course_title=course.title,
                        certificate_uid=uid,
                        output_filename=cert_file
                    )
                    db.add(Certificate(
                        student_id=current_user.id,
                        course_id=course.id,
                        certificate_uid=uid,
                        file_path=f"storage/certificates/{cert_file}"
                    ))
                    db.commit()

    # Create Notification
    status_msg = "Passed" if passed else "Needs Review"
    db.add(Notification(
        recipient_id=current_user.id,
        title=f"Quiz Graded: {sec.title} ({score_percentage}%)",
        message=f"Attempt {attempt.attempt_num} evaluated: {status_msg}. {feedback_plan}",
        notification_type="quiz_graded",
        link=f"/learn/{course.id}"
    ))
    db.commit()
    
    return {
        "attempt_id": attempt.id,
        "attempt_num": attempt.attempt_num,
        "attempts_remaining": max_attempts - attempt.attempt_num,
        "score": score_percentage,
        "total_questions": total_count,
        "correct_count": correct_count,
        "passed": passed,
        "passing_threshold": passing_threshold,
        "weak_concepts": weak_list,
        "strong_concepts": strong_list,
        "feedback_plan": feedback_plan,
        "evaluations": question_evaluations
    }


@router.get("/{section_id}/attempts", response_model=List[QuizAttemptOut])
def get_quiz_attempts(
    section_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.section_id == section_id
    ).order_by(QuizAttempt.attempt_num.desc()).all()
    
    result = []
    for a in attempts:
        try:
            sub_ans = json.loads(a.submitted_answers) if a.submitted_answers else {}
        except Exception:
            sub_ans = {}
        try:
            weak = json.loads(a.weak_concepts) if a.weak_concepts else []
        except Exception:
            weak = []
        try:
            strong = json.loads(a.strong_concepts) if a.strong_concepts else []
        except Exception:
            strong = []
            
        result.append(QuizAttemptOut(
            id=a.id,
            student_id=a.student_id,
            section_id=a.section_id,
            attempt_num=a.attempt_num,
            submitted_answers=sub_ans,
            score=a.score,
            total_questions=a.total_questions,
            correct_count=a.correct_count,
            passed=a.passed,
            weak_concepts=weak,
            strong_concepts=strong,
            feedback_plan=a.feedback_plan,
            completed_at=a.completed_at
        ))
    return result


@router.put("/{section_id}/questions")
def update_quiz_questions(
    section_id: int,
    questions: List[QuizQuestionCreate],
    current_user: User = Depends(require_role(["teacher", "admin"])),
    db: Session = Depends(get_db)
):
    sec = db.query(Section).filter(Section.id == section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
        
    db.query(QuizQuestion).filter(QuizQuestion.section_id == section_id).delete()
    for q in questions:
        db.add(QuizQuestion(
            section_id=sec.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=json.dumps(q.options),
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            associated_concept=q.associated_concept
        ))
    db.commit()
    return {"message": f"Successfully updated {len(questions)} quiz questions."}
