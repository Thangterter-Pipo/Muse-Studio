"""Tai khoanTac vu（JSON ，）。"""
from __future__ import annotations

import base64
import json
import os
import tempfile
import threading
import time
import uuid

_LOCK = threading.Lock()

# ---- Hardening: cookie encryption at-rest (v1.5.5) ----
try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:  # cryptography chưa cài -> fallback obfuscation yếu
    Fernet = None
    InvalidToken = Exception

def _get_cookie_fernet(cfg):
    """Lấy Fernet từ env MUSE_STUDIO_COOKIE_KEY hoặc file data/.cookie_key (tự sinh)."""
    if not getattr(cfg, "cookie_encrypt", True):
        return None
    if Fernet is None:
        return None
    env_key = (getattr(cfg, "cookie_key", "") or "").strip()
    if env_key:
        try:
            return Fernet(env_key.encode())
        except Exception:
            pass
    key_file = getattr(cfg, "cookie_key_file", None) or os.path.join(cfg.data_dir, ".cookie_key")
    try:
        if os.path.isfile(key_file):
            with open(key_file, "rb") as f:
                k = f.read().strip()
                if k:
                    return Fernet(k)
    except Exception:
        pass
    # sinh mới
    try:
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        k = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(k)
        try:
            os.chmod(key_file, 0o600)
        except Exception:
            pass
        return Fernet(k)
    except Exception:
        return None

def _enc_cookies(fernet, cookies: dict) -> dict:
    if not fernet or not cookies:
        return {"__enc__": "", "__plain_fallback__": cookies} if fernet is None else {"__enc__": ""}
    try:
        raw = json.dumps(cookies, ensure_ascii=False).encode("utf-8")
        tok = fernet.encrypt(raw).decode("utf-8")
        return {"__enc__": tok}
    except Exception:
        return {"__enc__": ""}

