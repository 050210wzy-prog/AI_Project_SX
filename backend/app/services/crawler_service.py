from __future__ import annotations

import re
from datetime import date, datetime
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from app.models.models import CrawlRecord, CrawlSource, SiteArticle


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._href = ""
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            attr = dict(attrs)
            self._href = attr.get("href") or ""
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            text = clean_text("".join(self._text))
            if text:
                self.links.append({"href": self._href, "title": text})
            self._href = ""
            self._text = []


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 ACVTC crawler"})
    with urlopen(request, timeout=12) as response:
        raw = response.read()
    for encoding in ("utf-8", "gbk", "gb2312"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def extract_links(html: str, base_url: str) -> list[dict[str, str]]:
    parser = LinkParser()
    parser.feed(html)
    rows = []
    seen = set()
    for item in parser.links:
        href = item["href"]
        if href.startswith("#") or href.lower().startswith("javascript"):
            continue
        url = urljoin(base_url, href)
        title = clean_text(item["title"])
        if len(title) < 6 or url in seen:
            continue
        if "/info/" not in url and "content.jsp" not in url:
            continue
        if url.lower().endswith((".pdf", ".jpg", ".png", ".gif", ".zip", ".rar")):
            continue
        if not url.startswith("http"):
            continue
        seen.add(url)
        rows.append({"title": title[:255], "url": url})
    return rows


def strip_tags(html: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return clean_text(text)


def extract_date(text: str) -> date | None:
    match = re.search(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", text)
    if not match:
        return None
    year, month, day = map(int, match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def extract_title(html: str, fallback: str) -> str:
    match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    if match:
        title = clean_text(strip_tags(match.group(1)))
        title = re.split(r"[-_—|]", title)[0].strip()
        if len(title) >= 4:
            return title[:255]
    return fallback[:255]


def extract_cover(html: str, article_url: str) -> str | None:
    match = re.search(r'(?is)<img[^>]+src=["\']([^"\']+)["\']', html)
    if not match:
        return None
    return urljoin(article_url, match.group(1))


def pick_candidates(source: CrawlSource, links: Iterable[dict[str, str]], limit: int) -> list[dict[str, str]]:
    keywords = {
        "学校新闻": ["新闻", "学院", "学校", "我校", "我院"],
        "通知公告": ["通知", "公告", "公示", "安排"],
        "招标采购": ["招标", "采购", "询价", "项目"],
        "部门动态": ["学院", "开展", "举办", "活动"],
    }.get(source.channel, [])
    selected = []
    for item in links:
        title = item["title"]
        if "/info/" not in item["url"] and "content.jsp" not in item["url"]:
            continue
        if keywords and not any(key in title for key in keywords):
            continue
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected or list(links)[:limit]


def crawl_source(db: Session, source: CrawlSource, limit: int = 8) -> dict:
    html = fetch_html(source.list_url)
    links = extract_links(html, source.list_url)
    candidates = pick_candidates(source, links, limit)
    created = 0
    skipped = 0
    errors = []

    for item in candidates:
        url = item["url"]
        existing = db.query(CrawlRecord).filter(CrawlRecord.article_url == url).first()
        if existing:
            skipped += 1
            continue
        try:
            detail_html = fetch_html(url)
            text = strip_tags(detail_html)
            title = extract_title(detail_html, item["title"])
            publish_date = extract_date(text) or date.today()
            content = text[:8000]
            summary = content[:180]
            article = SiteArticle(
                title=title,
                channel=source.channel,
                summary=summary,
                content=content,
                source="安徽交通职业技术学院官网",
                author="官网采集",
                cover_url=extract_cover(detail_html, url),
                publish_status=source.publish_status,
                review_status=source.publish_status,
                publish_date=publish_date,
            )
            db.add(article)
            db.flush()
            db.add(
                CrawlRecord(
                    source_id=source.id,
                    source_name=source.name,
                    article_url=url,
                    article_id=article.id,
                    title=title,
                    status="已采集",
                )
            )
            created += 1
        except Exception as exc:
            errors.append(f"{item['title']}: {exc}")
            db.add(
                CrawlRecord(
                    source_id=source.id,
                    source_name=source.name,
                    article_url=url,
                    title=item["title"],
                    status="失败",
                    message=str(exc),
                )
            )
    source.last_run_at = datetime.now()
    source.last_count = created
    db.commit()
    return {"source": source.name, "created": created, "skipped": skipped, "errors": errors}
