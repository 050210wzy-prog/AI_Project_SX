from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import ROLE_PERMISSIONS, get_current_user
from app.core.security import create_access_token, verify_password
from app.models.models import StudentRecord, User
from app.schemas.schemas import LoginRequest, StudentLoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(user.id, {"role": user.role, "username": user.username})
    return Token(access_token=token, username=user.username, role=user.role, permissions=ROLE_PERMISSIONS.get(user.role, []))


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"id": user.id, "username": user.username, "role": user.role, "permissions": ROLE_PERMISSIONS.get(user.role, [])}


@router.post("/student-login")
def student_login(payload: StudentLoginRequest, db: Session = Depends(get_db)) -> dict:
    account = (payload.student_no or payload.exam_no or "").strip()
    student = db.query(StudentRecord).filter(StudentRecord.student_no == account).first()
    if not student:
        student = db.query(StudentRecord).filter(StudentRecord.exam_no == account).first()
    if not student:
        raise HTTPException(status_code=401, detail="学号或密码错误")
    if not student.student_no:
        student.student_no = student.exam_no
        db.commit()
    if payload.password != student.student_no:
        raise HTTPException(status_code=401, detail="学号或密码错误")
    token = create_access_token(f"student:{student.id}", {"role": "student", "student_no": student.student_no, "exam_no": student.exam_no, "student_id": student.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "student": {
            "id": student.id,
            "name": student.name,
            "studentNo": student.student_no,
            "examNo": student.exam_no,
            "className": student.class_name,
            "major": student.major,
        },
    }
