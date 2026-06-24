import asyncio
import math
import os
import subprocess
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from moviepy import AudioFileClip, ImageClip, concatenate_videoclips


ROOT = Path(r"C:\Users\30587\Desktop\222")
DESKTOP = Path(r"C:\Users\30587\Desktop")
OUT_DIR = ROOT / "output" / "demo_video"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_PATH = DESKTOP / "安徽交通职业技术学院智慧官网与AI系统5分钟演示.mp4"
W, H = 1920, 1080
FONT = Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf")
BOLD = Path(r"C:\Windows\Fonts\simhei.ttf")


SCENES = [
    {
        "title": "安徽交通职业技术学院智慧官网与 AI 系统",
        "tag": "项目总览",
        "kind": "home",
        "points": ["官网展示", "后台管理", "学生端", "AI 助手", "实时采集"],
        "voice": "大家好，下面演示的是安徽交通职业技术学院智慧官网与招生服务系统。系统已经由旧版单体应用升级为前后端分离架构，首页、二级页面、后台管理、学生课表成绩、官网采集和人工智能助手都集中在同一个项目中。接下来我会按照真实使用流程，用大约五分钟介绍核心功能和运行效果。",
    },
    {
        "title": "运行环境与技术架构",
        "tag": "Vue + FastAPI + MySQL",
        "kind": "architecture",
        "points": ["前端 Vue 3 与 Element Plus", "后端 FastAPI 接口服务", "MySQL 持久化数据", "智谱 GLM 大模型问答", "官网采集与审核发布"],
        "voice": "项目采用 Vue 三和 Element Plus 构建前端界面，FastAPI 提供后端接口，MySQL 保存官网内容、学生信息、成绩、课表、后台配置和采集记录。AI 助手支持智谱 GLM 等模型，并把本地招生数据、校园生活知识库和官网采集内容结合起来回答问题。",
    },
    {
        "title": "官网首页：蓝绿交织，通达未来",
        "tag": "首页展示",
        "kind": "portal",
        "points": ["顶部快捷入口", "全屏轮播图", "学校要闻与通知", "数字交院", "专业集群"],
        "voice": "首页围绕蓝绿交织、通达未来的主题设计。顶部提供学生课表、在线服务大厅、WebVPN、电子邮箱、信息门户、后台登录和英文官网入口；中间是带图片的轮播主视觉，下方展示学校要闻、通知公告、数字交院、专业集群、产教融合和校园文化。",
    },
    {
        "title": "二级页面与学院内页",
        "tag": "内容体系",
        "kind": "pages",
        "points": ["学校概况", "历史沿革", "院系设置", "招生就业", "面包屑返回"],
        "voice": "系统不是只有首页外壳。点击学校概况、院系设置、招生就业、教学科研、校园文化等导航，会进入独立二级页面。每个页面保留统一页头页脚，并加入面包屑导航。学院卡片还可以进入学院内页，展示专业列表、师资力量、实训条件和就业方向。",
    },
    {
        "title": "后台管理系统",
        "tag": "管理员入口",
        "kind": "admin",
        "points": ["数据看板", "官网内容管理", "招生数据管理", "学生档案", "教务管理"],
        "voice": "管理员从首页进入后台登录后，可以看到数据看板。后台把官网管理、招生管理、官网采集、创新中心、学生管理、教务管理、工单和系统设置放在统一侧边栏中。管理员可以维护新闻、通知、轮播图、专业库、学生档案、课程、成绩和考勤。",
    },
    {
        "title": "官网实时采集与审核",
        "tag": "数据更新",
        "kind": "crawler",
        "points": ["采集源状态", "手动采集", "采集记录", "内容审核", "发布到官网"],
        "voice": "官网实时采集功能用于对接学校官网内容。后台可以维护学校新闻、通知公告、招标采购和部门动态等采集源，查看成功率、最近运行时间和采集数量。采集到的内容进入审核流程，管理员确认后发布到前端页面，让官网内容保持持续更新。",
    },
    {
        "title": "学生端：登录、课表、成绩与考勤",
        "tag": "学生服务",
        "kind": "student",
        "points": ["学号登录", "18 周课表", "个人成绩", "考勤记录", "只看本人数据"],
        "voice": "学生端已经从公开页面改为登录后使用。学生用学号登录，初始密码与学号一致。进入后只能看到自己的班级、课表、成绩和考勤。课表从第一周到第十八周都可以自由切换，课程分布按导入的班级课程统一展示。",
    },
    {
        "title": "教务管理：课程、成绩与考核",
        "tag": "教学管理",
        "kind": "academic",
        "points": ["课程表维护", "平时成绩", "期末成绩", "总评自动计算", "批量操作"],
        "voice": "教务管理页面围绕班级课程和学生名单展开。管理员可以查看课程表，维护每名学生的平时成绩、期末成绩和考勤情况。系统根据配置自动计算总评成绩，并且和学生详情页联动，便于按人查看完整学习档案。",
    },
    {
        "title": "招生 AI 助手与数字人播报",
        "tag": "智能问答",
        "kind": "ai",
        "points": ["智谱 GLM 接入", "招生咨询", "校园百事通", "来源引用", "语音朗读"],
        "voice": "招生 AI 助手支持模型平台选择，当前可接入智谱 GLM。用户可以询问专业、分数线、就业方向、招生政策，也可以切换到校园生活百事通，咨询请假、奖学金、报修、一卡通和选课问题。回答完成后，页面中的数字人会自动朗读，也可以重播、停止或静音。",
    },
    {
        "title": "校园生活百事通：案例 A",
        "tag": "实训案例",
        "kind": "campus",
        "points": ["请假流程", "奖学金政策", "宿舍报修", "一卡通处理", "绩点与教学周工具"],
        "voice": "根据实训指导书中的案例 A，系统加入了校园生活百事通助手。它不仅回答常见校园生活问题，还包含教学周查询和绩点计算等工具能力。这样项目不只是官网展示，也能体现智能问答、知识库检索和工具调用的综合应用。",
    },
    {
        "title": "创新中心与英文官网",
        "tag": "特色扩展",
        "kind": "innovation",
        "points": ["招生智能推荐", "专业画像", "数据大屏", "VR 校园导览", "英文内容映射"],
        "voice": "创新中心集中展示八项扩展能力，包括招生智能推荐、专业画像、官网内容同步、校园服务入口、可视化数据大屏、AI 引用问答、VR 校园导览和英文官网内容映射。右上角 English 入口会进入英文官网，让项目具备双语展示能力。",
    },
    {
        "title": "运行展示与项目总结",
        "tag": "完成效果",
        "kind": "summary",
        "points": ["后端接口正常", "前端页面可访问", "后台可维护", "学生端可查询", "AI 问答可播报"],
        "voice": "最后总结一下，本系统已经形成官网展示、后台维护、学生服务、教务管理、官网采集和 AI 咨询的一体化闭环。运行时先启动 FastAPI 后端，再启动 Vue 前端；浏览器访问前端地址即可进入首页，管理员、学生和访客分别使用对应入口完成不同操作。这就是本项目的主要演示内容，谢谢观看。",
    },
]


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def draw_round(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(text, width):
    rows = []
    for paragraph in text.split("\n"):
        buf = ""
        units = list(paragraph)
        for ch in units:
            if len(buf) >= width and ch not in "，。、；： ":
                rows.append(buf)
                buf = ch
            else:
                buf += ch
        if buf:
            rows.append(buf)
    return rows


def gradient_bg():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    r = 245 - 28 * y + 4 * x
    g = 249 - 18 * y + 9 * x
    b = 250 - 16 * y + 22 * x
    img = np.dstack([r, g, b]).astype(np.uint8)
    return Image.fromarray(img, "RGB")


def draw_header(draw, title, tag):
    draw.text((96, 62), "ACVTC 智慧官网与招生服务系统", font=font(30, True), fill="#12384f")
    draw_round(draw, (1510, 54, 1815, 112), 20, "#e8f3ef", "#b9d8cd")
    draw.text((1542, 68), tag, font=font(26, True), fill="#1f6b48")
    draw.text((96, 138), title, font=font(58, True), fill="#0d2d45")
    draw.line((96, 220, 1824, 220), fill="#c8dce6", width=2)


def draw_nav(draw, x, y):
    labels = ["首页", "学校概况", "院系设置", "招生就业", "教学科研", "校园文化", "信息服务", "English"]
    cx = x
    for i, label in enumerate(labels):
        w = 92 if len(label) <= 2 else 142
        fill = "#0066b3" if i == 0 else "#ffffff"
        color = "#ffffff" if i == 0 else "#234"
        draw_round(draw, (cx, y, cx + w, y + 44), 14, fill, "#c6d6df")
        draw.text((cx + 18, y + 7), label, font=font(20, True), fill=color)
        cx += w + 12


def card(draw, xy, title, body, color="#ffffff", accent="#0066b3"):
    x1, y1, x2, y2 = xy
    draw_round(draw, xy, 22, color, "#d7e4ea")
    draw.rectangle((x1, y1, x1 + 8, y2), fill=accent)
    draw.text((x1 + 30, y1 + 26), title, font=font(28, True), fill="#12384f")
    yy = y1 + 76
    for row in wrap_text(body, 22):
        draw.text((x1 + 30, yy), row, font=font(22), fill="#4e6370")
        yy += 34


def draw_points(draw, points, x=1210, y=300):
    draw_round(draw, (x, y, 1818, 900), 28, "#ffffff", "#d7e4ea")
    draw.text((x + 42, y + 36), "本段演示重点", font=font(34, True), fill="#0d2d45")
    yy = y + 104
    colors = ["#0066b3", "#2e7d32", "#c41e3a", "#0097a7", "#6a5acd"]
    for idx, p in enumerate(points):
        draw.ellipse((x + 46, yy + 9, x + 68, yy + 31), fill=colors[idx % len(colors)])
        draw.text((x + 88, yy), p, font=font(28, True), fill="#263d4c")
        yy += 78


def draw_footer(draw, scene_no):
    draw.text((96, 1008), f"{scene_no:02d} / {len(SCENES):02d}", font=font(22, True), fill="#587181")
    draw.text((1480, 1008), "演示视频自动生成 | 含中文语音讲解", font=font(22), fill="#587181")


def draw_dashboard(draw, x, y, w, h, labels):
    draw_round(draw, (x, y, x + w, y + h), 28, "#f9fcfd", "#cbdde6")
    draw_round(draw, (x, y, x + w, y + 70), 28, "#12384f")
    draw.text((x + 34, y + 18), "系统运行界面", font=font(26, True), fill="#ffffff")
    for i in range(3):
        draw.ellipse((x + w - 128 + i * 34, y + 25, x + w - 108 + i * 34, y + 45), fill=["#ff6b6b", "#ffd166", "#4ecdc4"][i])
    yy = y + 112
    for i, label in enumerate(labels):
        xx = x + 42 + (i % 2) * ((w - 110) // 2 + 26)
        cy = yy + (i // 2) * 142
        draw_round(draw, (xx, cy, xx + (w - 110) // 2, cy + 108), 18, "#ffffff", "#d7e4ea")
        draw.text((xx + 24, cy + 20), label, font=font(26, True), fill="#0d2d45")
        draw.line((xx + 24, cy + 68, xx + (w - 150), cy + 68), fill="#e0edf2", width=4)


def make_scene(scene, idx):
    img = gradient_bg().filter(ImageFilter.GaussianBlur(0.2))
    draw = ImageDraw.Draw(img)
    draw_header(draw, scene["title"], scene["tag"])

    kind = scene["kind"]
    if kind in {"home", "portal"}:
        draw_round(draw, (96, 280, 1120, 890), 34, "#ffffff", "#cfdee6")
        draw_nav(draw, 136, 320)
        draw_round(draw, (136, 398, 1080, 710), 26, "#0066b3")
        draw.rectangle((136, 560, 1080, 710), fill="#2e7d32")
        draw.text((184, 448), "勤奋、通达、敬业、乐群", font=font(46, True), fill="#ffffff")
        draw.text((184, 522), "蓝绿交织，通达未来", font=font(30), fill="#e9f8ff")
        for i, name in enumerate(["学校要闻", "通知公告", "数字交院"]):
            card(draw, (136 + i * 315, 744, 420 + i * 315, 858), name, "内容实时更新", accent=["#0066b3", "#c41e3a", "#2e7d32"][i])
    elif kind == "architecture":
        draw_dashboard(draw, 112, 296, 1020, 590, ["Vue 3 前端", "FastAPI 后端", "MySQL 数据库", "智谱 GLM", "官网采集", "后台管理"])
        for x1, y1, x2, y2 in [(510, 430, 728, 430), (510, 572, 728, 572), (510, 714, 728, 714)]:
            draw.line((x1, y1, x2, y2), fill="#6aa4be", width=5)
    elif kind == "pages":
        draw_dashboard(draw, 112, 296, 1020, 590, ["学校简介", "历史沿革", "现任领导", "学院内页", "招生简章", "历年分数"])
        draw.text((158, 812), "首页 / 学校概况 / 学校简介", font=font(26, True), fill="#2e7d32")
    elif kind == "admin":
        draw_round(draw, (112, 286, 1128, 904), 30, "#ffffff", "#d2e0e7")
        draw_round(draw, (112, 286, 330, 904), 30, "#0d2d45")
        for i, label in enumerate(["数据看板", "招生管理", "官网管理", "学生管理", "教务管理", "系统设置"]):
            fill = "#1e7fc3" if i == 0 else "#24465d"
            draw_round(draw, (144, 340 + i * 72, 298, 390 + i * 72), 12, fill)
            draw.text((166, 351 + i * 72), label, font=font(20, True), fill="#ffffff")
        for i, label in enumerate(["文章 128", "学生 42", "课程 18", "问答 356"]):
            card(draw, (374 + (i % 2) * 350, 342 + (i // 2) * 180, 680 + (i % 2) * 350, 480 + (i // 2) * 180), label, "今日状态正常", accent="#2e7d32")
    elif kind == "crawler":
        draw_dashboard(draw, 112, 296, 1020, 590, ["学校新闻源", "通知公告源", "招标采购源", "部门动态源", "采集记录", "审核发布"])
        for i, pct in enumerate([0.82, 0.68, 0.75, 0.9]):
            x, y = 175, 760 + i * 34
            draw.text((x, y - 6), f"源 {i + 1}", font=font(18), fill="#456")
            draw_round(draw, (x + 76, y, x + 650, y + 16), 8, "#e5eef2")
            draw_round(draw, (x + 76, y, x + 76 + int(574 * pct), y + 16), 8, "#0066b3")
    elif kind == "student":
        draw_round(draw, (112, 286, 1128, 904), 30, "#ffffff", "#d2e0e7")
        draw.text((154, 330), "学生端登录后视图", font=font(34, True), fill="#0d2d45")
        cols = ["周一", "周二", "周三", "周四", "周五"]
        rows = ["1-2节", "3-4节", "5-6节", "7-8节"]
        for i, c in enumerate(cols):
            draw.text((295 + i * 148, 396), c, font=font(22, True), fill="#0066b3")
        for j, r in enumerate(rows):
            draw.text((158, 462 + j * 92), r, font=font(20), fill="#536b78")
            for i in range(5):
                color = ["#e8f3ff", "#eaf7ed", "#fff1f3"][(i + j) % 3]
                draw_round(draw, (280 + i * 148, 450 + j * 92, 410 + i * 148, 524 + j * 92), 12, color, "#d5e3ea")
        draw.text((154, 824), "第 1 周 - 第 18 周可切换，只显示本人数据", font=font(28, True), fill="#2e7d32")
    elif kind == "academic":
        draw_dashboard(draw, 112, 296, 1020, 590, ["课程维护", "名单导入", "平时成绩", "期末成绩", "总评计算", "考勤记录"])
        draw.text((160, 806), "总评 = 平时成绩 × 40% + 期末成绩 × 60%", font=font(30, True), fill="#c41e3a")
    elif kind == "ai":
        draw_round(draw, (112, 286, 1128, 904), 30, "#ffffff", "#d2e0e7")
        draw_round(draw, (152, 326, 410, 820), 24, "#f1f8fb", "#d7e4ea")
        draw.ellipse((224, 388, 338, 502), fill="#0066b3")
        draw.ellipse((255, 430, 272, 446), fill="#ffffff")
        draw.ellipse((292, 430, 309, 446), fill="#ffffff")
        draw.arc((258, 446, 306, 485), 0, 180, fill="#ffffff", width=4)
        draw.text((192, 540), "招生数字人", font=font(28, True), fill="#0d2d45")
        draw_round(draw, (460, 340, 1068, 496), 24, "#eaf7ed", "#c6e0cc")
        draw.text((492, 374), "AI：人工智能技术应用专业就业方向包括...", font=font(28), fill="#263d4c")
        draw_round(draw, (690, 552, 1068, 676), 24, "#e8f3ff", "#c5ddec")
        draw.text((722, 588), "用户：安徽物理 430 分能报哪些专业？", font=font(26), fill="#263d4c")
        draw_round(draw, (460, 724, 1068, 838), 24, "#fff8e8", "#eadbbd")
        draw.text((492, 756), "来源：招生专业库 / 官网采集 / 校园知识库", font=font(25, True), fill="#8a5a00")
    elif kind == "campus":
        draw_dashboard(draw, 112, 296, 1020, 590, ["请假流程", "奖学金", "宿舍报修", "一卡通", "选课退课", "绩点计算"])
        draw.text((156, 822), "案例 A：校园生活百事通助手", font=font(34, True), fill="#0066b3")
    elif kind == "innovation":
        draw_dashboard(draw, 112, 296, 1020, 590, ["招生推荐", "专业画像", "内容同步", "数据大屏", "VR 导览", "英文官网"])
        draw.text((156, 822), "English 入口进入英文官网", font=font(34, True), fill="#2e7d32")
    else:
        draw_dashboard(draw, 112, 296, 1020, 590, ["后端 8000", "前端 5173", "接口文档", "后台登录", "学生登录", "AI 问答"])
        draw.text((156, 822), "启动后端与前端，即可完整演示项目", font=font(34, True), fill="#0066b3")

    draw_points(draw, scene["points"])
    subtitle = wrap_text(scene["voice"], 48)[:3]
    draw_round(draw, (170, 912, 1750, 982), 20, "#102f42")
    draw.text((205, 927), " ".join(subtitle), font=font(24), fill="#ffffff")
    draw_footer(draw, idx + 1)
    path = OUT_DIR / f"scene_{idx + 1:02d}.png"
    img.save(path, quality=95)
    return path


async def edge_tts(text, out):
    import edge_tts

    communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural", rate="+0%")
    await communicate.save(str(out))


def sapi_tts(text, out):
    safe = text.replace("'", "''")
    ps = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.Volume = 100
$synth.SetOutputToWaveFile('{str(out)}')
$synth.Speak('{safe}')
$synth.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)


def make_audio(scene, idx):
    mp3 = OUT_DIR / f"voice_{idx + 1:02d}.mp3"
    wav = OUT_DIR / f"voice_{idx + 1:02d}.wav"
    if not mp3.exists():
        try:
            asyncio.run(edge_tts(scene["voice"], mp3))
        except Exception:
            sapi_tts(scene["voice"], wav)
            return wav
    return mp3


def build_video():
    clips = []
    for idx, scene in enumerate(SCENES):
        image_path = make_scene(scene, idx)
        audio_path = make_audio(scene, idx)
        audio = AudioFileClip(str(audio_path))
        duration = max(audio.duration + 0.6, 18.0)
        clip = ImageClip(str(image_path)).with_duration(duration).with_audio(audio)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    if video.duration < 285:
        # Keep the final result close to five minutes without unnaturally slowing speech.
        last = ImageClip(str(OUT_DIR / f"scene_{len(SCENES):02d}.png")).with_duration(285 - video.duration)
        clips.append(last)
        video = concatenate_videoclips(clips, method="compose")

    video.write_videofile(
        str(VIDEO_PATH),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=max(os.cpu_count() or 2, 2),
        bitrate="5000k",
    )
    return video.duration


if __name__ == "__main__":
    total = build_video()
    print(f"created={VIDEO_PATH}")
    print(f"duration={total:.2f}")
