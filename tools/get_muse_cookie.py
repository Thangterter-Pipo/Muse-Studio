#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""musestudio Cookie  ——  muse.ai  cookie Tai khoan。

？
    muse.ai  4  cookie（hatch_sess / hatch_gw / hatch_vml /
    hatch_native_auth_device） httpOnly ， document.cookie
    。（Chrome DevTools Protocol）。
    「」「」，。

？
    1.  Chrome （）
    2.  muse.ai
    3.  cookie， musestudio
    4. ，

：
    python get_muse_cookie.py --base http://your-server-ip:18610 --key mst_xxx
    python get_muse_cookie.py --base http://your-server-ip:18610 --key mst_xxx --label acc-01

，：
    set MUSE_STUDIO_BASE=http://your-server-ip:18610     (Windows)
    set MUSE_STUDIO_KEY=mst_xxx
    export MUSE_STUDIO_BASE=...                          (macOS / Linux)
    export MUSE_STUDIO_KEY=...

 Python （Python 3.8+）， pip install 。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

SITE = "https://muse.ai/"
CDP_PORT = 9333
ESSENTIAL = ("hatch_sess", "hatch_gw", "hatch_vml", "hatch_native_auth_device")
DOMAIN_HINT = "muse.ai"


# Muse Studio configuration and operations
def say(msg=""):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:                     #  Windows 
        print(msg.encode("utf-8", "replace").decode("utf-8", "replace"), flush=True)


def init_console():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")   # Python 3.7+
        except Exception:                          # noqa: BLE001
            pass


# Muse Studio configuration and operations
class WS:
    """ CDP  WebSocket （RFC6455，）。"""

    def __init__(self, url: str, timeout: float = 15.0):
        assert url.startswith("ws://"), url
        rest = url[5:]
        hostport, _, path = rest.partition("/")
        path = "/" + path
        host, _, port = hostport.partition(":")
        port = int(port or 80)

        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {path} HTTP/1.1\r\n"
               f"Host: {host}:{port}\r\n"
               "Upgrade: websocket\r\n"
               "Connection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\n"
               "Sec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("WebSocket ")
            buf += chunk
        status = buf.split(b"\r\n", 1)[0]
        if b" 101" not in status:
            raise ConnectionError(f"WebSocket That bai: {status!r}")
        self._id = 0

# Muse Studio configuration and operations
    def _frame(self, opcode: int, payload: bytes):
        head = bytearray([0x80 | opcode])
        n = len(payload)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126)
            head += struct.pack(">H", n)
        else:
            head.append(0x80 | 127)
            head += struct.pack(">Q", n)
        mask = os.urandom(4)
        head += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(head) + masked)

    def send_text(self, text: str):
        self._frame(0x1, text.encode("utf-8"))

# Muse Studio configuration and operations
    def _read(self, n: int) -> bytes:
        out = b""
        while len(out) < n:
            chunk = self.sock.recv(n - len(out))
            if not chunk:
                raise ConnectionError("Dong")
            out += chunk
        return out

    def recv_text(self) -> str:
        while True:
            h = self._read(2)
            opcode = h[0] & 0x0F
            masked = h[1] & 0x80
            ln = h[1] & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._read(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._read(8))[0]
            mk = self._read(4) if masked else None
            data = self._read(ln) if ln else b""
            if mk:
                data = bytes(b ^ mk[i % 4] for i, b in enumerate(data))
            if opcode == 0x1:
                return data.decode("utf-8", "replace")
            if opcode == 0x9:                       # ping -> pong
                self._frame(0xA, data)
            elif opcode == 0x8:
                raise ConnectionError("Dong")
