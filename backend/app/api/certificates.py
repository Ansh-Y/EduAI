import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.models import User, Certificate, Course
from app.schemas.schemas import CertificateOut
from app.services.pdf_generator import generate_course_certificate_pdf
from app.core.config import settings

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("", response_model=List[CertificateOut])
def list_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Certificate)
    if current_user.role == "student":
        query = query.filter(Certificate.student_id == current_user.id)
    certificates = query.order_by(Certificate.completion_date.desc()).all()
    
    results = []
    for cert in certificates:
        course = cert.course
        student = cert.student
        results.append(CertificateOut(
            id=cert.id,
            certificate_uid=cert.certificate_uid,
            course_id=cert.course_id,
            course_title=course.title if course else "University Course",
            student_name=student.name if student else current_user.name,
            completion_date=cert.completion_date,
            download_url=f"/api/certificates/{cert.id}/download"
        ))
    return results


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
        
    filename = f"certificate_{cert.certificate_uid}.pdf"
    filepath = os.path.join(settings.CERTIFICATES_DIR, filename)
    
    # If file was deleted or moved, regenerate dynamically
    if not os.path.exists(filepath):
        student = cert.student
        course = cert.course
        generate_course_certificate_pdf(
            student_name=student.name if student else "Student",
            course_title=course.title if course else "University Course",
            certificate_uid=cert.certificate_uid,
            completion_date=cert.completion_date.strftime("%B %d, %Y"),
            output_filename=filename
        )
        
    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail="Certificate file could not be rendered.")
        
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"EduAI_Certificate_{cert.certificate_uid}.pdf"
    )
