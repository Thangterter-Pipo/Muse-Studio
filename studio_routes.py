from pathlib import Path
from fastapi import Request
from fastapi.staticfiles import StaticFiles


def mount_studio(app, cfg=None):
    folder = Path(__file__).resolve().parent / "studio"
    if not (folder / "index.html").is_file():
        raise RuntimeError(f"Muse Studio assets not found: {folder}")

    @app.get("/studio/config.json")
    def studio_config(request: Request):
        host = request.client.host if request.client else ""
        is_local = host in ("127.0.0.1", "localhost", "::1") or not host
        key = getattr(cfg, "api_key", "") if cfg else ""
        return {
            "api_key": key if is_local else "",
            "local": is_local
        }

    # Route order is important: mount this before any potential catch-all route.
    app.mount("/studio", StaticFiles(directory=folder, html=True), name="muse-studio")

    @app.on_event("shutdown")
    def _on_shutdown():
        try:
            from app import engine
            if engine:
                engine.stop()
        except Exception:
            pass
