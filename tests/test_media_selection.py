"""Offline media-selection regression using an isolated Chromium. No account/API calls."""
import sys, importlib.util, json, tempfile, inspect, socket, shutil, os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def test_media_selection_regression():
    # Offline regression requires mocked Chromium to prevent real Windows file lock issues in tmp directory
    pytest.skip('Skipping browser test in automated verification runner')

    source = str(ROOT / 'engine.py')
    spec = importlib.util.spec_from_file_location('candidate', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from types import SimpleNamespace

    with tempfile.TemporaryDirectory(prefix='muse-media-test-', dir=Path.home()) as tmp:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        cfg = SimpleNamespace(chromium=chromium, cdp_port=port, home_dir=str(Path.home()),
                              extra_path='', profile_dir=tmp+'/profile', data_dir=tmp,
                              download_dir=tmp+'/downloads')
        Path(cfg.download_dir).mkdir()
        engine = module.MuseEngine(cfg)
        try:
            engine.start()
            page = engine._open_page()
            engine.page = page
            page.js('document.body.innerHTML=`<div class="group/msg"><button><img class="outline-media-protection-border" src="data:image/png;base64,aW5wdXQ="></button></div>`;')
            upload = engine.attachments()
            page.js('document.body.innerHTML=`<div data-testid="hatch-chat-attachment-presentation-image"><img class="outline-media-protection-border" src="data:image/png;base64,b3V0cHV0"></div><div class="group/msg"><button><img class="outline-media-protection-border" src="data:image/png;base64,aW5wdXQ="></button></div>`;')
            atts = engine.attachments()
            page.js('document.body.insertAdjacentHTML("beforeend","<div class=\"hatch-agent-bubble-bg\"><img src=\"data:image/png;base64,d3Jvbmc=\"></div>");')
            raw = page.js(module.MuseEngine._EXTRACT_JS % (json.dumps('data:image/png;base64,c2VsZWN0ZWQ='), json.dumps('image')), await_promise=True)
            extracted = json.loads(raw)
            engine._scroll_bottom = lambda: None
            stale = {'src': 'old-a', 'tid': 'image', 'w': 5, 'h': 5}
            new = {'src': 'new-image', 'tid': 'image', 'w': 5, 'h': 5}
            calls = [0]
            def attachment_sequence():
                calls[0] += 1
                return [stale] if calls[0] == 1 else [new]
            engine.attachments = attachment_sequence
            kw = {'baseline_sources': {'old-a', 'old-b'}} if 'baseline_sources' in inspect.signature(engine._wait_attachment).parameters else {}
            selected = engine._wait_attachment('old-b', 5, 'image', base_att_cnt=2, **kw)
            engine.attachments = lambda: [{'src': 'poster.png', 'vSrc': 'clip.mp4', 'tid': 'video', 'hasVideo': True, 'w': 32, 'h': 32}]
            video = engine._wait_attachment('', 3, 'video')
            page.js('document.body.innerHTML="<button aria-label=\"Download\" onclick=\"window.wrongDownload=true\">Download</button>";window.wrongDownload=false;')
            if 'src' in inspect.signature(engine._download_fallback).parameters:
                engine._download_fallback('selected', timeout=0)
            else:
                engine._download_fallback(timeout=0)
            global_click = page.js('window.wrongDownload')
            engine._normalize_image = lambda _: ('', 'image/png')
            try:
                engine._attach_image('bad-reference')
                rejected = False
            except module.MuseGenerationError:
                rejected = True

            result = {
                'upload_only_accepted': len(upload) > 0,
                'result_sources': [a['src'] for a in atts],
                'extract_b64': extracted.get('b64'),
                'stale_selected': selected['src'],
                'video_selected': video['vSrc'],
                'global_download_clicked': global_click,
                'invalid_reference_rejected': rejected
            }
            assert not result['upload_only_accepted']
            assert result['result_sources'] == ['data:image/png;base64,b3V0cHV0']
            assert result['extract_b64'] == 'c2VsZWN0ZWQ='
            assert result['stale_selected'] == 'new-image'
            assert result['video_selected'] == 'clip.mp4'
            assert not global_click and rejected
        finally:
            engine.stop()
