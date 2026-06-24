from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.database import Base
from app.core.security import hash_password


DEFAULT_MAJORS = [
    ("安全技术与管理", "土木建筑学院", "三年", "安全管理、应急管理、工程安全评价", "安全生产管理、安全评价、工程安全技术服务"),
    ("道路与桥梁工程技术", "土木建筑学院", "三年", "道路工程、桥梁工程、工程测量、施工组织", "道路桥梁施工、试验检测、工程管理"),
    ("道路工程检测技术", "土木建筑学院", "三年", "工程材料检测、道路检测、桥梁检测", "公路水运检测、工程质量检测"),
    ("土木工程检测技术", "土木建筑学院", "三年", "工程材料、结构检测、无损检测", "土建检测、质量监督、工程咨询"),
    ("装配式建筑工程技术", "土木建筑学院", "三年", "装配式施工、BIM技术、建筑构造", "装配式建筑施工、BIM建模、项目管理"),
    ("建筑消防技术", "土木建筑学院", "三年", "消防工程、建筑设备、消防检测", "消防施工、消防维保、安全评价"),
    ("工程造价", "土木建筑学院", "三年", "工程计量、造价软件、招投标", "造价咨询、招投标、工程审计"),
    ("建设工程监理", "土木建筑学院", "三年", "工程监理、合同管理、质量控制", "工程监理、项目管理"),
    ("市政工程技术", "土木建筑学院", "三年", "城市道路、管网工程、施工技术", "市政施工、工程管理"),
    ("机电一体化技术", "汽车工程学院", "三年", "机械基础、电气控制、PLC技术", "机电设备安装、维护、自动化运行"),
    ("工业机器人技术", "汽车工程学院", "三年", "机器人编程、自动化产线、传感器", "工业机器人运维、自动化集成"),
    ("电气自动化技术", "汽车工程学院", "三年", "电气控制、PLC、工业网络", "电气设备维护、自动化工程"),
    ("汽车制造与试验技术", "汽车工程学院", "三年", "汽车构造、制造工艺、性能检测", "汽车制造、质量检测、试验验证"),
    ("新能源汽车技术", "汽车工程学院", "三年", "动力电池、电机电控、整车维护", "新能源汽车检测、维修、售后服务"),
    ("智能网联汽车技术", "汽车工程学院", "三年", "智能传感、车联网、自动驾驶基础", "智能网联测试、车联网运维"),
    ("汽车检测与维修技术", "汽车工程学院", "三年", "汽车检测、故障诊断、维修工艺", "汽车维修、检测诊断、服务顾问"),
    ("汽车技术服务与营销", "汽车工程学院", "三年", "汽车营销、售后服务、客户管理", "汽车销售、服务顾问、配件管理"),
    ("城市轨道交通工程技术", "轨道交通学院", "三年", "轨道线路、施工测量、工程维护", "轨道工程施工、线路维护"),
    ("城市轨道车辆应用技术", "轨道交通学院", "三年", "车辆构造、检修技术、车辆电气", "轨道车辆检修、车辆运用"),
    ("城市轨道交通机电技术", "轨道交通学院", "三年", "机电设备、自动售检票、屏蔽门", "轨道机电设备维护"),
    ("城市轨道交通通信信号技术", "轨道交通学院", "三年", "通信系统、信号控制、联锁设备", "通信信号维护、系统调试"),
    ("城市轨道交通运营管理", "轨道交通学院", "三年", "客运组织、行车组织、票务管理", "站务员、行车值班、运营调度"),
    ("航海技术", "航运工程学院", "三年", "船舶驾驶、航海气象、海上安全", "船舶驾驶、航运管理"),
    ("轮机工程技术", "航运工程学院", "三年", "船舶动力、轮机维护、机舱管理", "轮机管理、船舶设备维护"),
    ("港口与航运管理", "航运工程学院", "三年", "港口业务、航运组织、物流管理", "港口调度、航运业务、物流运营"),
    ("水路运输安全管理", "航运工程学院", "三年", "水运法规、安全管理、应急处置", "水运安全管理、港航监管服务"),
    ("无人机应用技术", "航空与低空经济学院", "三年", "无人机操控、航测、维护", "无人机飞手、航测数据处理、低空应用服务"),
    ("空中乘务", "航空与低空经济学院", "三年", "民航服务、客舱安全、服务礼仪", "民航乘务、机场服务"),
    ("民航运输服务", "航空与低空经济学院", "三年", "民航客货运、机场运行、票务服务", "机场地勤、票务、民航服务"),
    ("飞机机电设备维修", "航空与低空经济学院", "三年", "飞机结构、机电设备、维修规范", "飞机维修、航材管理"),
    ("通用航空器维修", "航空与低空经济学院", "三年", "通航器结构、发动机、维修工艺", "通航维修、航空器维护"),
    ("计算机应用技术", "人工智能学院", "三年", "程序设计、数据库、Web开发", "软件开发、系统运维、信息化服务"),
    ("计算机网络技术", "人工智能学院", "三年", "网络组建、网络安全、服务器管理", "网络运维、网络安全、系统集成"),
    ("数字媒体技术", "人工智能学院", "三年", "图形图像、交互设计、短视频制作", "数字内容制作、新媒体运营"),
    ("大数据技术", "人工智能学院", "三年", "数据采集、数据分析、可视化", "数据分析、BI开发、数据处理"),
    ("人工智能技术应用", "人工智能学院", "三年", "Python、机器学习、数据库、智能交通应用", "AI应用开发、数据标注与分析、智能系统运维"),
    ("智能交通技术", "人工智能学院", "三年", "交通信息采集、智能控制、交通大数据", "智慧交通运维、交通信息化"),
    ("现代物流管理", "经济管理学院", "三年", "仓储配送、供应链管理、物流信息", "物流运营、仓储管理、供应链专员"),
    ("电子商务", "经济管理学院", "三年", "网店运营、网络营销、直播电商", "电商运营、网络营销、客户服务"),
    ("大数据与会计", "经济管理学院", "三年", "财务会计、税务、财务软件", "会计核算、税务助理、财务管理"),
    ("商务英语", "经济管理学院", "三年", "商务沟通、跨境电商、外贸实务", "外贸业务、跨境电商运营"),
    ("旅游管理", "经济管理学院", "三年", "旅游服务、景区运营、酒店管理", "旅游顾问、景区运营、酒店服务"),
    ("酒店管理与数字化运营", "经济管理学院", "三年", "酒店运营、数字化管理、服务礼仪", "酒店运营、前厅管理、客户服务"),
    ("交通运营管理", "经济管理学院", "三年", "运输组织、客货运管理、交通服务", "运输调度、运营管理"),
]

