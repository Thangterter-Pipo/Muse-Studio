// ==UserScript==
// @name         MuseStudio Cookie Muse Studio internal logic
// @namespace    https://musestudio.local
// @version      1.1.0
// @description  Muse Studio internal logic muse.ai Muse Studio internal logic Cookie Muse Studio internal logic musestudio Tai khoanMuse Studio internal logic，Muse Studio internal logic、Muse Studio internal logic
// @author       MUSE_STUDIO Contributors
// @match        https://muse.ai/*
// @match        https://*.muse.ai/*
// @grant        GM_cookie
// @grant        GM_setClipboard
// @grant        GM_xmlhttpRequest
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_registerMenuCommand
// @connect      *
// @run-at       document-end
// ==/UserScript==

(function () {
  'use strict';

  const STORE_KEY = '***';
  const ESSENTIAL = ['hatch_sess', 'hatch_gw', 'hatch_vml'];

  function loadCfg() {
    const fallback = { base: '', key: '', label: '' };
    if (typeof GM_getValue === 'function') {
      return GM_getValue(STORE_KEY, fallback);
    }
    try {
      return JSON.parse(localStorage.getItem(STORE_KEY)) || fallback;
    } catch (_) {
      return fallback;
    }
  }

  function saveCfg(cfg) {
    if (typeof GM_setValue === 'function') {
      GM_setValue(STORE_KEY, cfg);
    } else {
      localStorage.setItem(STORE_KEY, JSON.stringify(cfg));
    }
  }

  function normBase(v) {
    let s = (v || '').trim();
    if (!s) return '';
    if (!/^https?:\/\//i.test(s)) {
      s = (/^(127\.|100\.|10\.|192\.168\.|localhost)/i.test(s) ? 'http://' : 'https://') + s;
    }
    s = s.replace(/\/+$/, '').replace(/\/v1$/i, '');
    return s;
  }

  function showToast(msg, type = 'info') {
    const el = document.createElement('div');
    el.textContent = msg;
    const bg = type === 'ok' ? '#059669' : type === 'err' ? '#dc2626' : '#2563eb';
    el.style.cssText = `position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:9999999;padding:10px 18px;background:${bg};color:#fff;border-radius:10px;font-size:13px;font-weight:500;font-family:-apple-system,BlinkMacSystemFont,sans-serif;box-shadow:0 12px 30px rgba(0,0,0,0.5);transition:opacity 0.3s;max-width:420px;text-align:center;line-height:1.5;pointer-events:none;`;
    document.body.appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 300);
    }, 4000);
  }

  async function getCookies() {
    const out = {}, exp = {};
    if (typeof GM_cookie !== 'undefined' && typeof GM_cookie.list === 'function') {
      try {
        const queries = [
          { url: 'https://muse.ai/' },
          { domain: '.muse.ai' },
          { domain: 'muse.ai' },
        ];
        const all = [];
        for (const q of queries) {
          try {
            const list = await new Promise((resolve) => {
              GM_cookie.list(q, (cookies, error) => {
                resolve(error ? [] : (cookies || []));
              });
            });
            if (Array.isArray(list)) all.push(...list);
          } catch (_) {}
        }

        for (const c of all) {
          if (!c || !c.name) continue;
          const dom = (c.domain || '').replace(/^\./, '');
          if (!dom.endsWith('muse.ai')) continue;
          out[c.name] = c.value;
          if (c.expirationDate) exp[c.name] = Math.floor(c.expirationDate);
        }
      } catch (_) {}
    }

    try {
      const parts = document.cookie.split(';');
      for (const p of parts) {
        const idx = p.indexOf('=');
        if (idx > 0) {
          const k = p.slice(0, idx).trim();
          const v = p.slice(idx + 1).trim();
          if (k && !(k in out)) out[k] = v;
        }
      }
    } catch (_) {}

    return { cookies: out, expires: exp };
  }

  async function checkSessionStatus() {
    const { cookies } = await getCookies();
    const missing = ESSENTIAL.filter(n => !(n in cookies));
    const hasCore = missing.length === 0;
    return { hasCore, count: Object.keys(cookies).length, missing, cookies };
  }

  async function executePush(btnEl = null) {
    const cfg = loadCfg();
    const base = normBase(cfg.base);
    const key = (cfg.key || '').trim();
    const label = (cfg.label || '').trim();

    if (btnEl) {
      btnEl.disabled = true;
      btnEl.innerHTML = '<span style="opacity:0.8">⏳ …</span>';
    }

    try {
      const { cookies, expires } = await getCookies();
      const names = Object.keys(cookies);

      if (!names.length) {
        showToast(' muse.ai Cookie，Tai khoan！', 'err');
        return;
      }

      const missing = ESSENTIAL.filter(n => !(n in cookies));
      if (missing.length) {
        showToast(` ${names.length}  Cookie，：${missing.join(', ')}。。`, 'err');
        return;
      }

      const cookieStr = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ');
      if (typeof GM_setClipboard === 'function') {
        GM_setClipboard(cookieStr);
      }

      if (!base) {
        showToast('✓  Cookie ！Bat。', 'ok');
        return;
      }

      if (btnEl) btnEl.innerHTML = '<span style="opacity:0.8">🚀 …</span>';

      const headers = { 'Content-Type': 'application/json' };
      if (key) {
        headers['Authorization'] = 'Bearer ' + key;
      }

      const payload = JSON.stringify({ label, cookies, expires });

      const doFetch = () => {
        if (typeof GM_xmlhttpRequest === 'function') {
          return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
              method: 'POST',
              url: base + '/admin/accounts',
              headers: headers,
              data: payload,
              onload: (res) => resolve({ ok: res.status >= 200 && res.status < 300, status: res.status, text: () => Promise.resolve(res.responseText) }),
              onerror: reject,
              ontimeout: reject,
            });
          });
        }
        return fetch(base + '/admin/accounts', { method: 'POST', headers, body: payload });
      };

      const r = await doFetch();
      const txt = await r.text();
      let data = {};
      try { data = JSON.parse(txt); } catch (_) {}

      if (r.status === 401) {
        showToast('That bai：API Key  (401)', 'err');
        return;
      }
      if (!r.ok) {
        showToast(`That bai (HTTP ${r.status})：${txt.slice(0, 80)}。 Cookie ！`, 'err');
        return;
      }

      const a = (data.added && data.added[0]) || {};
      const expDate = a.expires_at ? new Date(a.expires_at * 1000).toLocaleDateString() : 'Hop le';
      showToast(`✓ Tai khoanThanh cong musestudio！\nID: ${a.id || '?'}\nHop le: ${expDate}`, 'ok');
      updateStatusBadge();
    } catch (e) {
      showToast(`：${e.message || e}。 Cookie ！`, 'err');
    } finally {
      if (btnEl) {
        btnEl.disabled = false;
        btnEl.innerHTML = '⚡ Tai khoan';
      }
    }
  }

  async function updateStatusBadge() {
    const badge = document.getElementById('muse-status-tag');
    if (!badge) return;
    const st = await checkSessionStatus();
    if (st.hasCore) {
      badge.style.color = '#22c55e';
      badge.textContent = `✓  (${st.count} )`;
    } else {
      badge.style.color = '#f59e0b';
      badge.textContent = `⚠ `;
    }
  }

  function togglePanel() {
    const existing = document.getElementById('musestudio-token-panel');
    if (existing) {
      existing.remove();
      return;
    }
    showPanel();
  }

  function showPanel() {
    if (document.getElementById('musestudio-token-panel')) {
      document.getElementById('musestudio-token-panel').remove();
    }

    const cfg = loadCfg();
    const panel = document.createElement('div');
    panel.id = 'musestudio-token-panel';
    panel.innerHTML = `
      <div style="position:fixed; top:20px; right:20px; z-index:999999;
                  background:linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 15, 30, 0.96) 100%);
                  color:#f8fafc; padding:20px 22px; width:360px; max-width:calc(100vw - 40px);
                  border-radius:16px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                  box-shadow:0 20px 50px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(96, 165, 250, 0.25);
                  backdrop-filter:blur(16px); font-size:13px; line-height:1.4;">
        
        <!-- Muse Studio internal logic -->
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid #1e293b;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#38bdf8; box-shadow:0 0 10px #38bdf8;"></span>
            <b style="font-size:15px; color:#f1f5f9; letter-spacing:0.3px;">musestudio </b>
            <span style="font-size:11px; background:#1e293b; color:#94a3b8; padding:1px 6px; border-radius:6px;">v1.1</span>
          </div>
          <button id="muse-close-btn" style="background:transparent; border:none; color:#64748b; font-size:18px; cursor:pointer; padding:0 4px; line-height:1;">✕</button>
        </div>

        <!-- Muse Studio internal logic -->
        <div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:10px 12px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:12px; color:#94a3b8;"></span>
          <span id="muse-status-tag" style="font-size:12px; font-weight:600; color:#94a3b8;">…</span>
        </div>

        <!-- Muse Studio internal logic（Muse Studio internal logic，Muse Studio internal logic） -->
        <div style="margin-bottom:12px;">
          <div style="font-size:11px; color:#94a3b8; margin-bottom:5px; font-weight:500;"> (Base URL)</div>
          <input id="muse-cfg-base" type="text" placeholder=" https://muse.yourdomain.com  http://localhost:18610"
                 value="${cfg.base || ''}"
                 style="width:100%; box-sizing:border-box; padding:8px 11px; background:#0b1120; border:1px solid #334155;
                        border-radius:8px; color:#f1f5f9; font-size:12px; font-family:monospace; outline:none; transition:border-color 0.2s;">
        </div>

        <div style="margin-bottom:12px;">
          <div style="font-size:11px; color:#94a3b8; margin-bottom:5px; font-weight:500;">API Key（）</div>
          <input id="muse-cfg-key" type="password" placeholder="mst_..."
                 value="${cfg.key || ''}"
                 style="width:100%; box-sizing:border-box; padding:8px 11px; background:#0b1120; border:1px solid #334155;
                        border-radius:8px; color:#f1f5f9; font-size:12px; font-family:monospace; outline:none;">
        </div>

        <div style="margin-bottom:16px;">
          <div style="font-size:11px; color:#94a3b8; margin-bottom:5px; font-weight:500;">Tai khoan ()</div>
          <input id="muse-cfg-label" type="text" placeholder=" acc-01（）"
                 value="${cfg.label || ''}"
                 style="width:100%; box-sizing:border-box; padding:8px 11px; background:#0b1120; border:1px solid #334155;
                        border-radius:8px; color:#f1f5f9; font-size:12px; outline:none;">
        </div>

        <!-- Muse Studio internal logic -->
        <div style="display:flex; flex-direction:column; gap:8px;">
          <button id="muse-action-push" style="width:100%; padding:10px 0; border:none; border-radius:10px;
                  background:linear-gradient(135deg, #0284c7, #2563eb); color:#fff;
                  font-weight:600; font-size:13px; cursor:pointer; box-shadow:0 4px 14px rgba(37, 99, 235, 0.4);
                  transition:all 0.2s;">
            ⚡ Tai khoan
          </button>

          <div style="display:flex; gap:8px;">
            <button id="muse-action-copy" style="flex:1; padding:7px 0; border:1px solid #334155; border-radius:8px;
                    background:#0f172a; color:#cbd5e1; font-size:12px; cursor:pointer; transition:all 0.2s;">
              📋  Cookie
            </button>
            <button id="muse-action-save" style="flex:1; padding:7px 0; border:1px solid #334155; border-radius:8px;
                    background:#0f172a; color:#cbd5e1; font-size:12px; cursor:pointer; transition:all 0.2s;">
              💾 Luu
            </button>
          </div>
        </div>

        <!-- Muse Studio internal logic -->
        <div style="margin-top:14px; padding-top:10px; border-top:1px solid #1e293b; display:flex; justify-content:space-between; align-items:center; font-size:11px; color:#64748b;">
          <span>Luu</span>
          <span> Esc Dong</span>
        </div>
      </div>
    `;

    document.body.appendChild(panel);
    updateStatusBadge();

    // Muse Studio internal logicLuu
    const baseIn = document.getElementById('muse-cfg-base');
    const keyIn = document.getElementById('muse-cfg-key');
    const labelIn = document.getElementById('muse-cfg-label');

    function saveInputs() {
      const newCfg = {
        base: normBase(baseIn.value),
        key: keyIn.value.trim(),
        label: labelIn.value.trim(),
      };
      saveCfg(newCfg);
      return newCfg;
    }

    baseIn.addEventListener('change', saveInputs);
    keyIn.addEventListener('change', saveInputs);
    labelIn.addEventListener('change', saveInputs);

    document.getElementById('muse-close-btn').onclick = () => panel.remove();
    document.getElementById('muse-action-save').onclick = () => {
      saveInputs();
      showToast('✓ Luu！', 'ok');
    };

    document.getElementById('muse-action-copy').onclick = async () => {
      const { cookies } = await getCookies();
      const str = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ');
      if (str) {
        if (typeof GM_setClipboard === 'function') GM_setClipboard(str);
        showToast('✓  Cookie ！', 'ok');
      } else {
        showToast(' Cookie！', 'err');
      }
    };

    document.getElementById('muse-action-push').onclick = function () {
      saveInputs();
      executePush(this);
    };
  }

  function mountFloatingTrigger() {
    if (document.getElementById('musestudio-floating-ball')) return;
    const ball = document.createElement('div');
    ball.id = 'musestudio-floating-ball';
    ball.innerHTML = `
      <div style="position:fixed; bottom:24px; right:24px; z-index:999990;
                  width:42px; height:42px; border-radius:50%; background:linear-gradient(135deg, #0284c7, #2563eb);
                  color:#fff; display:flex; align-items:center; justify-content:center;
                  cursor:pointer; box-shadow:0 8px 24px rgba(37, 99, 235, 0.45); font-size:18px;
                  user-select:none; transition:transform 0.2s, box-shadow 0.2s;"
           title=" musestudio "
           onmouseover="this.style.transform='scale(1.08)'"
           onmouseout="this.style.transform='scale(1)'">
        ⚡
      </div>
    `;
    ball.addEventListener('click', togglePanel);
    document.body.appendChild(ball);
  }

  if (typeof GM_registerMenuCommand === 'function') {
    GM_registerMenuCommand('🚀  musestudio ', togglePanel);
    GM_registerMenuCommand('⚡ Tai khoan', () => executePush());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountFloatingTrigger);
  } else {
    mountFloatingTrigger();
  }
})();
