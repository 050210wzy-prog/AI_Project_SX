from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Major, RankSegment, Score
from app.schemas.schemas import MajorOut, MatchPayload, ReportPayload, ScoreOut

router = APIRouter(prefix="/admissions", tags=["招生"])


@router.get("/majors", response_model=list[MajorOut])
def list_majors(keyword: str = "", db: Session = Depends(get_db)) -> list[Major]:
    query = db.query(Major)
    if keyword:
        query = query.filter(Major.name.like(f"%{keyword}%"))
    return query.order_by(Major.id.desc()).all()


@router.get("/scores", response_model=list[ScoreOut])
def list_scores(
    major: str = "",
    province: str = Query(default="安徽"),
    subject: str = "",
    db: Session = Depends(get_db),
) -> list[Score]:
    query = db.query(Score)
    if major:
        query = query.filter(Score.major.like(f"%{major}%"))
    if province:
        query = query.filter(Score.province == province)
    if subject:
        query = query.filter(Score.subject.like(f"%{subject}%"))
    return query.order_by(Score.year.desc(), Score.min_score.desc()).limit(200).all()


@router.get("/recommend")
def recommend(score: float, province: str = "安徽", subject: str = "", db: Session = Depends(get_db)) -> dict:
    rows = list_scores("", province, subject, db)
    items = []
    rank_row = (
        db.query(RankSegment)
        .filter(RankSegment.province == province, RankSegment.subject.like(f"%{subject}%"), RankSegment.score <= score)
        .order_by(RankSegment.score.desc())
        .first()
    )
    user_rank = rank_row.cumulative_rank if rank_row else None
    for row in rows:
        gap = score - float(row.min_score or 0)
        level = "稳妥" if gap >= 20 else ("冲刺" if gap >= 0 else "希望较小")
        rank_gap = (user_rank - row.rank_min) if user_rank and row.rank_min else None
        items.append({"major": row.major, "min_score": row.min_score, "gap": gap, "level": level, "rank_min": row.rank_min, "rank_gap": rank_gap})
    return {"score": score, "rank": user_rank, "province": province, "subject": subject, "items": items[:8]}


@router.get("/scores/trend")
def score_trend(major: str, province: str = "安徽", subject: str = "", db: Session = Depends(get_db)) -> dict:
    query = db.query(Score).filter(Score.major == major, Score.province == province)
    if subject:
        query = query.filter(Score.subject.like(f"%{subject}%"))
    rows = query.order_by(Score.year.asc()).all()
    return {
        "major": major,
        "items": [
            {"year": row.year, "min_score": row.min_score, "max_score": row.max_score, "avg_score": row.avg_score, "rank_min": row.rank_min}
            for row in rows
        ],
    }


@router.get("/rank")
def rank_by_score(score: float, province: str = "安徽", subject: str = "物理", db: Session = Depends(get_db)) -> dict:
    row = (
        db.query(RankSegment)
        .filter(RankSegment.province == province, RankSegment.subject.like(f"%{subject}%"), RankSegment.score <= score)
        .order_by(RankSegment.score.desc())
        .first()
    )
    return {"score": score, "province": province, "subject": subject, "rank": row.cumulative_rank if row else None}