DEFAULT_SITE_ARTICLES = [
    ("招生信息网", "招生就业", "招生章程、招生计划、历年分数和录取查询入口。", "面向考生提供专业介绍、招生政策、历年录取数据和录取查询服务。"),
    ("2026年分类考试招生章程发布", "招生就业", "学校发布分类考试招生章程和报考提示。", "章程涵盖招生对象、招生专业、录取规则、联系方式和重要时间安排。"),
    ("安徽交通职业技术学院2026年招生计划", "招生就业", "各省份、各科类招生计划汇总。", "招生计划按省份、专业、科类和批次展示，考生可结合历年分数进行参考。"),
    ("匠心铸鼎 数字传魂 安徽交院学子斩获省级赛事荣誉", "学校新闻", "学生在数字文创赛道取得佳绩。", "学校持续推进以赛促学、以赛促教，鼓励学生在数字创意、智能应用和文化传播中提升综合素养。"),
    ("学校召开高质量发展专题调研座谈会", "学校新闻", "围绕交通职教高质量发展开展交流。", "会议聚焦专业建设、产教融合、人才培养和社会服务，推动重点任务落地。"),
    ("校党委理论学习中心组开展专题学习", "学校新闻", "深入学习职业教育改革与交通强国建设相关内容。", "学校结合办学实际推进党建与事业发展深度融合。"),
    ("关于2026年劳动节放假安排的通知", "通知公告", "发布节假日调休和安全提示。", "各部门、各学院需做好假期值班、安全教育和校园服务保障。"),
    ("校园文化建设项目方案征集公告", "通知公告", "面向校园文化建设项目开展方案征集。", "请相关单位按要求提交方案材料，学校将组织评审和后续实施。"),
    ("人工智能学院智慧交通与安全实训室建设项目公告", "招标采购", "服务智慧交通与安全实训条件建设。", "采购项目用于完善人工智能、智慧交通和安全实训教学环境。"),
    ("内控制度建设服务项目询价采购公告", "招标采购", "学校内控制度建设服务项目开展询价采购。", "公告用于规范采购流程，提高内部治理和风险防控能力。"),
    ("土木建筑学院开展无烟宿舍倡议活动", "部门动态", "弘扬青春榜样，强化学生宿舍安全与健康管理。", "学院通过主题班会、宿舍走访等方式营造健康文明的校园环境。"),
    ("人工智能学院新年晚会圆满落幕", "部门动态", "展示青年学子青春风采和学院育人成果。", "晚会融合专业特色、文艺展示和学生社团活动，丰富校园文化生活。"),
]


