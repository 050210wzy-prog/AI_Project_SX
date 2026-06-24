from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import MailMessage, SiteArticle, User

router = APIRouter(prefix="/systems", tags=["校内系统"])


class MailCreate(BaseModel):
    recipient: str
    subject: str
    body: str


@router.get("/portal")
def portal(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    notices = (
        db.query(SiteArticle)
        .filter(or_(SiteArticle.channel == "通知公告", SiteArticle.channel == "信息服务"))
        .order_by(SiteArticle.publish_date.desc(), SiteArticle.id.desc())
        .limit(6)
        .all()
    )
    return {
        "user": {"username": user.username, "role": user.role, "email": user.email},
        "today": date.today().isoformat(),
        "schedule": [
            {"time": "08:30", "title": "综合交通专业群课程", "location": "新桥校区 教学楼A区"},
            {"time": "10:20", "title": "实训项目训练", "location": "综合实训中心"},
            {"time": "14:30", "title": "校园服务事项办理", "location": "线上办事大厅"},
        ],
        "apps": [
            {"title": "我的课表", "desc": "查看本周课程、教学地点和任课教师"},
            {"title": "成绩查询", "desc": "查看课程成绩、考试安排和学业进度"},
            {"title": "待办事项", "desc": "查看审批、通知、报修和个人待办"},
            {"title": "常用应用", "desc": "进入教务、办公、图书馆、缴费和服务系统"},
        ],
        "notices": [
            {"id": item.id, "title": item.title, "date": item.publish_date.isoformat() if item.publish_date else ""}
            for item in notices
        ],
    }


@router.get("/vpn/resources")
def vpn_resources(_: User = Depends(get_current_user)) -> dict:
    return {
        "resources": [
            {"title": "教务系统", "url": "/service/常用系统导航", "desc": "课表、选课、成绩和教学评价"},
            {"title": "图书馆数据库", "url": "https://www.acvtc.edu.cn/tsg/", "desc": "图书馆主页、电子资源和学习服务"},
            {"title": "协同办公系统", "url": "https://jyoa.acvtc.edu.cn/", "desc": "公文流转、会议和流程审批"},
            {"title": "网上办事大厅", "url": "https://ehall.acvtc.edu.cn/", "desc": "师生一站式在线办理服务"},
        ]
    }


@router.get("/mail/messages")
def mail_messages(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    mailbox = user.email or user.username
    rows = (
        db.query(MailMessage)
        .filter(or_(MailMessage.recipient == mailbox, MailMessage.recipient == user.username, MailMessage.sender_id == user.id))
        .order_by(MailMessage.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "mailbox": mailbox,
        "messages": [
            {
                "id": item.id,
                "sender": item.sender_name,
                "recipient": item.recipient,
                "subject": item.subject,
                "body": item.body,
                "is_read": item.is_read,
                "created_at": item.created_at.isoformat() if item.created_at else "",
            }
            for item in rows
        ],
    }


@router.post("/mail/messages")
def send_mail(payload: MailCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if not payload.recipient.strip() or not payload.subject.strip() or not payload.body.strip():
        raise HTTPException(status_code=400, detail="收件人、主题和正文不能为空")
    row = MailMessage(
        sender_id=user.id,
        sender_name=user.username,
        recipient=payload.recipient.strip(),
        subject=payload.subject.strip(),
        body=payload.body.strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"success": True, "id": row.id}


@router.post("/mail/messages/{message_id}/read")
def mark_read(message_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    row = db.get(MailMessage, message_id)
    if not row:
        raise HTTPException(status_code=404, detail="邮件不存在")
    mailbox = user.email or user.username
    if row.recipient not in {mailbox, user.username} and row.sender_id != user.id:
        raise HTTPException(status_code=403, detail="无权操作该邮件")
    row.is_read = True
    db.commit()
    return {"success": True}
