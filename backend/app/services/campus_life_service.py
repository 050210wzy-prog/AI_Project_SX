import re
import csv
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.vector_service import add_chunks_to_chroma, query_chroma


ROOT = Path(__file__).resolve().parents[3]
CAMPUS_DATA_PATH = ROOT / "backend" / "data" / "campus_data.csv"
CAMPUS_COLLECTION = "campus_life_kb"


FALLBACK_CAMPUS_KNOWLEDGE = [
    {
        "id": 1,
        "category": "请假",
        "question": "怎么请病假？",
        "answer": "病假应先联系辅导员说明情况，填写请假申请，准备校医院或正规医院诊断证明。返校后按班级要求补交材料，较长时间请假需学院审批。",
        "source": "学生手册示例：请假流程",
    },
    {
        "id": 2,
        "category": "请假",
        "question": "怎么请事假？",
        "answer": "事假应提前向辅导员提交申请，写明请假原因、时间和去向。请假期间保持手机畅通，返校后及时销假。",
        "source": "学生手册示例：事假管理",
    },
    {
        "id": 3,
        "category": "请假",
        "question": "请假超过三天怎么办？",
        "answer": "超过三天的请假通常需要辅导员、学院或相关部门逐级审批。建议提前准备证明材料，并确认是否影响课程、考试和考勤。",
        "source": "学生手册示例：长假审批",
    },
    {
        "id": 4,
        "category": "奖学金",
        "question": "奖学金需要什么条件？",
        "answer": "奖学金一般综合考察学习成绩、综合测评、纪律表现和体测情况。通常要求无违纪、无挂科，并达到学院规定的成绩或绩点要求。",
        "source": "学生手册示例：奖学金评定",
    },
    {
        "id": 5,
        "category": "奖学金",
        "question": "奖学金要多少绩点？",
        "answer": "示例规则中，奖学金参考条件为学年平均绩点不低于 3.0、无挂科、体测合格。具体以学院当年评定通知为准。",
        "source": "学生手册示例：奖学金绩点",
    },
    {
        "id": 6,
        "category": "助学",
        "question": "家庭困难怎么申请助学金？",
        "answer": "家庭经济困难学生可关注班级和学院通知，按要求提交困难认定材料、申请表和相关证明，经班级评议、学院审核后进入资助流程。",
        "source": "学生资助流程示例",
    },
    {
        "id": 7,
        "category": "宿舍",
        "question": "宿舍灯坏了找谁？",
        "answer": "宿舍设施损坏可先向宿管登记，或通过学校后勤报修渠道提交房间号、故障位置和联系方式，等待维修人员处理。",
        "source": "后勤报修流程示例",
    },
    {
        "id": 8,
        "category": "宿舍",
        "question": "宿舍水管漏水怎么办？",
        "answer": "发现漏水应及时关闭附近水源，通知宿管，并通过后勤报修渠道提交紧急报修。若影响安全，应第一时间联系宿管值班人员。",
        "source": "后勤报修流程示例",
    },
    {
        "id": 9,
        "category": "一卡通",
        "question": "一卡通丢了怎么办？",
        "answer": "一卡通丢失后应尽快挂失，避免余额被他人使用。随后携带本人有效证件到指定窗口或服务点办理补卡。",
        "source": "校园卡服务示例",
    },
    {
        "id": 10,
        "category": "一卡通",
        "question": "一卡通怎么补办？",
        "answer": "补办一卡通通常需要先挂失，再携带身份证或学生证到校园卡服务窗口办理。补卡费用和领取时间以现场通知为准。",
        "source": "校园卡服务示例",
    },
    {
        "id": 11,
        "category": "选课",
        "question": "选错了课能退吗？",
        "answer": "选错课程一般应在学校规定的退选时间内处理。超过时间可能无法退选，建议及时联系教务老师或辅导员确认。",
        "source": "教务选课流程示例",
    },
    {
        "id": 12,
        "category": "选课",
        "question": "什么时候选课？",
        "answer": "选课时间以教务系统和学院通知为准。建议关注教务通知、班级群和辅导员提醒，按时完成选课确认。",
        "source": "教务通知示例",
    },
    {
        "id": 13,
        "category": "考试",
        "question": "考试冲突怎么办？",
        "answer": "如遇考试时间冲突，应尽快联系辅导员和教务部门，提交冲突课程信息，按学校流程申请协调或缓考。",
        "source": "教务考试流程示例",
    },
    {
        "id": 14,
        "category": "考试",
        "question": "挂科后怎么办？",
        "answer": "挂科后应关注补考或重修通知，按要求报名并认真复习。若不清楚流程，可咨询任课教师、辅导员或教务部门。",
        "source": "教务学业管理示例",
    },
    {
        "id": 15,
        "category": "图书馆",
        "question": "图书馆借书怎么借？",
        "answer": "借书一般需要凭学生证或一卡通，在图书馆检索图书位置后到借阅台或自助借还设备办理。具体借阅期限以图书馆规则为准。",
        "source": "图书馆服务示例",
    },
    {
        "id": 16,
        "category": "图书馆",
        "question": "图书逾期了怎么办？",
        "answer": "图书逾期应尽快归还，并按图书馆规则处理逾期记录或费用。若图书遗失，应及时联系图书馆工作人员。",
        "source": "图书馆服务示例",
    },
    {
        "id": 17,
        "category": "网络",
        "question": "校园网连不上怎么办？",
        "answer": "可先检查账号密码、网络信号和设备设置，再尝试重新连接。若仍无法使用，联系校园网络服务或信息中心报修。",
        "source": "网络服务示例",
    },
    {
        "id": 18,
        "category": "证明",
        "question": "在读证明怎么开？",
        "answer": "在读证明通常需通过学院或教务相关窗口申请，按要求填写用途并核验身份。部分证明可能可在信息门户或办事大厅办理。",
        "source": "办事指南示例",
    },
    {
        "id": 19,
        "category": "就业",
        "question": "校园招聘信息在哪里看？",
        "answer": "校园招聘信息可关注学校就业信息网、学院通知、班级群和招聘会公告。建议提前准备简历并留意宣讲会时间。",
        "source": "就业服务示例",
    },
    {
        "id": 20,
        "category": "安全",
        "question": "晚上回宿舍晚了怎么办？",
        "answer": "晚归应遵守宿舍管理规定，必要时提前向辅导员或宿管说明情况。遇到安全问题应及时联系老师、宿管或校园安保。",
        "source": "宿舍安全管理示例",
    },
]