def uuid_str() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Major(Base):
    __tablename__ = "majors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    code: Mapped[str | None] = mapped_column(String(50))
    college: Mapped[str | None] = mapped_column(String(100))
    duration: Mapped[str | None] = mapped_column(String(20))
    tuition: Mapped[float | None] = mapped_column(Float)
    degree: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    courses: Mapped[str | None] = mapped_column(Text)
    jobs: Mapped[str | None] = mapped_column(Text)
    features: Mapped[str | None] = mapped_column(Text)


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    major: Mapped[str] = mapped_column(String(100), index=True)
    max_score: Mapped[float | None] = mapped_column(Float)
    min_score: Mapped[float | None] = mapped_column(Float)
    avg_score: Mapped[float | None] = mapped_column(Float)
    rank_min: Mapped[int | None] = mapped_column(Integer)
    enrollment: Mapped[int | None] = mapped_column(Integer)
    province: Mapped[str | None] = mapped_column(String(50), index=True)
    subject: Mapped[str | None] = mapped_column(String(50), index=True)
    source: Mapped[str | None] = mapped_column(String(255))


class RankSegment(Base):
    __tablename__ = "rank_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    province: Mapped[str] = mapped_column(String(50), index=True)
    subject: Mapped[str] = mapped_column(String(50), index=True)
    score: Mapped[float] = mapped_column(Float, index=True)
    rank_count: Mapped[int] = mapped_column(Integer, default=0)
    cumulative_rank: Mapped[int] = mapped_column(Integer, default=0)


class AdmissionPlan(Base):
    __tablename__ = "admission_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    province: Mapped[str | None] = mapped_column(String(50))
    subject: Mapped[str | None] = mapped_column(String(50))
    major: Mapped[str] = mapped_column(String(100), index=True)
    plan_count: Mapped[int] = mapped_column(Integer, default=0)
    batch_name: Mapped[str | None] = mapped_column(String(100))
    remark: Mapped[str | None] = mapped_column(Text)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(80))
    question: Mapped[str] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(String(120))
    priority: Mapped[str] = mapped_column(String(50), default="普通")
    status: Mapped[str] = mapped_column(String(50), default="待处理")
    assignee: Mapped[str | None] = mapped_column(String(80))
    answer: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ResourceFile(Base):
    __tablename__ = "resource_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    file_url: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str | None] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    usage_type: Mapped[str] = mapped_column(String(50), default="资源库")
    owner_type: Mapped[str | None] = mapped_column(String(50))
    owner_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SiteChannel(Base):
    __tablename__ = "site_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    parent: Mapped[str | None] = mapped_column(String(100))
    slug: Mapped[str | None] = mapped_column(String(100), unique=True)
    channel_type: Mapped[str] = mapped_column(String(50), default="list")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_nav: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SiteArticle(Base):
    __tablename__ = "site_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    channel: Mapped[str | None] = mapped_column(String(100), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(100))
    author: Mapped[str | None] = mapped_column(String(100))
    cover_url: Mapped[str | None] = mapped_column(String(500))
    publish_status: Mapped[str] = mapped_column(String(50), default="已发布")
    review_status: Mapped[str] = mapped_column(String(50), default="已发布")
    review_comment: Mapped[str | None] = mapped_column(Text)
    is_top: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    publish_date: Mapped[date | None] = mapped_column(Date)
    attachments: Mapped[list["SiteAttachment"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class SiteArticleVersion(Base):
    __tablename__ = "site_article_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    editor: Mapped[str | None] = mapped_column(String(100))
    version_note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SiteAttachment(Base):
    __tablename__ = "site_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("site_articles.id"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_type: Mapped[str | None] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    article: Mapped[SiteArticle] = relationship(back_populates="attachments")


class SiteBanner(Base):
    __tablename__ = "site_banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    link_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SiteLink(Base):
    __tablename__ = "site_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    url: Mapped[str | None] = mapped_column(String(500))
    link_type: Mapped[str] = mapped_column(String(50), default="快捷入口")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(80))
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.id"))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(80), index=True)
    source: Mapped[str | None] = mapped_column(String(255))
    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")


class AiConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(80))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    sources: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AiFeedback(Base):
    __tablename__ = "ai_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer)
    question: Mapped[str | None] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    sentiment: Mapped[str] = mapped_column(String(20))
    suggestion: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MailMessage(Base):
    __tablename__ = "mail_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[str] = mapped_column(String(36), index=True)
    sender_name: Mapped[str] = mapped_column(String(50))
    recipient: Mapped[str] = mapped_column(String(120), index=True)
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str | None] = mapped_column(Text)
    group_name: Mapped[str] = mapped_column(String(50), default="通用")
    description: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(String(50), index=True)
    action: Mapped[str] = mapped_column(String(100))
    target: Mapped[str | None] = mapped_column(String(120))
    detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class InnovationConfig(Base):
    __tablename__ = "innovation_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    config_json: Mapped[str | None] = mapped_column(Text)


