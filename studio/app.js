/* Muse Studio frontend for musestudio (FastAPI 1.5.x).
 * No third-party JavaScript dependencies. No demo/mock business metrics.
 */
(() => {
'use strict';
const ICONS = {
  'layout-dashboard':'<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
  sparkles:'<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3Z"/><path d="m20 18 .6 1.5L22 20l-1.4.5L20 22l-.6-1.5L18 20l1.4-.5L20 18ZM4 2l.7 1.3L6 4l-1.3.7L4 6l-.7-1.3L2 4l1.3-.7L4 2Z"/>',
  users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  'list-checks':'<path d="m3 7 2 2 4-4M3 17l2 2 4-4M13 6h8M13 18h8"/>',
  images:'<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>',
  braces:'<path d="M8 3H6a2 2 0 0 0-2 2v4a2 2 0 0 1-2 2 2 2 0 0 1 2 2v6a2 2 0 0 0 2 2h2M16 3h2a2 2 0 0 1 2 2v4a2 2 0 0 0 2 2 2 2 0 0 0-2 2v6a2 2 0 0 1-2 2h-2"/>',
  'settings-2':'<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',
  'refresh-cw':'<path d="M20 11a8 8 0 0 0-14-5L4 8m0-5v5h5M4 13a8 8 0 0 0 14 5l2-2m0 5v-5h-5"/>',
  menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
  ellipsis:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  arrow:'<path d="M5 12h14m-7-7 7 7-7 7"/>',
  'external-link':'<path d="M13 5h6v6M19 5l-9 9"/><path d="M19 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>',
  'circle-check':'<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  'alert-circle':'<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 17h.01"/>',
  server:'<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 8h.01M7 17h.01"/>',
  activity:'<path d="M3 12h4l3-7 4 14 3-7h4"/>',
  film:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 3v18M17 3v18M3 8h4m-4 8h4m10-8h4m-4 8h4"/>',
  image:'<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>',
  message:'<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8A8.5 8.5 0 0 1 12.5 20a8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8A8.5 8.5 0 0 1 12.5 3h.5A8.5 8.5 0 0 1 21 11v.5Z"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  trash:'<path d="M3 6h18M8 6V4h8v2m3 0-1 15H6L5 6M10 10v7m4-7v7"/>',
  download:'<path d="M12 3v12m-4-4 4 4 4-4M5 18v3h14v-3"/>',
  play:'<path d="m8 5 12 7-12 7V5Z"/>',
  plus:'<path d="M12 5v14M5 12h14"/>',
  x:'<path d="M18 6 6 18M6 6l12 12"/>',
  eye:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  'eye-off':'<path d="M2 2l20 20M10.6 5.1A10.7 10.7 0 0 1 12 5c6 0 10 7 10 7a17 17 0 0 1-3.2 3.7M6 6C3.4 7.5 2 12 2 12s4 7 10 7a10.2 10.2 0 0 0 4.3-.9"/>',
  copy:'<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
  bolt:'<path d="m13 2-9 11h7l-1 9 10-12h-7l0-8Z"/>',
  moon:'<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  shield:'<path d="m12 22 7-4V6l-7-4-7 4v12l7 4Z"/><path d="m9 12 2 2 4-4"/>',
  'file-up':'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M12 18v-7m-3 3 3-3 3 3"/>'
};
const icon=(name,size=18)=>`<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]||ICONS.sparkles}</svg>`;
const escapeHTML=(s)=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $=(sel,scope=document)=>scope.querySelector(sel);
const $$=(sel,scope=document)=>Array.from(scope.querySelectorAll(sel));
const labels={dashboard:'Tổng quan',playground:'AI Playground',accounts:'Tài khoản Muse',tasks:'Hàng đợi tác vụ',media:'Thư viện media',api:'API & kết nối',settings:'Cài đặt'};
const state={base:localStorage.getItem('muse_studio_base')||'',key:sessionStorage.getItem('muse_studio_key')||'',page:'dashboard',tab:'image',busy:false,status:null,accounts:[],tasks:[],media:[],models:[],apiKeys:[],imageTask:null,videoTask:null,preview:null,reference:null,referenceName:'',messages:[],chatBusy:false,chatAbort:null,pollTimers:{image:null,video:null},refreshTimer:null,showKey:false};
// Back-end expects base origin, not /v1. Prevent inadvertent remote-relative URL confusion.
function cleanBase(v){let x=String(v||'').trim().replace(/\/+$/,'');x=x.replace(/\/v1$/,'');return x;}
function apiUrl(path){return `${state.base||window.location.origin}${path}`;}
async function request(path,{method='GET',body,signal,headers={},timeout=25000,plain=false}={}){
  const ctl=new AbortController();const t=setTimeout(()=>ctl.abort(),timeout);
  if(signal)signal.addEventListener('abort',()=>ctl.abort(),{once:true});
  try{
    const response=await fetch(apiUrl(path),{method,signal:ctl.signal,headers:{...(state.key?{Authorization:`Bearer ${state.key}`}:{}) ,...(body!==undefined?{'Content-Type':'application/json'}:{}),...headers},...(body===undefined?{}:{body:JSON.stringify(body)})});
    if(plain)return response;
    const payload=await response.json().catch(()=>({}));
    if(!response.ok){
      if(response.status===401) throw new Error('Chưa nhập hoặc sai MUSE_STUDIO_KEY. Hãy kiểm tra tab Cài đặt (⚙).');
      const msg=payload?.error?.message||payload?.detail||`HTTP ${response.status}`;
      throw new Error(typeof msg==='string'?msg:JSON.stringify(msg));
    }
    return payload;
  }catch(e){if(e.name==='AbortError'&&signal?.aborted)throw e; if(e.name==='AbortError')throw new Error('Yêu cầu đã quá thời gian chờ');throw e}
  finally{clearTimeout(t)}
}
const post=(url,body={})=>request(url,{method:'POST',body});
const patch=(url,body)=>request(url,{method:'PATCH',body});
const remove=(url)=>request(url,{method:'DELETE'});
const short=(s,n=30)=>{s=String(s||'');return s.length>n?s.slice(0,n-1)+'…':s};
const fmtDate=(ts)=>{if(!ts)return '—';let n=Number(ts);if(!Number.isFinite(n))return '—';return new Date(n<1e12?n*1000:n).toLocaleString('vi-VN',{dateStyle:'short',timeStyle:'short'})};
const fmtBytes=(v)=>{if(!Number.isFinite(Number(v)))return '—';let n=Number(v),i=0;while(n>=1024&&i<4){n/=1024;i++}return `${n.toFixed(i?1:0)} ${['B','KB','MB','GB','TB'][i]}`};
const accountState=(a)=>!a.enabled?'disabled':a.ok===true?'good':a.ok===false?'bad':'unknown';
const accountBadge=(a)=>{const s=accountState(a);return s==='good'?chip('Khả dụng'):s==='bad'?chip('Lỗi phiên','error'):s==='disabled'?chip('Đã tắt','neutral'):chip('Chưa kiểm tra','warning')};
function chip(txt,type=''){return `<span class="chip ${type}"><span class="mini-dot"></span>${escapeHTML(txt)}</span>`;}
function taskState(t){const s=String(t.status||'').toLowerCase();return ['succeeded','success','done','complete','completed'].includes(s)?'completed':['failed','error'].includes(s)?'failed':['processing','running','in_progress'].includes(s)?'processing':s||'queued';}
function taskBadge(t){const s=taskState(t);return s==='completed'?chip('Hoàn tất'):s==='failed'?chip('Thất bại','error'):s==='processing'?chip('Đang xử lý','warning'):chip('Chờ xử lý','neutral');}
function mediaLink(item){
  const name=item?.name||item?.filename||'';
  if(name)return apiUrl(`/v1/media/${encodeURIComponent(name)}`);
  const raw=item?.url||item?.result?.url||item?.data?.[0]?.url||'';
  try{const u=new URL(raw,apiUrl('/'));if(u.pathname.startsWith('/v1/media/'))return apiUrl(u.pathname);if(u.protocol==='https:'||u.protocol==='http:')return u.href;}catch{}return '';
}
function resultUrl(t){if(t?.result?.filename)return mediaLink({name:t.result.filename});return mediaLink({url:t?.url||t?.result?.url||t?.data?.[0]?.url});}
function toast(message,error=false){const layer=$('#toast-layer');const el=document.createElement('div');el.className='toast'+(error?' error':'');el.textContent=String(message);layer.append(el);setTimeout(()=>el.remove(),4500)}
function header(title,subtitle,actions=''){return `<div class="page-heading"><div><div class="eyebrow">${icon('sparkles',13)} MUSE STUDIO · ${escapeHTML(title)}</div><h1>${escapeHTML(title)}</h1><p class="subtitle">${subtitle}</p></div><div class="heading-actions">${actions}</div></div>`}
function empty(title,desc=''){return `<div class="empty"><div class="empty-icon">✧</div><strong>${escapeHTML(title)}</strong>${desc?`<p style="margin-top:7px">${escapeHTML(desc)}</p>`:''}</div>`}
const navbtn=(text,page)=>`<button class="btn" data-nav="${page}">${text} ${icon('arrow',15)}</button>`;
function getMetrics(){const acc=state.accounts||[],tasks=state.tasks||[];return {total:acc.length,ready:acc.filter(x=>accountState(x)==='good').length,active:tasks.filter(x=>['processing','queued'].includes(taskState(x))).length,done:tasks.filter(x=>taskState(x)==='completed').length,failed:tasks.filter(x=>taskState(x)==='failed').length,media:state.status?.media_count??state.media.length};}
function renderDashboard(){const m=getMetrics(),tasks=state.tasks.slice(0,5),connected=Boolean(state.status);return `
${header('Tổng quan', 'Quản lý sáng tạo và vận hành Muse từ một không gian duy nhất.', `<button class="btn" id="dash-refresh">${icon('refresh-cw')} Làm mới</button><button class="btn primary" data-nav="playground">${icon('plus')} Tạo mới</button>`)}
<div class="hero-banner"><div class="hero-copy"><div class="hero-tag">${icon('sparkles',13)} YOUR CREATIVE WORKSPACE</div><h2>Biến ý tưởng thành hình ảnh,<br>video và những điều phi thường.</h2><p>Kiểm soát toàn bộ quy trình sáng tạo AI cùng Muse Studio.</p><button class="hero-action" data-nav="playground">Khám phá Playground &nbsp; ↗</button></div><div class="hero-orbit"></div><div class="hero-star">✦</div><div class="hero-micro">Create without limits ✧</div></div>
${!connected?`<div class="notice warning" style="margin-bottom:19px">${icon('alert-circle')} Chưa có dữ liệu backend. Hãy cấu hình địa chỉ và API key, sau đó kiểm tra kết nối. <button class="btn small" style="margin-left:auto" data-nav="settings">Kết nối</button></div>`:''}
<div class="stats-grid">
${stat('Tổng tài khoản',connected?m.total:'—','users','purple','Tài khoản trong pool')}
${stat('Tài khoản khả dụng',connected?m.ready:'—','circle-check','green','Trạng thái được xác minh gần nhất')}
${stat('Tác vụ đang chạy',connected?m.active:'—','activity','orange','Bao gồm cả tác vụ chờ')}
${stat('Media đã tạo',connected?m.media:'—','images','blue','Tệp được lưu trên backend')}
</div>
<div class="two-cols">
  <section class="panel"><div class="panel-head"><div><h2>Hoạt động gần đây</h2><small>Số tác vụ theo ngày từ lịch sử backend</small></div>${chip('7 ngày','neutral')}</div>${activityChart()}</section>
  <section class="panel"><div class="panel-head"><div><h2>Trạng thái hệ thống</h2><small>Thông tin dịch vụ theo thời gian thực</small></div></div>
  <div class="health-list">
    ${healthRow('API Server','FastAPI · /healthz',connected?'Hoạt động':'Chưa kết nối','server',connected)}
    ${healthRow('Trình duyệt Chromium','CDP execution engine',state.status?.browser_running?'Đã khởi động':'Chưa chạy','activity',Boolean(state.status?.browser_running))}
    ${healthRow('Account pool',`${m.total} tài khoản đã thêm`,m.ready?'Có tài khoản':'Cần kiểm tra','users',Boolean(m.ready))}
    ${healthRow('Model gateway','Chat · Image · Video',connected?'Sẵn sàng API':'Chưa kết nối','bolt',connected)}
  </div></section>
</div>
<section class="panel"><div class="panel-head"><div><h2>Tác vụ mới nhất</h2><small>Theo dõi yêu cầu vừa thực hiện</small></div><button class="link" data-nav="tasks">Xem tất cả →</button></div>${taskTable(tasks)}</section>
<section class="section-gap"><div class="split-top"><div><h2>Khởi đầu sáng tạo</h2><p class="subtitle">Chọn một công cụ để bắt đầu.</p></div></div><div class="cards-grid">${featureCard('Sáng tạo hình ảnh','Tạo ảnh từ mô tả, đa tỉ lệ và ảnh tham chiếu.','image','violet','image')}${featureCard('Sản xuất video','Biến ý tưởng thành thước phim AI hấp dẫn.','film','orange','video')}${featureCard('Trò chuyện Muse','Sáng tác, viết mã và khám phá ý tưởng mới.','message','blue','chat')}</div></section>`}
function stat(name,value,ico,color,foot){return `<section class="stat-card"><div class="stat-top"><span>${escapeHTML(name)}</span><div class="stat-icon ${color}">${icon(ico)}</div></div><div class="stat-value">${value}</div><div class="stat-foot">${escapeHTML(foot)}</div></section>`}
function healthRow(name,detail,status,ico,good){return `<div class="health-row"><div class="health-ico">${icon(ico)}</div><div class="health-desc"><b>${escapeHTML(name)}</b><small>${escapeHTML(detail)}</small></div>${chip(status,good?'':'warning')}</div>`}
function activityChart(){const now=new Date();now.setHours(0,0,0,0);const days=Array.from({length:7},(_,i)=>{let dt=new Date(now);dt.setDate(dt.getDate()-(6-i));return dt});const counts=days.map(day=>state.tasks.filter(t=>{const ts=Number(t.created_at||0);const d=new Date(ts<1e12?ts*1000:ts);return !Number.isNaN(d.getTime())&&d.getFullYear()===day.getFullYear()&&d.getMonth()===day.getMonth()&&d.getDate()===day.getDate()}).length);const max=Math.max(1,...counts);return `<div class="chart-frame"><div class="chart-y"><span></span><span></span><span></span><span></span></div><div class="chart-bars">${days.map((d,i)=>`<div class="chart-col"><div class="chart-bar ${counts[i]?'':'zero'}" style="height:${Math.max(3,counts[i]/max*95)}%" title="${d.toLocaleDateString('vi-VN')}: ${counts[i]} tác vụ"></div><div class="chart-day">${d.getDate()}/${d.getMonth()+1}</div></div>`).join('')}</div>${!counts.some(Boolean)?'<span class="chart-empty">Chưa có hoạt động trong 7 ngày</span>':''}</div>`}
function featureCard(title,desc,ico,color,tab){return `<article class="feature-card" data-tab-nav="${tab}"><div class="feature-ico ${color}">${icon(ico,26)}</div><h3>${title}</h3><p>${desc}</p><span>Khám phá →</span></article>`}
function taskTable(tasks){return tasks.length?`<div class="table-wrap"><table class="table"><thead><tr><th>Tác vụ</th><th>Loại</th><th>Trạng thái</th><th>Tiến độ</th><th>Thời gian</th><th></th></tr></thead><tbody>${tasks.map(t=>`<tr><td><strong>${escapeHTML(short(t.prompt||t.id,43))}</strong><span class="subtext">${escapeHTML(short(t.id,20))}</span></td><td>${t.kind==='video'?icon('film',15):icon('image',15)} <span>${t.kind==='video'?'Video':'Ảnh'}</span></td><td>${taskBadge(t)}</td><td style="min-width:115px"><div style="display:flex;gap:10px;align-items:center"><div class="progress" style="width:75px"><span style="width:${Math.max(0,Math.min(100,Number(t.progress)||0))}%"></span></div><small>${Math.round(Number(t.progress)||0)}%</small></div></td><td>${fmtDate(t.created_at)}</td><td><div class="table-actions">${taskState(t)==='completed'&&resultUrl(t)?`<button class="tiny" data-open-url="${escapeHTML(resultUrl(t))}" title="Xem kết quả">${icon('external-link')}</button>`:''}<button class="tiny" data-remove-task="${escapeHTML(t.id)}" title="Xóa tác vụ">${icon('trash')}</button></div></td></tr>`).join('')}</tbody></table></div>`:empty('Chưa có tác vụ','Tác vụ tạo ảnh và video sẽ xuất hiện tại đây.')}
function renderAccounts(){return `${header('Tài khoản Muse','Theo dõi trạng thái đăng nhập, hạn mức và phân bổ tài khoản.',`<button class="btn" id="keepalive-all">${icon('refresh-cw')} Gia hạn toàn bộ</button><button class="btn" id="autox-account">${icon('eye')} Tự động trích xuất</button><button class="btn primary" id="add-account">${icon('plus')} Thêm tài khoản</button>`)}
<div class="stats-grid">${stat('Tổng tài khoản',state.accounts.length,'users','purple','Tất cả tài khoản')}${stat('Đã xác minh',state.accounts.filter(a=>a.ok===true&&a.enabled).length,'circle-check','green','Trạng thái gần nhất')}${stat('Lỗi / hết phiên',state.accounts.filter(a=>a.ok===false&&a.enabled).length,'alert-circle','orange','Cần kiểm tra')}${stat('Đang bật',state.accounts.filter(a=>a.enabled).length,'activity','blue','Được phép điều phối')}</div>
<div class="notice" style="margin-bottom:21px">${icon('shield')} Đánh giá tình trạng dựa trên lần xác minh gần nhất. "Khả dụng" không đồng nghĩa chắc chắn còn hạn mức hoặc luôn kết nối được tới Muse.</div>
<div class="panel"><div class="split-top"><div><h2>Account pool</h2><p class="subtitle">Tài khoản và quota được đồng bộ từ musestudio.</p></div><div class="searchbox">${icon('search')}<input id="accounts-search" placeholder="Tìm tài khoản..." aria-label="Tìm tài khoản"></div></div><div id="accounts-list">${accountTable(state.accounts)}</div></div>`}
function accountTable(accounts){return accounts.length?`<div class="table-wrap"><table class="table"><thead><tr><th>Tài khoản</th><th>Trạng thái</th><th style="min-width:240px">Gói & Hạn mức sử dụng</th><th>Phiên hết hạn</th><th>Kích hoạt</th><th>Thao tác</th></tr></thead><tbody>${accounts.map(a=>{
  const q = a.quota || {};
  const weeklyPct = q.weekly_used_pct != null ? Math.max(0, Math.min(100, Math.round(Number(q.weekly_used_pct)))) : null;
  const extraPct = q.extra_used_pct != null ? Math.max(0, Math.min(100, Math.round(Number(q.extra_used_pct)))) : null;
  return `<tr><td><strong>${escapeHTML(a.label||'Muse Account')}</strong><span class="subtext">${escapeHTML(short(a.id,24))}</span></td><td>${accountBadge(a)}</td>
  <td>
    <div style="display:flex;flex-direction:column;gap:7px;padding:3px 0">
      <div>
        <div style="display:flex;justify-content:space-between;font-size:11px;font-weight:700;margin-bottom:3px">
          <span>${escapeHTML(q.plan || 'Gói miễn phí')}</span>
          <span style="color:#7458ed">${weeklyPct != null ? weeklyPct + '%' : '—'}</span>
        </div>
        <div class="progress" style="height:6px;background:#eef0f6"><span style="width:${weeklyPct || 0}%;background:#7458ed"></span></div>
        ${q.weekly_reset ? `<small style="font-size:9.5px;color:#9da4b5;display:block;margin-top:2px">Đặt lại: ${escapeHTML(q.weekly_reset)}</small>` : ''}
      </div>
      ${(q.extra_left || q.extra_expires || extraPct != null) ? `
      <div style="border-top:1px dashed #ebedf4;padding-top:5px;margin-top:2px">
        <div style="display:flex;justify-content:space-between;font-size:10.5px;color:#555">
          <span>Token bổ sung</span>
          <span style="font-weight:700">${escapeHTML(q.extra_left || '0%')}</span>
        </div>
        <div class="progress" style="height:5px;background:#eef0f6;margin-top:3px"><span style="width:${extraPct || 0}%;background:#27c78e"></span></div>
        ${q.extra_expires ? `<small style="font-size:9px;color:#a0a6b8;display:block;margin-top:2px">Thời hạn: ${q.extra_expires === 'never' ? 'Không bao giờ hết hạn' : escapeHTML(q.extra_expires)}</small>` : ''}
      </div>` : ''}
    </div>
  </td>
  <td>${fmtDate(a.expires_at)}</td><td><button type="button" class="switch ${a.enabled?'on':''}" role="switch" aria-checked="${Boolean(a.enabled)}" aria-label="Bật tắt ${escapeHTML(a.label)}" data-toggle-account="${escapeHTML(a.id)}"></button></td><td><div class="table-actions"><button class="tiny" data-test-account="${escapeHTML(a.id)}" title="Kiểm tra tài khoản">${icon('activity')}</button><button class="tiny" data-quota-account="${escapeHTML(a.id)}" title="Lấy quota">${icon('bolt')}</button><button class="tiny" data-rename-account="${escapeHTML(a.id)}" title="Đổi tên">${icon('settings-2')}</button><button class="tiny" data-delete-account="${escapeHTML(a.id)}" title="Xóa">${icon('trash')}</button></div></td></tr>`}).join('')}</tbody></table></div>`:empty('Chưa có tài khoản','Nhấn "Thêm tài khoản" để nhập cookie từ Muse.')}
function renderTasks(){return `${header('Hàng đợi tác vụ','Giám sát tiến độ bất đồng bộ và chẩn đoán lỗi thực tế từ backend.',`<button class="btn" id="tasks-refresh">${icon('refresh-cw')} Cập nhật</button><button class="btn critical" id="clear-tasks">${icon('trash')} Dọn lịch sử</button>`)}
<div class="stats-grid">${stat('Tổng tác vụ',state.tasks.length,'list-checks','purple','Trong lịch sử hiện tại')}${stat('Đang xử lý',state.tasks.filter(t=>taskState(t)==='processing'||taskState(t)==='queued').length,'clock','orange','Được theo dõi tự động')}${stat('Hoàn tất',state.tasks.filter(t=>taskState(t)==='completed').length,'circle-check','green','Tạo nội dung thành công')}${stat('Thất bại',state.tasks.filter(t=>taskState(t)==='failed').length,'alert-circle','blue','Xem chi tiết lỗi trong bảng')}</div>
<section class="panel"><div class="split-top"><h2>Tất cả tác vụ</h2><div class="toolbar-actions"><select class="form-control" id="task-filter" aria-label="Lọc tác vụ" style="width:165px"><option value="all">Tất cả trạng thái</option><option value="processing">Đang xử lý</option><option value="completed">Hoàn tất</option><option value="failed">Thất bại</option></select></div></div><div id="tasks-list">${taskTable(state.tasks)}</div></section>`}
function renderMedia(){return `${header('Thư viện media','Hình ảnh và video được lưu trữ trực tiếp trên máy chủ.',`<button class="btn" id="media-refresh">${icon('refresh-cw')} Đồng bộ</button><button class="btn primary" data-nav="playground">${icon('plus')} Tạo media</button>`)}
<div class="split-top"><div class="tabs" style="margin:0"><button class="tab active" data-media-filter="all">Tất cả</button><button class="tab" data-media-filter="image">Hình ảnh</button><button class="tab" data-media-filter="video">Video</button></div><div class="searchbox">${icon('search')}<input id="media-search" placeholder="Tìm theo tên tệp..." aria-label="Tìm media"></div></div><div id="media-list" style="margin-top:20px">${mediaGrid(state.media)}</div>`}
function mediaGrid(list){return list.length?`<div class="media-grid">${list.map(item=>{const u=mediaLink(item);return `<article class="media-card"><div class="media-img">${item.kind==='video'?`<video src="${escapeHTML(u)}#t=0.1" preload="metadata" muted playsinline></video>`:`<img src="${escapeHTML(u)}" loading="lazy" alt="${escapeHTML(item.name)}">`}</div><div class="media-info"><strong title="${escapeHTML(item.name)}">${escapeHTML(item.name)}</strong><small>${fmtBytes(item.bytes)} · ${fmtDate(item.mtime)}</small><div class="media-acts"><button class="btn small" data-open-url="${escapeHTML(u)}">${icon('eye',13)} Xem</button><button class="btn small" data-download-name="${escapeHTML(item.name)}">${icon('download',13)} Tải</button><button class="btn small critical" data-delete-media="${escapeHTML(item.name)}" aria-label="Xóa tệp">${icon('trash',13)}</button></div></div></article>`}).join('')}</div>`:empty('Thư viện đang trống','Các ảnh và video hoàn tất sẽ được lưu ở đây.')}
function renderPlayground(){const tabs=[['image','Tạo ảnh'],['video','Tạo video'],['chat','Chat Muse']];return `${header('AI Playground','Không gian sáng tạo kết nối trực tiếp đến Muse Spark, Image và Video.',`<button class="btn" data-nav="media">${icon('images')} Xem thư viện</button>`)}<div class="tabs">${tabs.map(([id,label])=>`<button class="tab ${state.tab===id?'active':''}" data-play-tab="${id}">${label}</button>`).join('')}</div><div id="generator-root">${state.tab==='image'?imageUI():state.tab==='video'?videoUI():chatUI()}</div>`}
function refUpload(){return `<div class="form-field"><label class="form-label">Ảnh tham chiếu <span class="muted" style="font-weight:400">(tùy chọn)</span></label><label class="upload">${state.reference?`<img class="upload-preview" src="${state.reference}" alt="Ảnh tham chiếu"><small>${escapeHTML(state.referenceName)} · Nhấn để đổi ảnh</small>`:`${icon('file-up',23)}<b>Chọn ảnh tham chiếu</b><small>PNG, JPG, WebP · tối đa 10 MB</small>`}<input id="reference-file" type="file" accept="image/png,image/jpeg,image/webp" aria-label="Chọn ảnh tham chiếu"></label>${state.reference?`<button class="btn small ghost" id="clear-reference">Bỏ ảnh tham chiếu</button>`:''}</div>`}
function imageUI(){const t=state.imageTask;return `<div class="generator-grid"><section class="panel"><div class="editor-title"><div class="editor-icon">${icon('image',20)}</div><div><h2>Image Generation</h2><p>Text-to-Image · Image-to-Image</p></div></div><form id="image-form"><div class="form-field"><label class="form-label" for="image-prompt">Mô tả hình ảnh</label><textarea class="form-control prompt-field" id="image-prompt" required placeholder="Một căn nhà giữa khu rừng huyền ảo, ánh nắng xuyên qua tán cây, cinematic lighting...">${escapeHTML(state.imagePrompt||'')}</textarea><div class="prompt-tips"><span>Viết mô tả càng cụ thể càng tốt</span><span>muse-image</span></div></div><div class="form-row"><div class="form-field"><label class="form-label" for="image-ratio">Tỉ lệ khung hình</label><select id="image-ratio" class="form-control">${['16:9','1:1','9:16','4:3','3:4'].map(x=>`<option ${state.imageRatio===x?'selected':''}>${x}</option>`).join('')}</select></div><div class="form-field"><label class="form-label">Mô hình</label><input class="form-control" value="muse-image" disabled></div></div>${refUpload()}<button class="btn primary generate-button" type="submit" ${state.busy?'disabled':''}>${state.busy?icon('refresh-cw'):icon('sparkles')} ${state.busy?'Đang tạo ảnh...':'Tạo hình ảnh'}</button></form></section><section class="panel"><div class="panel-head"><div><h2>Kết quả sáng tạo</h2><small>${t?'Trạng thái tác vụ #'+escapeHTML(short(t.id,10)):'Sản phẩm được tạo từ Muse AI'}</small></div>${t?taskBadge(t):chip('Đang chờ','neutral')}</div><div class="result-window ${t&&taskState(t)==='completed'&&resultUrl(t)?'has-result':''}">${t&&taskState(t)==='completed'&&resultUrl(t)?`<img src="${escapeHTML(resultUrl(t))}" alt="Ảnh đã tạo">`:`<div class="result-placeholder"><div class="symbol">✦</div><h3>${t&&taskState(t)==='failed'?'Tạo ảnh thất bại':t?'Đang xử lý yêu cầu':'Sẵn sàng cho ý tưởng của bạn'}</h3><p>${t&&taskState(t)==='failed'?escapeHTML(t.error||'Backend không thể tạo ảnh'):t?'Hệ thống đang xử lý ảnh. Tiến độ sẽ được cập nhật tự động.':'Hãy nhập mô tả ở bên trái và nhấn Tạo hình ảnh.'}</p></div>`}</div><div class="result-meta"><span>${t?escapeHTML(t.status||'queued'):'Chưa có tác vụ'}</span><span>${t?Math.round(Number(t.progress)||0)+'%':'—'}</span></div><div class="progress" style="margin-top:7px"><span style="width:${Math.max(0,Math.min(100,Number(t?.progress)||0))}%"></span></div>${t&&taskState(t)==='completed'&&resultUrl(t)?`<div style="margin-top:16px"><button class="btn" data-open-url="${escapeHTML(resultUrl(t))}">${icon('external-link')} Mở ảnh</button></div>`:''}</section></div>`}
function videoUI(){const t=state.videoTask;return `<div class="generator-grid"><section class="panel"><div class="editor-title"><div class="editor-icon">${icon('film',20)}</div><div><h2>Video Generation</h2><p>Text-to-Video · Image-to-Video</p></div></div><form id="video-form"><div class="form-field"><label class="form-label" for="video-prompt">Ý tưởng và chuyển động</label><textarea class="form-control prompt-field" id="video-prompt" required placeholder="A cinematic tracking shot through a luminous forest, slow camera push-in, soft golden particles...">${escapeHTML(state.videoPrompt||'')}</textarea><p class="field-note">Nêu chuyển động máy quay, ánh sáng, chủ thể và phong cách.</p></div><div class="form-row"><div class="form-field"><label class="form-label" for="video-ratio">Tỉ lệ video</label><select id="video-ratio" class="form-control">${['16:9','9:16'].map(x=>`<option ${state.videoRatio===x?'selected':''}>${x}</option>`).join('')}</select></div><div class="form-field"><label class="form-label" for="video-duration">Thời lượng yêu cầu</label><select id="video-duration" class="form-control">${[5,6,8,10].map(x=>`<option value="${x}" ${state.videoDuration===x?'selected':''}>${x} giây</option>`).join('')}</select></div></div>${refUpload()}<div class="notice warning" style="margin-bottom:16px">${icon('clock')} Thời lượng thành phẩm phụ thuộc Muse upstream. Tạo video chạy bất đồng bộ và được theo dõi tự động.</div><button type="submit" class="btn primary generate-button" ${state.busy?'disabled':''}>${icon('film')} ${state.busy?'Đang gửi tác vụ...':'Tạo video'}</button></form></section><section class="panel"><div class="panel-head"><div><h2>Video Preview</h2><small>Xem video đã render</small></div>${t?taskBadge(t):chip('Đang chờ','neutral')}</div><div class="result-window ${t&&taskState(t)==='completed'&&resultUrl(t)?'has-result':''}">${t&&taskState(t)==='completed'&&resultUrl(t)?`<video controls src="${escapeHTML(resultUrl(t))}" playsinline></video>`:`<div class="result-placeholder"><div class="symbol">▶</div><h3>${t&&taskState(t)==='failed'?'Tạo video thất bại':t?'Video đang được xử lý':'Storyboard của bạn bắt đầu tại đây'}</h3><p>${t&&taskState(t)==='failed'?escapeHTML(t.error||'Backend đã báo lỗi'):t?'Chờ Muse hoàn tất. Có thể đóng tab rồi mở lại lịch sử tác vụ.':'Nhập một cảnh phim hoặc tải ảnh khung hình đầu tiên.'}</p></div>`}</div><div class="result-meta"><span>${t?escapeHTML(t.status||'queued'):'Chưa có tác vụ'}</span><span>${t?Math.round(Number(t.progress)||0)+'%':'—'}</span></div><div class="progress" style="margin-top:7px"><span style="width:${Math.max(0,Math.min(100,Number(t?.progress)||0))}%"></span></div>${t&&taskState(t)==='completed'&&resultUrl(t)?`<div style="margin-top:16px"><button class="btn" data-open-url="${escapeHTML(resultUrl(t))}">${icon('external-link')} Mở video</button></div>`:''}</section></div>`}
function chatUI(){return `<div class="generator-grid"><section class="panel"><div class="editor-title"><div class="editor-icon">${icon('message',20)}</div><div><h2>Muse Spark Chat</h2><p>OpenAI-compatible Chat Completions</p></div></div><div class="notice">${icon('sparkles')} Hỗ trợ hội thoại nhiều lượt. Tin nhắn được giữ trong phiên trình duyệt, không lưu trên backend.</div><div class="form-field" style="margin-top:24px"><label class="form-label" for="system-prompt">System prompt</label><textarea class="form-control" id="system-prompt" rows="4" placeholder="Bạn là một trợ lý sáng tạo, trả lời bằng tiếng Việt...">${escapeHTML(state.systemPrompt||'')}</textarea></div><button class="btn" id="reset-chat">${icon('refresh-cw')} Bắt đầu hội thoại mới</button></section><section class="panel"><div class="panel-head"><div><h2>Hội thoại trực tiếp</h2><small>Model muse-spark · Streaming SSE</small></div>${chip(state.chatBusy?'Đang phản hồi':'Sẵn sàng',state.chatBusy?'warning':'')}</div><div class="chat-wrap"><div class="messages" id="chat-messages">${state.messages.length?state.messages.map(m=>`<div class="msg-row ${m.role==='user'?'user':''}"><span class="msg-avatar">${m.role==='user'?'B':'✦'}</span><div class="msg ${m.role==='user'?'user':''}">${escapeHTML(m.content)}</div></div>`).join(''):`<div class="result-placeholder" style="margin:auto"><div class="symbol">✧</div><h3>Hãy bắt đầu cuộc trò chuyện</h3><p>Hỏi bất kỳ điều gì hoặc yêu cầu Muse giúp viết và sáng tạo.</p></div>`}</div><form class="chat-compose" id="chat-form"><input class="form-control" id="chat-input" autocomplete="off" placeholder="Nhập tin nhắn..." required aria-label="Tin nhắn"><button class="btn primary" ${state.chatBusy?'disabled':''}>${icon('arrow')}</button></form></div>${state.chatBusy?`<div class="progress-inline">${icon('refresh-cw')} Đang nhận phản hồi streaming...</div>`:''}</section></div>`}
function renderAPI(){
  const base = cleanBase(state.base || window.location.origin), v1 = base + '/v1';
  const keys = state.apiKeys || [];
  return `${header('API & Khóa truy cập', 'Kết nối Muse Studio tới các công cụ AI khác (NextChat, OpenWebUI, Cherry Studio, Dify, Cursor...) chuẩn OpenAI.', `<button class="btn primary" id="btn-create-apikey">${icon('plus')} Tạo API Key mới</button>`)}
<div class="two-cols">
  <section class="panel">
    <div class="panel-head"><h2>Thông tin Base URL</h2>${chip('OpenAI Compatible', 'neutral')}</div>
    <div class="form-field"><label class="form-label">Base URL (Dán vào OpenAI Base URL)</label><div class="api-code" style="cursor:pointer" id="copy-endpoint" title="Nhấp để sao chép">${escapeHTML(v1)}</div><p class="field-note">Hỗ trợ đầy đủ endpoint: <code>/chat/completions</code>, <code>/models</code>, <code>/images/generations</code></p></div>
    <div class="form-field"><label class="form-label">Models hỗ trợ</label>
      <div class="health-row"><span class="health-ico">${icon('message')}</span><span class="health-desc"><b>muse-spark</b><small>Trò chuyện, viết code, kịch bản (Stream SSE)</small></span></div>
      <div class="health-row"><span class="health-ico">${icon('image')}</span><span class="health-desc"><b>muse-image</b><small>Tạo ảnh Text-to-Image & Image-to-Image</small></span></div>
      <div class="health-row"><span class="health-ico">${icon('film')}</span><span class="health-desc"><b>muse-video</b><small>Tạo video chuyển động AI</small></span></div>
    </div>
  </section>
  <section class="panel">
    <div class="panel-head"><h2>Hướng dẫn kết nối các công cụ</h2>${chip('Khách hàng', '')}</div>
    <div style="font-size:12px;line-height:1.7;color:#555">
      <p style="margin-bottom:8px"><strong>1. NextChat / ChatGPT-Next-Web / LobeChat:</strong></p>
      <ul style="margin:0 0 10px 18px;padding:0">
        <li>Endpoint / Base URL: <code>${escapeHTML(v1)}</code></li>
        <li>API Key: <em>(Tạo ở bảng bên dưới và dán vào)</em></li>
        <li>Tên Model: <code>muse-spark</code></li>
      </ul>
      <p style="margin-bottom:8px"><strong>2. Cherry Studio / Dify / Chatbox:</strong></p>
      <ul style="margin:0 0 10px 18px;padding:0">
        <li>Nhà cung cấp: Chọn <strong>OpenAI</strong> hoặc <strong>OpenAI Tùy chỉnh</strong></li>
        <li>Địa chỉ API: <code>${escapeHTML(v1)}</code></li>
      </ul>
    </div>
  </section>
</div>
<section class="panel" style="margin-top:20px">
  <div class="panel-head"><div><h2>Danh sách API Keys đã cấp</h2><small>Quản lý các khóa cấp cho từng ứng dụng ngoài</small></div></div>
  ${keys.length ? `
  <div class="table-wrap"><table class="table">
    <thead><tr><th>Tên ứng dụng</th><th>API Key</th><th>Lần dùng cuối</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
    <tbody>${keys.map(k => `<tr>
      <td><strong>${escapeHTML(k.name || 'API Key')}</strong></td>
      <td><code style="background:#f1f3f9;padding:3px 6px;border-radius:6px;font-size:11px">${escapeHTML(k.key)}</code> <button class="tiny" data-copy-key="${escapeHTML(k.key)}" title="Sao chép">${icon('copy', 13)}</button></td>
      <td><span class="subtext">${k.last_used ? fmtDate(k.last_used) : 'Chưa sử dụng'} (${k.use_count || 0} lần)</span></td>
      <td><button type="button" class="switch ${k.enabled ? 'on' : ''}" role="switch" data-toggle-key="${escapeHTML(k.id)}"></button></td>
      <td><button class="tiny" data-delete-key="${escapeHTML(k.id)}" title="Xóa khóa">${icon('trash', 14)}</button></td>
    </tr>`).join('')}</tbody>
  </table></div>` : empty('Chưa có API Key nào được cấp', 'Bấm nút "Tạo API Key mới" ở góc trên để tạo key cho NextChat, Cherry Studio, Dify...')}
</section>`;
}
function renderSettings(){return `${header('Cài đặt','Thiết lập kết nối và kiểm tra khả năng truy cập backend.')}
<div class="two-cols"><section class="panel"><div class="panel-head"><div><h2>Kết nối backend</h2><small>Không cần sửa mã nguồn khi đổi máy chủ</small></div></div><form id="settings-form"><div class="form-field"><label class="form-label" for="base-input">Địa chỉ máy chủ</label><input class="form-control" id="base-input" type="url" placeholder="http://localhost:18610" value="${escapeHTML(state.base)}"><p class="field-note">Để trống khi frontend được phục vụ cùng origin với musestudio. Nếu nhập URL, không cần /v1.</p></div><div class="form-field"><label class="form-label" for="key-input">MUSE_STUDIO_KEY</label><div class="key-input-wrap"><input class="form-control" id="key-input" type="${state.showKey?'text':'password'}" autocomplete="off" spellcheck="false" placeholder="mst_••••••••••" value="${escapeHTML(state.key)}"><button class="btn" type="button" id="toggle-key" aria-label="Hiện ẩn API key">${icon(state.showKey?'eye-off':'eye')}</button></div><p class="field-note">Lưu trong sessionStorage của tab; đóng phiên trình duyệt sẽ xóa. Không dùng localStorage để lưu khóa.</p></div><div class="toolbar-actions"><button class="btn primary" type="submit">${icon('circle-check')} Lưu & kiểm tra kết nối</button><button class="btn" type="button" id="test-connection">${icon('activity')} Kiểm tra lại</button></div></form></section>
<section class="panel"><div class="panel-head"><h2>Trạng thái kết nối</h2></div>${healthRow('Backend API','/healthz',state.status?'Đã kết nối':'Chưa xác thực','server',Boolean(state.status))}${healthRow('Trình duyệt tự động','Chromium (CDP)',state.status?.browser_running?'Đang chạy':'Chưa chạy','activity',Boolean(state.status?.browser_running))}</section></div>`}
function render(){const page=state.page;$('#breadcrumb').textContent=labels[page];$$('[data-page]').forEach(x=>x.classList.toggle('active',x.dataset.page===page));$('#page-content').innerHTML=`<div class="page">${page==='dashboard'?renderDashboard():page==='accounts'?renderAccounts():page==='tasks'?renderTasks():page==='media'?renderMedia():page==='playground'?renderPlayground():page==='api'?renderAPI():renderSettings()}</div>`;$('#profile-label').textContent=state.status?'Đã kết nối backend':'Chưa kết nối';$('#connection-dot').classList.toggle('offline',!state.status);$('#connection-text').textContent=state.status?'Backend Online':'Chưa kết nối';hydrateIcons()}
function hydrateIcons(){$$('[data-icon]').forEach(el=>{el.innerHTML=icon(el.dataset.icon)})}
function navigation(page){if(!labels[page])page='dashboard';state.page=page;location.hash='#'+page;$('#sidebar').classList.remove('open');$('#sidebar-overlay').classList.remove('open');render();if(page==='tasks'||page==='media')syncPage(page).catch(e=>toast(e.message,true));}
async function syncPage(page){if(!state.key){return}if(page==='tasks'){const d=await request('/admin/tasks?limit=100');state.tasks=d.tasks||[]}else if(page==='media'){const d=await request('/admin/media');state.media=d.media||[]}else if(page==='accounts'){const d=await request('/admin/accounts');state.accounts=d.accounts||[]}
else if(page==='api'){const d=await request('/admin/apikeys');state.apiKeys=d.keys||[]}if(state.page===page)render()}
async function loadDashboard(){const [status,tasks,media,models]=await Promise.all([request('/admin/status'),request('/admin/tasks?limit=100'),request('/admin/media'),request('/v1/models')]);state.status=status;state.accounts=status.accounts||[];state.tasks=tasks.tasks||status.tasks||[];state.media=media.media||[];state.models=models.data||[];render();return status}
async function connect(){try{const status=await loadDashboard();toast(`Đã kết nối musestudio · ${status.accounts?.length||0} tài khoản`)}catch(e){state.status=null;state.accounts=[];state.tasks=[];state.media=[];state.models=[];render();toast('Không thể xác thực backend: '+e.message,true);throw e}}
function modal(title,body,footer){$('#modal-layer').innerHTML=`<div class="modal-backdrop" id="modal-backdrop"><section class="modal-card" role="dialog" aria-modal="true" aria-label="${escapeHTML(title)}"><div class="modal-header"><h2>${escapeHTML(title)}</h2><button class="icon-btn" id="modal-close" aria-label="Đóng">${icon('x')}</button></div>${body}<div class="modal-footer">${footer||'<button class="btn" id="modal-cancel">Đóng</button>'}</div></section></div>`}
const closeModal=()=>$('#modal-layer').innerHTML='';
function addAccountModal(){modal('Thêm tài khoản Muse',`<form id="account-form"><div class="form-field"><label class="form-label" for="new-account-label">Tên hiển thị</label><input id="new-account-label" class="form-control" placeholder="Muse account #1"></div><div class="form-field"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><label class="form-label" for="account-cookies" style="margin:0">Cookie header hoặc batch</label><button type="button" class="btn small ghost" id="btn-show-cookie-guide" style="color:#7458ed;font-weight:700">💡 Hướng dẫn lấy Cookie (3 bước)</button></div><textarea id="account-cookies" class="form-control" rows="6" placeholder="hatch_sess=...; hatch_vml=..." required></textarea><p class="field-note">Dán chuỗi cookie lấy từ trang muse.ai. Không chia sẻ cookie với người khác.</p><label class="check-line"><input type="checkbox" id="batch-input"> Chế độ batch (mỗi dòng một tài khoản)</label></div><button class="btn primary" type="submit" style="display:none" id="account-submit-hidden">Thêm</button></form>`,`<button class="btn" id="modal-cancel">Hủy</button><button class="btn primary" id="save-account">${icon('plus')} Thêm tài khoản</button>`)}
function showCookieGuideModal(){modal('Cách lấy Cookie Muse (3 bước đơn giản)',`<div style="font-size:12.5px;line-height:1.8;color:#333"><p style="margin-bottom:12px">Để hệ thống có thể kết nối tạo ảnh và video bằng tài khoản của bạn, hãy làm theo 3 bước sau:</p><ol style="padding-left:18px;margin-bottom:15px;display:grid;gap:8px"><li><strong>Bước 1:</strong> Mở trình duyệt Chrome/Edge và đăng nhập vào <a href="https://muse.ai" target="_blank" style="color:#7458ed;text-decoration:underline">muse.ai</a>.</li><li><strong>Bước 2:</strong> Nhấn phím <code>F12</code> (hoặc chuột phải chọn <em>Kiểm tra / Inspect</em>) &rarr; chọn tab <strong>Network (Mạng)</strong> &rarr; lọc từ khóa <code>session</code>.</li><li><strong>Bước 3:</strong> Nhấn <kbd>F5</kbd> tải lại trang, click vào request <code>session</code> đầu tiên &rarr; ở mục <em>Request Headers</em>, tìm dòng <strong>Cookie:</strong> &rarr; chuột phải chọn <em>Copy value (Sao chép giá trị)</em> rồi dán vào ô bên trên.</li></ol><div class="notice">${icon('shield')} <strong>Mẹo:</strong> Chuỗi cookie hợp lệ luôn chứa <code>hatch_sess=...</code> và <code>hatch_vml=...</code>. Hệ thống chỉ lưu cục bộ trên máy của bạn để tạo tác vụ.</div></div>`,`<button class="btn primary" id="modal-cancel">Đã hiểu</button>`)}
async function act(action,el){const id=el.dataset[action],a=state.accounts.find(v=>v.id===id);try{
if(action==='toggleAccount'){await patch(`/admin/accounts/${encodeURIComponent(id)}`,{enabled:!a.enabled});toast('Đã cập nhật tài khoản');await syncPage('accounts')}
if(action==='testAccount'){toast('Đang kiểm tra phiên tài khoản...');const d=await post(`/admin/accounts/${encodeURIComponent(id)}/test`);toast(d.message|| (d.ok?'Phiên hoạt động':'Không xác minh được'),!d.ok);await syncPage('accounts')}
if(action==='quotaAccount'){const d=await post(`/admin/accounts/${encodeURIComponent(id)}/quota`);toast('Quota đã được cập nhật: '+(d.plan||'Muse'));await syncPage('accounts')}
if(action==='renameAccount'){const value=window.prompt('Tên tài khoản mới',a.label||'');if(value===null||!value.trim())return;await patch(`/admin/accounts/${encodeURIComponent(id)}`,{label:value.trim()});toast('Đã đổi tên');await syncPage('accounts')}
if(action==='deleteAccount'){if(!confirm('Xóa tài khoản này khỏi pool?'))return;await remove(`/admin/accounts/${encodeURIComponent(id)}`);toast('Đã xóa tài khoản');await syncPage('accounts')}
}catch(e){toast(e.message,true)}}
function setTab(tab){state.tab=tab;state.reference=null;state.referenceName='';render()}
function rememberForm(){if(state.page!=='playground')return;const p=$('#image-prompt');if(p)state.imagePrompt=p.value;const v=$('#video-prompt');if(v)state.videoPrompt=v.value;const s=$('#system-prompt');if(s)state.systemPrompt=s.value;const ir=$('#image-ratio');if(ir)state.imageRatio=ir.value;const vr=$('#video-ratio');if(vr)state.videoRatio=vr.value;const vd=$('#video-duration');if(vd)state.videoDuration=Number(vd.value)}
async function createImage(){if(!state.key){toast('Vui lòng cấu hình API key trước',true);navigation('settings');return}rememberForm();if(!state.imagePrompt?.trim()){toast('Hãy nhập prompt tạo ảnh',true);return}state.busy=true;render();try{const payload={model:'muse-image',prompt:state.imagePrompt,size:state.imageRatio||'16:9',response_format:'url',...(state.reference?{reference_image:state.reference}:{})};const d=await request('/v1/images/tasks',{method:'POST',body:payload,headers:{'Idempotency-Key':crypto.randomUUID()},timeout:30000});state.imageTask={...d,kind:'image'};toast('Đã gửi tác vụ tạo ảnh');startTaskPoll('image',d.id)}catch(e){toast('Không thể tạo ảnh: '+e.message,true)}finally{state.busy=false;render()}}
async function createVideo(){if(!state.key){navigation('settings');return}rememberForm();if(!state.videoPrompt?.trim()){toast('Hãy nhập prompt tạo video',true);return}state.busy=true;render();try{const d=await post('/v1/videos',{model:'muse-video',prompt:state.videoPrompt,size:state.videoRatio||'16:9',duration:state.videoDuration||5,...(state.reference?{reference_image:state.reference}:{})});state.videoTask={...d,kind:'video'};toast('Đã gửi tác vụ tạo video');startTaskPoll('video',d.id||d.task_id)}catch(e){toast('Không thể tạo video: '+e.message,true)}finally{state.busy=false;render()}}
function startTaskPoll(kind,id){clearTimeout(state.pollTimers[kind]);if(!id)return;let tries=0;const poll=async()=>{try{const t=await request(kind==='image'?`/v1/images/tasks/${encodeURIComponent(id)}`:`/v1/videos/${encodeURIComponent(id)}`,{timeout:22000});if(kind==='image')state.imageTask=t;else state.videoTask=t;if(state.page==='playground'&&state.tab===kind){rememberForm();render()}const st=taskState(t);if(st==='completed'){toast(kind==='image'?'Đã tạo ảnh thành công':'Đã tạo video thành công');await syncTasksQuietly();return}if(st==='failed'){toast('Tác vụ thất bại: '+(t.error||'Lỗi không xác định'),true);await syncTasksQuietly();return}tries=0;state.pollTimers[kind]=setTimeout(poll,3000)}catch(e){if(++tries>5){toast('Mất kết nối tới tác vụ; có thể theo dõi trong Hàng đợi.',true);return}state.pollTimers[kind]=setTimeout(poll,Math.min(15000,tries*3000))}};state.pollTimers[kind]=setTimeout(poll,2400)}
async function syncTasksQuietly(){try{const [tasks,media]=await Promise.all([request('/admin/tasks?limit=100'),request('/admin/media')]);state.tasks=tasks.tasks||[];state.media=media.media||[]}catch{}}
async function sendChat(){if(state.chatBusy)return;if(!state.key){navigation('settings');return}rememberForm();const input=$('#chat-input');const content=input?.value.trim();if(!content)return;state.messages.push({role:'user',content});state.messages.push({role:'assistant',content:''});state.chatBusy=true;render();const abort=new AbortController();state.chatAbort=abort;let buffer='';let error=null;try{
 const messages=[...(state.systemPrompt?.trim()?[{role:'system',content:state.systemPrompt}]:[]),...state.messages.slice(0,-1)];const r=await request('/v1/chat/completions',{method:'POST',body:{model:'muse-spark',messages,stream:true},signal:abort.signal,timeout:310000,plain:true});if(!r.ok){const b=await r.json().catch(()=>({}));throw new Error(b.error?.message||b.detail||`HTTP ${r.status}`)}if(!r.body){throw new Error('Server không cung cấp streaming response')}
 const reader=r.body.getReader(),decoder=new TextDecoder();let end=false;while(!end){const x=await reader.read();if(x.done)break;buffer+=decoder.decode(x.value,{stream:true}).replace(/\r\n/g,'\n');const chunks=buffer.split('\n\n');buffer=chunks.pop()||'';for(const c of chunks){for(const line of c.split('\n')){if(!line.startsWith('data:'))continue;const msg=line.slice(5).trim();if(msg==='[DONE]'){end=true;break}try{const o=JSON.parse(msg);if(o.error)throw new Error(o.error.message||'Streaming error');const delta=o.choices?.[0]?.delta?.content;if(delta)state.messages.at(-1).content+=delta}catch(e){if(e instanceof SyntaxError)continue;throw e}}}const box=$('#chat-messages');if(box){const last=$$('.msg',box).at(-1);if(last)last.textContent=state.messages.at(-1).content;box.scrollTop=box.scrollHeight}}
 }catch(e){error=e;if(e.name!=='AbortError')toast('Chat thất bại: '+e.message,true)}finally{if(!state.messages.at(-1).content)state.messages.at(-1).content=error?'[Không nhận được phản hồi]':'[Không có nội dung]';state.chatBusy=false;state.chatAbort=null;render()}}
function showDonateModal(){
  modal('Ủng hộ tác giả (Donate)', `
    <div style="text-align:center;padding:10px 0">
      <div style="max-width:260px;margin:0 auto;background:#f8f9fe;padding:14px;border-radius:16px;border:1px solid #e9ebf4">
        <img src="./donate_qr.png" alt="Mã QR Donate" style="width:100%;height:auto;border-radius:12px;display:block">
      </div>
      <p style="font-size:14px;font-weight:700;color:#7155e9;margin-top:16px">Tùy tâm 500 :D</p>
      <p style="font-size:11.5px;color:#8d93a6;margin-top:6px">Cảm ơn bạn đã đồng hành và ủng hộ Muse Studio!</p>
    </div>
  `, '<button class="btn primary" id="modal-cancel">Đóng</button>');
}

let autoxSid=null,autoxTimer=null;
function autoxModal(){
  modal('Tự động trích xuất từ trình duyệt',
  `<form id="autox-form"><div class="form-field"><label class="form-label" for="autox-label">Tên hiển thị</label><input id="autox-label" class="form-control" placeholder="Muse account #1"></div><div id="autox-status"><div class="notice">${icon('shield')} Nhấn <b>Bắt đầu</b>, một cửa sổ trình duyệt sẽ mở ra trên <b>máy đang chạy Muse Studio</b>. Hãy đăng nhập muse.ai trong cửa sổ đó — hệ thống sẽ tự nhận diện cookie (kể cả httpOnly) và thêm tài khoản, không cần F12.</div></div><button type="submit" style="display:none" id="autox-submit-hidden"></button></form>`,
  `<button class="btn" id="modal-cancel">Đóng</button><button class="btn primary" id="autox-start">${icon('eye')} Bắt đầu trích xuất</button>`);
}
async function autoxStart(){
  if(!state.key){
    toast('Chưa có MUSE_STUDIO_KEY. Hãy vào mục Cài đặt (⚙) nhập khóa trước khi trích xuất.', true);
    return;
  }
  const label=($('#autox-label')||{}).value||'';
  const btn=$('#autox-start');if(btn){btn.disabled=true;btn.innerHTML='Đang mở trình duyệt...';}
  try{
    const d=await request('/admin/accounts/auto-extract/start',{method:'POST',body:{label},timeout:60000});
    autoxSid=d.sid;
    $('#autox-status').innerHTML=`<div class="notice warning">${icon('clock')} <b>Trình duyệt đã mở.</b> Hãy đăng nhập muse.ai trong cửa sổ vừa mở...<br><span id="autox-prog">Đang chờ đăng nhập (0/4 cookie cốt lõi)</span></div><div class="progress" style="margin-top:10px"><span id="autox-bar" style="width:5%"></span></div>`;
    const foot=$('#modal-layer .modal-footer');
    if(foot)foot.innerHTML=`<button class="btn critical" id="autox-cancel">Hủy bỏ</button>`;
    clearInterval(autoxTimer);
    autoxTimer=setInterval(autoxPoll,3000);
  }catch(e){
    toast('Không thể mở trình duyệt: '+e.message,true);
    if(btn){btn.disabled=false;btn.innerHTML='Bắt đầu trích xuất';}
  }
}
async function autoxPoll(){
  if(!autoxSid)return;
  try{
    const s=await request('/admin/accounts/auto-extract/'+encodeURIComponent(autoxSid));
    const have=(s.have||[]).length, need=(s.need||[]).length||4;
    const bar=$('#autox-bar'),prog=$('#autox-prog');
    if(bar)bar.style.width=Math.max(5,have/need*100)+'%';
    if(s.status==='waiting'&&prog)prog.textContent=`Đã nhận ${have}/${need} cookie cốt lõi (${(s.have||[]).join(', ')||'chưa có'}) — hãy hoàn tất đăng nhập trong trình duyệt.`;
    if(s.status==='done'){
      clearInterval(autoxTimer);autoxTimer=null;
      toast('Đã tự động thêm tài khoản: '+(s.label||s.account_id));
      closeModal();autoxSid=null;
      await syncPage('accounts');
    }else if(s.status==='error'||s.status==='expired'){
      clearInterval(autoxTimer);autoxTimer=null;
      const st=$('#autox-status');
      if(st)st.innerHTML=`<div class="notice warning">${icon('alert-circle')} ${escapeHTML(s.error||'Trích xuất thất bại.')}</div>`;
      const foot=$('#modal-layer .modal-footer');
      if(foot)foot.innerHTML=`<button class="btn" id="modal-cancel">Đóng</button><button class="btn primary" id="autox-start">${icon('eye')} Thử lại</button>`;
      autoxSid=null;
    }else if(s.status==='cancelled'){
      clearInterval(autoxTimer);autoxTimer=null;closeModal();autoxSid=null;
    }
  }catch(e){/* giữ nguyên, thử lại kỳ sau */}
}
async function autoxCancel(){
  clearInterval(autoxTimer);autoxTimer=null;
  if(autoxSid){try{await post('/admin/accounts/auto-extract/'+encodeURIComponent(autoxSid)+'/cancel')}catch{}}
  autoxSid=null;closeModal();
}
function applyTheme(theme,save=true){
  const t=theme||localStorage.getItem('muse_studio_theme')||'light';
  document.documentElement.setAttribute('data-theme',t);
  if(save)localStorage.setItem('muse_studio_theme',t);
  const btn=document.querySelector('#theme-toggle');
  if(btn)btn.innerHTML='<span>'+icon(t==='dark'?'sun':'moon')+'</span>';
  const meta=document.querySelector('meta[name="theme-color"]');
  if(meta)meta.setAttribute('content',t==='dark'?'#0e1016':'#f5f6fa');
}
function toggleTheme(){
  const cur=document.documentElement.getAttribute('data-theme')||'light';
  applyTheme(cur==='dark'?'light':'dark');
  toast(cur==='dark'?'Đã chuyển sang giao diện sáng':'Đã chuyển sang giao diện tối');
}
async function handleAction(e){const el=e.target.closest('button,[data-nav],[data-tab-nav],[data-open-url]');if(!el)return;
if(el.dataset.nav){navigation(el.dataset.nav);return}
if(el.dataset.tabNav){state.page='playground';state.tab=el.dataset.tabNav;navigation('playground');return}
if(el.dataset.playTab){rememberForm();setTab(el.dataset.playTab);return}
if(el.dataset.mediaFilter){$$('[data-media-filter]').forEach(x=>x.classList.toggle('active',x===el));filterMedia();return}
if(el.dataset.openUrl){const url=el.dataset.openUrl;if(/^https?:\/\//.test(url))window.open(url,'_blank','noopener,noreferrer');return}
if(el.dataset.downloadName){downloadMedia(el.dataset.downloadName);return}
if(el.dataset.copyKey){copyText(el.dataset.copyKey);return}
if(el.dataset.toggleKey){
  const kId=el.dataset.toggleKey;
  const k=state.apiKeys.find(x=>x.id===kId);
  if(k){
    try{
      await patch(`/admin/apikeys/${encodeURIComponent(kId)}`,{enabled:!k.enabled});
      toast('Đã cập nhật trạng thái API Key');
      await syncPage('api');
    }catch(e){toast(e.message,true)}
  }
  return;
}
if(el.dataset.deleteKey){
  if(!confirm('Xóa vĩnh viễn API Key này? Các công cụ AI đang dùng key này sẽ mất kết nối.'))return;
  try{
    await remove(`/admin/apikeys/${encodeURIComponent(el.dataset.deleteKey)}`);
    toast('Đã xóa API Key');
    await syncPage('api');
  }catch(e){toast(e.message,true)}
  return;
}
for(const action of ['toggleAccount','testAccount','quotaAccount','renameAccount','deleteAccount'])if(el.dataset[action]){await act(action,el);return}
if(el.dataset.removeTask){if(!confirm('Xóa tác vụ khỏi lịch sử?'))return;try{await remove(`/admin/tasks/${encodeURIComponent(el.dataset.removeTask)}`);toast('Đã xóa');await syncPage('tasks')}catch(e){toast(e.message,true)}return}
if(el.dataset.deleteMedia){if(!confirm('Xóa vĩnh viễn media này?'))return;try{await remove(`/admin/media/${encodeURIComponent(el.dataset.deleteMedia)}`);toast('Đã xóa tệp');await syncPage('media')}catch(e){toast(e.message,true)}return}
switch(el.id){
case 'menu-toggle':$('#sidebar').classList.add('open');$('#sidebar-overlay').classList.add('open');break;
case 'refresh': case 'dash-refresh':await refreshAll();break;
case 'profile-settings':case 'top-avatar':navigation('settings');break;
case 'btn-donate':showDonateModal();break;
case 'btn-show-cookie-guide':showCookieGuideModal();break;
case 'btn-create-apikey':{
  const name = window.prompt('Đặt tên cho ứng dụng dùng API (VD: NextChat, Cursor, Dify, v.v.):', 'My App Key');
  if(!name || !name.trim()) return;
  try{
    const d = await post('/admin/apikeys', {name: name.trim()});
    toast('Đã tạo API Key thành công!');
    await syncPage('api');
  }catch(e){toast(e.message, true)}
  break;
}
case 'add-account':addAccountModal();break;
case 'autox-account':autoxModal();break;
case 'autox-start':autoxStart();break;
case 'autox-cancel':autoxCancel();break;
case 'modal-cancel':case 'modal-close':closeModal();break;
case 'save-account':$('#account-submit-hidden')?.click();break;
case 'keepalive-all':if(!confirm('Chạy gia hạn phiên cho toàn bộ tài khoản? Có thể mất một lúc.'))return;try{toast('Đang thực hiện gia hạn toàn bộ tài khoản...');const d=await post('/admin/accounts/keepalive');toast(d.message||`Gia hạn kết thúc: ${d.status||'OK'}`);await syncPage('accounts')}catch(e){toast(e.message,true)}break;
case 'tasks-refresh':await syncPage('tasks');break;
case 'media-refresh':await syncPage('media');break;
case 'clear-tasks':if(!confirm('Dọn toàn bộ lịch sử tác vụ?'))return;try{const d=await post('/admin/tasks/clear',{keep:0});toast(`Đã xóa ${d.removed} tác vụ`);await syncPage('tasks')}catch(e){toast(e.message,true)}break;
case 'clear-reference':state.reference=null;state.referenceName='';rememberForm();render();break;
case 'reset-chat':if(state.chatAbort)state.chatAbort.abort();state.messages=[];state.chatBusy=false;render();break;
case 'copy-endpoint':copyText(cleanBase(state.base||location.origin)+'/v1');break;
case 'copy-curl':copyText($('#curl-example')?.textContent);break;
case 'toggle-key':{const inp=$('#key-input');state.showKey=!state.showKey;inp.type=state.showKey?'text':'password';el.innerHTML=icon(state.showKey?'eye-off':'eye');break}
case 'test-connection':try{await connect()}catch{}break;
case 'theme-toggle':toggleTheme();break;
}}
async function refreshAll(){if(!state.key){navigation('settings');toast('Hãy nhập API key để kết nối',true);return}try{await loadDashboard();toast('Dữ liệu đã cập nhật')}catch(e){state.status=null;render();toast(e.message,true)}}
function filterMedia(){const text=($('#media-search')?.value||'').toLowerCase(),kind=$('[data-media-filter].active')?.dataset.mediaFilter||'all';$('#media-list').innerHTML=mediaGrid(state.media.filter(m=>(kind==='all'||m.kind===kind)&&String(m.name).toLowerCase().includes(text)))}
async function copyText(s){try{await navigator.clipboard.writeText(s||'');toast('Đã sao chép')}catch{toast('Không thể sao chép tự động',true)}}
async function downloadMedia(name){const url=mediaLink({name});try{const r=await fetch(url);if(!r.ok)throw new Error(`HTTP ${r.status}`);const b=await r.blob();const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),2000)}catch{window.open(url,'_blank','noopener,noreferrer');toast('Trình duyệt đang mở media ở tab mới')}}
function handleFile(e){if(e.target.id!=='reference-file')return;const f=e.target.files?.[0];if(!f)return;if(!['image/png','image/jpeg','image/webp'].includes(f.type)){toast('Chỉ hỗ trợ PNG, JPG, WebP',true);return}if(f.size>10*1024*1024){toast('Ảnh tham chiếu phải nhỏ hơn 10 MB',true);return}const reader=new FileReader();reader.onload=()=>{rememberForm();state.reference=reader.result;state.referenceName=f.name;render()};reader.onerror=()=>toast('Không thể đọc ảnh',true);reader.readAsDataURL(f)}
async function handleSubmit(e){if(!e.target.matches('#settings-form,#image-form,#video-form,#chat-form,#account-form'))return;e.preventDefault();const id=e.target.id;
if(id==='settings-form'){const base=cleanBase($('#base-input').value);if(base&&!/^https?:\/\//i.test(base)){toast('Backend URL phải bắt đầu bằng http:// hoặc https://',true);return}state.base=base;state.key=$('#key-input').value.trim();localStorage.setItem('muse_studio_base',state.base);if(state.key)sessionStorage.setItem('muse_studio_key',state.key);else sessionStorage.removeItem('muse_studio_key');try{await connect();navigation('dashboard')}catch{}return}
if(id==='account-form'){const text=$('#account-cookies').value.trim();if(!text)return;const batch=$('#batch-input').checked;try{const d=await post('/admin/accounts',{label:$('#new-account-label').value.trim(),...(batch?{batch:text}:{cookie_header:text})});closeModal();toast(`Đã nhập ${d.count||0} tài khoản${d.warning?' · '+d.warning:''}`);await syncPage('accounts')}catch(e){toast(e.message,true)}return}
if(id==='image-form'){await createImage();return}if(id==='video-form'){await createVideo();return}if(id==='chat-form'){await sendChat()}}
async function bootstrap(){
  hydrateIcons();
  try{
    const r=await fetch('/studio/config.json');
    if(r.ok){
      const cfg=await r.json();
      if(cfg.api_key&&!state.key){
        state.key=cfg.api_key;
        sessionStorage.setItem('muse_studio_key',state.key);
      }
    }
  }catch{}applyTheme(null,false);const hash=location.hash.replace('#','');state.page=labels[hash]?hash:'dashboard';window.addEventListener('hashchange',()=>{const p=location.hash.replace('#','');if(labels[p]&&p!==state.page)navigation(p)});
document.addEventListener('click',handleAction);document.addEventListener('submit',handleSubmit);document.addEventListener('change',handleFile);document.addEventListener('input',e=>{if(e.target.id==='accounts-search'){const term=e.target.value.toLowerCase();$('#accounts-list').innerHTML=accountTable(state.accounts.filter(a=>(a.label+' '+a.id).toLowerCase().includes(term)))}if(e.target.id==='media-search')filterMedia();if(e.target.id==='task-filter')$('#tasks-list').innerHTML=taskTable(state.tasks.filter(t=>e.target.value==='all'||taskState(t)===e.target.value))});$('#sidebar-overlay').addEventListener('click',()=>{$('#sidebar').classList.remove('open');$('#sidebar-overlay').classList.remove('open')});$('#modal-layer').addEventListener('click',e=>{if(e.target.id==='modal-backdrop')closeModal()});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});render();
if(state.key){try{await loadDashboard()}catch(e){state.status=null;render();toast('Không thể kết nối: '+e.message,true)}}
state.refreshTimer=setInterval(async()=>{if(!state.key||document.hidden)return;try{const [status,tasks]=await Promise.all([request('/admin/status'),request('/admin/tasks?limit=100')]);state.status=status;state.accounts=status.accounts||[];state.tasks=tasks.tasks||[];if(['dashboard','tasks','accounts'].includes(state.page))render()}catch{state.status=null;if(state.page==='dashboard')render()}},20000);
}
bootstrap();
})();
