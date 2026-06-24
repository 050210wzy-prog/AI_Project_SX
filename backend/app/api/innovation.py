from collections import Counter, defaultdict
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AiConversation, Major, Score, SiteArticle, Ticket

router = APIRouter(prefix="/innovation", tags=["智慧官网创新"])


class SmartRecommendPayload(BaseModel):
    province: str = "安徽"
    subject: str = "物理"
    score: float
    rank: int | None = None
    interest: str = ""


def _level(gap: float) -> str:
    if gap >= 25:
        return "保"
    if gap >= 8:
        return "稳"
    if gap >= -12:
        return "冲"
    return "慎报"


def _level_reason(level: str, gap: float) -> str:
    if level == "保":
        return f"高出近年最低分 {gap:.0f} 分，录取把握较高，可作为保底选择。"
    if level == "稳":
        return f"高出近年最低分 {gap:.0f} 分，匹配度较好，适合重点考虑。"
    if level == "冲":
        return f"与近年最低分相差 {gap:.0f} 分，存在机会，但建议搭配稳妥专业。"
    return f"低于近年最低分 {abs(gap):.0f} 分，建议谨慎填报。"


@router.post("/recommend")
def smart_recommend(payload: SmartRecommendPayload, db: Session = Depends(get_db)) -> dict:
    majors = db.query(Major).all()
    scores = db.query(Score).filter(Score.province.like(f"%{payload.province}%")).all()
    score_map: dict[str, list[Score]] = defaultdict(list)
    for row in scores:
        if not payload.subject or not row.subject or payload.subject in row.subject:
            score_map[row.major].append(row)

    interest = payload.interest.strip()
    results = []
    for major in majors:
        rows = sorted(score_map.get(major.name, []), key=lambda item: item.year, reverse=True)[:3]
        if rows:
            avg_min = sum(float(row.min_score or 0) for row in rows) / len(rows)
            gap = payload.score - avg_min
        else:
            avg_min = None
            gap = 0
        text = f"{major.name}{major.college or ''}{major.description or ''}{major.courses or ''}{major.jobs or ''}"
        interest_hit = bool(interest and interest in text)
        level = _level(gap)
        match_score = gap + (18 if interest_hit else 0)
        results.append(
            {
                "major": major.name,
                "college": major.college,
                "level": level,
                "score_gap": round(gap, 1),
                "avg_min_score": round(avg_min, 1) if avg_min is not None else None,
                "reason": _level_reason(level, gap) + (" 兴趣关键词与专业培养方向匹配。" if interest_hit else ""),
                "jobs": major.jobs,
                "match_score": round(match_score, 1),
            }
        )

    ordered = sorted(results, key=lambda item: ({"保": 3, "稳": 4, "冲": 2, "慎报": 1}[item["level"]], item["match_score"]), reverse=True)
    return {
        "profile": payload.model_dump(),
        "summary": "系统已结合分数、近年最低分和兴趣关键词生成冲稳保建议。",
        "items": ordered[:12],
    }


@router.get("/major-profile/{major_name}")
def major_profile(major_name: str, db: Session = Depends(get_db)) -> dict:
    major = db.query(Major).filter(Major.name == major_name).first()
    scores = db.query(Score).filter(Score.major == major_name).order_by(Score.year.asc()).all()
    if not major:
        major = db.query(Major).first()
    trend = [
        {"year": row.year, "min_score": row.min_score, "max_score": row.max_score, "avg_score": row.avg_score, "rank_min": row.rank_min}
        for row in scores
    ]
    return {
        "name": major.name if major else major_name,
        "college": major.college if major else "",
        "duration": major.duration if major else "",
        "tuition": major.tuition if major else None,
        "description": major.description if major else "",
        "courses": [item.strip() for item in (major.courses or "").replace("、", "，").split("，") if item.strip()] if major else [],
        "jobs": [item.strip() for item in (major.jobs or "").replace("、", "，").split("，") if item.strip()] if major else [],
        "certificates": ["职业技能等级证书", "行业岗位能力证书", "普通话/英语/计算机应用能力证书"],
        "training": ["校内综合实训中心", "校企合作实训基地", "岗位项目化实训课程"],
        "partners": ["中铁大桥局", "合肥轨道交通集团", "通用汽车", "安徽民航机场集团"],
        "trend": trend,
    }


