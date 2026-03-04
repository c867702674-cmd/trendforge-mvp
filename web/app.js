function tfGetTrendIdFromHash() {
  const h = (location.hash || '').trim();
  const m = h.match(/#\/trend\/(\d+)/);
  return m ? parseInt(m[1], 10) : null;
}

function tfHighlightTrendCard(trendId) {
  // 你页面里每条卡片如果有 data-id 或 id 前缀，就能精确定位
  // 这里做一个通用查找：包含 '#<id>' 或 'task #<id>' 的元素
  const candidates = Array.from(document.querySelectorAll('*'));
  const el = candidates.find(x => (x.textContent || '').includes(`#${trendId}`));
  if (!el) return false;
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  el.style.outline = '2px solid rgba(255,160,60,0.9)';
  el.style.borderRadius = '12px';
  setTimeout(() => { el.style.outline = ''; }, 6000);
  return true;
}
/* TrendForge Web - app.js (A4 + UI toolbar fix)
function tfGetTrendIdFromHash() {
  const h = (location.hash || '').trim();
  const m = h.match(/#\/trend\/(\d+)/);
  return m ? parseInt(m[1], 10) : null;
}

function tfHighlightTrendCard(trendId) {
  // 你页面里每条卡片如果有 data-id 或 id 前缀，就能精确定位
  // 这里做一个通用查找：包含 '#<id>' 或 'task #<id>' 的元素
  const candidates = Array.from(document.querySelectorAll('*'));
  const el = candidates.find(x => (x.textContent || '').includes(`#${trendId}`));
  if (!el) return false;
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  el.style.outline = '2px solid rgba(255,160,60,0.9)';
  el.style.borderRadius = '12px';
  setTimeout(() => { el.style.outline = ''; }, 6000);
  return true;
} * Fix: toolbar overlap by using fixed positioning and safe spacing.
 */

(() => {
  'use strict';

  const API_BASE = '/api';
  const STATUSES = [
    { key: 'DO_NOW', title: 'DO_NOW', desc: '立即执行（优先上架）' },
    { key: 'DOING', title: 'DOING', desc: '观察中（小批测试）' },
    { key: 'WATCH', title: 'WATCH', desc: '关注中（暂不投入）' },
  ];

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function safeJsonParse(maybeJson, fallback = null) {
    if (maybeJson == null) return fallback;
    if (typeof maybeJson === 'object') return maybeJson;
    try { return JSON.parse(maybeJson); } catch { return fallback; }
  }

  function escapeHtml(s) {
    return String(s ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function debounce(fn, wait = 150) {
    let t = null;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), wait); };
  }

  function downloadJson(filename, data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function downloadText(filename, text, mime = 'text/plain;charset=utf-8') {
    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  async function copyText(text) {
    const s = String(text ?? '');
    try { await navigator.clipboard.writeText(s); return true; }
    catch {
      const ta = document.createElement('textarea');
      ta.value = s;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.focus(); ta.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch { ok = false; }
      ta.remove();
      return ok;
    }
  }

  function compactLines(arr) {
    if (!Array.isArray(arr)) return [];
    return arr.map(x => String(x ?? '').trim()).filter(Boolean);
  }

  function pickExecution(payload) {
    if (!payload) return null;
    const exRaw = payload.execution;
    if (!exRaw) return null;
    if (typeof exRaw === 'object') return exRaw;
    const parsed = safeJsonParse(exRaw, null);
    return parsed;
  }

  function setStatus(text) {
    const el = $('#tf_status');
    if (el) el.textContent = `状态：${text}`;
  }

  // ----------------------------
  // Toolbar (FIXED, non-overlapping)
  // ----------------------------
  function ensureToolbar() {
    if ($('#tf_toolbar')) return $('#tf_toolbar');

    // Add top padding so fixed toolbar never covers your native header
    if (!document.body.dataset.tfPadTop) {
      document.body.style.paddingTop = '56px';
      document.body.dataset.tfPadTop = '1';
    }

    const toolbar = document.createElement('div');
    toolbar.id = 'tf_toolbar';
    toolbar.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 9999;
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: flex-end;
      flex-wrap: wrap;

      max-width: calc(100vw - 20px);
      padding: 8px 10px;
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.12);
      background: rgba(0,0,0,0.55);
      backdrop-filter: blur(8px);

      color: #eaeaea;
      font-size: 14px;
    `;

    const makeCb = (id, text) => {
      const wrap = document.createElement('label');
      wrap.style.cssText = `
        display:flex; gap:8px; align-items:center;
        cursor:pointer; user-select:none;
        padding: 4px 6px;
        border-radius: 10px;
      `;
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.id = id;
      cb.checked = false;
      cb.style.cssText = `transform: translateY(1px);`;
      const t = document.createElement('span');
      t.textContent = text;
      wrap.append(cb, t);
      return wrap;
    };

    const mkBtn = (id, text) => {
      const b = document.createElement('button');
      b.id = id;
      b.textContent = text;
      b.style.cssText = `
        border: 1px solid rgba(255,255,255,0.18);
        background: rgba(255,255,255,0.08);
        color: #fff;
        padding: 6px 10px;
        border-radius: 12px;
        cursor: pointer;
        white-space: nowrap;
      `;
      b.onmouseenter = () => (b.style.background = 'rgba(255,255,255,0.12)');
      b.onmouseleave = () => (b.style.background = 'rgba(255,255,255,0.08)');
      return b;
    };

    const savedWrap = makeCb('tf_only_saved', '只看收藏');
    const undoneWrap = makeCb('tf_only_undone', '只看未做');
    const exportJsonBtn = mkBtn('tf_export_saved', '导出收藏(JSON)');
    const exportCsvBtn = mkBtn('tf_export_amazon_csv', '导出上架CSV');

    // 🔥 Batch Generate Execution for DO_NOW (D4-2)
const batchBtn = document.createElement('button');
batchBtn.id = 'tf_batch_generate';
batchBtn.textContent = '🔥 一键生成执行包(DO_NOW)';
batchBtn.style.cssText = `
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(255,160,60,0.18);
  color: #fff;
  padding: 6px 10px;
  border-radius: 10px;
  cursor: pointer;
  margin-left: 8px;
`;
batchBtn.onmouseenter = () => (batchBtn.style.background = 'rgba(255,160,60,0.26)');
batchBtn.onmouseleave = () => (batchBtn.style.background = 'rgba(255,160,60,0.18)');

batchBtn.onclick = async () => {
  try {
    const limit = 30; // 你可以改成 20/50
    if (!confirm(`将对 DO_NOW 批量生成执行包（limit=${limit}，不覆盖已有手工内容）。继续？`)) return;

    const r = await fetch(`${API_BASE}/trends/generate_execution_batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ limit }),
    });
    const data = await r.json();
    if (!r.ok || !data.ok) throw new Error(data?.detail || JSON.stringify(data));

    alert(`批量生成完成：updated=${data.updated}, skipped=${data.skipped}`);

    // 尽量走你原来的刷新逻辑；没有就刷新页面
    if (typeof window.loadTrends === 'function') {
      window.loadTrends();
    } else if (typeof window.refreshAll === 'function') {
      window.refreshAll();
    } else {
      location.reload();
    }
    setTimeout(() => {
  const tid = tfGetTrendIdFromHash();
  if (tid) tfHighlightTrendCard(tid);
}, 600);//建议600-800
  } catch (e) {
    alert(`批量生成失败：${e?.message || e}`);
  }
};

