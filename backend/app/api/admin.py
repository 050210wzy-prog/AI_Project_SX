from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree
from zipfile import ZipFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin, require_permission
from app.models.models import (
    AiFeedback,
    AdminNotice,
    AttendanceRecord,
    CrawlRecord,
    CrawlSource,
    GradeRecord,
    AI_CLASS_SCHEDULE,
    KnowledgeChunk,
    KnowledgeDocument,
    Major,
    InnovationConfig,
    OperationLog,
    ResourceFile,
    Score,
    SiteArticle,
    SiteArticleVersion,
    SiteBanner,
    SiteChannel,
    SystemConfig,
    StudentRecord,
    Ticket,
    TeachingSchedule,
    User,
    seed_defaults,
)
from app.schemas.schemas import (
    ArticleOut,
    ArticlePayload,
    ArticleVersionOut,
    BannerOut,
    BannerPayload,
    ChannelOut,
    ChannelPayload,
    KnowledgeOut,
    ResourceOut,
    TicketOut,
    TicketReplyPayload,
)
from app.services.vector_service import add_chunks_to_chroma
from app.services.crawler_service import crawl_source

router = APIRouter(prefix="/admin", tags=["绠＄悊鍚庡彴"])
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"


class ConfigPayload(BaseModel):
    key: str
    value: str | None = ""
    group_name: str = "閫氱敤"
    description: str | None = None


class InnovationPayload(BaseModel):
    title: str
    description: str | None = None
    enabled: bool = True
    sort_order: int = 0
    config_json: str | None = None


class StudentPayload(BaseModel):
    exam_no: str
    name: str
    major: str | None = ""
    class_name: str | None = ""
    phone: str | None = ""
    status: str = "待确认"
    counselor: str | None = "待分配"
    student_no: str | None = ""
    province: str | None = ""
    city: str | None = ""
    department: str | None = ""
    remark: str | None = ""
    id_card: str | None = ""
    birthday: str | None = ""
    gender: str | None = ""
    admission_type: str | None = ""
    admission_batch: str | None = ""
    subject: str | None = ""
    major_code: str | None = ""
    political_status: str | None = ""
    ethnicity: str | None = ""
    candidate_type: str | None = ""
    graduate_type: str | None = ""
    middle_school: str | None = ""
    foreign_language: str | None = ""
    area_code: str | None = ""
    area_name: str | None = ""
    address: str | None = ""
    postal_code: str | None = ""
    receiver: str | None = ""
    score: float | None = None
    application_choice: str | None = ""
    first_major: str | None = ""
    second_major: str | None = ""
    third_major: str | None = ""
    fourth_major: str | None = ""
    fifth_major: str | None = ""
    sixth_major: str | None = ""
    adjustment: str | None = ""
    chinese_score: float | None = None
    math_score: float | None = None
    foreign_score: float | None = None
    comprehensive_score: float | None = None
    subject_name: str | None = ""


class SchedulePayload(BaseModel):
    day: str
    time: str
    course: str
    teacher: str | None = ""
    room: str | None = ""
    class_name: str | None = ""
    status: str = "鑽夌"


class GradePayload(BaseModel):
    process_score: float = 0
    final_score: float = 0
    practice_score: float = 0
    attendance: int = 100
    assessment: str = "骞虫椂+鏈熸湯"
    status: str = "姝ｅ父"


class GradeSyncPayload(BaseModel):
    class_name: str
    course: str
    assessment: str = "骞虫椂+鏈熸湯"


class AttendancePayload(BaseModel):
    status: str = "宸插埌"
    remark: str | None = ""


class CrawlSourcePayload(BaseModel):
    name: str
    channel: str
    list_url: str
    base_url: str = "https://www.acvtc.edu.cn"
    enabled: bool = True
    publish_status: str = "待审核"


def write_log(db: Session, user: User, action: str, target: str = "", detail: str = "") -> None:
    db.add(OperationLog(username=user.username, action=action, target=target, detail=detail))


def read_xlsx_rows(path: Path) -> list[list[str]]:
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", namespace):
                shared.append("".join(text.text or "" for text in item.findall(".//m:t", namespace)))
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))

    rows = []
    for row in sheet.findall(".//m:sheetData/m:row", namespace):
        values = []
        for cell in row.findall("m:c", namespace):
            ref = cell.attrib.get("r", "")
            column = "".join(ch for ch in ref if ch.isalpha())
            column_index = 0
            for ch in column:
                column_index = column_index * 26 + ord(ch.upper()) - 64
            while len(values) < max(column_index - 1, 0):
                values.append("")
            raw = cell.find("m:v", namespace)
            inline = cell.find("m:is/m:t", namespace)
            value = ""
            if inline is not None:
                value = inline.text or ""
            elif raw is not None:
                value = raw.text or ""
                if cell.attrib.get("t") == "s":
                    value = shared[int(value)] if value.isdigit() and int(value) < len(shared) else ""
            values.append(str(value).strip())
        rows.append(values)
    return rows


