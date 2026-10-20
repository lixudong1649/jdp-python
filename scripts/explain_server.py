#!/usr/bin/env python3
"""本机 AI 代码讲解服务（标准库 only，127.0.0.1）。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import threading
import urllib.error
import urllib.request
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROMPT_FILE = Path(__file__).resolve().parent / "explain_prompt.md"
CACHE: dict[str, dict[str, Any]] = {}
CACHE_LOCK = threading.Lock()
DAILY_COUNT = 0
DAILY_KEY = ""


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def prompt_version() -> str:
    if not PROMPT_FILE.is_file():
        return "explain-prompt-v1"
    m = re.search(r"version:\s*(\S+)", PROMPT_FILE.read_text(encoding="utf-8"))
    return m.group(1) if m else "explain-prompt-v1"


def read_system_prompt() -> str:
    text = PROMPT_FILE.read_text(encoding="utf-8")
    return re.sub(r"^---[\s\S]*?---\n", "", text).strip()


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "")
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def today_key() -> str:
    return date.today().isoformat()


def bump_daily() -> bool:
    global DAILY_COUNT, DAILY_KEY
    limit = env_int("JDP_PYTHON_EXPLAIN_DAILY_LIMIT", 200)
    with CACHE_LOCK:
        if DAILY_KEY != today_key():
            DAILY_KEY = today_key()
            DAILY_COUNT = 0
        if DAILY_COUNT >= limit:
            return False
        DAILY_COUNT += 1
        return True


def code_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:16]


def allowed_links(analysis: dict[str, Any]) -> set[str]:
    links: set[str] = set()
    for p in analysis.get("syntax_points") or []:
        for lnk in p.get("course_links") or []:
            links.add(str(lnk))
    for c in analysis.get("concepts") or []:
        for lnk in c.get("course_links") or []:
            links.add(str(lnk))
    return links


def sanitize_response(data: dict[str, Any], analysis: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """丢弃模型自造链接，返回 (对象, 丢弃数)。"""
    allowed = allowed_links(analysis)
    dropped = 0
    sections = []
    for sec in data.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        body = str(sec.get("body", ""))
        for token in re.findall(r"https?://[^\s)]+|\.\./[^\s)]+|/课程/[^\s)]+", body):
            if token not in allowed:
                dropped += 1
                body = body.replace(token, "")
        sections.append({"title": str(sec.get("title", "")), "body": body.strip()})
    out = {
        "intent": str(data.get("intent", "")),
        "sections": sections,
        "issues": [str(x) for x in (data.get("issues") or [])][:8],
        "concept_ids": [str(x) for x in (data.get("concept_ids") or [])][:20],
    }
    return out, dropped


def validate_ai_schema(data: dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    if not isinstance(data.get("intent"), str):
        return False
    secs = data.get("sections")
    if not isinstance(secs, list):
        return False
    for s in secs:
        if not isinstance(s, dict) or "title" not in s or "body" not in s:
            return False
    return isinstance(data.get("issues"), list) and isinstance(data.get("concept_ids"), list)


def ollama_has_model(model: str) -> bool:
    host = os.environ.get("JDP_PYTHON_EXPLAIN_OLLAMA_HOST", "127.0.0.1:11434")
    url = f"http://{host}/api/tags"
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        base = model.split(":")[0]
        for m in data.get("models") or []:
            name = str(m.get("name", ""))
            if name == model or name.startswith(f"{base}:"):
                return True
        return False
    except Exception:
        return False


def call_ollama(messages: list[dict[str, str]], model: str, timeout: float) -> str:
    host = os.environ.get("JDP_PYTHON_EXPLAIN_OLLAMA_HOST", "127.0.0.1:11434")
    url = f"http://{host}/api/chat"
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return str(body.get("message", {}).get("content", ""))


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


class ExplainHandler(BaseHTTPRequestHandler):
    server_version = "jdp-explain/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

    def _json(self, status: int, obj: dict[str, Any]) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors_headers()
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _cors_headers(self) -> None:
        origin = self.headers.get("Origin", "")
        if origin.startswith(("http://127.0.0.1:", "http://localhost:")):
            self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors_headers()
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") != "/v1/health":
            self._json(404, {"ok": False, "message": "未找到"})
            return
        model = os.environ.get("JDP_PYTHON_EXPLAIN_MODEL", "qwen2.5-coder:7b")
        ready = ollama_has_model(model)
        self._json(200, {"ok": True, "model": model, "ready": ready, "provider": "ollama"})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/v1/explain":
            self._json(404, {"ok": False, "message": "未找到"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "message": "JSON 无效"})
            return
        code = str(payload.get("code", ""))
        analysis = payload.get("analysis") or {}
        if not isinstance(analysis, dict):
            self._json(400, {"ok": False, "message": "缺少 analysis"})
            return
        lines = code.count("\n") + (1 if code else 0)
        if lines > env_int("JDP_PYTHON_EXPLAIN_MAX_LINES", 400):
            self._json(413, {"ok": False, "message": f"输入超过 {env_int('JDP_PYTHON_EXPLAIN_MAX_LINES', 400)} 行上限"})
            return
        if not bump_daily():
            self._json(429, {"ok": False, "message": "已达今日请求上限"})
            return
        if os.environ.get("JDP_PYTHON_EXPLAIN_SKIP_LLM") == "1":
            stub = {
                "ok": True,
                "intent": "限额测试桩响应",
                "sections": [{"title": "测试", "body": "不调用模型"}],
                "issues": [],
                "concept_ids": [],
                "retries": 0,
                "dropped_links": 0,
                "cached": False,
            }
            self._json(200, stub)
            return
        pv = prompt_version()
        cache_key = hashlib.sha256(f"{pv}|{code_hash(code)}".encode()).hexdigest()
        with CACHE_LOCK:
            if cache_key in CACHE:
                self._json(200, {**CACHE[cache_key], "cached": True})
                return
        model = os.environ.get("JDP_PYTHON_EXPLAIN_MODEL", "qwen2.5-coder:7b")
        sys_prompt = read_system_prompt()
        user_msg = json.dumps(
            {"code_lines": lines, "code_hash": code_hash(code), "analysis": analysis},
            ensure_ascii=False,
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_msg},
        ]
        timeout = float(env_int("JDP_PYTHON_EXPLAIN_TIMEOUT_SEC", 60))
        retries = 0
        parsed: dict[str, Any] | None = None
        for attempt in range(2):
            try:
                raw = call_ollama(messages, model, timeout=timeout)
                parsed = extract_json(raw)
                if validate_ai_schema(parsed):
                    break
            except TimeoutError:
                self._json(504, {"ok": False, "message": "模型响应超时"})
                return
            except Exception:
                parsed = None
            retries = attempt + 1
        if not parsed or not validate_ai_schema(parsed):
            self._json(502, {"ok": False, "message": "模型输出不符合 Schema", "retries": retries})
            return
        clean, dropped = sanitize_response(parsed, analysis)
        out = {"ok": True, **clean, "retries": retries, "dropped_links": dropped, "cached": False}
        with CACHE_LOCK:
            CACHE[cache_key] = out
        self._json(200, out)


def main() -> None:
    load_dotenv()
    host = os.environ.get("JDP_PYTHON_EXPLAIN_HOST", "127.0.0.1")
    port = env_int("JDP_PYTHON_EXPLAIN_PORT", 8031)
    if host not in ("127.0.0.1", "localhost"):
        print("只允許监听 127.0.0.1", file=sys.stderr)
        sys.exit(2)
    httpd = ThreadingHTTPServer((host, port), ExplainHandler)
    print(f"explain_server listening http://{host}:{port}/", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