# Muse Studio configuration and operations

    def call(self, method: str, params: dict | None = None,
             timeout: float = 20.0) -> dict:
        self._id += 1
        mid = self._id
        self.send_text(json.dumps({"id": mid, "method": method,
                                   "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                msg = json.loads(self.recv_text())
            except socket.timeout:
                continue
            except ConnectionError:
                raise
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(f"CDP {method} Qua thoi gian")

    def close(self):
        try:
            self.sock.close()
        except Exception:                              # noqa: BLE001
            pass


# Muse Studio configuration and operations
CHROME_EXES = ("chrome.exe", "msedge.exe", "brave.exe", "chromium.exe")


def _win_registry_paths() -> list[str]:
    """ App Paths 。

     %ProgramFiles%  ——  shell / 
    （ ProgramFiles  PROGRAMFILES  None）。
    """
    out: list[str] = []
    try:
        import winreg
    except ImportError:
        return out
    sub = (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for exe in CHROME_EXES:
            for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
                try:
                    with winreg.OpenKey(root, sub + "\\" + exe, 0,
                                        winreg.KEY_READ | view) as k:
                        val = winreg.QueryValueEx(k, "")[0]
                        if val:
                            out.append(os.path.expandvars(val))
                except OSError:
                    continue
    return out


def _win_common_paths() -> list[str]:
    roots = [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
             os.environ.get("LOCALAPPDATA"), r"C:\Program Files",
             r"C:\Program Files (x86)"]
    rel = [
        r"Google\Chrome\Application\chrome.exe",
        r"Microsoft\Edge\Application\msedge.exe",
        r"BraveSoftware\Brave-Browser\Application\brave.exe",
    ]
    return [os.path.join(r, p) for r in roots if r for p in rel]


def find_chrome() -> str | None:
    if sys.platform == "win32":
        cands = _win_registry_paths() + _win_common_paths()
    elif sys.platform == "darwin":
        cands = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
    else:
        cands = ["google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "microsoft-edge", "brave-browser"]
    seen = set()
    for c in cands:
        if not c or c in seen:
            continue
        seen.add(c)
        if os.path.isfile(c):
            return c
        if not os.path.isabs(c):
            w = shutil.which(c)
            if w:
                return w
    return None


def wait_cdp(port: int, timeout: float = 30.0) -> str:
    """ DevTools ， WebSocket 。"""
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/json/version"
    last = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                return json.load(r)["webSocketDebuggerUrl"]
        except Exception as exc:                       # noqa: BLE001
            last = exc
            time.sleep(0.5)
    raise RuntimeError(f"（{port}）：{last}")


# Muse Studio configuration and operations
def read_cookies(ws: WS) -> dict[str, dict]:
    """ Storage.getCookies  cookie， muse.ai。

    ：CDP  httpOnly  cookie， JS 。
    """
    res = ws.call("Storage.getCookies", {}, timeout=20)
    out: dict[str, dict] = {}
    for c in res.get("cookies", []):
        domain = (c.get("domain") or "").lstrip(".")
        if DOMAIN_HINT not in domain:
            continue
        name = c.get("name")
        if not name:
            continue
        try:
            exp = int(float(c.get("expires", -1)))
        except (TypeError, ValueError):
            exp = -1
        out[name] = {"value": c.get("value", ""), "expires": exp,
                     "httpOnly": bool(c.get("httpOnly"))}
    return out


# Muse Studio configuration and operations
def upload(base: str, key: str, label: str, cookies: dict[str, dict]) -> dict:
    payload = {
        "label": label,
        "cookies": {k: v["value"] for k, v in cookies.items()},
        "expires": {k: v["expires"] for k, v in cookies.items() if v["expires"] > 0},
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/admin/accounts",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"That bai HTTP {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f" {base}：{e.reason}") from None


def fmt_ts(ts: int) -> str:
    if ts <= 0:
        return ""
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))


# Muse Studio configuration and operations
def main() -> int:
    init_console()
    ap = argparse.ArgumentParser(
        description=" muse.ai  cookie  musestudio Tai khoan")
    ap.add_argument("--base", default=os.environ.get("MUSE_STUDIO_BASE", ""),
                    help="musestudio ， http://your-server-ip:18610")
    ap.add_argument("--key", default=os.environ.get("MUSE_STUDIO_KEY", ""),
                    help="API Key（mst_ ）")
    ap.add_argument("--label", default="", help="Tai khoan， acc-01")
    ap.add_argument("--timeout", type=int, default=300,
                    help="， 300")
    ap.add_argument("--keep-open", action="store_true",
                    help="Thanh congDong")
    ap.add_argument("--port", type=int, default=CDP_PORT,
                    help=f"， {CDP_PORT}")
    ap.add_argument("--chrome", default="", help="")
    args = ap.parse_args()

    say("=" * 66)
    say("  musestudio Cookie ")
    say("=" * 66)
    say()

    if not args.base or not args.key:
        say("✗ 。：")
        say("    python get_muse_cookie.py --base https:// --key mst_xxx")
        say()
        say("  （ musestudio 「」）")
        return 2
    if not args.label:
        args.label = "muse-" + time.strftime("%m%d-%H%M")

    chrome = args.chrome or find_chrome()
    if not chrome:
        say("✗  Chrome / Edge 。")
        say("   Chrome， --chrome \"\" 。")
        return 3
    say(f"：{chrome}")

    profile = os.path.join(tempfile.gettempdir(), "musestudio-cookie-profile")
    shutil.rmtree(profile, ignore_errors=True)
    os.makedirs(profile, exist_ok=True)

    args_cmd = [
        chrome,
        f"--remote-debugging-port={args.port}",
        f"--user-data-dir={profile}",
        "--no-first-run", "--no-default-browser-check",
# Muse Studio configuration and operations
        #   "sandbox initialization failed: Operation not permitted"
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
        "--no-sandbox", "--disable-gpu",
        "--new-window", SITE,
    ]
    say("（）…")
    proc = subprocess.Popen(args_cmd, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

    ws = None
    try:
        try:
            ws_url = wait_cdp(args.port, 30)
        except RuntimeError as exc:
            say(f"✗ {exc}")
            say("  ：，。")
            say("  （ Chrome ，，。）")
            return 4
        ws = WS(ws_url)

        say()
        say("┌" + "─" * 64 + "┐")
        say("│   muse.ai（）  │")
        say("│  Thanh cong、，，。    │")
        say("└" + "─" * 64 + "┘")
        say()

        deadline = time.time() + args.timeout
        got: dict[str, dict] = {}
        last_note = 0.0
        while time.time() < deadline:
            try:
                got = read_cookies(ws)
            except Exception as exc:                    # noqa: BLE001
                say(f"   cookie ，…（{exc}）")
                time.sleep(2)
                continue

            have = [n for n in ESSENTIAL if n in got]
            if len(have) == len(ESSENTIAL):
                break

            now = time.time()
            if now - last_note > 5:
                last_note = now
                left = int(deadline - now)
                say(f"  …  {len(have)}/{len(ESSENTIAL)}  cookie"
                    f"（{', '.join(have) or ''}） {left}s")
            time.sleep(2)
        else:
            say()
            say("✗ Qua thoi gian，Thanh cong。")
            say("  ，。")
            return 5

        say()
        say("✓  cookie：")
        say()
        say(f"  {'cookie ':<30}{'httpOnly':<10}{'Hop le'}")
        say("  " + "-" * 62)
        for name in ESSENTIAL:
            c = got.get(name, {})
            say(f"  {name:<30}{('' if c.get('httpOnly') else ''):<10}"
                f"{fmt_ts(c.get('expires', -1))}")
        say()

        say(" musestudio…")
        try:
            r = upload(args.base, args.key, args.label, got)
        except RuntimeError as exc:
            say(f"✗ {exc}")
            say()
            say("  cookie ，That bai。，")
            say("  「Tai khoan」：")
            say()
            say("  " + "; ".join(f"{k}={v['value']}" for k, v in got.items()))
            return 6

        say()
        say("=" * 66)
        say(f"✓ Thanh cong！Tai khoan：{r['added'][0]['label']}")
        say(f"  Tai khoan ID：{r['added'][0]['id']}")
        say(f"   {r['added'][0]['cookie_count']}  cookie")
        if r.get("warning"):
            say(f"  ⚠ {r['warning']}")
        say()
        say(f"   {args.base.rstrip('/')}/ Tai khoan。")
        say("=" * 66)
        return 0

    finally:
        if ws:
            ws.close()
        if not args.keep_open:
            try:
                proc.terminate()
            except Exception:                           # noqa: BLE001
                pass
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say()
        say("。")
        sys.exit(130)
