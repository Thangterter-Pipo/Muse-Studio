"""Muse Studio - AI Generation & Creative Control Center."""
from __future__ import annotations

from typing import Any

import asyncio
import base64
import io
import hashlib
import json
import logging
import os
import re
import shutil
import socket as _socket_mod
import subprocess
import tempfile
import threading
import time
import uuid
import zipfile

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                               RedirectResponse, Response, StreamingResponse)
from pydantic import BaseModel, Field

from config import CFG
from engine import ESSENTIAL_COOKIES, MuseAuthError, MuseEngine, MuseGenerationError
from store import Store, account_expiry, min_expiry

import sys
log = logging.getLogger("musestudio")
log.setLevel(logging.INFO)
if not log.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    log.addHandler(_h)

CFG.ensure_dirs()
app = FastAPI(title="musestudio", version="1.5.8-ui")
from studio_routes import mount_studio; mount_studio(app, CFG)  # muse-studio-ui

# Muse Studio configuration and operations
# Muse Studio configuration and operations
#
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
_origins = [o.strip() for o in (CFG.cors_origins or "").split(",") if o.strip()]
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

# ---- Hardening v1.5.5: CORS có thể siết lại ----
# Mặc định vẫn allow * để tương thích, nhưng có thể đặt MUSE_STUDIO_CORS_ALLOW_ALL=0
# và liệt kê domain trong MUSE_STUDIO_CORS_ORIGINS để khóa lại.
_cors_allow_all = bool(getattr(CFG, "cors_allow_all", True))
_cors_origins = _origins if _origins else []
if _cors_allow_all and not _cors_origins:
    _cors_effective = ["*"]
elif _cors_origins:
    _cors_effective = _cors_origins
else:
    _cors_effective = ["*"]
if not _cors_allow_all and _cors_effective == ["*"]:
    log.warning("CORS đang mở *, hãy đặt MUSE_STUDIO_CORS_ALLOW_ALL=0 và cấu hình MUSE_STUDIO_CORS_ORIGINS khi expose ra internet")
app.add_middleware(CORSMiddleware,
                   allow_origins=_cors_effective,
                   allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
                   allow_headers=["*"],
                   expose_headers=["*"],
                   max_age=600)

# ---- Security headers ----
@app.middleware("http")
async def _sec_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    # Không cache admin
    if request.url.path.startswith("/admin"):
        resp.headers["Cache-Control"] = "no-store"
    return resp

# ---- Rate limit đơn giản cho /v1/* ----
import collections as _collections
_RL_BUCKETS: dict[str, _collections.deque] = {}
_RL_LOCK = threading.Lock()
def _rate_limited(ip: str) -> bool:
    limit = int(getattr(CFG, "rate_limit_per_min", 120) or 0)
    if limit <= 0:
        return False
    now = time.time()
    with _RL_LOCK:
        dq = _RL_BUCKETS.get(ip)
        if dq is None:
            dq = _collections.deque()
            _RL_BUCKETS[ip] = dq
        while dq and now - dq[0] > 60:
            dq.popleft()
        if len(dq) >= limit:
            return False if False else True
        dq.append(now)
        # dọn bucket cũ để khỏi phình
        if len(_RL_BUCKETS) > 2000:
            for k in list(_RL_BUCKETS.keys())[:500]:
                _RL_BUCKETS.pop(k, None)
        return False

@app.middleware("http")
async def _rl_mw(request: Request, call_next):
    if request.url.path.startswith("/v1/"):
        ip = request.client.host if request.client else "unknown"
        if _rate_limited(ip):
            return JSONResponse(status_code=429, content={"error": {"message": "Rate limit: quá nhiều request, thử lại sau 60s", "type": "rate_limit_error", "param": None, "code": 429}})
    return await call_next(request)

store = Store(CFG)
engine = MuseEngine(CFG)
GEN_LOCK = threading.Lock()
IMAGE_TASK_LOCK = threading.Lock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
def _err_type(status: int) -> str:
    if status == 404:
        return "not_found_error"
    if status == 429:
        return "rate_limit_error"
    if status >= 500:
        return "server_error"
    return "invalid_request_error"


@app.exception_handler(HTTPException)
async def _http_exc(request: Request, exc: HTTPException):
    if request.url.path.startswith("/v1/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"message": str(exc.detail),
                               "type": _err_type(exc.status_code),
                               "param": None, "code": exc.status_code}},
            headers=getattr(exc, "headers", None))
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": exc.detail},
                        headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
