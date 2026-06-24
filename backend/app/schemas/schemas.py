from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    permissions: list[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    username: str
    password: str


class StudentLoginRequest(BaseModel):
    student_no: str | None = ""
    exam_no: str | None = ""
    password: str


class MajorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    college: str | None = None
    duration: str | None = None
    tuition: float | None = None
    description: str | None = None
    courses: str | None = None
    jobs: str | None = None


class ScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    major: str
    min_score: float | None = None
    max_score: float | None = None
    avg_score: float | None = None
    province: str | None = None
    subject: str | None = None
    enrollment: int | None = None


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    channel: str | None = None
    summary: str | None = None
    content: str | None = None
    source: str | None = None
    author: str | None = None
    cover_url: str | None = None
    publish_status: str
    review_status: str
    view_count: int
    publish_date: date | None = None


class ArticlePayload(BaseModel):
    title: str
    channel: str = "学校新闻"
    summary: str | None = None
    content: str | None = None
    source: str | None = "学校官网"
    author: str | None = "管理员"
    cover_url: str | None = None
    publish_status: str = "已发布"
    review_status: str = "已发布"
    is_top: bool = False
    publish_date: date | None = None
    version_note: str | None = None


class BannerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    subtitle: str | None = None
    image_url: str | None = None
    link_url: str | None = None


class BannerPayload(BaseModel):
    title: str
    subtitle: str | None = None
    image_url: str | None = None
    link_url: str | None = None
    sort_order: int = 0
    is_active: bool = True


class ChannelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent: str | None = None
    slug: str | None = None
    channel_type: str = "list"
    sort_order: int = 0
    is_nav: bool = True
    is_active: bool = True


class ChannelPayload(BaseModel):
    name: str
    parent: str | None = None
    slug: str | None = None
    channel_type: str = "list"
    sort_order: int = 0
    is_nav: bool = True
    is_active: bool = True


class TicketCreate(BaseModel):
    title: str
    category: str = "招生咨询"
    question: str
    contact: str | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str | None = None
    question: str
    contact: str | None = None
    priority: str
    status: str
    answer: str | None = None
    created_at: datetime


class TicketReplyPayload(BaseModel):
    answer: str
    feed_knowledge: bool = True


class ChatRequest(BaseModel):
    question: str
    assistant_mode: str = "admissions"
    provider: str = "spark"
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    thinking: str = "auto"
    web_search: bool = False
    search_mode: str = "normal"
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    conversation_id: int | None = None
    intent: str
    answer: str
    confidence: float = 0.75
    sources: list[dict] = Field(default_factory=list)


class FeedbackPayload(BaseModel):
    conversation_id: int | None = None
    question: str | None = None
    answer: str | None = None
    sentiment: str
    suggestion: str | None = None


class MatchPayload(BaseModel):
    field: str
    career: str
    math: str
    code: str
    postgrad: str
    score: float | None = None
    province: str = "安徽"
    subject: str = "物理"


class ReportPayload(BaseModel):
    question: str
    answer: str
    student_name: str | None = None


class KnowledgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    category: str | None = None
    chunk_count: int
    created_at: datetime


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    file_url: str
    file_type: str | None = None
    file_size: int
    usage_type: str
    owner_type: str | None = None
    owner_id: int | None = None
    created_at: datetime


class ArticleVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    title: str
    summary: str | None = None
    content: str | None = None
    editor: str | None = None
    version_note: str | None = None
    created_at: datetime