@router.get("/sync-center")
def sync_center(db: Session = Depends(get_db)) -> dict:
    articles = db.query(SiteArticle).order_by(SiteArticle.publish_date.desc(), SiteArticle.id.desc()).limit(10).all()
    channels = Counter(item.channel or "未分类" for item in db.query(SiteArticle.channel).all())
    return {
        "source": "本项目官网后台内容库",
        "today": date.today().isoformat(),
        "status": [
            {"name": "新闻同步", "state": "正常", "count": db.query(SiteArticle).count()},
            {"name": "通知同步", "state": "正常", "count": db.query(SiteArticle).filter(SiteArticle.channel.like("%通知%")).count()},
            {"name": "图片资源", "state": "待完善", "count": db.query(SiteArticle).filter(SiteArticle.cover_url.isnot(None)).count()},
        ],
        "channels": [{"name": name, "count": count} for name, count in channels.most_common(8)],
        "latest": [
            {
                "id": item.id,
                "title": item.title,
                "channel": item.channel,
                "date": item.publish_date.isoformat() if item.publish_date else "",
                "summary": item.summary,
            }
            for item in articles
        ],
    }


@router.get("/service-desk")
def service_desk(role: str = "学生") -> dict:
    base = [
        {"title": "信息门户", "desc": "统一身份认证、个人信息、待办事项", "url": "/service/信息门户"},
        {"title": "电子邮箱", "desc": "站内邮件收发与通知", "url": "/service/电子邮箱"},
        {"title": "WebVPN", "desc": "校外访问校内资源入口", "url": "/service/WebVPN"},
        {"title": "网上办事大厅", "desc": "一站式线上办事服务", "url": "https://ehall.acvtc.edu.cn/"},
    ]
    by_role = {
        "学生": ["课表查询", "成绩查询", "图书馆资源", "宿舍报修"],
        "教师": ["协同办公", "科研申报", "教学管理", "工资查询"],
        "考生": ["招生信息", "历年分数", "专业画像", "报考指南"],
        "校友": ["校友活动", "返校预约", "校友捐赠", "校友招聘"],
        "访客": ["校园地图", "联系方式", "办事指南", "信息公开"],
    }
    return {
        "role": role,
        "apps": base + [{"title": item, "desc": f"{role}常用服务", "url": f"/service/{item}"} for item in by_role.get(role, by_role["学生"])],
    }


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)) -> dict:
    hot_articles = db.query(SiteArticle).order_by(SiteArticle.view_count.desc()).limit(8).all()
    hot_majors = (
        db.query(Score.major, func.count(Score.id).label("count"), func.avg(Score.min_score).label("avg_score"))
        .group_by(Score.major)
        .order_by(func.count(Score.id).desc())
        .limit(8)
        .all()
    )
    ticket_status = db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    intents = db.query(AiConversation.intent, func.count(AiConversation.id)).group_by(AiConversation.intent).all()
    return {
        "cards": [
            {"label": "官网文章", "value": db.query(SiteArticle).count()},
            {"label": "专业数据", "value": db.query(Major).count()},
            {"label": "咨询记录", "value": db.query(AiConversation).count()},
            {"label": "服务工单", "value": db.query(Ticket).count()},
        ],
        "hot_articles": [{"title": item.title, "views": item.view_count} for item in hot_articles],
        "hot_majors": [{"major": major, "count": count, "avg_score": round(float(avg or 0), 1)} for major, count, avg in hot_majors],
        "ticket_status": [{"name": name, "count": count} for name, count in ticket_status],
        "intents": [{"name": name or "未识别", "count": count} for name, count in intents],
    }


@router.get("/ai-sources")
def ai_sources(db: Session = Depends(get_db)) -> dict:
    articles = db.query(SiteArticle).order_by(SiteArticle.publish_date.desc(), SiteArticle.id.desc()).limit(6).all()
    return {
        "answer": "已启用带来源引用的招生问答展示。回答招生政策、专业、分数线问题时，可引用官网文章、专业库和历年分数数据。",
        "sources": [
            {"title": item.title, "channel": item.channel, "date": item.publish_date.isoformat() if item.publish_date else "", "id": item.id}
            for item in articles
        ],
    }


@router.get("/campus-guide")
def campus_guide() -> dict:
    return {
        "campuses": [
            {
                "name": "新桥校区",
                "address": "安徽新桥国际产业园寿州大道16号",
                "spots": ["图书馆", "综合实训中心", "学生公寓", "运动场", "轨道交通实训基地"],
            },
            {
                "name": "包河校区",
                "address": "合肥市包河区合巢路114号",
                "spots": ["继续教育中心", "培训基地", "行政服务点", "校园生活区"],
            },
        ],
        "routes": ["合肥方向可经新桥国际产业园抵达新桥校区", "包河校区可按合巢路导航前往"],
    }


@router.get("/english-mapping")
def english_mapping(db: Session = Depends(get_db)) -> dict:
    articles = db.query(SiteArticle).order_by(SiteArticle.publish_date.desc(), SiteArticle.id.desc()).limit(6).all()
    return {
        "mode": "中文内容映射英文官网草稿",
        "items": [
            {
                "zh_title": item.title,
                "en_title": f"Draft: {item.title}",
                "status": "待审核",
                "channel": item.channel,
                "date": item.publish_date.isoformat() if item.publish_date else "",
            }
            for item in articles
        ],
    }