STUDENT_EXTRA_FIELDS = [
    "student_no",
    "province",
    "city",
    "department",
    "remark",
    "id_card",
    "birthday",
    "gender",
    "admission_type",
    "admission_batch",
    "subject",
    "major_code",
    "political_status",
    "ethnicity",
    "candidate_type",
    "graduate_type",
    "middle_school",
    "foreign_language",
    "area_code",
    "area_name",
    "address",
    "postal_code",
    "receiver",
    "score",
    "application_choice",
    "first_major",
    "second_major",
    "third_major",
    "fourth_major",
    "fifth_major",
    "sixth_major",
    "adjustment",
    "chinese_score",
    "math_score",
    "foreign_score",
    "comprehensive_score",
    "subject_name",
]


STUDENT_EXCEL_FIELD_MAP = {
    "student_no": "瀛﹀彿",
    "province": "鐪佷唤",
    "city": "鍩庡競",
    "department": "闄㈢郴",
    "remark": "澶囨敞",
    "id_card": "韬唤璇佸彿",
    "birthday": "鍑虹敓骞存湀",
    "gender": "鎬у埆",
    "admission_type": "褰曞彇鏂瑰紡",
    "admission_batch": "褰曞彇鎵规",
    "subject": "绉戠被",
    "major_code": "涓撲笟浠ｇ爜",
    "political_status": "鏀挎不闈㈣矊",
    "ethnicity": "姘戞棌",
    "candidate_type": "鑰冪敓绫诲埆",
    "graduate_type": "姣曚笟绫诲埆",
    "middle_school": "涓鍚嶇О",
    "foreign_language": "澶栬璇",
    "area_code": "鍦板尯浠ｇ爜",
    "area_name": "鍦板尯鍚嶇О",
    "address": "瀹跺涵鍦板潃",
    "postal_code": "閭斂缂栫爜",
    "receiver": "收件人",
    "score": "鎶曟。鎴愮哗",
    "application_choice": "鎶曟。蹇楁効",
    "first_major": "濉姤涓撲笟1",
    "second_major": "濉姤涓撲笟2",
    "third_major": "濉姤涓撲笟3",
    "fourth_major": "濉姤涓撲笟4",
    "fifth_major": "濉姤涓撲笟5",
    "sixth_major": "濉姤涓撲笟6",
    "adjustment": "涓撲笟蹇楁効璋冨墏",
    "chinese_score": "璇枃",
    "math_score": "鏁板",
    "foreign_score": "澶栬",
    "comprehensive_score": "缁煎悎",
    "subject_name": "绉戠被鍚嶇О",
}


def parse_float(value: str) -> float | None:
    try:
        return float(value) if value != "" else None
    except ValueError:
        return None


def student_to_dict(row: StudentRecord) -> dict:
    data = {
        "id": row.id,
        "examNo": row.exam_no,
        "name": row.name,
        "major": row.major,
        "className": row.class_name,
        "phone": row.phone,
        "status": row.status,
        "counselor": row.counselor,
    }
    for field in STUDENT_EXTRA_FIELDS:
        data[field] = getattr(row, field)
    return data


def grade_to_dict(row: GradeRecord) -> dict:
    return {
        "id": row.id,
        "studentId": row.student_id,
        "examNo": row.exam_no,
        "student": row.student,
        "className": row.class_name,
        "major": row.major,
        "course": row.course,
        "score": row.score,
        "processScore": row.process_score,
        "finalScore": row.final_score,
        "practiceScore": row.practice_score,
        "totalScore": row.total_score,
        "attendance": row.attendance,
        "assessment": row.assessment,
        "status": row.status,
    }


def attendance_to_dict(row: AttendanceRecord) -> dict:
    return {
        "id": row.id,
        "scheduleId": row.schedule_id,
        "studentId": row.student_id,
        "examNo": row.exam_no,
        "student": row.student,
        "className": row.class_name,
        "course": row.course,
        "week": row.week,
        "status": row.status,
        "remark": row.remark,
        "updatedAt": row.updated_at.isoformat() if row.updated_at else "",
    }


def calculate_total_score(process_score: float, final_score: float, practice_score: float, assessment: str) -> float:
    if assessment == "项目考核":
        total = process_score * 0.4 + practice_score * 0.6
    elif assessment == "实训考核":
        total = process_score * 0.3 + practice_score * 0.7
    elif assessment == "过程性评价":
        total = process_score * 0.7 + practice_score * 0.3
    else:
        total = process_score * 0.3 + final_score * 0.5 + practice_score * 0.2
    return round(max(0, min(100, total)), 1)