async def _validation_exc(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/v1/"):
        return JSONResponse(status_code=422, content={"error": {
            "message": "Tham số không hợp lệ: " + str(exc.errors())[:400],
            "type": "invalid_request_error", "param": None, "code": 422}})
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

MODELS = [
    {"id": "muse-spark", "object": "model", "owned_by": "muse",
     "description": "Muse Spark - Trò chuyện & Kịch bản AI (Streaming)"},
    {"id": "muse-image", "object": "model", "owned_by": "muse",
     "description": "Muse Image - Tạo ảnh và chỉnh sửa ảnh AI"},
    {"id": "muse-video", "object": "model", "owned_by": "muse",
     "description": "Muse Video - Tạo video chuyển động AI"},
]

# Muse Studio configuration and operations
# Muse Studio configuration and operations
#
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
MODEL_ALIASES = {
# Muse Studio configuration and operations
    "muse-text": "muse-spark", "muse-chat": "muse-spark", "muse-llm": "muse-spark",
    "koda": "muse-spark",
    "gpt-3.5-turbo": "muse-spark", "gpt-4": "muse-spark", "gpt-4-turbo": "muse-spark",
    "gpt-4o": "muse-spark", "gpt-4o-mini": "muse-spark", "gpt-4.1": "muse-spark",
    "gpt-4.1-mini": "muse-spark", "gpt-5": "muse-spark", "gpt-5-codex": "muse-spark",
    "o1": "muse-spark", "o1-mini": "muse-spark", "o3": "muse-spark",
    "o3-mini": "muse-spark", "o4-mini": "muse-spark",
    "codex": "muse-spark", "codex-mini-latest": "muse-spark",
    "claude-3-5-sonnet": "muse-spark", "claude-3-5-sonnet-latest": "muse-spark",
    "claude-3-7-sonnet": "muse-spark", "claude-sonnet-4": "muse-spark",
    "claude-opus-4": "muse-spark", "claude-3-opus": "muse-spark",
    "claude-3-haiku": "muse-spark",
    "deepseek-chat": "muse-spark", "deepseek-coder": "muse-spark",
    "deepseek-reasoner": "muse-spark", "qwen-coder": "muse-spark",
    "gemini-2.5-pro": "muse-spark", "gemini-2.5-flash": "muse-spark",
# Muse Studio configuration and operations
    "muse-img": "muse-image", "dall-e": "muse-image", "dall-e-3": "muse-image",
    "gpt-image-1": "muse-image", "flux": "muse-image", "midjourney": "muse-image",
# Muse Studio configuration and operations
    "muse-vid": "muse-video", "muse-videos": "muse-video",
    "sora": "muse-video", "sora-2": "muse-video", "veo": "muse-video",
    "veo-3": "muse-video", "kling": "muse-video", "runway": "muse-video",
}


def resolve_model(name: str | None, default: str = "muse-image") -> str:
    n = (name or "").strip().lower()
    return MODEL_ALIASES.get(n, n or default)


# Muse Studio configuration and operations
def _load_client_keys() -> list[dict]:
    """Đọc danh sách Client API Keys từ data/api_keys.json"""
    path = os.path.join(CFG.data_dir, "api_keys.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_client_keys(keys: list[dict]):
    """Lưu danh sách Client API Keys vào data/api_keys.json"""
    os.makedirs(CFG.data_dir, exist_ok=True)
    path = os.path.join(CFG.data_dir, "api_keys.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def auth(authorization: str | None = Header(default=None)):
    """Xác thực Bearer token: chấp nhận Admin Master Key HOẶC Client API Key được cấp."""
    if not CFG.api_key:
        return True
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Thiếu Authorization: Bearer <key>")
    parts = authorization.split(None, 1)
    token = parts[1].strip() if len(parts) > 1 else ""
    if not token:
        raise HTTPException(401, "API key không hợp lệ")

    # 1. Khớp Master Key
    if token == CFG.api_key:
        return True

    # 2. Khớp Client API Keys
    client_keys = _load_client_keys()
    for item in client_keys:
        if item.get("key") == token and item.get("enabled", True):
            item["last_used"] = int(time.time())
            item["use_count"] = item.get("use_count", 0) + 1
            try:
                _save_client_keys(client_keys)
            except Exception:
                pass
            return True

    raise HTTPException(401, "API key không hợp lệ hoặc đã bị vô hiệu hóa")


# Muse Studio configuration and operations

def _renew_and_persist(acc_id: str, wake_vm: bool = True, force: bool = False) -> dict | None:
    """Gia han cookie qua /api/session va cap nhat store.
    （10phut）， 2~3  HTTP 。"""
    acc = store.get_account(acc_id)
    if not acc or not acc.get("cookies"):
        return acc
    now = time.time()
    last_sync = max(
        int(acc.get("synced_at") or 0),
        int(acc.get("last_keepalive") or 0),
        int(engine._last_http_renew.get(acc_id, 0)),
    )
    if not force and acc.get("ok") is True and (now - last_sync) < 600:
        engine._last_http_renew[acc_id] = last_sync
        return acc
    try:
        res = engine.renew_session_http(acc["cookies"], acc.get("cookies_exp"), wake_vm=wake_vm)
        engine._last_http_renew[acc_id] = now
        if res.get("cookies"):
            store.update_account(acc_id, cookies=res["cookies"],
                                 cookies_exp=res.get("cookies_exp"),
                                 ok=True if res.get("ok") else acc.get("ok"),
                                 synced_at=int(now))
            store.touch_keepalive(acc_id, True, f" (VM: {res.get('vm_state') or 'RUNNING'})")
    except MuseAuthError as exc:
        store.mark(acc_id, False, str(exc))
        raise
    except Exception as exc:
        log.warning("HTTP Status %s Status: %s", acc_id, exc)
    return store.get_account(acc_id)


def safe_chat_stream(cookies: dict, prompt: str, expires: dict | None,
                     timeout: int, account_id: str | None):
    """ chat_stream  GEN_LOCK， Queue 。
    、，stop_event + finally  100%  GEN_LOCK，。
     VM ，。"""
    import queue
    q = queue.Queue(maxsize=100)
    stop_event = threading.Event()

    def worker():
        cur_id = account_id
        cur_cookies = cookies
        cur_exp = expires
        last_exc = None
        try:
            for attempt in range(2):
                if stop_event.is_set():
                    return
                if attempt > 0:
                    alt = store.pick_account(rotate=True, force_rotate=True, exclude_id=cur_id)
                    if not alt or alt["id"] == cur_id:
                        break
                    cur_id = alt["id"]
                    cur_cookies = alt["cookies"]
                    cur_exp = alt.get("cookies_exp")
                    log.info("【Status】Status %s (%s) Status...", alt.get("label"), cur_id)
                yielded = False
                try:
                    if cur_id:
                        refreshed = _renew_and_persist(cur_id, wake_vm=True, force=(attempt > 0))
                        if refreshed:
                            cur_cookies = refreshed["cookies"]
                            cur_exp = refreshed.get("cookies_exp")
                    with GEN_LOCK:
                        if stop_event.is_set():
                            return
                        engine.start()
                        for chunk in engine.chat_stream(
                            cur_cookies, prompt, cur_exp, timeout,
                            account_id=cur_id, stop_event=stop_event
                        ):
                            yielded = True
                            q.put(("data", chunk))
                            if stop_event.is_set():
                                return
                    if cur_id:
                        store.mark(cur_id, True, "")
                        _sync_cookies(cur_id)
                    return
                except MuseAuthError as exc:
                    last_exc = exc
                    if cur_id:
                        store.mark(cur_id, False, str(exc))
                    if yielded:
                        break
                except Exception as exc:
                    last_exc = exc
                    try:
                        engine.reset_thread()
                    except Exception:
                        pass
                    if yielded:
                        break
            if last_exc is not None:
                q.put(("error", last_exc))
        finally:
            q.put(("done", None))

    threading.Thread(target=worker, daemon=True).start()

    try:
        while True:
            kind, val = q.get()
            if kind == "data":
                yield val
            elif kind == "error":
                raise val
            else:
                break
    finally:
        stop_event.set()


class ImageRequest(BaseModel):
    prompt: str
    model: str = "muse-image"
    n: int = 1
    size: str | None = None
    aspect_ratio: str | None = None
    response_format: str = "url"      # url | b64_json
    timeout: int | None = Field(default=None, ge=1, le=600)
    extra: str | None = None
    image: Any = None
    images: list | None = None
    reference_image: str | None = None
    async_: bool = Field(False, alias="async")


class VideoRequest(BaseModel):
    prompt: str
    model: str = "muse-video"
    duration: int | None = None
    size: str | None = None
    aspect_ratio: str | None = None
    resolution: str | None = None
    timeout: int | None = None
    extra: str | None = None
    image: Any = None
    image_url: Any = None
    reference_image: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str | list | None = None
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list | None = None


class ChatRequest(BaseModel):
    """OpenAI Chat Completions 。

    ：（Pydantic ），
     ——  422。
    """
    model: str = "muse-spark"
    messages: list[ChatMessage] = []
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    timeout: int | None = None
    prompt: str | None = None       #  prompt 
# Muse Studio configuration and operations
    tools: list | None = None
    tool_choice: object | None = None
    response_format: object | None = None
    stream_options: object | None = None


class ResponsesRequest(BaseModel):
    """OpenAI Responses API（ Codex ）。"""
    model: str = "muse-spark"
    input: str | list | None = None
    instructions: str | None = None
    stream: bool = False
    max_output_tokens: int | None = None
    timeout: int | None = None
    tools: list | None = None
    store: bool | None = None


class AccountRequest(BaseModel):
    label: str = ""
    cookies: dict[str, str] = Field(default_factory=dict)
    cookie_header: str | None = None
    batch: str | None = None          # ，
    expires: dict[str, int] = Field(default_factory=dict)   # cookie  -> 


class AccountPatch(BaseModel):
    label: str | None = None
    enabled: bool | None = None


# Muse Studio configuration and operations
def build_image_prompt(r: ImageRequest) -> str:
    has_ref = bool(r.reference_image or r.image or r.images)
    if has_ref:
        parts = [f"/：{r.prompt.strip()}"]
    else:
        parts = [f"（，，）：{r.prompt.strip()}"]
    ar = (r.aspect_ratio or "").strip().lower()
    sz = (r.size or "").strip().lower()

    if any(k in ar or k in sz for k in ("9:16", "9/16", "portrait", "", "720x1280", "1080x1920")):
        parts.append("【】： 9:16 （9:16 vertical portrait aspect ratio，），，")
    elif any(k in ar or k in sz for k in ("16:9", "16/9", "landscape", "", "1280x720", "1920x1080")):
        parts.append("【】：16:9 （16:9 widescreen landscape aspect ratio）")
    elif any(k in ar or k in sz for k in ("1:1", "square", "", "1024x1024")):
        parts.append("【】：1:1 （1:1 square aspect ratio）")
    elif any(k in ar or k in sz for k in ("4:3", "4/3")):
        parts.append("【】：4:3 ")
    elif any(k in ar or k in sz for k in ("3:4", "3/4")):
        parts.append("【】：3:4 ")
    elif r.aspect_ratio:
        parts.append(f"【】：{r.aspect_ratio} ")
    elif r.size:
        parts.append(f"/：{r.size}")

    if has_ref:
        parts.append("【】：、、、Logo（clean image without any watermark, text, or logo），")

    if r.extra:
        parts.append(r.extra)
    return "，".join(parts)


def _content_text(content) -> str:
    """ OpenAI  content （ list ）。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                t = item.get("type")
                if t in (None, "text", "input_text", "output_text"):
                    parts.append(str(item.get("text") or ""))
                elif t == "image_url":
                    parts.append("[]")
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(p for p in parts if p)
    return str(content)


def build_chat_prompt(messages: list[ChatMessage]) -> str:
    """ messages  muse.ai 。

    muse.ai ， API （
    /）， prompt  ——  Codex 
    「」。
    """
    system, turns = [], []
    for m in messages:
        role = (m.role or "").strip().lower()
        text = _content_text(m.content).strip()
        if role == "tool":
# Muse Studio configuration and operations
            if text:
                turns.append(("user", "【】\n" + text))
            continue
        if not text:
# Muse Studio configuration and operations
            if role == "assistant" and m.tool_calls:
                turns.append(("assistant", "【】" + json.dumps(
                    m.tool_calls, ensure_ascii=False)[:600]))
            continue
        if role in ("system", "developer"):
            system.append(text)
        else:
            turns.append((role, text))

# Muse Studio configuration and operations
    if len(turns) == 1 and not system and turns[0][0] == "user":
        return turns[0][1]

    parts = []
    if system:
        sys_text = "\n\n".join(system)
        sys_text = sys_text.replace("danger-full-access", "standard-workspace-access")
        # Nén bớt system prompt quá dài nếu vượt quá 6000 ký tự để tăng tốc gõ phím của web agent
        if len(sys_text) > 6000:
            sys_text = sys_text[:5000] + "\n...(ngữ cảnh hệ thống rút gọn)..."
        parts.append(f"Quy tắc & Bối cảnh hệ thống:\n{sys_text}")

    # Chỉ giữ tối đa 14 lượt hội thoại gần nhất (tránh gửi 50-100 turns khiến web Muse bị nghẽn)
    if len(turns) > 14:
        turns = turns[-14:]

    for role, text in turns:
        # Cắt ngắn nếu một turn đơn lẻ vượt quá 8000 ký tự (như file dump hoặc tool output khổng lồ)
        if len(text) > 8000:
            text = text[:4000] + "\n...(nội dung dài đã được rút gọn)...\n" + text[-3000:]
        label = "Trợ lý AI" if role == "assistant" else "Người dùng"
        parts.append(f"{label}:\n{text}")
    return "\n\n".join(parts)


# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
#
# Muse Studio configuration and operations
# Muse Studio configuration and operations
_TOOL_PROTOCOL_HEAD = """Bạn có thể gọi các công cụ dưới đây để hỗ trợ người dùng thực hiện nhiệm vụ khi cần thiết.
Nếu cần gọi công cụ, hãy xuất một khối mã JSON theo định dạng sau (không giải thích rườm rà):
```json
{"name": "<tên_công_cụ>", "arguments": {<tham_số>}}
```
Nếu không cần gọi công cụ, hãy trả lời tự nhiên bằng ngôn ngữ được yêu cầu.

Danh sách công cụ khả dụng:
"""


def _describe_params(params) -> str:
    """ JSON Schema 。"""
    if not isinstance(params, dict):
        return "      (Khong co tham so)"
    props = params.get("properties") or {}
    required = set(params.get("required") or [])
    if not props:
        return "      (Khong co tham so)"
    lines = []
    for name, spec in props.items():
        spec = spec if isinstance(spec, dict) else {}
        lines.append("      - %s (%s, %s)%s" % (
            name, spec.get("type") or "any",
            "Bắt buộc" if name in required else "Tùy chọn",
            (" " + spec["description"]) if spec.get("description") else ""))
    return "\n".join(lines)


def build_tools_prompt(tools: list | None) -> str:
    """ tools （）。

     Chat Completions  `{"type":"function","function":{...}}`
     Responses API  `{"type":"function","name":...,"parameters":...}`。
    """
    if not tools:
        return ""
    items = []
    for t in tools:
        if not isinstance(t, dict):
            continue
        fn = t.get("function") if isinstance(t.get("function"), dict) else t
        if not fn.get("name"):
            continue
        desc = fn.get("description") or ""
        items.append("%d. %s%s\n   ：\n%s" % (
            len(items) + 1, fn["name"], (" — " + desc) if desc else "",
            _describe_params(fn.get("parameters"))))
    if not items:
        return ""
    return _TOOL_PROTOCOL_HEAD + "\n".join(items) + "\n"


_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*([\s\S]*?)```")


def _as_tool_calls(obj) -> list[dict] | None:
    """ JSON  OpenAI tool_calls； None。"""
    raw = obj if isinstance(obj, list) else [obj]
    if not raw:
        return None
    out = []
    for item in raw:
        if not isinstance(item, dict):
            return None
        name = item.get("tool") or item.get("name") or item.get("function")
        if not isinstance(name, str) or not name:
            return None
        args = item.get("arguments")
        if args is None:
            args = item.get("parameters") or item.get("args") or {}
        if not isinstance(args, str):
            args = json.dumps(args, ensure_ascii=False)
        out.append({"id": "call_" + uuid.uuid4().hex[:20], "type": "function",
                    "function": {"name": name, "arguments": args}})
    return out or None


def parse_tool_calls(text: str) -> tuple[list[dict] | None, str]:
    """。

     (tool_calls, )； (None, )。
    ：
    1) ```json ... ``` ；
    2)  JSON（ json/JSON ）；
    3)  JSON 。
    """
    if not text:
        return None, text
    for m in reversed(list(_FENCE_RE.finditer(text))):
        try:
            calls = _as_tool_calls(json.loads(m.group(1).strip()))
        except Exception:
            continue
        if calls:
            return calls, (text[:m.start()] + text[m.end():]).strip()

    stripped = text.strip()
    clean_stripped = re.sub(r"^(?:```)?(?:json|JSON)?\s*", "", stripped).rstrip("`").strip()
    if clean_stripped.startswith(("{", "[")):
        try:
            calls = _as_tool_calls(json.loads(clean_stripped))
            if calls:
                return calls, ""
        except Exception:
            pass

    m_json = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if m_json:
        try:
            calls = _as_tool_calls(json.loads(m_json.group(1).strip()))
            if calls:
                rest = (text[:m_json.start()] + text[m_json.end():]).strip()
                if re.sub(r"^(?:```)?(?:json|JSON)?\s*", "", rest).strip("`").strip() == "":
                    rest = ""
                return calls, rest
        except Exception:
            pass

    return None, text


def build_video_prompt(r: VideoRequest) -> str:
    user_prompt = r.prompt.strip()
    ar = (r.aspect_ratio or "").strip().lower()
    sz = (r.size or "").strip().lower()
    dur = r.duration or 6
    has_ref = bool(r.reference_image or r.image or r.image_url)

    is_vertical = any(k in ar or k in sz for k in ("9:16", "9/16", "portrait", "", "720x1280", "1080x1920"))

    parts = []
    if is_vertical:
        if has_ref:
            parts.append(f"（，）：9:16（9:16 vertical portrait video，720x1280，，，， {dur} ）：{user_prompt}")
        else:
            parts.append(f"（，）：9:16（9:16 vertical portrait video，720x1280，，，， {dur} ）：{user_prompt}")
    elif any(k in ar or k in sz for k in ("16:9", "16/9", "landscape", "", "1280x720", "1920x1080")):
        if has_ref:
            parts.append(f"（，）：16:9（16:9 widescreen landscape video，， {dur} ）：{user_prompt}")
        else:
            parts.append(f"（，）：16:9（16:9 widescreen landscape video， {dur} ）：{user_prompt}")
    else:
        if has_ref:
            parts.append(f"（，）：（， {dur} ）：{user_prompt}")
        else:
            parts.append(f"（，）：（ {dur} ）：{user_prompt}")

    if r.resolution:
        parts.append(f"：{r.resolution}")
    if r.extra:
        parts.append(r.extra)
    return "，".join(parts)


def media_url(name: str) -> str:
    """。

     public_base ** URL** —— OpenAI （
    ） data[].url ，
    ， 404。public_base 。
    """
    base = _public_base()
    return f"{base}/v1/media/{name}" if base else f"/v1/media/{name}"


# Muse Studio configuration and operations
def parse_cookie_text(text: str) -> dict[str, str]:
    """ `a=1; b=2` / JSON / Set-Cookie  dict。"""
    text = (text or "").strip()
    if not text:
        return {}
    if text.startswith("{"):
        import json
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                return {str(k): str(v) for k, v in obj.items()}
        except Exception:  # noqa: BLE001
            pass
    out: dict[str, str] = {}
    for part in re.split(r"[;\n]+", text):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        if k:
            out[k] = v.strip()
    return out


def parse_batch(text: str) -> list[tuple[str, dict]]:
    """： ` | cookie`，。"""
    out: list[tuple[str, dict]] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        label = ""
        body = line
        if "|" in line:
            head, tail = line.split("|", 1)
            if "=" not in head:          # `|`  cookie 
                label, body = head.strip(), tail.strip()
        cookies = parse_cookie_text(body)
        if cookies:
            out.append((label, cookies))
    return out


# Muse Studio configuration and operations
def _sync_cookies(acc_id: str) -> dict:
    """ cookie 。

    ：** cookie  expires **（hatch_vml 
     2 ），
    cookie（_fbp / wd / dpr ），。

    ：**** —— ，
    ，。
    """
    try:
        live = engine.read_cookies()
        if not live:
            return {"synced": 0}
        acc = store.get_account(acc_id)
        if not acc:
            return {"synced": 0}
        cur = dict(acc.get("cookies") or {})
        new_vals = {k: v["value"] for k, v in live.items() if v.get("value")}
# Muse Studio configuration and operations
# Muse Studio configuration and operations
        exps = dict(acc.get("cookies_exp") or {})
        exps.update({k: v["expires"] for k, v in live.items()
                     if _pos(v.get("expires"))})
        changed = sum(1 for k, v in new_vals.items() if cur.get(k) != v)
        store.update_account(acc_id, cookies={**cur, **new_vals},
                             cookies_exp=exps, synced_at=int(time.time()))
        updated = store.get_account(acc_id) or {}
        return {"synced": len(new_vals), "changed": changed,
                "expires_at": updated.get("expires_at")}
    except Exception as exc:  # noqa: BLE001
        log.warning("cookie Status（Status）: %s", exc)
        return {"synced": 0, "error": str(exc)[:200]}


def _pos(v) -> bool:
    try:
        return int(v) > 0
    except (TypeError, ValueError):
        return False


def _run_generation(prompt: str, kind: str, timeout: int,
                    account_id: str | None = None, on_progress=None,
                    reference_image: str | None = None) -> tuple[dict, str | None]:
    # Browser ownership covers account selection, retry and cleanup, not just generate().
    deadline = time.monotonic() + max(1, timeout)
    if not GEN_LOCK.acquire(timeout=max(1, timeout)):
        raise MuseGenerationError("，")
    try:
        return _run_generation_locked(prompt, kind, timeout, account_id,
                                      on_progress, reference_image, deadline=deadline)
    finally:
        GEN_LOCK.release()


def _run_generation_locked(prompt: str, kind: str, timeout: int,
                    account_id: str | None = None, on_progress=None,
                    reference_image: str | None = None, deadline=None) -> tuple[dict, str | None]:
    acc = store.get_account(account_id) if account_id else None
    if acc and not acc.get("enabled", True):
        acc = None
    if not acc:
        acc = store.pick_account(rotate=True, preferred_id=getattr(engine, "current_acc_id", None))
    if not acc:
        raise MuseAuthError("Không có tài khoản khả dụng， cookie")

    last_exc = None
    cur_acc = acc
    for attempt in range(2):
        if deadline is not None and time.monotonic() >= deadline:
            raise MuseGenerationError("，")
        if attempt > 0:
            if last_exc and "，" in str(last_exc):
                break
            alt = store.pick_account(rotate=True, force_rotate=True, exclude_id=cur_acc["id"])
            if not alt or alt["id"] == cur_acc["id"]:
                break
            cur_acc = alt
            log.info("【Status/Status】Status %s (%s) Status...", cur_acc.get("label"), cur_acc["id"])
        try:
            refreshed = _renew_and_persist(cur_acc["id"], wake_vm=True, force=(attempt > 0))
            if refreshed:
                cur_acc = refreshed
            engine.start()
            remaining = int(deadline - time.monotonic()) if deadline is not None else timeout
            if remaining <= 0:
                raise MuseGenerationError("，")
            res = engine.generate(cur_acc["cookies"], prompt, expect=kind,
                                  timeout=remaining, expires=cur_acc.get("cookies_exp"),
                                  account_id=cur_acc["id"], on_progress=on_progress,
                                  reference_image=reference_image)
            store.mark(cur_acc["id"], True, "")
            _sync_cookies(cur_acc["id"])
            return res, cur_acc["id"]
        except MuseAuthError as exc:
            last_exc = exc
            store.mark(cur_acc["id"], False, str(exc))
            engine.stop()
        except MuseGenerationError as exc:
            last_exc = exc
            store.mark(cur_acc["id"], True, f": {str(exc)[:60]}")
            try:
                engine.reset_thread()
            except Exception:
                pass
        except Exception as exc:  # noqa: BLE001
            engine.stop()
            last_exc = MuseGenerationError(f": {exc}")
    raise last_exc


# Muse Studio configuration and operations
@app.get("/healthz")
def healthz():
    return {"status": "ok", "time": int(time.time())}


@app.get("/readyz")
def readyz():
    accs = [a for a in store.list_accounts() if a.get("enabled", True)]
    return {"status": "ready" if accs else "no_account",
            "accounts": len(accs),
            "browser_running": bool(engine.proc and engine.proc.poll() is None)}


@app.get("/v1/models")
def models(_=Depends(auth)):
    return {"object": "list", "data": MODELS}


# Muse Studio configuration and operations
def _image_response(req: ImageRequest, res: dict) -> dict:
    item = {"revised_prompt": req.prompt, "url": media_url(res["filename"]),
            "size": req.size or "auto", "kind": res["kind"], "bytes": res["size"]}
    if req.response_format == "b64_json":
        fpath = res.get("path") or os.path.join(CFG.media_dir, res["filename"])
        with open(fpath, "rb") as f:
            item["b64_json"] = base64.b64encode(f.read()).decode()
        item.pop("url", None)
    return {"created": int(time.time()), "data": [item]}


def _queue_image(req: ImageRequest, prompt: str, reference_image: str | None,
                 idempotency_key: str | None = None):
    """Opt-in polling avoids reverse-proxy timeouts; no generation is repeated by polling."""
    if idempotency_key and len(idempotency_key) > 256:
        raise HTTPException(400, "Idempotency-Key too long")
    key_hash = hashlib.sha256(idempotency_key.encode()).hexdigest() if idempotency_key else None
    request_hash = hashlib.sha256(json.dumps(
        {"request": req.model_dump(by_alias=True), "reference": reference_image},
        sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    with IMAGE_TASK_LOCK:
        tasks = list(store.tasks.values())
        if key_hash:
            for existing in tasks:
                if existing.get("image_request_key") == key_hash:
                    if existing.get("image_request_hash") != request_hash:
                        raise HTTPException(409, "Idempotency-Key reused with different request")
                    return JSONResponse(status_code=202, content={
                        "id": existing["id"], "task_id": existing["id"],
                        "object": "image.task", "status": existing["status"],
                        "progress": existing.get("progress", 0),
                        "created_at": existing["created_at"]})
        # ponytail: one Chromium worker; cap admission instead of adding a broker.
        if sum(t.get("kind") == "image" and t.get("status") in ("queued", "processing")
               for t in tasks) >= 8:
            raise HTTPException(429, "Image queue is full; retry later")
        task = store.create_task("image", req.prompt)
        tid = task["id"]
        store.update_task(tid, api_prompt=prompt, size=req.size,
                          response_format=req.response_format, progress=0,
                          image_request_key=key_hash, image_request_hash=request_hash)

    def worker():
        t0 = time.time()
        store.update_task(tid, status="processing", progress=5)
        try:
            res, acc_id = _run_generation(
                prompt, "image", req.timeout or CFG.image_timeout,
                reference_image=reference_image,
                on_progress=lambda p: store.update_task(tid, progress=p))
            # Store only media metadata, not large base64 payloads or reference credentials.
            store.update_task(tid, status="completed", progress=100, account=acc_id,
                              elapsed=round(time.time() - t0, 1),
                              url=media_url(res["filename"]),
                              result={**{k: res[k] for k in ("filename", "size", "kind")},
                                      "url": media_url(res["filename"])})
        except Exception as exc:  # noqa: BLE001
            store.update_task(tid, status="failed", error=str(exc),
                              elapsed=round(time.time() - t0, 1))

    threading.Thread(target=worker, daemon=True).start()
    return JSONResponse(status_code=202, content={
        "id": tid, "task_id": tid, "object": "image.task", "status": "queued",
        "progress": 0, "created_at": task["created_at"]})


@app.post("/v1/images/tasks")
def create_image_task(req: ImageRequest,
                      idempotency_key: str | None = Header(default=None), _=Depends(auth)):
    ref_img = req.reference_image or req.image
    if isinstance(ref_img, dict):
        ref_img = ref_img.get("url") or ref_img.get("b64_json")
    if not ref_img and req.images:
        first = req.images[0]
        ref_img = first.get("image_url") or first.get("url") if isinstance(first, dict) else first
    return _queue_image(req, build_image_prompt(req), ref_img, idempotency_key)


@app.get("/v1/images/tasks/{task_id}")
def get_image_task(task_id: str, _=Depends(auth)):
    task = store.get_task(task_id)
    if not task or task.get("kind") != "image":
        raise HTTPException(404, "image task Request error")
    out = dict(task)
    if out.get("status") == "completed":
        req = ImageRequest(prompt=out["prompt"], size=out.get("size"),
                           response_format=out.get("response_format") or "url")
        out.update(_image_response(req, out["result"]))
    return out


@app.post("/v1/images/generations")
async def images_generations(req: ImageRequest, _=Depends(auth)):
    ref_img = req.reference_image or req.image
    if isinstance(ref_img, dict):
        ref_img = ref_img.get("url") or ref_img.get("b64_json")
    if not ref_img and req.images and isinstance(req.images, list):
        first = req.images[0]
        ref_img = first.get("image_url") or first.get("url") if isinstance(first, dict) else first

    prompt = build_image_prompt(req)
    timeout = req.timeout or CFG.image_timeout
    if req.async_:
        return _queue_image(req, prompt, ref_img)
    try:
        res, _acc = await asyncio.to_thread(_run_generation, prompt, "image", timeout, reference_image=ref_img)
    except MuseAuthError as exc:
        raise HTTPException(401, str(exc)) from exc
    except MuseGenerationError as exc:
        raise HTTPException(502, str(exc)) from exc
    return _image_response(req, res)


@app.post("/v1/images/edits")
async def images_edits(request: Request, _=Depends(auth)):
    """OpenAI /， multipart/form-data  application/json。"""
    content_type = request.headers.get("content-type", "").lower()
    prompt = ""
    model = "muse-image"
    size = None
    aspect_ratio = None
    response_format = "url"
    timeout = None
    ref_image_data = None
    async_mode = False

    if "multipart/form-data" in content_type:
        form = await request.form()
        async_mode = form.get("async", False)
        prompt = form.get("prompt") or ""
        model = form.get("model") or "muse-image"
        size = form.get("size")
        aspect_ratio = form.get("aspect_ratio")
        response_format = form.get("response_format") or "url"
        timeout_val = form.get("timeout")
        if timeout_val:
            try:
                timeout = int(timeout_val)
            except ValueError:
                pass
        img_field = form.get("image")
        if img_field and hasattr(img_field, "read"):
            content = await img_field.read()
            ref_mime = getattr(img_field, "content_type", "image/png") or "image/png"
            ref_image_data = f"data:{ref_mime};base64,{base64.b64encode(content).decode('ascii')}"
        elif isinstance(img_field, str):
            ref_image_data = img_field
    else:
        body = await request.json()
        async_mode = body.get("async", False)
        prompt = body.get("prompt") or ""
        model = body.get("model") or "muse-image"
        size = body.get("size")
        aspect_ratio = body.get("aspect_ratio")
        response_format = body.get("response_format") or "url"
        timeout = body.get("timeout")
        img_val = body.get("image")
        if isinstance(img_val, dict):
            ref_image_data = img_val.get("url") or img_val.get("b64_json")
        elif isinstance(img_val, str):
            ref_image_data = img_val
        if not ref_image_data and body.get("images") and isinstance(body.get("images"), list):
            first = body["images"][0]
            if isinstance(first, dict):
                ref_image_data = first.get("image_url") or first.get("url")
            elif isinstance(first, str):
                ref_image_data = first
        if not ref_image_data:
            ref_image_data = body.get("reference_image") or body.get("image_url")

    if not prompt:
        prompt = ""

    req_obj = ImageRequest(
        prompt=prompt,
        model=model,
        size=size,
        aspect_ratio=aspect_ratio,
        response_format=response_format,
        timeout=timeout,
        reference_image=ref_image_data,
        **{"async": async_mode}
    )
    full_prompt = build_image_prompt(req_obj)
    gen_timeout = timeout or CFG.image_timeout
    if req_obj.async_:
        return _queue_image(req_obj, full_prompt, ref_image_data)
    try:
        res, _acc = await asyncio.to_thread(_run_generation, full_prompt, "image", gen_timeout, reference_image=ref_image_data)
    except MuseAuthError as exc:
        raise HTTPException(401, str(exc)) from exc
    except MuseGenerationError as exc:
        raise HTTPException(502, str(exc)) from exc

    return _image_response(req_obj, res)


# Muse Studio configuration and operations
@app.post("/v1/videos")
@app.post("/v1/videos/generations")
async def create_video(req: VideoRequest, _=Depends(auth)):
    ref_img = None
    if req.reference_image:
        ref_img = req.reference_image
    elif req.image_url:
        ref_img = req.image_url if isinstance(req.image_url, str) else (req.image_url.get("url") if isinstance(req.image_url, dict) else None)
    elif req.image:
        ref_img = req.image.get("url") if isinstance(req.image, dict) else req.image

    prompt = build_video_prompt(req)
    timeout = req.timeout or CFG.video_timeout
    task = store.create_task("video", req.prompt)
    store.update_task(task["id"], api_prompt=prompt)

    store.update_task(task["id"], progress=10)

    def worker():
        store.update_task(task["id"], status="processing", progress=15)
        t0 = time.time()
        try:
            def prog_cb(p):
                store.update_task(task["id"], progress=p)
            res, acc_id = _run_generation(prompt, "video", timeout, on_progress=prog_cb, reference_image=ref_img)
            vurl = media_url(res["filename"])
            store.update_task(task["id"], status="completed", progress=100, account=acc_id,
                              elapsed=round(time.time() - t0, 1),
                              url=vurl,
                              video={"url": vurl},
                              result={"url": vurl,
                                      "filename": res["filename"],
                                      "bytes": res["size"], "kind": res["kind"]})
        except Exception as exc:  # noqa: BLE001
            store.update_task(task["id"], status="failed",
                              elapsed=round(time.time() - t0, 1), error=str(exc))

    threading.Thread(target=worker, daemon=True).start()
    return {"id": task["id"], "task_id": task["id"], "object": "video.task", "status": "queued",
            "progress": 10, "created_at": task["created_at"]}


@app.get("/v1/videos/{task_id}")
@app.get("/v1/videos/generations/{task_id}")
def get_video(task_id: str, _=Depends(auth)):
    t = store.get_task(task_id)
    if not t:
        raise HTTPException(404, "task Request error")
    out = dict(t)
    status = out.get("status")
    if status in ("succeeded", "success", "done"):
        out["status"] = "completed"
    if out.get("status") == "completed":
        out["progress"] = 100
    elif out.get("status") == "processing":
        elapsed = time.time() - out.get("created_at", time.time())
        calc_prog = min(92, int(20 + elapsed * 1.1))
        out["progress"] = max(out.get("progress", 0) or 0, calc_prog)
    vurl = out.get("url")
    if not vurl and isinstance(out.get("result"), dict):
        vurl = out["result"].get("url")
    if vurl:
        out["url"] = vurl
        if "video" not in out:
            out["video"] = {"url": vurl}
    return out


# Muse Studio configuration and operations
def _sse(obj: dict) -> str:
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


def _chat_chunk(cid: str, created: int, model: str, delta: dict,
                finish: str | None = None) -> dict:
    return {"id": cid, "object": "chat.completion.chunk", "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}


def _want_usage(stream_options) -> bool:
    """（LangChain、 SDK / ）
    `stream_options.include_usage=true`， [DONE] 
    `choices: []` + `usage` 。 usage 。"""
    if isinstance(stream_options, dict):
        return bool(stream_options.get("include_usage"))
    return False


def _pace_text(text: str, chunk_size: int = 2, delay: float = 0.012):
    """ LLM  Token。
    （<= 3 ），，；
    （ DOM ）， chunk_size  delay 。
    """
    if not text:
        return
    if len(text) <= 3 or delay <= 0:
        yield text
        return
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
        if i + chunk_size < len(text):
            time.sleep(delay)


_SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest, _=Depends(auth)):
    """OpenAI  —— 。

    ：muse.ai **** agent，，
    （ Koda， Muse ）。
    `model` ，。

     `tools` ，【】 JSON 
    `tool_calls`（muse.ai  function calling，）。

    /， `GEN_LOCK` 。
    """
    prompt = build_chat_prompt(req.messages) or (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(400, "messages Request error")

# Muse Studio configuration and operations
# Muse Studio configuration and operations
    tool_note = build_tools_prompt(req.tools) if CFG.tool_protocol else ""
    if tool_note:
# Muse Studio configuration and operations
# Muse Studio configuration and operations
        prompt = prompt + "\n\n" + tool_note

    model = resolve_model(req.model, default="muse-spark")
    timeout = int(req.timeout or CFG.chat_timeout)
    acc = store.pick_account(rotate=True, preferred_id=getattr(engine, "current_acc_id", None))
    if not acc:
        raise HTTPException(400, "Request error，Request error cookie")

    cid = "chatcmpl-" + uuid.uuid4().hex[:24]
    created = int(time.time())
    acc_id = acc["id"]
    cookies = acc["cookies"]
    expires = acc.get("cookies_exp")

    def tool_call_deltas(calls: list[dict]) -> list[list[dict]]:
        """ OpenAI ： id/name， arguments 。"""
        head = [{"index": i, "id": c["id"], "type": "function",
                 "function": {"name": c["function"]["name"], "arguments": ""}}
                for i, c in enumerate(calls)]
        body = [{"index": i, "function": {"arguments": c["function"]["arguments"]}}
                for i, c in enumerate(calls)]
        return [head, body]

    if req.stream:
        def sync_stream():
            try:
# Muse Studio configuration and operations
                yield _sse(_chat_chunk(cid, created, model, {"role": "assistant"}))

                stream_gen = safe_chat_stream(cookies, prompt, expires, timeout, account_id=acc_id)
                if not tool_note:
                    for chunk in stream_gen:
                        for piece in _pace_text(chunk):
                            yield _sse(_chat_chunk(cid, created, model, {"content": piece}))
                    yield _sse(_chat_chunk(cid, created, model, {}, finish="stop"))
                else:
                    buf, mode = "", None
                    for chunk in stream_gen:
                        if mode == "text":
                            for piece in _pace_text(chunk):
                                yield _sse(_chat_chunk(cid, created, model, {"content": piece}))
                            continue
                        buf += chunk
                        if mode is None:
                            head = buf.lstrip()
                            if len(head) >= 2:
                                if head[0] in "{[" or head.startswith("```"):
                                    mode = "maybe_tool"
                                else:
                                    mode = "text"
                                    for piece in _pace_text(buf):
                                        yield _sse(_chat_chunk(cid, created, model, {"content": piece}))
                                    buf = ""
                    if mode == "text":
                        yield _sse(_chat_chunk(cid, created, model, {}, finish="stop"))
                    else:
                        calls, rest = parse_tool_calls(buf)
                        if calls:
                            if rest:
                                for piece in _pace_text(rest):
                                    yield _sse(_chat_chunk(cid, created, model, {"content": piece}))
                            for piece in tool_call_deltas(calls):
                                yield _sse(_chat_chunk(cid, created, model, {"tool_calls": piece}))
                            yield _sse(_chat_chunk(cid, created, model, {}, finish="tool_calls"))
                        else:
                            if buf:
                                for piece in _pace_text(buf):
                                    yield _sse(_chat_chunk(cid, created, model, {"content": piece}))
                            yield _sse(_chat_chunk(cid, created, model, {}, finish="stop"))
                if _want_usage(req.stream_options):
                    yield _sse({"id": cid, "object": "chat.completion.chunk",
                                "created": created, "model": model,
                                "choices": [],
                                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}})
                yield "data: [DONE]\n\n"
                store.mark(acc_id, True, "")
            except MuseAuthError as exc:
                store.mark(acc_id, False, str(exc))
                yield _sse({"error": {"message": str(exc), "type": "auth_error", "code": 401}})
            except MuseGenerationError as exc:
                store.mark(acc_id, True, f": {str(exc)[:60]}")
                try:
                    engine.reset_thread()
                except Exception:
                    pass
                yield _sse({"error": {"message": str(exc), "type": "server_error", "code": 502}})
            except Exception as exc:
                yield _sse({"error": {"message": f": {exc}", "type": "server_error", "code": 500}})
        return StreamingResponse(sync_stream(), media_type="text/event-stream", headers=_SSE_HEADERS)

    def run() -> str:
        return "".join(safe_chat_stream(cookies, prompt, expires, timeout, account_id=acc_id))

    try:
        text = await asyncio.to_thread(run)
    except MuseAuthError as exc:
        raise HTTPException(401, str(exc))
    except MuseGenerationError as exc:
        raise HTTPException(502, str(exc))

    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    if tool_note:
        calls, rest = parse_tool_calls(text)
        if calls:
            return {"id": cid, "object": "chat.completion", "created": created,
                    "model": model,
                    "choices": [{"index": 0, "finish_reason": "tool_calls",
                                 "message": {"role": "assistant",
                                             "content": rest or None,
                                             "tool_calls": calls}}],
                    "usage": usage}
    return {"id": cid, "object": "chat.completion", "created": created,
            "model": model,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": text}}],
            "usage": usage}


def _responses_messages(req: ResponsesRequest) -> list[ChatMessage]:
    """ Responses API  instructions / input  messages。"""
    msgs: list[ChatMessage] = []
    if req.instructions:
        msgs.append(ChatMessage(role="system", content=req.instructions))
    inp = req.input
    if isinstance(inp, str):
        msgs.append(ChatMessage(role="user", content=inp))
        return msgs
    if isinstance(inp, list):
        for item in inp:
            if isinstance(item, str):
                msgs.append(ChatMessage(role="user", content=item))
                continue
            if not isinstance(item, dict):
                continue
            itype = item.get("type")
            if item.get("role"):                      # message 
                msgs.append(ChatMessage(role=item["role"],
                                        content=item.get("content")))
            elif itype == "input_text":
                msgs.append(ChatMessage(role="user", content=item.get("text")))
            elif itype == "function_call_output":
                msgs.append(ChatMessage(role="user", content="【】\n"
                                        + str(item.get("output") or "")))
            elif itype == "function_call":
                msgs.append(ChatMessage(role="assistant", content="【】"
                                        + str(item.get("name") or "")))
    return msgs


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/v1/responses")
async def responses_api(req: ResponsesRequest, _=Depends(auth)):
    """OpenAI Responses API ——  Codex 。

     Codex ： → （）。
    muse.ai  tool_calls， README。
    """
    prompt = build_chat_prompt(_responses_messages(req))
    if not prompt:
        raise HTTPException(400, "input Request error")

    model = resolve_model(req.model, default="muse-spark")
    timeout = int(req.timeout or CFG.chat_timeout)
    acc = store.pick_account(rotate=True, preferred_id=getattr(engine, "current_acc_id", None))
    if not acc:
        raise HTTPException(400, "Request error，Request error cookie")

    rid = "resp_" + uuid.uuid4().hex[:24]
    mid = "msg_" + uuid.uuid4().hex[:24]
    created = int(time.time())
    acc_id, cookies, expires = acc["id"], acc["cookies"], acc.get("cookies_exp")

    def envelope(status: str, text: str = "") -> dict:
        done = status == "completed"
        return {"id": rid, "object": "response", "created_at": created,
                "status": status, "model": model,
                "output": [{"type": "message", "id": mid, "role": "assistant",
                            "status": "completed" if done else "in_progress",
                            "content": ([{"type": "output_text", "text": text,
                                          "annotations": []}] if text else [])}],
                "usage": {"input_tokens": 0, "output_tokens": 0,
                          "total_tokens": 0}}

    if req.stream:
        def sync_stream():
            try:
                yield _sse_event("response.created", {
                    "type": "response.created",
                    "response": envelope("in_progress")})
                yield _sse_event("response.output_item.added", {
                    "type": "response.output_item.added", "output_index": 0,
                    "item": {"id": mid, "type": "message", "role": "assistant",
                             "status": "in_progress", "content": []}})
                yield _sse_event("response.content_part.added", {
                    "type": "response.content_part.added", "item_id": mid,
                    "output_index": 0, "content_index": 0,
                    "part": {"type": "output_text", "text": "",
                             "annotations": []}})
                full = ""
                for chunk in safe_chat_stream(cookies, prompt, expires, timeout, account_id=acc_id):
                    full += chunk
                    yield _sse_event("response.output_text.delta", {
                        "type": "response.output_text.delta", "item_id": mid,
                        "output_index": 0, "content_index": 0, "delta": chunk})
                yield _sse_event("response.output_text.done", {
                    "type": "response.output_text.done", "item_id": mid,
                    "output_index": 0, "content_index": 0, "text": full})
                yield _sse_event("response.output_item.done", {
                    "type": "response.output_item.done", "output_index": 0,
                    "item": {"id": mid, "type": "message", "role": "assistant",
                             "status": "completed",
                             "content": [{"type": "output_text", "text": full,
                                          "annotations": []}]}})
                yield _sse_event("response.completed", {
                    "type": "response.completed",
                    "response": envelope("completed", full)})
            except Exception as exc:  # noqa: BLE001
                log.warning("responses Status: %s", exc)
                yield _sse_event("response.failed", {
                    "type": "response.failed",
                    "response": envelope("failed")})
        return StreamingResponse(sync_stream(), media_type="text/event-stream", headers=_SSE_HEADERS)

    def run() -> str:
        return "".join(safe_chat_stream(cookies, prompt, expires, timeout, account_id=acc_id))

    try:
        text = await asyncio.to_thread(run)
    except MuseAuthError as exc:
        raise HTTPException(401, str(exc))
    except MuseGenerationError as exc:
        raise HTTPException(502, str(exc))

    return envelope("completed", text)


@app.get("/v1/media/{name}")
def get_media(name: str):
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "Request error")
    p = os.path.join(CFG.media_dir, name)
    if not os.path.isfile(p):
        raise HTTPException(404, "Request error")
    return FileResponse(p)


# Muse Studio configuration and operations
@app.get("/admin/status")
def admin_status(_=Depends(auth)):
    base = _public_base()
    return {
        "accounts": store.list_accounts(),
        "stats": store.stats(),
        "tasks": store.list_tasks(20),
        "media_count": len(os.listdir(CFG.media_dir))
        if os.path.isdir(CFG.media_dir) else 0,
        "browser_running": bool(engine.proc and engine.proc.poll() is None),
        "essential_cookies": list(ESSENTIAL_COOKIES),
        "base_url": f"{base}/v1" if base else "",
        "config": {"site": CFG.site_url, "cdp_port": CFG.cdp_port,
                   "image_timeout": CFG.image_timeout,
                   "video_timeout": CFG.video_timeout,
                   "host": CFG.host, "port": CFG.port,
                   "public_base": base},
    }


# Muse Studio configuration and operations
@app.get("/admin/accounts")
def list_accounts(_=Depends(auth)):
    return {"accounts": store.list_accounts(), "stats": store.stats()}


@app.post("/admin/accounts")
def add_account(req: AccountRequest, _=Depends(auth)):
    added: list[dict] = []
    seen: list[dict] = []          #  cookie，

    if req.batch:
        for label, cookies in parse_batch(req.batch):
            acc = store.add_account(cookies, label)
            seen.append(cookies)
            added.append({"id": acc["id"], "label": acc["label"],
                          "cookie_count": len(cookies),
                          "expires_at": acc.get("expires_at")})

    cookies = dict(req.cookies)
    if req.cookie_header:
        cookies.update(parse_cookie_text(req.cookie_header))
    if cookies:
        acc = store.add_account(cookies, req.label, cookies_exp=req.expires)
        seen.append(cookies)
        added.append({"id": acc["id"], "label": acc["label"],
                      "cookie_count": len(cookies),
                      "expires_at": acc.get("expires_at")})

    if not added:
        raise HTTPException(400, "Request error cookie，Request error")

# Muse Studio configuration and operations
    missing = [n for n in ESSENTIAL_COOKIES
               if not any(n in c for c in seen)]
    return {"added": added, "count": len(added),
            "essential_missing": missing,
            "warning": (f"Thiếu cookie cốt lõi：{', '.join(missing)}，tài khoản này có thể không tạo được"
                        if missing else "")}


@app.patch("/admin/accounts/{aid}")
def patch_account(aid: str, req: AccountPatch, _=Depends(auth)):
    acc = store.update_account(aid, label=req.label, enabled=req.enabled)
    if not acc:
        raise HTTPException(404, "Request error")
    return {k: v for k, v in acc.items() if k != "cookies"} | {
        "cookie_count": len(acc.get("cookies", {}))}


@app.delete("/admin/accounts/{aid}")
def del_account(aid: str, _=Depends(auth)):
    ok = store.delete_account(aid)
    if not ok:
        raise HTTPException(404, "Request error")
    return {"deleted": True, "id": aid}


@app.post("/admin/accounts/{aid}/test")
async def test_account(aid: str, _=Depends(auth)):
    """ muse.ai  cookie 。"""
    acc = store.get_account(aid)
    if not acc:
        raise HTTPException(404, "Request error")
    if not acc.get("cookies"):
        raise HTTPException(400, "Request error cookie")

    def _probe():
        with GEN_LOCK:
            try:
                engine.start()
                engine.refresh(acc["cookies"], acc.get("cookies_exp"))
                synced = _sync_cookies(aid)
                quota = None
                try:  # ；
                    quota = engine.quota(acc["cookies"],
                                         acc.get("cookies_exp"))
                    quota["checked_at"] = int(time.time())
                    store.update_account(aid, quota=quota)
                except Exception:  # noqa: BLE001
                    quota = None
                store.mark(aid, True, "Phiên hoạt động")
                return {"ok": True, "message": "Phiên hoạt động，",
                        "synced": synced, "quota": quota}
            except MuseAuthError as exc:
                store.mark(aid, False, str(exc)[:200])
                return {"ok": False, "message": str(exc)[:200]}
            except Exception as exc:  # noqa: BLE001
                store.touch_keepalive(aid, None, f"Chưa xác minh được phiên: {str(exc)[:200]}")
                return {"ok": False, "message": str(exc)[:200]}

    res = await asyncio.to_thread(_probe)
    if not res["ok"]:
        return JSONResponse(res, status_code=200)
    return res


@app.post("/admin/accounts/{aid}/relogin")
async def relogin_account(aid: str, _=Depends(auth)):
    return await test_account(aid, _)


@app.post("/admin/accounts/{aid}/cookies")
def update_cookies(aid: str, payload: dict = Body(...), _=Depends(auth)):
    """ cookie（ cookie）。"""
    cookies = dict(payload.get("cookies") or {})
    if payload.get("cookie_header"):
        cookies.update(parse_cookie_text(payload["cookie_header"]))
    if not cookies:
        raise HTTPException(400, "Request error cookie")
    exp = {k: int(v) for k, v in (payload.get("expires") or {}).items()
           if _pos(v)}
# Muse Studio configuration and operations
# Muse Studio configuration and operations
    acc = store.update_account(aid, cookies=cookies, ok=None,
                               note=" cookie",
                               expiry_anchor=int(time.time()),
                               cookies_exp=exp or None)
    if not acc:
        raise HTTPException(404, "Request error")
    return {"ok": True, "id": aid, "cookie_count": len(cookies),
            "expires_at": acc.get("expires_at")}


# Muse Studio configuration and operations
# Mở một cửa sổ trình duyệt thật trên MÁY CHỦ (phù hợp chạy local như start.bat),
# người dùng đăng nhập muse.ai trong cửa sổ đó, backend tự đọc cookie qua CDP
# (kể cả httpOnly) và nhập vào account pool. Không cần F12 copy tay.
_AUTOX: dict[str, dict] = {}
_AUTOX_LOCK = threading.Lock()


def _autox_free_port() -> int:
    s = _socket_mod.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _autox_find_chrome() -> str | None:
    cands = []
    if getattr(CFG, "chromium", ""):
        cands.append(CFG.chromium)
    cands += [
        "google-chrome", "chrome", "chromium", "chromium-browser",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in cands:
        if c and (os.path.isfile(c) or shutil.which(c)):
            return c
    return None


def _autox_read_cookies(port: int) -> dict:
    """Đọc cookie muse.ai qua CDP (lấy được cả httpOnly). Trả về {name: {value, expires}}."""
    from cdp import CDP as _CDP, http_json as _http_json
    targets = _http_json(f"http://127.0.0.1:{port}/json/list", timeout=5)
    out: dict[str, dict] = {}
    for tg in targets or []:
        ws_url = tg.get("webSocketDebuggerUrl")
        if not ws_url:
            continue
        try:
            cdp = _CDP(ws_url, timeout=5)
            # 1. Thử lấy tất cả cookie của browser context
            try:
                r_all = cdp.send("Network.getAllCookies", {})
                for ck in (r_all.get("result", {}).get("cookies", []) or []):
                    name = ck.get("name")
                    val = ck.get("value")
                    if name and val:
                        out[name] = {"value": val, "expires": int(ck.get("expires") or 0)}
            except Exception:
                pass

            # 2. Thử Storage.getCookies
            try:
                r_st = cdp.send("Storage.getCookies", {})
                for ck in (r_st.get("result", {}).get("cookies", []) or []):
                    name = ck.get("name")
                    val = ck.get("value")
                    if name and val:
                        out[name] = {"value": val, "expires": int(ck.get("expires") or 0)}
            except Exception:
                pass

            cdp.close()
            if "hatch_sess" in out or "hatch_vml" in out:
                break
        except Exception:
            pass
    return out


def _autox_worker(sid: str, timeout: int):
    sess = _AUTOX.get(sid)
    if not sess:
        return
    proc = sess.get("proc")
    port = sess["port"]
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            if sess.get("status") != "waiting":
                return
            if proc.poll() is not None:
                sess["status"] = "error"
                sess["error"] = "Trình duyệt đã bị đóng trước khi đăng nhập xong."
                return
            try:
                got = _autox_read_cookies(port)
            except Exception:
                time.sleep(3)
                continue
            have = [n for n in ESSENTIAL_COOKIES if got.get(n, {}).get("value")]
            sess["have"] = have
            # Muse.ai web session: chỉ cần có hatch_sess (hoặc hatch_vml) là đã đăng nhập thành công
            # Không bắt buộc phải có đủ 4 cookie (hatch_native_auth_device thường chỉ có trên app native)
            is_logged_in = bool(got.get("hatch_sess", {}).get("value") or got.get("hatch_vml", {}).get("value"))
            if is_logged_in:
                cookies = {n: info["value"] for n, info in got.items() if info.get("value")}
                exp = {n: info["expires"] for n, info in got.items() if info.get("expires", 0) > 0}
                acc = store.add_account(cookies, sess.get("label") or "autox", cookies_exp=exp)
                sess["status"] = "done"
                sess["account_id"] = acc["id"]
                return
            time.sleep(1)
        sess["status"] = "expired"
        sess["error"] = "Hết thời gian chờ đăng nhập."
    finally:
        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception:
            pass
        # dọn profile tạm
        try:
            if os.path.isdir(sess.get("profile") or ""):
                shutil.rmtree(sess.get("profile") or "", ignore_errors=True)
        except Exception:
            pass


@app.post("/admin/accounts/auto-extract/start")
def autox_start(payload: dict = Body(default={}), _=Depends(auth)):
    """Mở cửa sổ trình duyệt để đăng nhập muse.ai, sau đó tự trích xuất cookie."""
    chrome = _autox_find_chrome()
    if not chrome:
        raise HTTPException(502, "Không tìm thấy Chrome/Edge trên máy chủ. Hãy cài đặt trình duyệt hoặc dùng cách copy cookie thủ công.")
    label = (payload.get("label") or "").strip() or ("studio-" + time.strftime("%m%d-%H%M"))
    try:
        timeout = int(payload.get("timeout") or 300)
    except (TypeError, ValueError):
        timeout = 300
    timeout = max(60, min(timeout, 900))
    port = _autox_free_port()
    profile = os.path.join(tempfile.gettempdir(), f"musestudio-autox-{uuid.uuid4().hex[:8]}")
    os.makedirs(profile, exist_ok=True)
    cmd = [chrome, f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
           "--remote-allow-origins=*",
           "--no-first-run", "--no-default-browser-check", "--no-sandbox",
           "--disable-gpu", "--new-window", "https://muse.ai/"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        raise HTTPException(502, f"Không mở được trình duyệt: {exc}")
    ws_ok = False
    for _ in range(30):
        if proc.poll() is not None:
            break
        try:
            from cdp import http_json as _hj
            v = _hj(f"http://127.0.0.1:{port}/json/version", timeout=2)
            if v and "webSocketDebuggerUrl" in v:
                ws_ok = True
                break
        except Exception:
            pass
        time.sleep(1)
    if not ws_ok:
        try:
            proc.terminate()
        except Exception:
            pass
        raise HTTPException(502, "Trình duyệt không phản hồi (máy chủ có thể không có màn hình). Hãy dùng cách copy cookie thủ công hoặc extension.")
    sid = "ax_" + uuid.uuid4().hex[:12]
    sess = {"sid": sid, "status": "waiting", "have": [], "label": label,
            "port": port, "proc": proc, "profile": profile,
            "created_at": int(time.time()), "account_id": None, "error": ""}
    with _AUTOX_LOCK:
        _AUTOX[sid] = sess
        # chỉ giữ 20 phiên gần nhất
        if len(_AUTOX) > 20:
            for k in sorted(_AUTOX, key=lambda x: _AUTOX[x].get("created_at", 0))[:-20]:
                _AUTOX.pop(k, None)
    threading.Thread(target=_autox_worker, args=(sid, timeout), daemon=True).start()
    return {"sid": sid, "status": "waiting", "label": label, "timeout": timeout}


@app.get("/admin/accounts/auto-extract/{sid}")
def autox_status(sid: str, _=Depends(auth)):
    sess = _AUTOX.get(sid)
    if not sess:
        raise HTTPException(404, "Phiên trích xuất không tồn tại")
    return {"sid": sid, "status": sess["status"], "have": sess.get("have", []),
            "need": list(ESSENTIAL_COOKIES), "label": sess.get("label"),
            "account_id": sess.get("account_id"), "error": sess.get("error", "")}


@app.post("/admin/accounts/auto-extract/{sid}/cancel")
def autox_cancel(sid: str, _=Depends(auth)):
    sess = _AUTOX.get(sid)
    if not sess:
        raise HTTPException(404, "Phiên trích xuất không tồn tại")
    if sess["status"] == "waiting":
        sess["status"] = "cancelled"
    proc = sess.get("proc")
    try:
        if proc and proc.poll() is None:
            proc.terminate()
    except Exception:
        pass
    return {"ok": True, "status": sess["status"]}


@app.post("/admin/relogin")
def relogin(_=Depends(auth)):
    acc = store.pick_account(rotate=True)
    if not acc:
        raise HTTPException(400, "Request error")
    try:
        engine.start()
        engine.refresh(acc["cookies"], acc.get("cookies_exp"))
        return {"ok": True, "account": acc["id"]}
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=502)


# Muse Studio configuration and operations
@app.post("/admin/accounts/{aid}/quota")
async def query_quota(aid: str, _=Depends(auth)):
    """ muse.ai  Settings （），。

    ：{"plan":"Free plan","weekly_reset":"Sep 30",
             "weekly_used_pct":1,"extra_left":"2B tokens left",
             "extra_used_pct":0,"extra_expires":"never"}
    """
    acc = store.get_account(aid)
    if not acc:
        raise HTTPException(404, "Request error")
    if not acc.get("cookies"):
        raise HTTPException(400, "Request error cookie")

    def _probe():
        with GEN_LOCK:
            engine.start()
            q = engine.quota(acc["cookies"], acc.get("cookies_exp"))
            q["checked_at"] = int(time.time())
            store.update_account(aid, quota=q)
            return q

    try:
        return await asyncio.to_thread(_probe)
    except MuseAuthError as exc:
        store.mark(aid, False, str(exc)[:200])
        raise HTTPException(401, str(exc)) from exc
    except MuseGenerationError as exc:
        raise HTTPException(502, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Request error: {exc}") from exc


@app.post("/admin/quota")
async def query_any_quota(_=Depends(auth)):
    """（ muse.ai 
    ；）。"""
    acc = store.pick_account(rotate=True)
    if not acc:
        raise HTTPException(400, "Request error")
    return await query_quota(acc["id"], _)


# Muse Studio configuration and operations
def _public_base() -> str:
    return (CFG.public_base or "").rstrip("/")


@app.get("/admin/apikey")
def get_apikey(_=Depends(auth)):
    base = _public_base()
    base_url = f"{base}/v1" if base else "/v1"
    return {"api_key": CFG.api_key, "base_url": base_url,
            "models_url": f"{base}/v1/models" if base else "/v1/models",
            "media_url": f"{base}/v1/media/{{name}}" if base else "/v1/media/{name}"}


# ------------------------- Quản lý nhiều Client API Keys -------------------------

@app.get("/admin/apikeys")
def list_client_apikeys(_=Depends(auth)):
    """Lấy danh sách tất cả API Key được cấp cho client/công cụ ngoài."""
    keys = _load_client_keys()
    base = _public_base()
    base_url = f"{base}/v1" if base else "/v1"
    return {
        "master_key": CFG.api_key,
        "base_url": base_url,
        "keys": keys
    }


@app.post("/admin/apikeys")
def create_client_apikey(payload: dict = Body(default={}), _=Depends(auth)):
    """Tạo mới một API Key để cấu hình cho Cursor, NextChat, Dify, OpenWebUI..."""
    import secrets
    name = (payload.get("name") or "").strip() or "Client App Key"
    new_key = "mst_" + secrets.token_hex(20)
    item = {
        "id": "key_" + uuid.uuid4().hex[:10],
        "name": name,
        "key": new_key,
        "created_at": int(time.time()),
        "last_used": None,
        "use_count": 0,
        "enabled": True
    }
    keys = _load_client_keys()
    keys.append(item)
    _save_client_keys(keys)
    return {"ok": True, "key": item}


@app.patch("/admin/apikeys/{key_id}")
def toggle_client_apikey(key_id: str, payload: dict = Body(default={}), _=Depends(auth)):
    """Bật / Tắt hoặc đổi tên API Key"""
    keys = _load_client_keys()
    target = next((k for k in keys if k.get("id") == key_id), None)
    if not target:
        raise HTTPException(404, "API Key không tồn tại")
    if "enabled" in payload:
        target["enabled"] = bool(payload["enabled"])
    if "name" in payload and payload["name"].strip():
        target["name"] = payload["name"].strip()
    _save_client_keys(keys)
    return {"ok": True, "key": target}


@app.delete("/admin/apikeys/{key_id}")
def delete_client_apikey(key_id: str, _=Depends(auth)):
    """Xóa hẳn một API Key"""
    keys = _load_client_keys()
    orig_len = len(keys)
    keys = [k for k in keys if k.get("id") != key_id]
    if len(keys) == orig_len:
        raise HTTPException(404, "API Key không tồn tại")
    _save_client_keys(keys)
    return {"ok": True, "deleted": key_id}


@app.post("/admin/apikey/rotate")
def rotate_apikey(_=Depends(auth)):
    """ API Key， .env （）。"""
    import secrets
    new_key = "mst_" + secrets.token_hex(24)
    old = CFG.api_key
    CFG.api_key = new_key
    _persist_env("MUSE_STUDIO_KEY", new_key)
    return {"ok": True, "api_key": new_key, "previous": old,
            "message": "Đã tạo Key mới thành công"}


def _persist_env(key: str, value: str):
    """ .env（，）。"""
    path = os.path.join(CFG.base_dir, ".env")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        lines = []
    found = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith(key + "="):
            lines[i] = f"{key}={value}"
            found = True
    if not found:
        lines.append(f"{key}={value}")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")
    os.replace(tmp, path)


# Muse Studio configuration and operations
@app.get("/admin/cookie-helper")
def cookie_helper(download: int = 0):
    """ cookie （， Python）。"""
    p = os.path.join(BASE_DIR, "tools", "get_muse_cookie.py")
    if not os.path.isfile(p):
        raise HTTPException(404, "Request error")
    headers = {}
    if download:
        headers["Content-Disposition"] = 'attachment; filename="get_muse_cookie.py"'
    return FileResponse(p, media_type="text/x-python", headers=headers)


@app.get("/admin/extension")
def extension_zip():
    """ zip （，）。

     → chrome://extensions  →  cookie。
    """
    src = os.path.join(BASE_DIR, "extension")
    if not os.path.isdir(src):
        raise HTTPException(404, "Request error")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(os.listdir(src)):
            p = os.path.join(src, name)
            if os.path.isfile(p):
                z.write(p, os.path.join("musestudio-extension", name))
    buf.seek(0)
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition":
                 'attachment; filename="musestudio-extension.zip"',
                 "Cache-Control": "no-store"})


@app.get("/admin/extension/files")
def extension_files():
    """（）。"""
    src = os.path.join(BASE_DIR, "extension")
    if not os.path.isdir(src):
        raise HTTPException(404, "Request error")
    return {"files": sorted(f for f in os.listdir(src)
                            if os.path.isfile(os.path.join(src, f)))}


# Muse Studio configuration and operations
@app.get("/admin/tasks")
def admin_tasks(limit: int = 50, _=Depends(auth)):
    return {"tasks": store.list_tasks(limit)}


@app.delete("/admin/tasks/{tid}")
def del_task(tid: str, _=Depends(auth)):
    if not store.delete_task(tid):
        raise HTTPException(404, "Request error")
    return {"deleted": True}


@app.post("/admin/tasks/clear")
def clear_tasks(payload: dict = Body(default={}), _=Depends(auth)):
    return {"removed": store.clear_tasks(int(payload.get("keep") or 0))}


@app.get("/admin/media")
def admin_media(_=Depends(auth)):
    d = CFG.media_dir
    items = []
    if os.path.isdir(d):
        for name in os.listdir(d):
            p = os.path.join(d, name)
            if not os.path.isfile(p):
                continue
            ext = os.path.splitext(name)[1].lower()
            items.append({"name": name, "url": media_url(name), "bytes": os.path.getsize(p),
                          "mtime": int(os.path.getmtime(p)),
                          "kind": "video" if ext in (".mp4", ".webm", ".mov") else "image"})
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return {"media": items, "count": len(items)}


@app.post("/admin/media/delete")
def delete_media(payload: dict = Body(default={}), _=Depends(auth)):
    names = payload.get("names", [])
    if isinstance(names, str):
        names = [names]
    if not isinstance(names, list):
        raise HTTPException(400, "names Request error")
    d = CFG.media_dir
    removed = 0
    errors = []
    for name in names:
        if not isinstance(name, str) or "/" in name or "\\" in name or ".." in name:
            errors.append(f": {name}")
            continue
        p = os.path.join(d, name)
        if os.path.isfile(p):
            try:
                os.remove(p)
                removed += 1
            except OSError as e:
                errors.append(f"{name}: {str(e)}")
    return {"removed": removed, "errors": errors}


@app.delete("/admin/media/{name}")
def delete_single_media(name: str, _=Depends(auth)):
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "Request error")
    p = os.path.join(CFG.media_dir, name)
    if not os.path.isfile(p):
        raise HTTPException(404, "Request error")
    try:
        os.remove(p)
        return {"status": "ok", "deleted": name}
    except OSError as e:
        raise HTTPException(500, f"Request error: {e}")


# Muse Studio configuration and operations
@app.get("/", response_class=HTMLResponse)
def index():
    return RedirectResponse(url="/studio/", status_code=307)


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return RedirectResponse(url="/studio/", status_code=307)



# Muse Studio configuration and operations
KEEPALIVE_LOCK = asyncio.Lock()
KEEPALIVE_STATE = {
    "running": False,
    "last_run": None,
    "last_result": None,
    "next_run": None,
}


def _probe_account_sync(aid: str, check_quota: bool = False) -> dict:
    """ muse.ai/api/session  Meta  hatch_vml (+48h) / hatch_sess (+30d)  VM。"""
    acc = store.get_account(aid)
    if not acc or not acc.get("cookies"):
        return {"ok": False, "id": aid, "label": (acc or {}).get("label", aid), "error": "Tài khoản không có cookie hợp lệ"}
    try:
        res = engine.renew_session_http(acc["cookies"], acc.get("cookies_exp"), wake_vm=True)
        store.update_account(
            aid,
            cookies=res["cookies"],
            cookies_exp=res["cookies_exp"],
            ok=True if res.get("ok") else False,
            synced_at=int(time.time()),
        )
        vm_state = res.get("vm_state") or "RUNNING"
        store.touch_keepalive(aid, True, f"Phiên hoạt động ·  (VM: {vm_state})")
        quota = acc.get("quota")
        if check_quota and GEN_LOCK.acquire(blocking=False):
            try:
                engine.start()
                quota = engine.quota(res["cookies"], res["cookies_exp"])
                quota["checked_at"] = int(time.time())
                store.update_account(aid, quota=quota)
            except Exception as qe:  # noqa: BLE001
                log.warning("Status %s Status: %s", aid, qe)
            finally:
                GEN_LOCK.release()
        updated = store.get_account(aid) or {}
        return {
            "ok": True,
            "id": aid,
            "label": acc.get("label", aid),
            "vm_id": res.get("vm_id"),
            "vm_state": vm_state,
            "wake_ok": res.get("wake_ok"),
            "expires_at": updated.get("expires_at"),
            "quota": quota,
        }
    except MuseAuthError as exc:
        store.touch_keepalive(aid, False, f": {str(exc)[:200]}")
        return {"ok": False, "id": aid, "label": acc.get("label", aid), "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        store.touch_keepalive(aid, None, f"（）: {str(exc)[:200]}")
        return {"ok": False, "id": aid, "label": acc.get("label", aid), "error": str(exc)}


async def run_keepalive_all(force: bool = False) -> dict:
    """：force=True ，/ VM 。"""
    async with KEEPALIVE_LOCK:
        now = int(time.time())
        KEEPALIVE_STATE["running"] = True
        KEEPALIVE_STATE["last_run"] = now
        results = []
        skipped = []

        try:
            include_disabled = getattr(CFG, "keepalive_disabled_accounts", False)
            accounts = [a for a in store.list_accounts() if include_disabled or a.get("enabled", True)]
            for a in accounts:
                aid = a["id"]
                label = a.get("label", aid)
                exp_at = a.get("expires_at")
                last_ka = a.get("last_keepalive") or 0

                needs_run = (
                    force
                    or not exp_at
                    or (exp_at - now < 36 * 3600)
                    or ((now - last_ka) > 15 * 60)
                    or (a.get("ok") is not True)
                )
                if not needs_run:
                    skipped.append({"id": aid, "label": label, "reason": ""})
                    continue

                log.info("【Status】Status %s (%s) Status VM Status...", label, aid)
                res = await asyncio.to_thread(_probe_account_sync, aid, False)
                results.append(res)
                log.info("【Status】Status %s Status: ok=%s expires_at=%s", label, res.get("ok"), res.get("expires_at"))
                await asyncio.sleep(0.5)

            summary = {
                "checked_at": now,
                "refreshed_count": len(results),
                "refreshed": results,
                "skipped_count": len(skipped),
                "skipped": skipped,
            }
            KEEPALIVE_STATE["last_result"] = summary
            KEEPALIVE_STATE["next_run"] = now + 900
            return summary
        finally:
            KEEPALIVE_STATE["running"] = False


def _warmup_browser_sync():
    """ WebSocket ，。"""
    if getattr(engine, "current_acc_id", None) and engine.page is not None:
        return
    acc = store.pick_account(rotate=False)
    if not acc or not acc.get("cookies"):
        return
    if not GEN_LOCK.acquire(blocking=False):
        return
    try:
        log.info("【Status】Status %s (%s) Status...", acc.get("label"), acc["id"])
        refreshed = _renew_and_persist(acc["id"], wake_vm=True, force=False) or acc
        engine.start()
        engine.ensure_page(refreshed["cookies"], refreshed.get("cookies_exp"), account_id=acc["id"])
        log.info("【Status】Status %s (%s) Status WebSocket Status", acc.get("label"), acc["id"])
    except Exception as exc:  # noqa: BLE001
        log.warning("【Status】Status: %s", exc)
    finally:
        GEN_LOCK.release()


async def _keepalive_loop():
    """： 15 phut VM 。"""
    log.info("【Status】Status，Status: 15 Status")
    await asyncio.sleep(1)
    try:
        await asyncio.to_thread(_warmup_browser_sync)
    except Exception as e:  # noqa: BLE001
        log.warning("【Status】Status: %s", e)
    while True:
        try:
            await run_keepalive_all(force=False)
            if not getattr(engine, "current_acc_id", None) or engine.page is None:
                await asyncio.to_thread(_warmup_browser_sync)
        except Exception as e:  # noqa: BLE001
            log.error("【Status】Status: %s", e)
        await asyncio.sleep(900)


@app.post("/admin/accounts/keepalive")
async def trigger_keepalive_all(force: bool = True, _=Depends(auth)):
    """。"""
    if KEEPALIVE_STATE["running"]:
        return {"status": "busy", "message": "，"}
    return await run_keepalive_all(force=force)


@app.post("/admin/accounts/{aid}/keepalive")
async def trigger_keepalive_single(aid: str, _=Depends(auth)):
    """。"""
    return await asyncio.to_thread(_probe_account_sync, aid, False)


@app.get("/admin/keepalive/status")
def get_keepalive_status(_=Depends(auth)):
    """。"""
    return KEEPALIVE_STATE


# Muse Studio configuration and operations
REPO_URL = ""  # rebrand: da go bo lien ket repo upstream (Muse Studio)
TRACKED_REPO_PATHS = [
    "app.py", "engine.py", "store.py", "cdp.py", "config.py",
    "admin.html", "README.md", "version.json", "requirements.txt",
    "Dockerfile", "docker-compose.yml", ".env.example", ".gitignore",
    "LICENSE", "extension", "deploy", "tools",
]
_UPDATE_CACHE: dict[str, Any] = {"ts": 0.0, "data": None}


def _read_env_key(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if val:
        return val
    path = os.path.join(CFG.base_dir, ".env")
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f.read().splitlines():
                s = ln.strip()
                if s.startswith(key + "="):
                    return s.split("=", 1)[1].strip()
    except OSError:
        pass
    return ""


def _read_local_version() -> dict:
    p = os.path.join(BASE_DIR, "version.json")
    try:
        with open(p, encoding="utf-8") as f:
            obj = json.load(f)
            if isinstance(obj, dict):
                return obj
    except Exception:
        pass
    return {"version": "1.5.0", "highlights": []}


def _installed_sha_file() -> str:
    return os.path.join(CFG.data_dir, ".installed_sha")


def _git(args: list[str], timeout: int = 30):
    import subprocess
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git", "-c", f"safe.directory={BASE_DIR}", *args],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _ensure_git_repo(token: str = ""):
    """ BASE_DIR  musestudio  Git 。"""
    git_dir = os.path.join(BASE_DIR, ".git")
    remote_url = f"https://example.invalid/musestudio.git" if token else f"{REPO_URL}.git"
    if not os.path.isdir(git_dir):
        _git(["init", "-b", "main"])
        _git(["remote", "add", "origin", remote_url])
        _git(["fetch", "origin", "main"], timeout=45)
        _git(["reset", "--mixed", "origin/main"])
    else:
        _git(["remote", "set-url", "origin", remote_url])
    _git(["config", "user.name", "musestudio"])
    _git(["config", "user.email", "musestudio@example.invalid"])


def _check_update_sync(force: bool = False) -> dict:
    """Kiem tra cap nhat - DA BI VO HIEU HOA trong ban Muse Studio rebrand."""
    if not REPO_URL:
        return {"ok": True, "disabled": True,
                "message": "Tính năng kiểm tra cập nhật đã bị vô hiệu hóa trong bản Muse Studio.",
                "version": str(_read_local_version().get("version") or "")}
    now = time.time()
    if not force and _UPDATE_CACHE["data"] and (now - _UPDATE_CACHE["ts"]) < 90:
        return _UPDATE_CACHE["data"]

    import requests
    token = _read_env_key("GITHUB_TOKEN")
    local_ver_obj = _read_local_version()
    local_version = str(local_ver_obj.get("version") or "1.5.0")

    has_git = os.path.isdir(os.path.join(BASE_DIR, ".git"))
    local_sha, local_msg, local_ts = "", "", 0
    if has_git:
        try:
            r_sha = _git(["rev-parse", "--short", "HEAD"])
            if r_sha.returncode == 0:
                local_sha = r_sha.stdout.strip()[:7]
            r_log = _git(["log", "-1", "--format=%s||%ct"])
            if r_log.returncode == 0 and "||" in r_log.stdout:
                parts = r_log.stdout.strip().split("||", 1)
                local_msg = parts[0]
                local_ts = int(parts[1])
        except Exception:
            pass

    if not local_sha and os.path.isfile(_installed_sha_file()):
        try:
            with open(_installed_sha_file(), encoding="utf-8") as f:
                local_sha = f.read().strip()[:7]
        except OSError:
            pass

    remote_version = local_version
    highlights = list(local_ver_obj.get("highlights") or [])
    try:
        rv = requests.get(
            f"https://raw.githubusercontent.com/musestudio/main/version.json?t={int(now)}",
            timeout=6,
        )
        if rv.status_code == 200:
            rvj = rv.json()
            if isinstance(rvj, dict):
                remote_version = str(rvj.get("version") or remote_version)
                if rvj.get("highlights"):
                    highlights = list(rvj["highlights"])
    except Exception:
        pass

    remote_sha, remote_msg, remote_time = "", "", ""
    recent_commits = []
    try:
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "musestudio-updater"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(
            "https://example.invalid/api/commits",
            headers=headers,
            timeout=6,
        )
        if resp.status_code == 200 and isinstance(resp.json(), list):
            commits = resp.json()
            for idx, c in enumerate(commits):
                sha7 = (c.get("sha") or "")[:7]
                c_msg = ((c.get("commit") or {}).get("message") or "").splitlines()[0]
                c_date = (((c.get("commit") or {}).get("committer") or {}).get("date") or "")
                c_url = c.get("html_url") or f"{REPO_URL}/commit/{sha7}"
                if idx == 0:
                    remote_sha = sha7
                    remote_msg = c_msg
                    remote_time = c_date
                recent_commits.append({
                    "sha": sha7,
                    "message": c_msg,
                    "date": c_date,
                    "url": c_url,
                })
    except Exception:
        pass

# Muse Studio configuration and operations
    if not local_sha and remote_sha and local_version == remote_version:
        local_sha = remote_sha
        try:
            with open(_installed_sha_file(), "w", encoding="utf-8") as f:
                f.write(remote_sha)
        except OSError:
            pass

    def _parse_v(v: str) -> tuple[int, ...]:
        try:
            return tuple(int(x) for x in re.findall(r"\d+", v))
        except Exception:
            return (0,)

    has_update = False
    if remote_sha and local_sha:
        has_update = (remote_sha != local_sha)
    elif remote_version and local_version:
        has_update = _parse_v(remote_version) > _parse_v(local_version)

    data = {
        "repo_url": REPO_URL,
        "has_git": has_git,
        "local_version": local_version,
        "remote_version": remote_version,
        "local_sha": local_sha,
        "local_msg": local_msg,
        "local_ts": local_ts,
        "remote_sha": remote_sha,
        "remote_msg": remote_msg,
        "remote_time": remote_time,
        "has_update": has_update,
        "up_to_date": not has_update and bool(remote_sha or remote_version),
        "highlights": highlights,
        "recent_commits": recent_commits,
        "checked_at": int(now),
    }
    _UPDATE_CACHE["ts"] = now
    _UPDATE_CACHE["data"] = data
    return data


def _upgrade_from_github_sync() -> dict:
    """ GitHub （ Git  Git  Docker/ZIP ）， .env  data/。"""
    import requests
    import tarfile

    token = _read_env_key("GITHUB_TOKEN")
    upgraded_via = ""
    try:
        _ensure_git_repo(token)
        f_res = _git(["fetch", "origin", "main"], timeout=45)
        if f_res.returncode == 0:
            _git(["checkout", "-f", "origin/main", "--", "."])
            _git(["reset", "--mixed", "origin/main"])
            upgraded_via = "git"
    except Exception as e:
        log.warning("Git Status，Status Tarball Status: %s", e)

    if not upgraded_via:
        resp = requests.get(
            "https://example.invalid/tarball",
            timeout=60,
        )
        if resp.status_code != 200:
            raise HTTPException(502, f"Request error GitHub Request error (HTTP {resp.status_code})")
        protected_files = {".env", "data/accounts.json", "data/tasks.json"}
        with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:gz") as tar:
            for member in tar.getmembers():
                parts = member.name.split("/", 1)
                if len(parts) < 2 or not parts[1]:
                    continue
                rel = parts[1].replace("\\", "/")
                if ".." in rel or rel in protected_files:
                    continue
                target_path = os.path.join(BASE_DIR, rel)
                if member.isdir():
                    os.makedirs(target_path, exist_ok=True)
                elif member.isfile():
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    fobj = tar.extractfile(member)
                    if fobj is not None:
                        with open(target_path, "wb") as out_f:
                            out_f.write(fobj.read())
        upgraded_via = "tarball"

    _UPDATE_CACHE["ts"] = 0.0
    status = _check_update_sync(force=True)
    if status.get("remote_sha"):
        try:
            with open(_installed_sha_file(), "w", encoding="utf-8") as f:
                f.write(status["remote_sha"])
            status["local_sha"] = status["remote_sha"]
            status["has_update"] = False
            status["up_to_date"] = True
        except OSError:
            pass
    return {
        "ok": True,
        "via": upgraded_via,
        "message": f" {status.get('remote_version')} ({status.get('remote_sha')})",
        "status": status,
    }


@app.get("/admin/update/check")
@app.get("/admin/repo/status")
async def admin_check_update(force: bool = False):
    """ GitHub 。"""
    return await asyncio.to_thread(_check_update_sync, force)


@app.post("/admin/update/upgrade")
@app.post("/admin/repo/pull")
async def admin_upgrade_now(payload: dict = Body(default={}), _=Depends(auth)):
    """ GitHub 。"""
    if not getattr(CFG, "enable_upgrade", False):
        raise HTTPException(403, "Tính năng online-upgrade đã bị tắt (MUSE_STUDIO_ENABLE_UPGRADE=0). Hãy update thủ công bằng git pull để đảm bảo an toàn.")
    res = await asyncio.to_thread(_upgrade_from_github_sync)
    restart = payload.get("restart", True) if isinstance(payload, dict) else True
    if restart:
        def _delayed_restart():
            time.sleep(0.5)
            try:
                engine.stop()
            except Exception:
                pass
            os._exit(0)
        threading.Thread(target=_delayed_restart, daemon=True).start()
    return res


@app.post("/admin/repo/push")
async def admin_repo_push(payload: dict = Body(default={}), _=Depends(auth)):
    """： GitHub （ .env  data ）。"""
    if not getattr(CFG, "enable_upgrade", False):
        raise HTTPException(403, "Tính năng repo-push đã bị tắt (MUSE_STUDIO_ENABLE_UPGRADE=0).")
    msg = (payload.get("message") or "").strip() or f"chore: sync update ({time.strftime('%Y-%m-%d %H:%M:%S')})"
    new_token = (payload.get("github_token") or "").strip()
    if new_token:
        _persist_env("GITHUB_TOKEN", new_token)
        os.environ["GITHUB_TOKEN"] = new_token
    token = new_token or _read_env_key("GITHUB_TOKEN")

    def _do_push():
        _ensure_git_repo(token)
        existing_paths = [p for p in TRACKED_REPO_PATHS if os.path.exists(os.path.join(BASE_DIR, p))]
        _git(["add", "--", *existing_paths])
        st = _git(["status", "--porcelain", "--", *existing_paths])
        committed = False
        if st.stdout.strip():
            c_res = _git(["commit", "-m", msg])
            if c_res.returncode != 0:
                raise HTTPException(500, f"Git commit Request error: {c_res.stderr or c_res.stdout}")
            committed = True
        p_res = _git(["push", "origin", "HEAD:main"], timeout=60)
        if p_res.returncode != 0:
            err = (p_res.stderr or p_res.stdout or "").strip()
            raise HTTPException(500, f"Git push Request error: {err[:300]}")
        _UPDATE_CACHE["ts"] = 0.0
        status = _check_update_sync(force=True)
        return {
            "ok": True,
            "committed": committed,
            "message": " GitHub ",
            "status": status,
        }

    return await asyncio.to_thread(_do_push)


@app.on_event("startup")
async def _startup():
    for task in list(store.tasks.values()):
        if task.get("kind") == "image" and task.get("status") in ("queued", "processing"):
            store.update_task(task["id"], status="failed", error="，")
    if not CFG.api_key:
        import secrets
        new_key = "mst_" + secrets.token_hex(24)
        CFG.api_key = new_key
        _persist_env("MUSE_STUDIO_KEY", new_key)
        log.info("🔑 Status MUSE_STUDIO_KEY，Status: %s", new_key)
    asyncio.create_task(_keepalive_loop())


@app.on_event("shutdown")
def _shutdown():
    engine.stop()