class StudentRecord(Base):
    __tablename__ = "student_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    major: Mapped[str | None] = mapped_column(String(120))
    class_name: Mapped[str | None] = mapped_column(String(80))
    phone: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="待确认")
    counselor: Mapped[str | None] = mapped_column(String(80), default="待分配")
    student_no: Mapped[str | None] = mapped_column(String(50))
    province: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(80))
    department: Mapped[str | None] = mapped_column(String(120))
    remark: Mapped[str | None] = mapped_column(Text)
    id_card: Mapped[str | None] = mapped_column(String(50))
    birthday: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[str | None] = mapped_column(String(20))
    admission_type: Mapped[str | None] = mapped_column(String(120))
    admission_batch: Mapped[str | None] = mapped_column(String(120))
    subject: Mapped[str | None] = mapped_column(String(80))
    major_code: Mapped[str | None] = mapped_column(String(50))
    political_status: Mapped[str | None] = mapped_column(String(80))
    ethnicity: Mapped[str | None] = mapped_column(String(80))
    candidate_type: Mapped[str | None] = mapped_column(String(120))
    graduate_type: Mapped[str | None] = mapped_column(String(120))
    middle_school: Mapped[str | None] = mapped_column(String(180))
    foreign_language: Mapped[str | None] = mapped_column(String(80))
    area_code: Mapped[str | None] = mapped_column(String(50))
    area_name: Mapped[str | None] = mapped_column(String(120))
    address: Mapped[str | None] = mapped_column(Text)
    postal_code: Mapped[str | None] = mapped_column(String(30))
    receiver: Mapped[str | None] = mapped_column(String(80))
    score: Mapped[float | None] = mapped_column(Float)
    application_choice: Mapped[str | None] = mapped_column(String(80))
    first_major: Mapped[str | None] = mapped_column(String(120))
    second_major: Mapped[str | None] = mapped_column(String(120))
    third_major: Mapped[str | None] = mapped_column(String(120))
    fourth_major: Mapped[str | None] = mapped_column(String(120))
    fifth_major: Mapped[str | None] = mapped_column(String(120))
    sixth_major: Mapped[str | None] = mapped_column(String(120))
    adjustment: Mapped[str | None] = mapped_column(String(50))
    chinese_score: Mapped[float | None] = mapped_column(Float)
    math_score: Mapped[float | None] = mapped_column(Float)
    foreign_score: Mapped[float | None] = mapped_column(Float)
    comprehensive_score: Mapped[float | None] = mapped_column(Float)
    subject_name: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TeachingSchedule(Base):
    __tablename__ = "teaching_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[str] = mapped_column(String(30))
    time: Mapped[str] = mapped_column(String(50))
    course: Mapped[str] = mapped_column(String(120))
    teacher: Mapped[str | None] = mapped_column(String(80))
    room: Mapped[str | None] = mapped_column(String(80))
    class_name: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(50), default="草稿")
    attendance_created: Mapped[bool] = mapped_column(Boolean, default=False)