def _dec_cookies(fernet, stored) -> dict:
    # stored có thể là dict plaintext cũ, hoặc {"__enc__": token}
    if not isinstance(stored, dict):
        return {}
    if "__enc__" not in stored:
        # plaintext legacy -> trả về nguyên
        return dict(stored)
    tok = stored.get("__enc__") or ""
    if not fernet:
        fb = stored.get("__plain_fallback__")
        if isinstance(fb, dict) and fb:
            return dict(fb)
        # legacy plaintext fallback đã migrate nhưng chưa có cryptography
        return {}
    if not tok:
        return {}
    try:
        raw = fernet.decrypt(tok.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


# Muse Studio configuration and operations
ESSENTIAL_COOKIES = ("hatch_sess", "hatch_gw", "hatch_vml",
                     "hatch_native_auth_device")


def _is_pos(v) -> bool:
    try:
        return int(v) > 0
    except (TypeError, ValueError):
        return False


# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
VML_TTL = 2 * 86400


def min_expiry(cookies_exp: dict | None) -> int | None:
    """ cookie （，）。"""
    if not cookies_exp:
        return None
    vals = []
    for name in ESSENTIAL_COOKIES:
        v = cookies_exp.get(name)
        try:
            v = int(v)
        except (TypeError, ValueError):
            continue
        if v > 0:
            vals.append(v)
    if not vals:
        for v in cookies_exp.values():
            try:
                v = int(v)
            except (TypeError, ValueError):
                continue
            if v > 0:
                vals.append(v)
    return min(vals) if vals else None


def account_expiry(cookies_exp: dict | None,
                   base_ts: int | None = None) -> int | None:
    """Tai khoan。

    ：
      1) hatch_vml  expires（）；
      2)  base_ts(/) + VML_TTL  ——  2 ；
      3)  cookie 。
    """
    ce = cookies_exp or {}
    vml = ce.get("hatch_vml")
    if _is_pos(vml):
        return int(vml)
    if base_ts:
        return int(base_ts) + VML_TTL
    return min_expiry(ce)


def _read(path: str, default):
    if not os.path.isfile(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return default


def _write(path: str, obj):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    # backup accounts.json trước khi ghi (giữ 3 bản gần nhất)
    try:
        if os.path.basename(path) == "accounts.json" and os.path.isfile(path):
            import shutil as _shutil, glob as _glob
            bk = path + ".bak"
            _shutil.copy2(path, bk)
            # xoay vòng bak.1..3
            for i in range(3, 0, -1):
                src = f"{bk}.{i-1}" if i > 1 else bk
                dst = f"{bk}.{i}"
                if os.path.isfile(src):
                    try: _shutil.move(src, dst)
                    except Exception: pass
    except Exception:
        pass
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Store:
    def __init__(self, cfg):
        self.cfg = cfg
        try:
            cfg.ensure_dirs()
        except Exception:
            pass
        self._fernet = _get_cookie_fernet(cfg)
        self.accounts: list[dict] = _read(cfg.accounts_file, [])
        migrated = False
        for a in self.accounts:
            ce = a.get("cookies_exp") or {}
            if _is_pos(ce.get("hatch_vml")):
                a["expires_at"] = int(ce["hatch_vml"])
            # migrate plaintext cookies -> encrypted
            ck = a.get("cookies")
            if isinstance(ck, dict) and "__enc__" not in ck and ck:
                a["cookies"] = _enc_cookies(self._fernet, ck)
                migrated = True
        if migrated:
            _write(cfg.accounts_file, self.accounts)
        self.tasks: dict[str, dict] = _read(cfg.tasks_file, {})

    # ---- helpers mã hóa trong suốt ----
    def _dec(self, stored):
        return _dec_cookies(self._fernet, stored)

    def _enc(self, cookies: dict):
        return _enc_cookies(self._fernet, cookies)

    def decrypted_cookies(self, acc: dict) -> dict:
        return self._dec(acc.get("cookies"))

# Muse Studio configuration and operations
    def add_account(self, cookies: dict, label: str = "",
                    cookies_exp: dict | None = None) -> dict:
        with _LOCK:
            aid = uuid.uuid4().hex[:12]
            exp = {k: int(v) for k, v in (cookies_exp or {}).items()
                   if _is_pos(v)}
            now = int(time.time())
            acc = {"id": aid, "label": label or aid, "cookies": self._enc(cookies or {}),
                   "cookies_exp": exp, "expires_at": account_expiry(exp, now),
                   "expiry_anchor": None,
                   "enabled": True, "created_at": now,
                   "last_used": None, "last_keepalive": None, "use_count": 0,
                   "ok": None, "note": "", "synced_at": None}
            self.accounts.append(acc)
            _write(self.cfg.accounts_file, self.accounts)
            return acc

    def list_accounts(self) -> list[dict]:
        out = []
        for a in self.accounts:
            item = {k: v for k, v in a.items() if k != "cookies"}
            ce = a.get("cookies_exp") or {}
            if _is_pos(ce.get("hatch_vml")):
                item["expires_at"] = int(ce["hatch_vml"])
            _ck = self._dec(a.get("cookies"))
            item["cookie_count"] = len(_ck)
            item["essential_ok"] = all(_ck.get(n) for n in ESSENTIAL_COOKIES)
# Muse Studio configuration and operations
            item["expires_estimated"] = not _is_pos(ce.get("hatch_vml"))
            out.append(item)
        return out

    def delete_account(self, aid: str) -> bool:
        with _LOCK:
            n = len(self.accounts)
            self.accounts = [a for a in self.accounts if a["id"] != aid]
            _write(self.cfg.accounts_file, self.accounts)
            return len(self.accounts) != n

    def pick_account(self, preferred_id: str | None = None, rotate: bool = True,
                     force_rotate: bool = False, exclude_id: str | None = None) -> dict | None:
        """Tai khoan：Tai khoan（）， 15 。"""
        with _LOCK:
            live = [a for a in self.accounts if a.get("enabled", True) and self._dec(a.get("cookies"))]
            if not live:
                return None
            if exclude_id and len(live) > 1:
                live = [a for a in live if a["id"] != exclude_id] or live
            if preferred_id and not force_rotate:
                for a in live:
                    if a["id"] == preferred_id and a.get("ok") is not False:
                        sticky_n = getattr(self, "_sticky_count", 0) if getattr(self, "_sticky_id", None) == preferred_id else 0
                        if not rotate or sticky_n < 15:
                            self._sticky_id = preferred_id
                            self._sticky_count = sticky_n + 1
                            a["last_used"] = time.time()
                            a["use_count"] = a.get("use_count", 0) + 1
                            _write(self.cfg.accounts_file, self.accounts)
                            out = dict(a); out["cookies"] = self._dec(a.get("cookies"))
                            return out
            healthy = [a for a in live if a.get("ok") is not False]
            candidates = healthy if healthy else live
            candidates.sort(key=lambda a: (a.get("last_used") or 0.0, a.get("use_count") or 0))
            acc = candidates[0]
            self._sticky_id = acc["id"]
            self._sticky_count = 1
            acc["last_used"] = time.time()
            acc["use_count"] = acc.get("use_count", 0) + 1
            _write(self.cfg.accounts_file, self.accounts)
            out = dict(acc); out["cookies"] = self._dec(acc.get("cookies"))
            return out

    def touch_keepalive(self, aid: str, ok: bool | None = True, note: str = ""):
        """ok=None ；Tai khoan、Thanh congHop le。"""
        with _LOCK:
            now_ts = int(time.time())
            for a in self.accounts:
                if a["id"] == aid:
                    if ok is not None:
                        a["ok"] = ok
                    if ok is True:
                        a["last_keepalive"] = now_ts
# Muse Studio configuration and operations
                        a["expires_at"] = account_expiry(
                            a.get("cookies_exp"), a.get("expiry_anchor") or a.get("created_at"))
                    if note:
                        a["note"] = note[:300]
                    a["checked_at"] = now_ts
            _write(self.cfg.accounts_file, self.accounts)

    def mark(self, aid: str, ok: bool, note: str = ""):
        with _LOCK:
            for a in self.accounts:
                if a["id"] == aid:
                    a["ok"] = ok
                    a["note"] = note[:300]
                    a["checked_at"] = int(time.time())
            _write(self.cfg.accounts_file, self.accounts)

    def get_account(self, aid: str) -> dict | None:
        for a in self.accounts:
            if a["id"] == aid:
                out = dict(a); out["cookies"] = self._dec(a.get("cookies"))
                return out
        return None

    def get_account_raw(self, aid: str) -> dict | None:
        for a in self.accounts:
            if a["id"] == aid:
                return a
        return None

    def update_account(self, aid: str, **kw) -> dict | None:
        """ / Bat / cookies / Hop le； None 。

         cookies_exp  expires_at，。
         expiry_anchor （Hop le）：
          -  hatch_vml  expires  -> ，；
          -                 -> （）；
          -  cookie（）      ->  expiry_anchor=now 。
        """
        with _LOCK:
            for a in self.accounts:
                if a["id"] == aid:
                    for k, v in kw.items():
                        if v is not None:
                            if k == "cookies" and isinstance(v, dict) and "__enc__" not in v:
                                a[k] = self._enc(v)
                            else:
                                a[k] = v
                    if "cookies_exp" in kw and kw["cookies_exp"] is not None:
                        ce = a["cookies_exp"]
                        if _is_pos(ce.get("hatch_vml")):
                            a["expiry_anchor"] = None
                        elif not a.get("expiry_anchor"):
                            a["expiry_anchor"] = int(time.time())
                        a["expires_at"] = account_expiry(
                            ce, a.get("expiry_anchor") or a.get("created_at"))
                    _write(self.cfg.accounts_file, self.accounts)
                    return a
        return None

    def stats(self) -> dict:
        now = int(time.time())
        total = len(self.accounts)
        enabled = sum(1 for a in self.accounts if a.get("enabled", True))
        bad = sum(1 for a in self.accounts
                  if a.get("enabled", True) and a.get("ok") is False)
        healthy = sum(1 for a in self.accounts
                      if a.get("enabled", True) and a.get("ok") is True)
        expiring = sum(1 for a in self.accounts
                       if a.get("enabled", True)
                       and a.get("expires_at")
                       and a["expires_at"] - now < 3 * 86400)
        expired = sum(1 for a in self.accounts
                      if a.get("enabled", True)
                      and a.get("expires_at") and a["expires_at"] <= now)
        return {"total": total, "enabled": enabled, "disabled": total - enabled,
                "healthy": healthy, "error": bad,
                "expiring": expiring, "expired": expired}

# Muse Studio configuration and operations
    def create_task(self, kind: str, prompt: str) -> dict:
        with _LOCK:
            tid = "task_" + uuid.uuid4().hex[:20]
            t = {"id": tid, "object": "task", "kind": kind, "prompt": prompt,
                 "status": "queued", "created_at": int(time.time()),
                 "updated_at": int(time.time()), "result": None, "error": None}
            self.tasks[tid] = t
            _write(self.cfg.tasks_file, self.tasks)
            return t

    def update_task(self, tid: str, **kw):
        with _LOCK:
            t = self.tasks.get(tid)
            if not t:
                return None
            t.update(kw)
            t["updated_at"] = int(time.time())
            _write(self.cfg.tasks_file, self.tasks)
            return t

    def get_task(self, tid: str) -> dict | None:
        return self.tasks.get(tid)

    def list_tasks(self, limit: int = 50) -> list[dict]:
        items = sorted(self.tasks.values(),
                       key=lambda t: t.get("created_at") or 0, reverse=True)
        return items[:limit]

    def delete_task(self, tid: str) -> bool:
        with _LOCK:
            if tid in self.tasks:
                del self.tasks[tid]
                _write(self.cfg.tasks_file, self.tasks)
                return True
            return False

    def clear_tasks(self, keep: int = 0) -> int:
        with _LOCK:
            items = sorted(self.tasks.values(),
                           key=lambda t: t.get("created_at") or 0, reverse=True)
            keep_ids = {t["id"] for t in items[:keep]}
            removed = len(self.tasks) - len(keep_ids)
            self.tasks = {k: v for k, v in self.tasks.items() if k in keep_ids}
            _write(self.cfg.tasks_file, self.tasks)
            return max(0, removed)
