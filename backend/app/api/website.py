from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.models import GradeRecord, SiteArticle, SiteAttachment, SiteBanner, SiteChannel, SiteLink, StudentRecord, TeachingSchedule, User
from app.schemas.schemas import ArticleOut, BannerOut, ChannelOut

router = APIRouter(prefix="/website", tags=["website"])
student_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/student-login")


def get_current_student(token: str = Depends(student_oauth2_scheme), db: Session = Depends(get_db)) -> StudentRecord:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        student_id = payload.get("student_id")
        role = payload.get("role")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="学生登录已失效") from exc
    if role != "student" or not student_id:
        raise HTTPException(status_code=401, detail="请先使用学生账号登录")
    student = db.get(StudentRecord, int(student_id))
    if not student:
        raise HTTPException(status_code=401, detail="学生档案不存在")
    return student


@router.get("/banners", response_model=list[BannerOut])
def banners(db: Session = Depends(get_db)) -> list[SiteBanner]:
    return db.query(SiteBanner).filter(SiteBanner.is_active == True).order_by(SiteBanner.sort_order.asc()).all()


@router.get("/channels", response_model=list[ChannelOut])
def channels(nav_only: bool = False, db: Session = Depends(get_db)) -> list[SiteChannel]:
    query = db.query(SiteChannel).filter(SiteChannel.is_active == True)
    if nav_only:
        query = query.filter(SiteChannel.is_nav == True)
    return query.order_by(SiteChannel.sort_order.asc(), SiteChannel.id.asc()).all()


@router.get("/links")
def links(link_type: str = "", db: Session = Depends(get_db)) -> list[dict]:
    query = db.query(SiteLink).filter(SiteLink.is_active == True)
    if link_type:
        query = query.filter(SiteLink.link_type == link_type)
    rows = query.order_by(SiteLink.sort_order.asc(), SiteLink.id.asc()).all()
    return [{"id": row.id, "title": row.title, "url": row.url, "link_type": row.link_type} for row in rows]


@router.get("/articles", response_model=list[ArticleOut])
def articles(channel: str = "", keyword: str = "", db: Session = Depends(get_db)) -> list[SiteArticle]:
    query = db.query(SiteArticle).filter(SiteArticle.publish_status == "已发布")
    if channel:
        query = query.filter(SiteArticle.channel == channel)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(SiteArticle.title.like(like), SiteArticle.summary.like(like), SiteArticle.content.like(like)))
    return query.order_by(SiteArticle.is_top.desc(), SiteArticle.publish_date.desc(), SiteArticle.id.desc()).limit(50).all()


@router.get("/articles/{article_id}")
def article_detail(article_id: int, db: Session = Depends(get_db)) -> dict:
    article = db.get(SiteArticle, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    article.view_count += 1
    db.commit()
    files = db.query(SiteAttachment).filter(SiteAttachment.article_id == article_id).all()
    attachments = [
        {
            "id": item.id,
            "file_name": item.file_name,
            "file_url": item.file_url,
            "file_type": item.file_type,
            "file_size": item.file_size,
            "download_count": item.download_count,
        }
        for item in files
    ]
    return {"article": ArticleOut.model_validate(article), "attachments": attachments}


@router.get("/schedule")
def public_schedule(class_name: str = "24人工智能班", db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(TeachingSchedule)
        .filter(TeachingSchedule.class_name == class_name)
        .order_by(TeachingSchedule.id.asc())
        .all()
    )
    return [
        {
            "id": row.id,
            "day": row.day,
            "time": row.time,
            "course": row.course,
            "teacher": row.teacher,
            "room": row.room,
            "className": row.class_name,
            "status": row.status,
        }
        for row in rows
    ]


@router.get("/student/me")
def student_me(student: StudentRecord = Depends(get_current_student)) -> dict:
    return {
        "id": student.id,
        "name": student.name,
        "studentNo": student.student_no,
        "examNo": student.exam_no,
        "className": student.class_name,
        "major": student.major,
    }


@router.get("/student/schedule")
def student_schedule(student: StudentRecord = Depends(get_current_student), db: Session = Depends(get_db)) -> dict:
    rows = (
        db.query(TeachingSchedule)
        .filter(TeachingSchedule.class_name == student.class_name)
        .order_by(TeachingSchedule.id.asc())
        .all()
    )
    grades = (
        db.query(GradeRecord)
        .filter(GradeRecord.student_id == student.id)
        .order_by(GradeRecord.id.asc())
        .all()
    )
    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "studentNo": student.student_no,
            "examNo": student.exam_no,
            "className": student.class_name,
            "major": student.major,
        },
        "schedules": [
            {
                "id": row.id,
                "day": row.day,
                "time": row.time,
                "course": row.course,
                "teacher": row.teacher,
                "room": row.room,
                "className": row.class_name,
                "status": row.status,
            }
            for row in rows
        ],
        "grades": [
            {
                "id": row.id,
                "course": row.course,
                "processScore": row.process_score,
                "finalScore": row.final_score,
                "practiceScore": row.practice_score,
                "totalScore": row.total_score,
                "attendance": row.attendance,
                "assessment": row.assessment,
                "status": row.status,
            }
            for row in grades
        ],
    }


@router.post("/articles/{article_id}/audit")
def audit_article(article_id: int, review_status: str, comment: str = "", db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    article = db.get(SiteArticle, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    article.review_status = review_status
    article.review_comment = comment
    article.publish_status = "已发布" if review_status == "已发布" else "草稿"
    db.commit()
    return {"success": True}