def load_campus_knowledge() -> list[dict]:
    if not CAMPUS_DATA_PATH.exists():
        return FALLBACK_CAMPUS_KNOWLEDGE
    rows = []
    with CAMPUS_DATA_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            if not row.get("question") or not row.get("answer"):
                continue
            rows.append(
                {
                    "id": int(row.get("id") or len(rows) + 1),
                    "category": row.get("category", "校园生活"),
                    "question": row["question"],
                    "answer": row["answer"],
                    "source": row.get("source", "campus_data.csv"),
                }
            )
    return rows or FALLBACK_CAMPUS_KNOWLEDGE


CAMPUS_KNOWLEDGE = load_campus_knowledge()


def build_campus_vector_db() -> int:
    chunks = [
        {
            "id": f"campus-{item['id']}",
            "content": f"问题：{item['question']}\n答案：{item['answer']}",
            "source": item["source"],
            "category": item["category"],
            "question": item["question"],
        }
        for item in load_campus_knowledge()
    ]
    add_chunks_to_chroma(chunks, collection_name=CAMPUS_COLLECTION, reset=True)
    return len(chunks)


def get_current_week(today: date | None = None) -> str:
    today = today or date.today()
    term_start = date(2026, 3, 2)
    week_num = (today - term_start).days // 7 + 1
    if week_num < 1:
        return "当前还未到本学期第 1 周，具体校历请以教务通知为准。"
    if week_num > 20:
        return f"按 2026 年 3 月 2 日开学估算，现在约为第 {week_num} 周，已超出常规 18 周教学周，请以最新校历为准。"
    return f"按 2026 年 3 月 2 日开学估算，现在是第 {week_num} 周。"


def calculate_gpa(scores: list[int]) -> str:
    if not scores:
        return "请告诉我各科分数，例如：绩点计算 85,90,78。"
    points = []
    for score in scores:
        if score >= 90:
            points.append(4.0)
        elif score >= 80:
            points.append(3.0)
        elif score >= 70:
            points.append(2.0)
        elif score >= 60:
            points.append(1.0)
        else:
            points.append(0.0)
    gpa = sum(points) / len(points)
    return f"按示例规则估算，您的平均绩点是：{gpa:.2f}。该结果仅用于学习演示，正式绩点请以教务系统为准。"


