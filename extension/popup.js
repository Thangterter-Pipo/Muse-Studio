/* MuseStudio Cookie Muse Studio internal logic —— Muse Studio internal logic muse.ai Muse Studio internal logic cookie Muse Studio internal logic POST Muse Studio internal logic musestudio Muse Studio internal logic。
 *
 * Muse Studio internal logic：Muse Studio internal logic chrome.cookies Muse Studio internal logic document.cookie。
 * muse.ai Muse Studio internal logic 4 Muse Studio internal logic cookie（hatch_sess / hatch_gw / hatch_vml /
 * hatch_native_auth_device）Muse Studio internal logic httpOnly，Muse Studio internal logic JS Muse Studio internal logic，
 * Muse Studio internal logic cookies Muse Studio internal logic。
 */

const $ = (id) => document.getElementById(id);
const STORE = 'musestudio_ext_cfg';

const ESSENTIAL = ['hatch_sess', 'hatch_gw', 'hatch_vml', 'hatch_native_auth_device'];

function log(html, cls) {
  const el = $('log');
  el.className = 'show';
  el.innerHTML = cls ? `<span class="${cls}">${html}</span>` : html;
}

/* Muse Studio internal logic：Muse Studio internal logic /v1 Muse Studio internal logic */
function normBase(v) {
  let s = (v || '').trim();
  if (!s) return '';
  if (!/^https?:\/\//i.test(s)) s = 'https://' + s;
  s = s.replace(/\/+$/, '');
  s = s.replace(/\/v1$/i, '');
  return s;
}

async function loadCfg() {
  const o = await chrome.storage.local.get(STORE);
  const c = o[STORE] || {};
  if (c.base) $('base').value = c.base;
  if (c.key) $('key').value = c.key;
  if (c.label) $('label').value = c.label;
  // Muse Studio internal logic（Muse Studio internal logic）
  if (!c.base) {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const u = tab && tab.url ? new URL(tab.url) : null;
      if (u && /\/admin/.test(u.pathname)) {
        $('base').value = u.origin;
        const k = new URLSearchParams(u.search).get('key');
        if (k) $('key').value = k;
      }
    } catch (e) { /*  */ }
  }
}

async function saveCfg() {
  await chrome.storage.local.set({
    [STORE]: {
      base: normBase($('base').value),
      key: $('key').value.trim(),
      label: $('label').value.trim(),
    },
  });
}

async function grabCookies() {
  const all = await chrome.cookies.getAll({ domain: 'muse.ai' });
  const out = {}, exp = {};
  for (const c of all) {
    const dom = (c.domain || '').replace(/^\./, '');
    if (!dom.endsWith('muse.ai')) continue;
    out[c.name] = c.value;
    if (c.expirationDate) exp[c.name] = Math.floor(c.expirationDate);
  }
  return { cookies: out, expires: exp };
}

async function run() {
  const base = normBase($('base').value);
  const key = $('key').value.trim();
  const label = $('label').value.trim();

  if (!base) return log('', 'bad');
  if (!key) return log(' API Key', 'bad');

  $('go').disabled = true;
  log(' muse.ai  Cookie…');

  try {
    const { cookies, expires } = await grabCookies();
    const names = Object.keys(cookies);
    if (!names.length) {
      return log(' muse.ai  Cookie。\n '
                 + 'https://muse.ai/ ，。', 'bad');
    }
    const missing = ESSENTIAL.filter((n) => !(n in cookies));
    if (missing.length) {
      log(` ${names.length}  Cookie，：${missing.join('、')}\n`
          + 'Thanh cong。。', 'warn');
      return;
    }

    log(` ${names.length}  Cookie， ${base} …`);

    const r = await fetch(base + '/admin/accounts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + key,
      },
      body: JSON.stringify({ label, cookies, expires }),
    });

    const text = await r.text();
    let data;
    try { data = JSON.parse(text); } catch (e) { data = { raw: text }; }

    if (r.status === 401) {
      return log('API Key （ 401）。\n'
                 + '「Tai khoan」 API Key。', 'bad');
    }
    if (!r.ok) {
      return log(`That bai：HTTP ${r.status}\n${text.slice(0, 300)}`, 'bad');
    }

    const a = (data.added && data.added[0]) || {};
    await saveCfg();
    log(`✓ Thanh cong\nTai khoan：${a.label || label || '()'}\n`
        + `Tai khoan ID：${a.id || '?'}\nCookie ：${a.cookie_count || names.length}\n`
        + `Hop le：${a.expires_at ? new Date(a.expires_at * 1000).toLocaleString() : 'Khong xac dinh'}\n`
        + (data.warning ? `\n：${data.warning}` : ''), 'ok');
  } catch (e) {
    log('：' + (e && e.message ? e.message : String(e))
        + '\n\n：\n'
        + '· \n'
        + '·  https（）\n'
        + '· ', 'bad');
  } finally {
    $('go').disabled = false;
  }
}

$('go').addEventListener('click', run);
loadCfg();
