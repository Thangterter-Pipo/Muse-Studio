import sys,importlib.util,json
from types import SimpleNamespace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
source = str(Path(__file__).resolve().parents[1] / 'engine.py')
spec = importlib.util.spec_from_file_location('candidate', source)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_vm_wait_attachment():
    clock = [0.0]
    m.time = SimpleNamespace(time=lambda: clock[0], sleep=lambda s: clock.__setitem__(0, clock[0] + s))
    engine = object.__new__(m.MuseEngine)
    engine._scroll_bottom = lambda: None
    engine.page = SimpleNamespace(js=lambda _: json.dumps({'tail': 'Connecting...', 'cnt': 0, 'txt': '', 'stop': True}))
    engine.attachments = lambda: [] if clock[0] < 20 else [{'src': 'generated', 'tid': 'image', 'w': 100, 'h': 100}]
    result = engine._wait_attachment('', 30, 'image')
    assert result['src'] == 'generated'
