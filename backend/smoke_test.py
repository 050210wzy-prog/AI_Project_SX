import sys

import requests


BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    checks = [
        ("GET", "/health", None),
        ("GET", "/api/website/articles", None),
        ("GET", "/api/admissions/majors", None),
        ("POST", "/api/innovation/recommend", {"province": "安徽", "subject": "物理", "score": 420, "interest": "人工智能"}),
    ]
    failed = []
    for method, path, payload in checks:
        try:
            response = requests.request(method, f"{BASE_URL}{path}", json=payload, timeout=8)
        except requests.RequestException as exc:
            failed.append(f"{method} {path} -> {exc}")
            continue
        if response.status_code >= 400:
            failed.append(f"{method} {path} -> {response.status_code}")
    if failed:
        print("冒烟测试失败，请确认后端已启动：")
        for item in failed:
            print(item)
        return 1
    print("冒烟测试通过：核心接口可访问。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