class GradeRecord(Base):
    __tablename__ = "grade_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int | None] = mapped_column(Integer, index=True)
    exam_no: Mapped[str | None] = mapped_column(String(80), index=True)
    student: Mapped[str] = mapped_column(String(80))
    class_name: Mapped[str | None] = mapped_column(String(80), index=True)
    major: Mapped[str | None] = mapped_column(String(120))
    course: Mapped[str] = mapped_column(String(120))
    score: Mapped[float] = mapped_column(Float, default=0)
    process_score: Mapped[float] = mapped_column(Float, default=0)
    final_score: Mapped[float] = mapped_column(Float, default=0)
    practice_score: Mapped[float] = mapped_column(Float, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0)
    attendance: Mapped[int] = mapped_column(Integer, default=100)
    assessment: Mapped[str] = mapped_column(String(80), default="平时+期末")
    status: Mapped[str] = mapped_column(String(50), default="正常")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(Integer, index=True)
    student_id: Mapped[int | None] = mapped_column(Integer, index=True)
    exam_no: Mapped[str | None] = mapped_column(String(80), index=True)
    student: Mapped[str] = mapped_column(String(80))
    class_name: Mapped[str | None] = mapped_column(String(80), index=True)
    course: Mapped[str] = mapped_column(String(120))
    week: Mapped[int] = mapped_column(Integer, default=1, index=True)
    status: Mapped[str] = mapped_column(String(50), default="已到")
    remark: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AdminNotice(Base):
    __tablename__ = "admin_notices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    target: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CrawlSource(Base):
    __tablename__ = "crawl_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    channel: Mapped[str] = mapped_column(String(100), index=True)
    list_url: Mapped[str] = mapped_column(String(500))
    base_url: Mapped[str] = mapped_column(String(200), default="https://www.acvtc.edu.cn")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    publish_status: Mapped[str] = mapped_column(String(50), default="待审核")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_count: Mapped[int] = mapped_column(Integer, default=0)


class CrawlRecord(Base):
    __tablename__ = "crawl_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int | None] = mapped_column(Integer, index=True)
    source_name: Mapped[str] = mapped_column(String(120))
    article_url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    article_id: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="已采集")
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


def _seed_majors(db: Session) -> None:
    for index, (name, college, duration, courses, jobs) in enumerate(DEFAULT_MAJORS, start=1):
        major = db.query(Major).filter(Major.name == name).first()
        description = f"{name}专业依托{college}建设，面向交通运输及相关产业培养高素质技术技能人才。"
        features = "校企协同、岗课赛证融通、面向交通行业真实岗位实践。"
        if major:
            major.code = major.code or f"ACVTC-{index:03d}"
            major.college = major.college or college
            major.duration = major.duration or duration
            major.tuition = major.tuition or 3900
            major.degree = major.degree or "高职专科"
            major.description = major.description or description
            major.courses = major.courses or courses
            major.jobs = major.jobs or jobs
            major.features = major.features or features
        else:
            db.add(
                Major(
                    name=name,
                    code=f"ACVTC-{index:03d}",
                    college=college,
                    duration=duration,
                    tuition=3900,
                    degree="高职专科",
                    description=description,
                    courses=courses,
                    jobs=jobs,
                    features=features,
                )
            )


