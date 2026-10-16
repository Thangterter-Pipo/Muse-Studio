"""musestudio 。"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field

_DEFAULT_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv():
    """ .env （）。"""
    base = (os.environ.get("MUSE_STUDIO_HOME")
            or os.environ.get("MUSE2API_HOME")  # legacy fallback
            or _DEFAULT_BASE_DIR)
    env_path = os.path.join(base, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except OSError:
        pass


_load_dotenv()


def _env(key: str, default: str) -> str:
    if key in os.environ:
        return os.environ[key]
    # Tuong thich nguoc: MUSE_STUDIO_X tu dong doc them MUSE2API_X cu
    if key.startswith("MUSE_STUDIO_"):
        legacy = "MUSE2API_" + key[len("MUSE_STUDIO_"):]
        if legacy in os.environ:
            return os.environ[legacy]
    return default


def _detect_chromium() -> str:
    """ MUSE_STUDIO_CHROMIUM；， Chromium/Chrome。"""
    configured = os.environ.get("MUSE_STUDIO_CHROMIUM", "").strip()
    if configured and (os.path.isfile(configured) or shutil.which(configured)):
        return configured
    candidates = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "chromium",
        "chromium-browser",
        "google-chrome",
        "chrome",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if os.path.isfile(c) or shutil.which(c):
            return c
    return configured or "chromium"


@dataclass
class Config:
    base_dir: str = field(default_factory=lambda: _env("MUSE_STUDIO_HOME", _DEFAULT_BASE_DIR))
    host: str = field(default_factory=lambda: _env("MUSE_STUDIO_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(_env("MUSE_STUDIO_PORT", "18610")))

# Muse Studio configuration and operations
    chromium: str = field(default_factory=_detect_chromium)
    cdp_port: int = field(default_factory=lambda: int(_env("MUSE_STUDIO_CDP_PORT", "19210")))
    home_dir: str = field(default_factory=lambda: _env("MUSE_STUDIO_HOME_DIR", os.path.expanduser("~")))
    extra_path: str = field(default_factory=lambda: _env("MUSE_STUDIO_EXTRA_PATH", "/snap/bin"))
    site_url: str = field(default_factory=lambda: _env("MUSE_STUDIO_SITE", "https://muse.ai/"))
    login_wait: int = field(default_factory=lambda: int(_env("MUSE_STUDIO_LOGIN_WAIT", "60")))

# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
    profile_root: str = field(
        default_factory=lambda: _env("MUSE_STUDIO_PROFILE_ROOT",
                                     os.path.join(os.path.expanduser("~"),
                                                  "musestudio-profiles")))

# Muse Studio configuration and operations
    api_key: str = field(default_factory=lambda: _env("MUSE_STUDIO_KEY", ""))

# Muse Studio configuration and operations
    public_base: str = field(
        default_factory=lambda: _env("MUSE_STUDIO_PUBLIC_BASE", ""))

# Muse Studio configuration and operations
    cors_origins: str = field(
        default_factory=lambda: _env("MUSE_STUDIO_CORS_ORIGINS",
                                     "https://muse.ai,https://www.muse.ai"))

# Muse Studio configuration and operations
    image_timeout: int = field(default_factory=lambda: int(_env("MUSE_STUDIO_IMAGE_TIMEOUT", "240")))
    video_timeout: int = field(default_factory=lambda: int(_env("MUSE_STUDIO_VIDEO_TIMEOUT", "600")))
    chat_timeout: int = field(default_factory=lambda: int(_env("MUSE_STUDIO_CHAT_TIMEOUT", "300")))

# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
    tool_protocol: bool = field(
        default_factory=lambda: _env("MUSE_STUDIO_TOOL_PROTOCOL", "0").strip() != "0")

# Muse Studio configuration and operations
# Muse Studio configuration and operations
# Muse Studio configuration and operations
    keepalive_disabled_accounts: bool = field(
        default_factory=lambda: _env("MUSE_STUDIO_KEEPALIVE_DISABLED_ACCOUNTS", "0").strip() != "0")

    # ---- Hardening (v1.5.5-hardened) ----
    # Ma hoa cookie at-rest. Mac dinh bat. Key lay tu MUSE_STUDIO_COOKIE_KEY (Fernet key),
    # neu trong se tu sinh va luu vao data/.cookie_key (chmod 600).
    cookie_encrypt: bool = field(
        default_factory=lambda: _env("MUSE_STUDIO_COOKIE_ENCRYPT", "1").strip() != "0")
    cookie_key: str = field(
        default_factory=lambda: _env("MUSE_STUDIO_COOKIE_KEY", ""))

    # CORS: mac dinh van cho phep * de tuong thich Open WebUI/LobeChat,
    # nhung co the siet lai bang MUSE_STUDIO_CORS_ALLOW_ALL=0 va liet ke domain trong CORS_ORIGINS.
    cors_allow_all: bool = field(
        default_factory=lambda: _env("MUSE_STUDIO_CORS_ALLOW_ALL", "1").strip() != "0")

    # Tat tinh nang tu dong upgrade/pull code tu GitHub theo mac dinh (nguy co RCE).
    # Muon bat lai: MUSE_STUDIO_ENABLE_UPGRADE=1
    enable_upgrade: bool = field(
        default_factory=lambda: _env("MUSE_STUDIO_ENABLE_UPGRADE", "0").strip() != "0")

    # Rate-limit don gian cho /v1/* (requests/phut/IP). 0 = KHONG GIOI HAN (unlimited, manh nhat).
    rate_limit_per_min: int = field(
        default_factory=lambda: int(_env("MUSE_STUDIO_RATE_LIMIT", "0")))

    @property
    def cookie_key_file(self) -> str:
        return os.path.join(self.data_dir, ".cookie_key")

    @property
    def data_dir(self) -> str:
        return os.path.join(self.base_dir, "data")

    @property
    def media_dir(self) -> str:
        return os.path.join(self.data_dir, "media")

    @property
    def download_dir(self) -> str:
        return os.path.join(self.data_dir, "downloads")

    @property
    def profile_dir(self) -> str:
        """ profile。"""
        return os.path.join(self.profile_root, "generate")

    @property
    def accounts_file(self) -> str:
        return os.path.join(self.data_dir, "accounts.json")

    @property
    def tasks_file(self) -> str:
        return os.path.join(self.data_dir, "tasks.json")

    def ensure_dirs(self):
        for d in (self.base_dir, self.data_dir, self.media_dir, self.download_dir,
                  self.profile_dir):
            os.makedirs(d, exist_ok=True)


CFG = Config()