def _score(query: str, item: dict) -> float:
    text = f"{item['category']} {item['question']} {item['answer']}"
    overlap = sum(1 for char in set(query) if char.strip() and char in text)
    ratio = SequenceMatcher(None, query, text).ratio()
    keyword_bonus = 0
    for keyword in ["请假", "病假", "事假", "奖学金", "绩点", "宿舍", "报修", "一卡通", "选课", "退课", "考试", "图书馆", "校园网"]:
        if keyword in query and keyword in text:
            keyword_bonus += 4
    return overlap + ratio * 10 + keyword_bonus


def _expand_query(question: str) -> str:
    expansions = {
        "发烧": "病假 请假 校医院 诊断证明",
        "生病": "病假 请假 校医院 诊断证明",
        "不舒服": "病假 请假 校医院 诊断证明",
        "灯坏": "宿舍 报修 宿管 后勤",
        "水管": "宿舍 报修 宿管 后勤",
        "卡丢": "一卡通 挂失 补办",
        "饭卡": "一卡通 挂失 补办",
        "选错": "选课 退课 退选 教务",
        "退课": "选课 退选 教务",
        "补助": "助学金 家庭困难 资助",
    }
    extra = [value for key, value in expansions.items() if key in question]
    return f"{question} {' '.join(extra)}".strip()


def retrieve_campus_knowledge(question: str, limit: int = 3) -> list[dict]:
    expanded = _expand_query(question)
    knowledge = load_campus_knowledge()
    ranked = sorted(knowledge, key=lambda item: _score(expanded, item), reverse=True)
    keyword_hits = [item for item in ranked[:limit] if _score(expanded, item) > 2]

    vector_hits = query_chroma(expanded, n_results=limit, collection_name=CAMPUS_COLLECTION)
    normalized_vector_hits = []
    for index, item in enumerate(vector_hits):
        content = item.get("content", "")
        if not content:
            continue
        normalized_vector_hits.append(
            {
                "id": index + 1,
                "category": item.get("category") or "校园生活",
                "question": item.get("question") or "相关校园规则",
                "answer": content.replace("问题：", "").replace("答案：", " "),
                "source": item.get("source") or "campus_data.csv",
            }
        )

    merged = keyword_hits + [item for item in normalized_vector_hits if item["question"] not in {hit["question"] for hit in keyword_hits}]
    reranked = sorted(merged, key=lambda item: _score(expanded, item), reverse=True)
    return reranked[:limit]


def campus_life_answer(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if ("周" in question and ("几" in question or "校历" in question or "第" in question)) or "教学周" in question:
        answer = get_current_week()
        return ChatResponse(intent="校园工具：教学周", answer=answer, confidence=0.9, sources=[{"source": "校园生活工具", "preview": "按学期开始日期估算当前教学周。"}])

    scores = [int(num) for num in re.findall(r"\d+", question) if 0 <= int(num) <= 100]
    wants_gpa_tool = "GPA" in question.upper() or "绩点计算" in question or ("绩点" in question and bool(scores))
    if wants_gpa_tool:
        answer = calculate_gpa(scores)
        return ChatResponse(intent="校园工具：绩点计算", answer=answer, confidence=0.92, sources=[{"source": "校园生活工具", "preview": "按 90/80/70/60 分段规则估算平均绩点。"}])

    hits = retrieve_campus_knowledge(question)
    if not hits:
        answer = "我不确定，建议咨询辅导员或相关部门。你也可以换一种问法，比如“怎么请病假”“奖学金要多少绩点”“宿舍灯坏了找谁”。"
        return ChatResponse(intent="校园生活问答", answer=answer, confidence=0.42, sources=[])

    lines = ["根据校园生活规则库，可以这样处理：", ""]
    for item in hits[:2]:
        lines.append(f"- {item['answer']}")
    lines.append("")
    lines.append("提醒：以上为校园生活百事通助手的规则库回答，具体办理以学校最新通知和辅导员要求为准。")
    sources = [{"source": item["source"], "preview": f"{item['category']}：{item['question']} - {item['answer'][:80]}"} for item in hits]
    return ChatResponse(intent="校园生活问答", answer="\n".join(lines), confidence=0.82, sources=sources)