def academic_status(total_score: float, attendance: int, manual_status: str) -> str:
    if manual_status and manual_status not in {"正常", "待录入"}:
        return manual_status
    if total_score <= 0:
        return "待录入"
    if total_score < 60:
        return "补考预警"
    if attendance < 80:
        return "需关注"
    return "正常"


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    if db.query(Major).count() == 0 and db.query(SiteArticle).count() == 0:
        seed_defaults(db)
    return {
        "majors": db.query(Major).count(),
        "scores": db.query(Score).count(),
        "articles": db.query(SiteArticle).count(),
        "pending_articles": db.query(SiteArticle).filter(SiteArticle.review_status == "待审核").count(),
        "pending_tickets": db.query(Ticket).filter(Ticket.status == "待处理").count(),
        "resources": db.query(ResourceFile).count(),
        "feedback": db.query(AiFeedback).count(),
        "hot_articles": [
            {"title": row.title, "views": row.view_count}
            for row in db.query(SiteArticle).order_by(SiteArticle.view_count.desc()).limit(6).all()
        ],
        "ticket_status": [
            {"status": status, "count": count}
            for status, count in db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
        ],
    }


@router.post("/dashboard/seed")
def seed_dashboard_data(db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    before = {
        "majors": db.query(Major).count(),
        "scores": db.query(Score).count(),
        "articles": db.query(SiteArticle).count(),
        "students": db.query(StudentRecord).count(),
        "schedules": db.query(TeachingSchedule).count(),
    }
    seed_defaults(db)
    after = {
        "majors": db.query(Major).count(),
        "scores": db.query(Score).count(),
        "articles": db.query(SiteArticle).count(),
        "students": db.query(StudentRecord).count(),
        "schedules": db.query(TeachingSchedule).count(),
    }
    write_log(db, user, "鍒濆鍖栧熀纭€鏁版嵁", "dashboard", f"{before} -> {after}")
    db.commit()
    return {"success": True, "before": before, "after": after}


@router.get("/tickets", response_model=list[TicketOut])
def tickets(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[Ticket]:
    return db.query(Ticket).order_by(Ticket.created_at.desc()).limit(100).all()


@router.post("/tickets/{ticket_id}/reply", response_model=TicketOut)
def reply_ticket(ticket_id: int, payload: TicketReplyPayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    ticket.answer = payload.answer
    ticket.assignee = user.username
    ticket.status = "已处理"
    if payload.feed_knowledge:
        doc = KnowledgeDocument(filename=f"工单反馈-{ticket_id}.txt", category=ticket.category or "人工答复", chunk_count=1)
        db.add(doc)
        db.flush()
        content = f"问题：{ticket.question}\n人工回复：{payload.answer}"
        chunk = KnowledgeChunk(document_id=doc.id, category=doc.category, source=doc.filename, content=content)
        db.add(chunk)
        db.flush()
        add_chunks_to_chroma([{"id": chunk.id, "content": chunk.content, "source": chunk.source, "category": chunk.category}])
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/site/channels", response_model=list[ChannelOut])
def site_channels(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[SiteChannel]:
    return db.query(SiteChannel).order_by(SiteChannel.sort_order.asc(), SiteChannel.id.asc()).all()


@router.post("/site/channels", response_model=ChannelOut)
def create_channel(payload: ChannelPayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteChannel:
    row = SiteChannel(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/site/channels/{row_id}", response_model=ChannelOut)
def update_channel(row_id: int, payload: ChannelPayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteChannel:
    row = db.get(SiteChannel, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="栏目不存在")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/site/channels/{row_id}")
def delete_channel(row_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    row = db.get(SiteChannel, row_id)
    if row:
        db.delete(row)
        db.commit()
    return {"success": True}


@router.get("/site/articles", response_model=list[ArticleOut])
def site_articles(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[SiteArticle]:
    return db.query(SiteArticle).order_by(SiteArticle.id.desc()).limit(200).all()


@router.post("/site/articles", response_model=ArticleOut)
def create_article(payload: ArticlePayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteArticle:
    row = SiteArticle(**payload.model_dump(exclude={"version_note"}))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/site/articles/{row_id}", response_model=ArticleOut)
def update_article(row_id: int, payload: ArticlePayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteArticle:
    row = db.get(SiteArticle, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="文章不存在")
    db.add(
        SiteArticleVersion(
            article_id=row.id,
            title=row.title,
            summary=row.summary,
            content=row.content,
            editor="admin",
            version_note=payload.version_note or "编辑前版本",
        )
    )
    for key, value in payload.model_dump(exclude={"version_note"}).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.get("/site/articles/{row_id}/versions", response_model=list[ArticleVersionOut])
def article_versions(row_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[SiteArticleVersion]:
    return db.query(SiteArticleVersion).filter(SiteArticleVersion.article_id == row_id).order_by(SiteArticleVersion.created_at.desc()).all()


@router.post("/site/articles/{row_id}/rollback/{version_id}", response_model=ArticleOut)
def rollback_article(row_id: int, version_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteArticle:
    article = db.get(SiteArticle, row_id)
    version = db.get(SiteArticleVersion, version_id)
    if not article or not version:
        raise HTTPException(status_code=404, detail="文章或版本不存在")
    db.add(
        SiteArticleVersion(
            article_id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            editor="admin",
            version_note="回滚前自动备份",
        )
    )
    article.title = version.title
    article.summary = version.summary
    article.content = version.content
    db.commit()
    db.refresh(article)
    return article


@router.delete("/site/articles/{row_id}")
def delete_article(row_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    row = db.get(SiteArticle, row_id)
    if row:
        db.delete(row)
        db.commit()
    return {"success": True}


@router.get("/site/banners", response_model=list[BannerOut])
def site_banners(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[SiteBanner]:
    return db.query(SiteBanner).order_by(SiteBanner.sort_order.asc(), SiteBanner.id.asc()).all()


@router.post("/site/banners", response_model=BannerOut)
def create_banner(payload: BannerPayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteBanner:
    row = SiteBanner(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/site/banners/{row_id}", response_model=BannerOut)
def update_banner(row_id: int, payload: BannerPayload, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> SiteBanner:
    row = db.get(SiteBanner, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="杞挱鍥句笉瀛樺湪")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/site/banners/{row_id}")
def delete_banner(row_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    row = db.get(SiteBanner, row_id)
    if row:
        db.delete(row)
        db.commit()
    return {"success": True}


@router.get("/knowledge", response_model=list[KnowledgeOut])
def knowledge_docs(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[KnowledgeDocument]:
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()


@router.post("/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...), category: str = "鎷涚敓鍜ㄨ", db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    raw = await file.read()
    text = raw.decode("utf-8", errors="ignore")
    chunks = [text[i : i + 500] for i in range(0, len(text), 450) if text[i : i + 500].strip()]
    doc = KnowledgeDocument(filename=file.filename or "knowledge.txt", category=category, chunk_count=len(chunks))
    db.add(doc)
    db.flush()
    created = []
    for chunk_text in chunks:
        row = KnowledgeChunk(document_id=doc.id, category=category, source=doc.filename, content=chunk_text)
        db.add(row)
        db.flush()
        created.append({"id": row.id, "content": row.content, "source": row.source, "category": row.category})
    db.commit()
    add_chunks_to_chroma(created)
    return {"success": True, "document_id": doc.id, "chunks": len(chunks)}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "file").suffix
    safe_name = f"{uuid4().hex}{suffix}"
    target = UPLOAD_DIR / safe_name
    target.write_bytes(await file.read())
    resource = ResourceFile(
        original_name=file.filename or safe_name,
        stored_name=safe_name,
        file_url=f"/uploads/{safe_name}",
        file_type=suffix.lstrip(".").lower(),
        file_size=target.stat().st_size,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return {
        "success": True,
        "id": resource.id,
        "filename": file.filename,
        "url": resource.file_url,
        "size": target.stat().st_size,
    }


@router.get("/resources", response_model=list[ResourceOut])
def resources(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[ResourceFile]:
    return db.query(ResourceFile).order_by(ResourceFile.created_at.desc()).all()


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    row = db.get(ResourceFile, resource_id)
    if row:
        db.delete(row)
        db.commit()
    return {"success": True}


@router.get("/system-configs")
def system_configs(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(SystemConfig).order_by(SystemConfig.group_name.asc(), SystemConfig.key.asc()).all()
    return [
        {
            "id": row.id,
            "key": row.key,
            "value": row.value,
            "group_name": row.group_name,
            "description": row.description,
            "updated_at": row.updated_at.isoformat() if row.updated_at else "",
        }
        for row in rows
    ]


@router.put("/system-configs/{key}")
def update_system_config(key: str, payload: ConfigPayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not row:
        row = SystemConfig(key=key)
        db.add(row)
    row.value = payload.value
    row.group_name = payload.group_name
    row.description = payload.description
    write_log(db, user, "鏇存柊绯荤粺閰嶇疆", key, payload.value or "")
    db.commit()
    return {"success": True}


@router.get("/innovation-configs")
def innovation_configs(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(InnovationConfig).order_by(InnovationConfig.sort_order.asc(), InnovationConfig.id.asc()).all()
    return [
        {
            "id": row.id,
            "feature_key": row.feature_key,
            "title": row.title,
            "description": row.description,
            "enabled": row.enabled,
            "sort_order": row.sort_order,
            "config_json": row.config_json,
        }
        for row in rows
    ]


@router.put("/innovation-configs/{feature_key}")
def update_innovation_config(
    feature_key: str,
    payload: InnovationPayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
) -> dict:
    row = db.query(InnovationConfig).filter(InnovationConfig.feature_key == feature_key).first()
    if not row:
        row = InnovationConfig(feature_key=feature_key, title=payload.title)
        db.add(row)
    row.title = payload.title
    row.description = payload.description
    row.enabled = payload.enabled
    row.sort_order = payload.sort_order
    row.config_json = payload.config_json
    write_log(db, user, "鏇存柊鍒涙柊鍔熻兘", feature_key, payload.title)
    db.commit()
    return {"success": True}


@router.get("/operation-logs")
def operation_logs(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(OperationLog).order_by(OperationLog.created_at.desc(), OperationLog.id.desc()).limit(100).all()
    return [
        {
            "id": row.id,
            "username": row.username,
            "action": row.action,
            "target": row.target,
            "detail": row.detail,
            "created_at": row.created_at.isoformat() if row.created_at else "",
        }
        for row in rows
    ]

@router.get("/health-check")
def health_check(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    db_ok = db.query(User).count() >= 0
    return {
        "database": "ok" if db_ok else "error",
        "upload_dir": "ok" if UPLOAD_DIR.exists() else "missing",
        "articles": db.query(SiteArticle).count(),
        "majors": db.query(Major).count(),
        "configs": db.query(SystemConfig).count(),
    }


@router.get("/students")
def student_records(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(StudentRecord).order_by(StudentRecord.created_at.desc(), StudentRecord.id.desc()).all()
    changed = False
    for row in rows:
        if not row.student_no:
            row.student_no = row.exam_no
            changed = True
    if changed:
        db.commit()
    return [student_to_dict(row) for row in rows]


@router.post("/students")
def create_student(payload: StudentPayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = StudentRecord(
        exam_no=payload.exam_no,
        name=payload.name,
        major=payload.major,
        class_name=payload.class_name,
        phone=payload.phone,
        status=payload.status,
        counselor=payload.counselor,
    )
    for field in STUDENT_EXTRA_FIELDS:
        setattr(row, field, getattr(payload, field))
    db.add(row)
    write_log(db, user, "鏂板瀛︾敓妗ｆ", payload.exam_no, payload.name)
    db.commit()
    return {"success": True, "id": row.id}


@router.post("/students/import")
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 学生表")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored = UPLOAD_DIR / f"{uuid4().hex}_{file.filename}"
    stored.write_bytes(await file.read())

    rows = read_xlsx_rows(stored)
    if not rows:
        raise HTTPException(status_code=400, detail="Excel 鏂囦欢涓虹┖")
    headers = rows[0]
    index = {name: pos for pos, name in enumerate(headers)}

    def value(row: list[str], name: str) -> str:
        pos = index.get(name)
        if pos is None or pos >= len(row):
            return ""
        return str(row[pos] or "").strip()

    def fill_extra_fields(target: StudentRecord, row: list[str]) -> None:
        for field, header in STUDENT_EXCEL_FIELD_MAP.items():
            raw = value(row, header)
            if field in {"score", "chinese_score", "math_score", "foreign_score", "comprehensive_score"}:
                setattr(target, field, parse_float(raw))
            else:
                setattr(target, field, raw)
        if not target.student_no:
            target.student_no = target.exam_no

    required = ["考生号", "姓名", "录取专业", "班级"]
    missing = [name for name in required if name not in index]
    if missing:
        raise HTTPException(status_code=400, detail=f"缂哄皯蹇呰鍒楋細{', '.join(missing)}")

    created = 0
    updated = 0
    skipped = 0
    for row in rows[1:]:
        exam_no = value(row, "考生号")
        name = value(row, "姓名")
        if not exam_no or not name:
            skipped += 1
            continue
        phone = value(row, "鑱旂郴鎵嬫満") or value(row, "鑱旂郴鐢佃瘽")
        student_no = value(row, "瀛﹀彿") or exam_no
        current = db.query(StudentRecord).filter(StudentRecord.exam_no == exam_no).first()
        if current:
            current.name = name
            current.major = value(row, "褰曞彇涓撲笟")
            current.class_name = value(row, "鐝骇")
            current.phone = phone
            current.student_no = student_no
            current.status = current.status or "已录取"
            current.counselor = current.counselor or "待分配"
            fill_extra_fields(current, row)
            updated += 1
        else:
            student = StudentRecord(
                exam_no=exam_no,
                name=name,
                major=value(row, "褰曞彇涓撲笟"),
                class_name=value(row, "鐝骇"),
                phone=phone,
                status="已录取",
                counselor="待分配",
                student_no=student_no,
            )
            fill_extra_fields(student, row)
            db.add(student)
            created += 1

    write_log(db, user, "瀵煎叆瀛︾敓 Excel", file.filename, f"鏂板 {created}锛屾洿鏂?{updated}锛岃烦杩?{skipped}")
    db.commit()
    return {"success": True, "created": created, "updated": updated, "skipped": skipped}


@router.put("/students/{student_id}")
def update_student(student_id: int, payload: StudentPayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(StudentRecord, student_id)
    if not row:
        raise HTTPException(status_code=404, detail="学生档案不存在")
    row.exam_no = payload.exam_no
    row.name = payload.name
    row.major = payload.major
    row.class_name = payload.class_name
    row.phone = payload.phone
    row.status = payload.status
    row.counselor = payload.counselor
    for field in STUDENT_EXTRA_FIELDS:
        setattr(row, field, getattr(payload, field))
    write_log(db, user, "鏇存柊瀛︾敓妗ｆ", payload.exam_no, payload.name)
    db.commit()
    return {"success": True}


@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(StudentRecord, student_id)
    if not row:
        raise HTTPException(status_code=404, detail="学生档案不存在")
    write_log(db, user, "鍒犻櫎瀛︾敓妗ｆ", row.exam_no, row.name)
    db.delete(row)
    db.commit()
    return {"success": True}


@router.post("/students/{student_id}/notice")
def notify_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(StudentRecord, student_id)
    if not row:
        raise HTTPException(status_code=404, detail="学生档案不存在")
    notice = AdminNotice(title=f"{row.name} 通知", content=f"已向 {row.name} 发送报到或材料提醒。", target=row.name)
    db.add(notice)
    write_log(db, user, "鍙戦€佸鐢熼€氱煡", row.exam_no, row.name)
    db.commit()
    return {"success": True}


@router.get("/admin-notices")
def admin_notices(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(AdminNotice).order_by(AdminNotice.created_at.desc()).limit(30).all()
    return [
        {
            "id": row.id,
            "time": row.created_at.date().isoformat() if row.created_at else "",
            "title": row.title,
            "content": row.content,
            "target": row.target,
        }
        for row in rows
    ]


@router.get("/academic/schedules")
def schedules(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    class_name = "24人工智能班"
    existing_ai_courses = {row[0] for row in db.query(TeachingSchedule.course).filter(TeachingSchedule.class_name == class_name).all()}
    expected_ai_courses = {course for _, _, course, _ in AI_CLASS_SCHEDULE}
    if not expected_ai_courses.issubset(existing_ai_courses):
        db.query(TeachingSchedule).filter(TeachingSchedule.class_name == class_name).delete()
        db.add_all(
            [
                TeachingSchedule(day=day, time=time, course=course, teacher="待分配", room=room, class_name=class_name, status="已发布")
                for day, time, course, room in AI_CLASS_SCHEDULE
            ]
        )
        db.commit()
    rows = db.query(TeachingSchedule).order_by(TeachingSchedule.id.asc()).all()
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
            "attendanceCreated": row.attendance_created,
        }
        for row in rows
    ]


@router.get("/academic/classes")
def academic_classes(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    classes = [
        row[0]
        for row in db.query(StudentRecord.class_name)
        .filter(StudentRecord.class_name.isnot(None), StudentRecord.class_name != "")
        .distinct()
        .order_by(StudentRecord.class_name.asc())
        .all()
    ]
    courses = [
        row[0]
        for row in db.query(TeachingSchedule.course)
        .filter(TeachingSchedule.course.isnot(None), TeachingSchedule.course != "")
        .distinct()
        .order_by(TeachingSchedule.course.asc())
        .all()
    ]
    if not courses:
        courses = ["Python程序设计", "人工智能基础", "数据库应用", "职业素养与就业指导"]
    return {"classes": classes, "courses": courses}


@router.post("/academic/schedules")
def create_schedule(payload: SchedulePayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = TeachingSchedule(
        day=payload.day,
        time=payload.time,
        course=payload.course,
        teacher=payload.teacher,
        room=payload.room,
        class_name=payload.class_name,
        status=payload.status,
    )
    db.add(row)
    write_log(db, user, "鏂板鎺掕", payload.class_name or "", payload.course)
    db.commit()
    return {"success": True, "id": row.id}


@router.put("/academic/schedules/{schedule_id}")
def update_schedule(schedule_id: int, payload: SchedulePayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(TeachingSchedule, schedule_id)
    if not row:
        raise HTTPException(status_code=404, detail="排课不存在")
    row.day = payload.day
    row.time = payload.time
    row.course = payload.course
    row.teacher = payload.teacher
    row.room = payload.room
    row.class_name = payload.class_name
    row.status = payload.status
    write_log(db, user, "鏇存柊鎺掕", str(schedule_id), payload.course)
    db.commit()
    return {"success": True}


@router.post("/academic/schedules/publish")
def publish_schedules(db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    count = 0
    for row in db.query(TeachingSchedule).all():
        row.status = "已发布"
        count += 1
    write_log(db, user, "发布课表", "academic", f"{count} 条")
    db.commit()
    return {"success": True, "count": count}


@router.post("/academic/schedules/{schedule_id}/attendance")
def create_attendance(schedule_id: int, week: int = 1, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(TeachingSchedule, schedule_id)
    if not row:
        raise HTTPException(status_code=404, detail="排课不存在")
    students = (
        db.query(StudentRecord)
        .filter(StudentRecord.class_name == row.class_name)
        .order_by(StudentRecord.name.asc(), StudentRecord.id.asc())
        .all()
    )
    created = 0
    for student in students:
        exists = (
            db.query(AttendanceRecord)
            .filter(AttendanceRecord.schedule_id == row.id, AttendanceRecord.week == week, AttendanceRecord.student_id == student.id)
            .first()
        )
        if exists:
            continue
        db.add(
            AttendanceRecord(
                schedule_id=row.id,
                student_id=student.id,
                exam_no=student.exam_no,
                student=student.name,
                class_name=student.class_name,
                course=row.course,
                week=week,
                status="已到",
            )
        )
        created += 1
    row.attendance_created = True
    write_log(db, user, "生成考勤名单", str(schedule_id), f"第{week}周 {row.course} 新增{created}人")
    db.commit()
    return {"success": True, "created": created, "total": len(students)}


@router.get("/academic/schedules/{schedule_id}/attendance")
def attendance_records(schedule_id: int, week: int = 1, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    create_attendance(schedule_id, week, db, _)
    rows = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.schedule_id == schedule_id, AttendanceRecord.week == week)
        .order_by(AttendanceRecord.student.asc(), AttendanceRecord.id.asc())
        .all()
    )
    return [attendance_to_dict(row) for row in rows]


@router.put("/academic/attendance/{attendance_id}")
def update_attendance_record(attendance_id: int, payload: AttendancePayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(AttendanceRecord, attendance_id)
    if not row:
        raise HTTPException(status_code=404, detail="考勤记录不存在")
    row.status = payload.status
    row.remark = payload.remark
    total = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == row.student_id, AttendanceRecord.course == row.course).count()
    if total:
        present = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.student_id == row.student_id,
                AttendanceRecord.course == row.course,
                AttendanceRecord.status.in_(["已到", "迟到", "请假"]),
            )
            .count()
        )
        attendance_rate = round(present / total * 100)
        grade = db.query(GradeRecord).filter(GradeRecord.student_id == row.student_id, GradeRecord.course == row.course).first()
        if grade:
            grade.attendance = attendance_rate
            grade.status = academic_status(grade.total_score, grade.attendance, grade.status)
    write_log(db, user, "更新考勤", row.student, f"{row.course}: {row.status}")
    db.commit()
    return {"success": True}


@router.get("/academic/grades")
def grade_records(
    class_name: str | None = None,
    course: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[dict]:
    query = db.query(GradeRecord)
    if class_name:
        query = query.filter(GradeRecord.class_name == class_name)
    if course:
        query = query.filter(GradeRecord.course == course)
    rows = query.order_by(GradeRecord.class_name.asc(), GradeRecord.student.asc(), GradeRecord.id.asc()).all()
    return [grade_to_dict(row) for row in rows]


@router.post("/academic/grades/sync")
def sync_grade_records(payload: GradeSyncPayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    students = (
        db.query(StudentRecord)
        .filter(StudentRecord.class_name == payload.class_name)
        .order_by(StudentRecord.name.asc(), StudentRecord.id.asc())
        .all()
    )
    created = 0
    updated = 0
    for student in students:
        row = (
            db.query(GradeRecord)
            .filter(GradeRecord.student_id == student.id, GradeRecord.course == payload.course)
            .first()
        )
        if not row:
            row = GradeRecord(
                student_id=student.id,
                exam_no=student.exam_no,
                student=student.name,
                class_name=student.class_name,
                major=student.major,
                course=payload.course,
                score=0,
                process_score=0,
                final_score=0,
                practice_score=0,
                total_score=0,
                attendance=100,
                assessment=payload.assessment,
                status="待录入",
            )
            db.add(row)
            created += 1
        else:
            row.exam_no = student.exam_no
            row.student = student.name
            row.class_name = student.class_name
            row.major = student.major
            row.assessment = payload.assessment or row.assessment
            updated += 1
    write_log(db, user, "同步班级成绩名单", payload.class_name, f"{payload.course}: 新增 {created}，更新 {updated}")
    db.commit()
    return {"success": True, "created": created, "updated": updated, "total": len(students)}


@router.put("/academic/grades/{grade_id}")
def update_grade_record(grade_id: int, payload: GradePayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(GradeRecord, grade_id)
    if not row:
        raise HTTPException(status_code=404, detail="成绩记录不存在")
    row.process_score = max(0, min(100, payload.process_score))
    row.final_score = max(0, min(100, payload.final_score))
    row.practice_score = max(0, min(100, payload.practice_score))
    row.attendance = max(0, min(100, payload.attendance))
    row.assessment = payload.assessment
    row.total_score = calculate_total_score(row.process_score, row.final_score, row.practice_score, row.assessment)
    row.score = row.total_score
    row.status = academic_status(row.total_score, row.attendance, payload.status)
    write_log(db, user, "鏇存柊鎴愮哗鑰冩牳", row.student, f"{row.course}: {row.total_score}/{row.attendance}")
    db.commit()
    return {"success": True}


@router.get("/students/{student_id}/academic")
def student_academic_detail(student_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> dict:
    student = db.get(StudentRecord, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生档案不存在")
    schedules = (
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
        "schedules": [
            {
                "id": row.id,
                "day": row.day,
                "time": row.time,
                "course": row.course,
                "teacher": row.teacher,
                "room": row.room,
                "status": row.status,
                "attendanceCreated": row.attendance_created,
            }
            for row in schedules
        ],
        "grades": [grade_to_dict(row) for row in grades],
    }


@router.get("/crawl/sources")
def crawl_sources(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(CrawlSource).order_by(CrawlSource.id.asc()).all()
    result = []
    for row in rows:
        latest = db.query(CrawlRecord).filter(CrawlRecord.source_id == row.id).order_by(CrawlRecord.created_at.desc(), CrawlRecord.id.desc()).first()
        failed = db.query(CrawlRecord).filter(CrawlRecord.source_id == row.id, CrawlRecord.status == "閲囬泦澶辫触").count()
        success = db.query(CrawlRecord).filter(CrawlRecord.source_id == row.id, CrawlRecord.status != "閲囬泦澶辫触").count()
        result.append(
            {
            "id": row.id,
            "name": row.name,
            "channel": row.channel,
            "list_url": row.list_url,
            "base_url": row.base_url,
            "enabled": row.enabled,
            "publish_status": row.publish_status,
            "last_run_at": row.last_run_at.isoformat() if row.last_run_at else "",
            "last_count": row.last_count,
            "latest_status": latest.status if latest else "未采集",
            "latest_message": latest.message if latest else "",
            "latest_title": latest.title if latest else "",
            "success_count": success,
            "failed_count": failed,
        }
        )
    return result


@router.post("/crawl/sources")
def create_crawl_source(payload: CrawlSourcePayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = CrawlSource(**payload.model_dump())
    db.add(row)
    write_log(db, user, "新增采集源", payload.name, payload.list_url)
    db.commit()
    return {"success": True, "id": row.id}


@router.put("/crawl/sources/{source_id}")
def update_crawl_source(source_id: int, payload: CrawlSourcePayload, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(CrawlSource, source_id)
    if not row:
        raise HTTPException(status_code=404, detail="閲囬泦婧愪笉瀛樺湪")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    write_log(db, user, "更新采集源", payload.name, payload.list_url)
    db.commit()
    return {"success": True}


@router.delete("/crawl/sources/{source_id}")
def delete_crawl_source(source_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    row = db.get(CrawlSource, source_id)
    if row:
        write_log(db, user, "删除采集源", row.name, row.list_url)
        db.delete(row)
        db.commit()
    return {"success": True}


@router.post("/crawl/run/{source_id}")
def run_crawl_source(source_id: int, limit: int = 8, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    source = db.get(CrawlSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="閲囬泦婧愪笉瀛樺湪")
    result = crawl_source(db, source, limit=limit)
    write_log(db, user, "杩愯瀹樼綉閲囬泦", source.name, str(result))
    db.commit()
    return result


@router.post("/crawl/run-all")
def run_all_crawlers(limit: int = 8, db: Session = Depends(get_db), user: User = Depends(get_current_admin)) -> dict:
    results = []
    for source in db.query(CrawlSource).filter(CrawlSource.enabled == True).all():
        try:
            results.append(crawl_source(db, source, limit=limit))
        except Exception as exc:
            results.append({"source": source.name, "created": 0, "skipped": 0, "errors": [str(exc)]})
    write_log(db, user, "杩愯鍏ㄩ儴瀹樼綉閲囬泦", "crawl", f"{len(results)} 涓噰闆嗘簮")
    db.commit()
    return {"success": True, "results": results}


@router.get("/crawl/records")
def crawl_records(db: Session = Depends(get_db), _: User = Depends(get_current_admin)) -> list[dict]:
    rows = db.query(CrawlRecord).order_by(CrawlRecord.created_at.desc(), CrawlRecord.id.desc()).limit(100).all()
    return [
        {
            "id": row.id,
            "source_name": row.source_name,
            "article_url": row.article_url,
            "article_id": row.article_id,
            "title": row.title,
            "status": row.status,
            "message": row.message,
            "created_at": row.created_at.isoformat() if row.created_at else "",
        }
        for row in rows
    ]