@router.post("/import/{kind}")
async def import_excel(kind: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    raw = await file.read()
    df = pd.read_excel(BytesIO(raw)) if file.filename and file.filename.endswith(".xlsx") else pd.read_csv(BytesIO(raw))
    count = 0
    if kind == "majors":
        for _, row in df.iterrows():
            name = str(row.get("专业名称") or row.get("name") or "").strip()
            if not name:
                continue
            item = db.query(Major).filter(Major.name == name).first() or Major(name=name)
            item.college = row.get("所属学院") or row.get("college") or item.college
            item.duration = row.get("学制") or row.get("duration") or item.duration
            item.description = row.get("简介") or row.get("description") or item.description
            item.courses = row.get("核心课程") or row.get("courses") or item.courses
            item.jobs = row.get("就业方向") or row.get("jobs") or item.jobs
            db.add(item)
            count += 1
    elif kind == "scores":
        for _, row in df.iterrows():
            major = str(row.get("专业名称") or row.get("major") or "").strip()
            year = int(row.get("年度") or row.get("year") or 2025)
            if not major:
                continue
            db.add(
                Score(
                    year=year,
                    major=major,
                    max_score=row.get("最高分") or row.get("max_score"),
                    min_score=row.get("最低分") or row.get("min_score"),
                    avg_score=row.get("平均分") or row.get("avg_score"),
                    rank_min=row.get("最低位次") or row.get("rank_min"),
                    enrollment=row.get("招生人数") or row.get("enrollment"),
                    province=row.get("省份") or row.get("province") or "安徽",
                    subject=row.get("科类") or row.get("subject") or "物理",
                    source=file.filename,
                )
            )
            count += 1
    elif kind == "rank":
        for _, row in df.iterrows():
            db.add(
                RankSegment(
                    year=int(row.get("年度") or row.get("year") or 2025),
                    province=row.get("省份") or row.get("province") or "安徽",
                    subject=row.get("科类") or row.get("subject") or "物理",
                    score=float(row.get("分数") or row.get("score")),
                    rank_count=int(row.get("本段人数") or row.get("rank_count") or 0),
                    cumulative_rank=int(row.get("累计位次") or row.get("cumulative_rank") or 0),
                )
            )
            count += 1
    db.commit()
    return {"success": True, "kind": kind, "count": count}


@router.get("/export/{kind}")
def export_excel(kind: str, db: Session = Depends(get_db)) -> StreamingResponse:
    if kind == "majors":
        rows = db.query(Major).all()
        df = pd.DataFrame([{"专业名称": r.name, "所属学院": r.college, "学制": r.duration, "简介": r.description, "核心课程": r.courses, "就业方向": r.jobs} for r in rows])
    elif kind == "scores":
        rows = db.query(Score).all()
        df = pd.DataFrame([{"年度": r.year, "专业名称": r.major, "省份": r.province, "科类": r.subject, "最低分": r.min_score, "最高分": r.max_score, "平均分": r.avg_score, "最低位次": r.rank_min, "招生人数": r.enrollment} for r in rows])
    else:
        rows = db.query(RankSegment).all()
        df = pd.DataFrame([{"年度": r.year, "省份": r.province, "科类": r.subject, "分数": r.score, "本段人数": r.rank_count, "累计位次": r.cumulative_rank} for r in rows])
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={kind}.xlsx"})


@router.post("/match")
def match_major(payload: MatchPayload, db: Session = Depends(get_db)) -> dict:
    rules = {
        "算法": ["人工智能技术应用", "大数据技术"],
        "数据": ["大数据技术", "计算机应用技术"],
        "硬件": ["智能网联汽车技术", "无人机应用技术"],
        "应用开发": ["计算机应用技术", "人工智能技术应用"],
        "交通工程": ["道路与桥梁工程技术", "城市轨道交通运营管理"],
    }
    names = rules.get(payload.field, ["人工智能技术应用", "大数据技术"])
    if payload.code == "不想写代码":
        names = ["现代物流管理", "电子商务", "城市轨道交通运营管理"]
    majors = db.query(Major).filter(Major.name.in_(names)).all()
    return {"answers": payload.model_dump(), "majors": [MajorOut.model_validate(item) for item in majors]}


@router.get("/compare")
def compare_majors(a: str, b: str, db: Session = Depends(get_db)) -> dict:
    result = []
    for name in [a, b]:
        major = db.query(Major).filter(Major.name == name).first()
        scores = db.query(Score).filter(Score.major == name).order_by(Score.year.desc()).limit(3).all()
        avg = sum(float(s.min_score or 0) for s in scores) / len(scores) if scores else None
        result.append({"name": name, "description": major.description if major else "", "courses": major.courses if major else "", "jobs": major.jobs if major else "", "avg_min_score": avg})
    return {"items": result}


@router.post("/report")
def report_pdf(payload: ReportPayload) -> StreamingResponse:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = BytesIO()
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "STSong-Light"
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="报考建议书")
    story = [Paragraph("安徽交通职业技术学院报考建议书", styles["Title"]), Spacer(1, 14)]
    if payload.student_name:
        story.append(Paragraph(f"考生：{payload.student_name}", styles["BodyText"]))
    story.append(Paragraph(f"<b>咨询问题：</b>{payload.question}", styles["BodyText"]))
    story.append(Spacer(1, 10))
    safe = payload.answer.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    story.append(Paragraph(f"<b>系统建议：</b><br/>{safe}", styles["BodyText"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("说明：本报告仅供志愿填报参考，最终以学校官方招生政策和录取结果为准。", styles["BodyText"]))
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=admission-report.pdf"})