def _seed_scores(db: Session) -> None:
    if db.query(Score).count() >= 20:
        return
    rows = []
    for index, (name, _, _, _, _) in enumerate(DEFAULT_MAJORS[:24]):
        base = 390 + (index % 9) * 5 + (index // 9) * 3
        plan = 35 + (index % 6) * 8
        rows.extend(
            [
                Score(year=2025, major=name, min_score=base + 12, max_score=base + 45, avg_score=base + 25, rank_min=150000 - index * 1800, enrollment=plan, province="安徽", subject="物理"),
                Score(year=2024, major=name, min_score=base + 5, max_score=base + 38, avg_score=base + 18, rank_min=158000 - index * 1600, enrollment=plan, province="安徽", subject="物理"),
                Score(year=2023, major=name, min_score=base, max_score=base + 34, avg_score=base + 16, rank_min=166000 - index * 1500, enrollment=plan, province="安徽", subject="物理"),
            ]
        )
    db.add_all(rows)


def _seed_site_articles(db: Session) -> None:
    for index, (title, channel, summary, content) in enumerate(DEFAULT_SITE_ARTICLES):
        row = db.query(SiteArticle).filter(SiteArticle.title == title).first()
        if row:
            row.channel = row.channel or channel
            row.summary = row.summary or summary
            row.content = row.content or content
            row.publish_status = row.publish_status or "已发布"
            row.review_status = row.review_status or "已发布"
            continue
        db.add(
            SiteArticle(
                title=title,
                channel=channel,
                summary=summary,
                content=content,
                source="学校官网",
                author="管理员",
                publish_status="已发布",
                review_status="已发布",
                publish_date=date.today(),
                is_top=index < 3,
            )
        )


AI_CLASS_SCHEDULE = [
    ("周一", "1-4节", "Python数据分析", "敏行楼B417机房"),
    ("周一", "5-8节", "深度学习框架技术", "敏行楼B417机房"),
    ("周二", "1-4节", "习近平新时代中国特色社会主义思想概论", "崇德楼A204教室"),
    ("周二", "5-8节", "人工智能应用开发技术", "敏行楼B417机房"),
    ("周三", "1-4节", "自然语言处理", "敏行楼B417机房"),
    ("周三", "9-12节", "数据结构", "敏行楼B417机房"),
    ("周四", "1-2节", "体育与健康4", "体育场"),
    ("周四", "5-8节", "习近平新时代中国特色社会主义思想概论", "崇德楼A204教室"),
    ("周五", "3-4节", "礼仪与沟通技巧", "崇德楼A401教室"),
]


def _seed_ai_class_schedule(db: Session) -> None:
    class_name = "24人工智能班"
    db.query(TeachingSchedule).filter(TeachingSchedule.class_name == class_name).delete()
    db.add_all(
        [
            TeachingSchedule(
                day=day,
                time=time,
                course=course,
                teacher="待分配",
                room=room,
                class_name=class_name,
                status="已发布",
            )
            for day, time, course, room in AI_CLASS_SCHEDULE
        ]
    )


def seed_defaults(db: Session) -> None:
    if not db.query(User).filter_by(username="admin").first():
        db.add(User(id="admin-001", username="admin", password_hash=hash_password("admin123"), email="admin@example.com", role="admin"))
    role_users = [
        ("teacher-001", "teacher", "teacher123", "teacher@example.com", "teacher"),
        ("admission-001", "admission", "admission123", "admission@example.com", "admission"),
        ("editor-001", "editor", "editor123", "editor@example.com", "editor"),
        ("operator-001", "operator", "operator123", "operator@example.com", "operator"),
    ]
    for user_id, username, password, email, role in role_users:
        if not db.query(User).filter_by(username=username).first():
            db.add(User(id=user_id, username=username, password_hash=hash_password(password), email=email, role=role))

    _seed_majors(db)
    _seed_scores(db)
    _seed_site_articles(db)
    _seed_ai_class_schedule(db)

    if not db.query(RankSegment).first():
        db.add_all(
            [
                RankSegment(year=2025, province="安徽", subject="物理", score=450, rank_count=1200, cumulative_rank=98000),
                RankSegment(year=2025, province="安徽", subject="物理", score=430, rank_count=1450, cumulative_rank=126000),
                RankSegment(year=2025, province="安徽", subject="物理", score=418, rank_count=1530, cumulative_rank=143000),
                RankSegment(year=2025, province="安徽", subject="历史", score=430, rank_count=980, cumulative_rank=62000),
            ]
        )

    if not db.query(SiteChannel).first():
        db.add_all(
            [
                SiteChannel(name="学校概况", slug="about", sort_order=1),
                SiteChannel(name="党政机构", slug="offices", sort_order=2),
                SiteChannel(name="教学机构", slug="schools", sort_order=3),
                SiteChannel(name="师资队伍", slug="faculty", sort_order=4),
                SiteChannel(name="教学科研", slug="research", sort_order=5),
                SiteChannel(name="招生就业", slug="admission", sort_order=6),
                SiteChannel(name="校园服务", slug="service", sort_order=7),
                SiteChannel(name="信息公开", slug="disclosure", sort_order=8),
                SiteChannel(name="学校新闻", slug="news", sort_order=9, is_nav=False),
                SiteChannel(name="通知公告", slug="notice", sort_order=10, is_nav=False),
                SiteChannel(name="招标采购", slug="bidding", sort_order=11, is_nav=False),
                SiteChannel(name="部门动态", slug="department", sort_order=12, is_nav=False),
                SiteChannel(name="专题网站", slug="features", sort_order=13, is_nav=False),
            ]
        )

    if not db.query(SiteBanner).first():
        db.add_all(
            [
                SiteBanner(title="安徽交通职业技术学院官网门户", subtitle="服务招生就业、新闻公告、校园服务和专题网站", image_url="https://www.acvtc.edu.cn/images/logo.png", sort_order=1),
                SiteBanner(title="水墨交院育匠心，交通职教向未来", subtitle="厚德 求是 笃行 致远", image_url="https://www.acvtc.edu.cn/images/nybanner_new.jpg", sort_order=2),
            ]
        )

    if not db.query(SiteLink).first():
        db.add_all(
            [
                SiteLink(title="书记信箱", link_type="顶部链接", sort_order=1),
                SiteLink(title="校长信箱", link_type="顶部链接", sort_order=2),
                SiteLink(title="信息公开", link_type="顶部链接", sort_order=3),
                SiteLink(title="OA", link_type="顶部链接", sort_order=4),
                SiteLink(title="网上办事大厅", link_type="顶部链接", sort_order=5),
                SiteLink(title="招生信息网", link_type="快捷入口", sort_order=1),
                SiteLink(title="就业信息网", link_type="快捷入口", sort_order=2),
                SiteLink(title="图书馆", link_type="快捷入口", sort_order=3),
                SiteLink(title="校历", link_type="快捷入口", sort_order=4),
            ]
        )

    if not db.query(KnowledgeChunk).first():
        doc = KnowledgeDocument(filename="内置招生知识库.md", category="招生咨询", chunk_count=4)
        db.add(doc)
        db.flush()
        db.add_all(
            [
                KnowledgeChunk(document_id=doc.id, category="专业介绍", source=doc.filename, content="人工智能技术应用专业面向智慧交通、智能应用开发和数据处理岗位，核心课程包括 Python、机器学习、数据库、智能交通应用。"),
                KnowledgeChunk(document_id=doc.id, category="专业介绍", source=doc.filename, content="大数据技术专业培养数据采集、清洗、分析与可视化能力，就业方向包括数据分析师、数据工程助理、BI开发。"),
                KnowledgeChunk(document_id=doc.id, category="专业介绍", source=doc.filename, content="道路与桥梁工程技术、城市轨道交通运营管理、新能源汽车技术等专业服务交通强国和安徽区域交通产业发展。"),
                KnowledgeChunk(document_id=doc.id, category="分数推荐", source=doc.filename, content="分数推荐规则：考生分数高于专业最低分20分以上为稳妥，0到20分为冲刺，低于最低分为希望较小。"),
            ]
        )
    if not db.query(SystemConfig).first():
        db.add_all(
            [
                SystemConfig(key="webvpn_url", value="", group_name="真实系统对接", description="学校真实 WebVPN 地址"),
                SystemConfig(key="mail_url", value="", group_name="真实系统对接", description="学校真实邮箱系统地址"),
                SystemConfig(key="portal_url", value="", group_name="真实系统对接", description="学校真实信息门户地址"),
                SystemConfig(key="ehall_url", value="https://ehall.acvtc.edu.cn/", group_name="真实系统对接", description="网上办事大厅"),
                SystemConfig(key="oa_url", value="https://jyoa.acvtc.edu.cn/", group_name="真实系统对接", description="协同办公系统"),
            ]
        )

    if not db.query(InnovationConfig).first():
        db.add_all(
            [
                InnovationConfig(feature_key="recommend", title="招生智能推荐系统", description="根据分数、科类和兴趣生成冲稳保建议", sort_order=1),
                InnovationConfig(feature_key="profile", title="专业画像页面", description="展示课程、岗位、证书、实训和录取趋势", sort_order=2),
                InnovationConfig(feature_key="sync", title="官网内容自动同步与审核", description="聚合后台文章、通知、图片状态", sort_order=3),
                InnovationConfig(feature_key="desk", title="校园服务统一入口", description="按身份聚合常用服务入口", sort_order=4),
                InnovationConfig(feature_key="analytics", title="可视化数据大屏", description="展示官网、招生、咨询和服务数据", sort_order=5),
                InnovationConfig(feature_key="ai", title="AI 招生问答增强版", description="展示问答来源引用", sort_order=6),
                InnovationConfig(feature_key="campus", title="VR/地图式校园导览", description="展示校区、地点和交通指引", sort_order=7),
                InnovationConfig(feature_key="english", title="英文官网自动内容映射", description="中文内容生成英文草稿池", sort_order=8),
            ]
        )

    if not db.query(StudentRecord).first():
        db.add_all(
            [
                StudentRecord(exam_no="253401001", name="王同学", major="人工智能技术应用", class_name="AI2501", phone="138****1021", status="已报到", counselor="李老师"),
                StudentRecord(exam_no="253401002", name="张同学", major="道路与桥梁工程技术", class_name="路桥2502", phone="139****2302", status="已录取", counselor="陈老师"),
                StudentRecord(exam_no="253401003", name="刘同学", major="新能源汽车技术", class_name="新能源2501", phone="136****7721", status="待确认", counselor="周老师"),
                StudentRecord(exam_no="253401004", name="赵同学", major="城市轨道交通运营管理", class_name="城轨2501", phone="135****8812", status="需补材料", counselor="吴老师"),
            ]
        )

    if not db.query(TeachingSchedule).first():
        db.add_all(
            [
                TeachingSchedule(day="周一", time="1-2节", course="Python程序设计", teacher="李老师", room="实训楼A402", class_name="AI2501", status="已发布"),
                TeachingSchedule(day="周二", time="3-4节", course="道路工程测量", teacher="陈老师", room="测量实训场", class_name="路桥2502", status="已发布"),
                TeachingSchedule(day="周三", time="5-6节", course="城市轨道运营组织", teacher="吴老师", room="教学楼C201", class_name="城轨2501", status="草稿"),
            ]
        )

    if not db.query(GradeRecord).first():
        db.add_all(
            [
                GradeRecord(student="王同学", course="Python程序设计", score=88, attendance=96),
                GradeRecord(student="张同学", course="道路工程测量", score=76, attendance=90),
                GradeRecord(student="刘同学", course="新能源汽车检测", score=58, attendance=78),
            ]
        )

    if not db.query(AdminNotice).first():
        db.add_all(
            [
                AdminNotice(title="新生报到提醒", content="已向待报到学生发送报到时间、地点和材料清单。", target="新生"),
                AdminNotice(title="材料补交通知", content="系统筛选身份证、照片、录取确认缺失学生并生成提醒。", target="需补材料学生"),
            ]
        )

    if not db.query(CrawlSource).first():
        db.add_all(
            [
                CrawlSource(name="学校新闻", channel="学校新闻", list_url="https://www.acvtc.edu.cn/index/xxxw.htm", publish_status="待审核"),
                CrawlSource(name="通知公告", channel="通知公告", list_url="https://www.acvtc.edu.cn/index/tzgg.htm", publish_status="待审核"),
                CrawlSource(name="招标采购", channel="招标采购", list_url="https://www.acvtc.edu.cn/index/zbgg.htm", publish_status="待审核"),
                CrawlSource(name="部门动态", channel="部门动态", list_url="https://www.acvtc.edu.cn/index/bmdt.htm", publish_status="待审核"),
            ]
        )
    db.commit()