toolbar.append(savedWrap, undoneWrap, batchBtn, exportJsonBtn, exportCsvBtn);
    document.body.appendChild(toolbar);
    return toolbar;
  }

  // ----------------------------
  // Lists
  // ----------------------------
  function ensureLists() {
    const ids = { DO_NOW: 'do_now_list', DOING: 'doing_list', WATCH: 'watch_list' };
    const main = $('.main') || $('.container') || $('.content') || $('#main') || document.body;

    let board = $('#tf_board');
    if (!board) {
      board = document.createElement('div');
      board.id = 'tf_board';
      board.style.cssText = `width:100%;`;
      main.appendChild(board);
    }

    for (const st of STATUSES) {
      const listId = ids[st.key];
      let listEl = document.getElementById(listId);
      if (!listEl) {
        const section = document.createElement('div');
        section.className = `tf_section tf_${st.key}`;
        section.style.cssText = `
          margin: 10px 8px;
          border-radius: 18px;
          border: 1px solid rgba(255,255,255,0.08);
          padding: 10px;
          background: rgba(0,0,0,0.08);
        `;

        const head = document.createElement('div');
        head.style.cssText = `display:flex; align-items:center; justify-content:space-between; margin-bottom: 10px;`;

        const left = document.createElement('div');
        left.innerHTML = `
          <div style="font-weight:700; font-size:16px;">${escapeHtml(st.title)}</div>
          <div style="opacity:0.75; font-size:12px; margin-top:2px;">${escapeHtml(st.desc)}</div>
        `;

        const right = document.createElement('div');
        right.style.cssText = `opacity:0.9; font-size:14px;`;
        right.innerHTML = `<span id="${st.key}_count">0</span>`;

        head.append(left, right);

        listEl = document.createElement('div');
        listEl.id = listId;
        listEl.style.cssText = `display:flex; flex-direction:column; gap:10px;`;

        section.append(head, listEl);
        board.appendChild(section);
      }

      if (!document.getElementById(`${st.key}_count`)) {
        const c = document.createElement('span');
        c.id = `${st.key}_count`;
        c.style.display = 'none';
        document.body.appendChild(c);
      }
    }

    if (!$('#tf_status')) {
      const status = document.createElement('div');
      status.id = 'tf_status';
      status.style.cssText = `
        position: fixed;
        left: 18px;
        bottom: 18px;
        font-size: 12px;
        opacity: .85;
        color:#cfcfcf;
        z-index: 9999;
        padding: 6px 10px;
        border-radius: 12px;
        background: rgba(0,0,0,0.45);
        border: 1px solid rgba(255,255,255,0.10);
        backdrop-filter: blur(8px);
      `;
      status.textContent = '状态：准备就绪';
      document.body.appendChild(status);
    }
  }

  // ----------------------------
  // State
  // ----------------------------
  const state = {
    country: 'US',
    category: 'POD',
    limit: 60,
    onlySaved: false,
    onlyUndone: false,
    dataByStatus: { DO_NOW: [], DOING: [], WATCH: [] },
    loading: false,
    executionOpen: {},
  };

  // ----------------------------
  // API
  // ----------------------------
  async function apiGetTrends(status) {
    const params = new URLSearchParams();
    params.set('status', status);
    params.set('country', state.country);
    if (state.category && String(state.category).trim() !== '') params.set('category', state.category);
    params.set('limit', String(state.limit));
    params.set('_ts', String(Date.now()));

    const url = `${API_BASE}/trends?${params.toString()}`;
    const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`GET ${url} -> ${res.status}`);
    const json = await res.json();
    return Array.isArray(json?.items) ? json.items : [];
  }

  async function apiPostFlags(trendId, flags) {
    const url = `${API_BASE}/trends/${encodeURIComponent(trendId)}/flags`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(flags),
    });
    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      throw new Error(`POST ${url} -> ${res.status} ${txt.slice(0, 200)}`);
    }
    return await res.json();
  }

  async function apiPostGenerateExecution(trendId) {
    const url = `${API_BASE}/trends/${encodeURIComponent(trendId)}/generate_execution`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      throw new Error(`POST ${url} -> ${res.status} ${txt.slice(0, 200)}`);
    }
    return await res.json();
  }

  // ----------------------------
  // Normalize / Filter
  // ----------------------------
  function normalizeItem(item) {
    const payload = safeJsonParse(item?.payload_json, item?.payload_json) || {};
    const flags = item?.flags || payload?.flags || {};
    return {
      id: item?.id,
      term: item?.term ?? '',
      date: item?.date ?? '',
      country: item?.country ?? '',
      category: item?.category ?? '',
      growth: item?.growth ?? '',
      hit_score: item?.hit_score ?? '',
      action_level: item?.action_level ?? item?.status ?? '',
      payload,
      flags: {
        saved: !!flags.saved || !!item?.saved,
        done: !!flags.done || !!item?.done,
      },
    };
  }

  function applyFilters(items) {
    let out = items.slice();
    if (state.onlySaved) out = out.filter(x => x.flags?.saved);
    if (state.onlyUndone) out = out.filter(x => !x.flags?.done);
    return out;
  }

  function btnStyles(active) {
    const base = `border:1px solid rgba(255,255,255,0.18); background:rgba(255,255,255,0.06); color:#fff; padding:6px 10px; border-radius:10px; cursor:pointer; font-size:12px;`;
    const on = `border:1px solid rgba(255,255,255,0.35); background:rgba(255,255,255,0.14); color:#fff; padding:6px 10px; border-radius:10px; cursor:pointer; font-size:12px;`;
    return active ? on : base;
  }

  // ----------------------------
  // Execution Render
  // ----------------------------
  function renderExecutionBlock(item) {
    const ex = pickExecution(item.payload);
    if (!ex) {
      return `<div style="margin-top:10px; opacity:.75; font-size:12px;">
        暂无执行包。点击「生成执行包」即可生成亚马逊标题/Bullets/搜索词/Prompt。
      </div>`;
    }

    const amazon = ex.amazon || {};
    const title = amazon.title || '';
    const bullets = compactLines(amazon.bullets || ex.bullet_points || []);
    const terms = (amazon.backend_search_terms || '').trim() || compactLines(ex.search_terms || []).join(' ');
    const sku = amazon.sku_style || '';
    const mj = ex?.design_prompt?.midjourney ?? '';
    const sd = ex?.design_prompt?.stable_diffusion ?? '';
    const qty = ex?.listing_strategy?.suggested_quantity ?? '';
    const price = ex?.listing_strategy?.price_range ?? '';
    const note = ex?.listing_strategy?.note ?? '';
    const genAt = ex?.generated_at ?? '';
    const compliance = ex.compliance_note || '';

    const blockStyle = `border:1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.12); border-radius: 12px; padding: 10px; margin-top: 10px;`;
    const hStyle = `font-weight:800; font-size:12px; opacity:.9; margin: 0 0 6px 0;`;
    const preStyle = `white-space:pre-wrap; word-break:break-word; font-size:12px; opacity:.95; line-height:1.45;`;
    const copyBtn = `border:1px solid rgba(255,255,255,0.16); background:rgba(255,255,255,0.06); color:#fff; padding:4px 8px; border-radius:999px; cursor:pointer; font-size:12px;`;

    const bulletText = bullets.map(x => `• ${x}`).join('\n');
    const stratText = `建议上架数量：${qty}\n建议定价区间：${price}\n建议：${note}`;

    return `
      <div style="${blockStyle}">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:8px;">
          <div style="font-weight:900; font-size:13px;">执行包（Amazon 字段级）</div>
          <div style="opacity:.75; font-size:12px;">${escapeHtml(genAt)}</div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">Amazon Title</div>
              <button class="tf_copy" data-copy="${escapeHtml(title)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(title || '(空)')}</pre>
          </div>

          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">Amazon Bullets (5)</div>
              <button class="tf_copy" data-copy="${escapeHtml(bulletText)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(bulletText || '(空)')}</pre>
          </div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;">
          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">Backend Search Terms</div>
              <button class="tf_copy" data-copy="${escapeHtml(terms)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(terms || '(空)')}</pre>
          </div>

          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">SKU 建议</div>
              <button class="tf_copy" data-copy="${escapeHtml(sku)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(sku || '(空)')}</pre>
          </div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;">
          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">Midjourney Prompt</div>
              <button class="tf_copy" data-copy="${escapeHtml(mj)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(mj || '(空)')}</pre>
          </div>

          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">Stable Diffusion Prompt</div>
              <button class="tf_copy" data-copy="${escapeHtml(sd)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(sd || '(空)')}</pre>
          </div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;">
          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">上架策略</div>
              <button class="tf_copy" data-copy="${escapeHtml(stratText)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(stratText || '(空)')}</pre>
          </div>

          <div style="flex:1; min-width:260px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="${hStyle}">合规提示</div>
              <button class="tf_copy" data-copy="${escapeHtml(compliance)}" style="${copyBtn}">复制</button>
            </div>
            <pre style="${preStyle}">${escapeHtml(compliance || '(空)')}</pre>
          </div>
        </div>
      </div>
    `;
  }

  // ----------------------------
  // Rendering
  // ----------------------------
  function renderStatus(statusKey) {
    const idMap = { DO_NOW: 'do_now_list', DOING: 'doing_list', WATCH: 'watch_list' };
    const listEl = document.getElementById(idMap[statusKey]);
    if (!listEl) return;

    const raw = state.dataByStatus[statusKey] || [];
    const items = applyFilters(raw);

    const countEl = document.getElementById(`${statusKey}_count`);
    if (countEl) countEl.textContent = String(items.length);

    if (items.length === 0) {
      listEl.innerHTML = `<div style="opacity:.65; padding: 10px 2px;">暂无数据</div>`;
      return;
    }

    const html = items.map(x => {
      const saved = !!x.flags?.saved;
      const done = !!x.flags?.done;

      const isDoNow = statusKey === 'DO_NOW';
      const open = !!state.executionOpen[String(x.id)];
      const hasExec = !!pickExecution(x.payload);

      const btnSaved = `<button class="tf_btn_saved" style="${btnStyles(saved)}">${saved ? '已收藏' : '收藏'}</button>`;
      const btnDone = `<button class="tf_btn_done" style="${btnStyles(done)}">${done ? '已做' : '标记已做'}</button>`;
      const btnExec = isDoNow ? `<button class="tf_btn_exec" style="${btnStyles(hasExec)}">${hasExec ? '更新执行包' : '生成执行包'}</button>` : '';
      const btnToggle = isDoNow ? `<button class="tf_btn_exec_toggle" style="${btnStyles(open)}">${open ? '收起' : '展开'}</button>` : '';

      const execHtml = (isDoNow && open) ? renderExecutionBlock(x) : '';

      return `
        <div class="tf_item" data-id="${escapeHtml(x.id)}" style="
          border:1px solid rgba(255,255,255,0.10);
          background: rgba(0,0,0,0.10);
          border-radius: 14px;
          padding: 10px 12px;
          display:block;
        ">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap: 10px;">
            <div style="min-width:0;">
              <div style="font-weight:800; font-size:16px; line-height:1.2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                ${escapeHtml(x.term)}
              </div>
              <div style="opacity:.75; font-size:12px; margin-top:6px;">
                ${escapeHtml(x.country)} · ${escapeHtml(x.category)} · date: ${escapeHtml(x.date)}
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; justify-content:flex-end;">
              <span style="opacity:.85; font-size:12px; border:1px solid rgba(255,255,255,0.14); padding:4px 8px; border-radius:999px;">hit: ${escapeHtml(x.hit_score)}</span>
              <span style="opacity:.85; font-size:12px; border:1px solid rgba(255,255,255,0.14); padding:4px 8px; border-radius:999px;">growth: ${escapeHtml(x.growth)}</span>

              ${btnSaved}
              ${btnDone}
              ${btnExec}
              ${btnToggle}
            </div>
          </div>

          ${execHtml}
        </div>
      `;
    }).join('');

    listEl.innerHTML = html;
  }

  function renderAll() { for (const st of STATUSES) renderStatus(st.key); }

  // ----------------------------
  // Refresh
  // ----------------------------
  async function refreshAll() {
    if (state.loading) return;
    state.loading = true;
    setStatus('刷新中...');
    try {
      const results = await Promise.allSettled(STATUSES.map(s => apiGetTrends(s.key)));
      results.forEach((r, idx) => {
        const key = STATUSES[idx].key;
        state.dataByStatus[key] = (r.status === 'fulfilled') ? r.value.map(normalizeItem) : [];
      });
      renderAll();
      setStatus('已刷新');
    } catch (e) {
      console.error(e);
      setStatus(`刷新失败：${e.message || e}`);
    } finally {
      state.loading = false;
    }
  }

  // ----------------------------
  // CSV Export
  // ----------------------------
  function csvEscape(v) {
    const s = String(v ?? '');
    if (s.includes('"') || s.includes(',') || s.includes('\n') || s.includes('\r')) {
      return `"${s.replaceAll('"', '""')}"`;
    }
    return s;
  }

  function rowsToCsv(rows) {
    return rows.map(r => r.map(csvEscape).join(',')).join('\n');
  }

  function buildAmazonCsvRows(savedItems) {
    const headers = [
      'id', 'term', 'action_level', 'country', 'category', 'date',
      'amazon_title',
      'bullet1', 'bullet2', 'bullet3', 'bullet4', 'bullet5',
      'backend_search_terms',
      'price_range', 'suggested_quantity', 'strategy_note',
      'midjourney_prompt', 'stable_diffusion_prompt',
      'sku_style',
      'generated_at', 'generator'
    ];

    const rows = [headers];

    let withExec = 0;
    for (const it of savedItems) {
      const ex = pickExecution(it.payload);
      if (!ex) continue;
      const amazon = ex.amazon || {};
      const bullets = compactLines(amazon.bullets || ex.bullet_points || []);
      while (bullets.length < 5) bullets.push('');

      rows.push([
        it.id,
        it.term,
        it.action_level,
        it.country,
        it.category,
        it.date,
        amazon.title || '',
        bullets[0] || '',
        bullets[1] || '',
        bullets[2] || '',
        bullets[3] || '',
        bullets[4] || '',
        amazon.backend_search_terms || compactLines(ex.search_terms || []).join(' '),
        ex?.listing_strategy?.price_range ?? '',
        ex?.listing_strategy?.suggested_quantity ?? '',
        ex?.listing_strategy?.note ?? '',
        ex?.design_prompt?.midjourney ?? '',
        ex?.design_prompt?.stable_diffusion ?? '',
        amazon.sku_style || '',
        ex.generated_at || '',
        ex.generator || '',
      ]);
      withExec += 1;
    }

    return { rows, withExec, totalSaved: savedItems.length };
  }

  // ----------------------------
  // Click handling
  // ----------------------------
  async function onClickList(e) {
    const itemEl = e.target.closest('.tf_item');
    if (!itemEl) return;
    const id = itemEl.getAttribute('data-id');
    if (!id) return;

    const savedBtn = e.target.closest('.tf_btn_saved');
    const doneBtn = e.target.closest('.tf_btn_done');
    const execBtn = e.target.closest('.tf_btn_exec');
    const toggleBtn = e.target.closest('.tf_btn_exec_toggle');
    const copyBtn = e.target.closest('.tf_copy');

    if (copyBtn) {
      const txt = copyBtn.getAttribute('data-copy') || '';
      const ok = await copyText(txt);
      setStatus(ok ? '已复制到剪贴板' : '复制失败（请手动选中复制）');
      return;
    }

    let found = null;
    let foundStatus = null;
    for (const st of STATUSES) {
      const arr = state.dataByStatus[st.key] || [];
      const hit = arr.find(x => String(x.id) === String(id));
      if (hit) { found = hit; foundStatus = st.key; break; }
    }
    if (!found) return;

    if (toggleBtn) {
      if (foundStatus !== 'DO_NOW') return;
      const key = String(id);
      state.executionOpen[key] = !state.executionOpen[key];
      renderStatus('DO_NOW');
      return;
    }

    if (execBtn) {
      if (foundStatus !== 'DO_NOW') return;
      try {
        execBtn.disabled = true;
        execBtn.style.opacity = '0.7';
        setStatus('生成执行包中...');
        await apiPostGenerateExecution(id);
        await refreshAll();
        state.executionOpen[String(id)] = true;
        renderStatus('DO_NOW');
        setStatus('执行包已生成并写回');
      } catch (e2) {
        console.error(e2);
        setStatus(`生成失败：${e2.message || e2}`);
      } finally {
        execBtn.disabled = false;
        execBtn.style.opacity = '1';
      }
      return;
    }

    if (!savedBtn && !doneBtn) return;

    try {
      if (savedBtn) {
        const next = !found.flags.saved;
        found.flags.saved = next;
        renderStatus(foundStatus);
        await apiPostFlags(id, { saved: next });
      }

      if (doneBtn) {
        const next = !found.flags.done;
        found.flags.done = next;
        renderStatus(foundStatus);
        await apiPostFlags(id, { done: next });
      }

      if (state.onlySaved || state.onlyUndone) renderAll();
      setStatus('已写回后端');
    } catch (e3) {
      console.error(e3);
      setStatus(`写回失败：${e3.message || e3}`);
      refreshAll();
    }
  }

  function bindEvents() {
    const idMap = { DO_NOW: 'do_now_list', DOING: 'doing_list', WATCH: 'watch_list' };
    for (const k of Object.keys(idMap)) {
      const el = document.getElementById(idMap[k]);
      if (el) el.addEventListener('click', onClickList);
    }

    const onlySaved = $('#tf_only_saved');
    const onlyUndone = $('#tf_only_undone');
    const exportJsonBtn = $('#tf_export_saved');
    const exportCsvBtn = $('#tf_export_amazon_csv');

    const onFilterChange = debounce(() => {
      state.onlySaved = !!onlySaved?.checked;
      state.onlyUndone = !!onlyUndone?.checked;
      renderAll();
      setStatus(`筛选：${state.onlySaved ? '只看收藏 ' : ''}${state.onlyUndone ? '只看未做' : ''}`.trim() || '无筛选');
    }, 80);

    if (onlySaved) onlySaved.addEventListener('change', onFilterChange);
    if (onlyUndone) onlyUndone.addEventListener('change', onFilterChange);

    if (exportJsonBtn) {
      exportJsonBtn.addEventListener('click', () => {
        const all = []
          .concat(state.dataByStatus.DO_NOW || [])
          .concat(state.dataByStatus.DOING || [])
          .concat(state.dataByStatus.WATCH || [])
          .filter(x => x?.flags?.saved);

        const payload = {
          meta: {
            exported_at: new Date().toISOString(),
            country: state.country,
            category: state.category,
            count: all.length,
          },
          items: all,
        };

        const ymd = new Date().toISOString().slice(0, 10).replaceAll('-', '');
        const fname = `trendforge_saved_${state.country}_${state.category || 'ALL'}_${ymd}.json`;
        downloadJson(fname, payload);
        setStatus(`已导出收藏：${all.length}条`);
      });
    }

    if (exportCsvBtn) {
      exportCsvBtn.addEventListener('click', () => {
        const saved = []
          .concat(state.dataByStatus.DO_NOW || [])
          .concat(state.dataByStatus.DOING || [])
          .concat(state.dataByStatus.WATCH || [])
          .filter(x => x?.flags?.saved);

        const { rows, withExec, totalSaved } = buildAmazonCsvRows(saved);
        const csv = rowsToCsv(rows);

        const ymd = new Date().toISOString().slice(0, 10).replaceAll('-', '');
        const fname = `trendforge_amazon_listing_${state.country}_${state.category || 'ALL'}_${ymd}.csv`;
        downloadText(fname, csv, 'text/csv;charset=utf-8');

        const skipped = totalSaved - withExec;
        setStatus(`已导出CSV：${withExec}条（跳过无执行包：${skipped}条）`);
      });
    }
  }

  function boot() {
    ensureToolbar();
    ensureLists();
    bindEvents();
    refreshAll();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();