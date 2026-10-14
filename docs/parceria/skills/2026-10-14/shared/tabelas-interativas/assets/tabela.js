/*!
 * tabela.js — tabela interativa PT-BR, sem dependências.
 * Filtro + ordenação na linha de cabeçalho · agrupamento multinível por qualquer coluna · drill-down.
 * Uso: const t = Tabela.create('#el', { rows: [...], columns: [...] });
 */
(function (global) {
  'use strict';

  const DARK = '--dt-bg:#0d1117;--dt-fg:#e6edf3;--dt-muted:#8d96a0;--dt-line:#30363d;--dt-head:#161b22;--dt-hover:#1b2230;--dt-accent:#4493f8;--dt-accent-soft:#132a45;--dt-group:#12171e;--dt-shadow:0 8px 24px rgba(0,0,0,.5)';
  const FONT = '13px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif';
  const CSS = `
.dt,.dt-pop,.dt-panel{--dt-bg:#fff;--dt-fg:#1f2328;--dt-muted:#656d76;--dt-line:#d8dee4;--dt-head:#f6f8fa;--dt-hover:#eef4fb;--dt-accent:#0969da;--dt-accent-soft:#ddf4ff;--dt-group:#f9fafb;--dt-shadow:0 8px 24px rgba(31,35,40,.15)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .dt,:root:not([data-theme="light"]) .dt-pop,:root:not([data-theme="light"]) .dt-panel{${DARK}}}
:root[data-theme="dark"] .dt,:root[data-theme="dark"] .dt-pop,:root[data-theme="dark"] .dt-panel{${DARK}}
.dt{font:${FONT};color:var(--dt-fg);background:var(--dt-bg);border:1px solid var(--dt-line);border-radius:8px;display:flex;flex-direction:column;min-width:0;overflow:hidden}
.dt *,.dt-pop *,.dt-panel *{box-sizing:border-box}
.dt [hidden],.dt-pop [hidden],.dt-panel [hidden]{display:none!important}
.dt button,.dt-pop button,.dt-panel button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;padding:0}
.dt button:disabled,.dt-panel button:disabled{opacity:.4;cursor:default}
.dt-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;padding:8px 10px;border-bottom:1px solid var(--dt-line)}
.dt-zone{flex:1 1 260px;display:flex;flex-wrap:wrap;align-items:center;gap:6px;min-height:30px;padding:3px 6px;border:1px dashed var(--dt-line);border-radius:6px;color:var(--dt-muted)}
.dt-zone.dt-over{border-color:var(--dt-accent);background:var(--dt-accent-soft)}
.dt-chip{display:inline-flex;align-items:center;gap:4px;padding:2px 3px 2px 8px;border-radius:999px;background:var(--dt-accent-soft);color:var(--dt-accent);font-weight:600;white-space:nowrap;cursor:grab}
.dt-chip button{width:18px;height:18px;border-radius:50%;line-height:18px}
.dt-chip button:hover{background:var(--dt-accent);color:var(--dt-bg)}
.dt-sep{color:var(--dt-muted)}
.dt-add{border:1px solid var(--dt-line);border-radius:6px;background:var(--dt-bg);color:var(--dt-fg);font:inherit;padding:4px 6px}
.dt-btn{border:1px solid var(--dt-line)!important;border-radius:6px;padding:4px 8px!important;white-space:nowrap}
.dt-btn:hover:not(:disabled){background:var(--dt-hover)!important}
.dt-count{margin-left:auto;color:var(--dt-muted);white-space:nowrap;font-variant-numeric:tabular-nums}
.dt-crumbs{display:flex;flex-wrap:wrap;align-items:center;gap:4px;padding:6px 10px;border-bottom:1px solid var(--dt-line);background:var(--dt-accent-soft)}
.dt-crumbs [data-crumb]{color:var(--dt-accent);font-weight:600;padding:1px 4px;border-radius:4px}
.dt-crumbs [data-crumb]:hover{text-decoration:underline}
.dt-crumbs .dt-back{margin-left:auto;color:var(--dt-fg);font-weight:500;text-decoration:none!important;background:var(--dt-bg)}
.dt-cur{font-weight:700}
.dt-scroll{overflow:auto;max-height:var(--dt-max-height,70vh)}
.dt table{border-collapse:separate;border-spacing:0;width:100%}
.dt th{position:sticky;top:0;z-index:2;background:var(--dt-head);border-bottom:1px solid var(--dt-line);padding:6px;text-align:left;vertical-align:top;font-weight:600;min-width:100px}
.dt th+th{border-left:1px solid var(--dt-line)}
.dt-h{display:flex;align-items:center;gap:2px;margin-bottom:4px}
.dt-sort{flex:1;display:flex;align-items:center;gap:4px;min-width:0;padding:2px 3px;border-radius:4px;cursor:pointer;user-select:none}
.dt-sort:hover{background:var(--dt-hover)}
.dt-sort:focus-visible,.dt-mbtn:focus-visible{outline:2px solid var(--dt-accent)}
.dt-lbl{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:grab}
.dt-arrow{color:var(--dt-muted);font-size:10px;white-space:nowrap;opacity:.6}
.dt-sorted .dt-arrow{color:var(--dt-accent);opacity:1}
.dt-mbtn{width:22px;height:22px;border-radius:4px;color:var(--dt-muted)}
.dt-mbtn:hover,.dt-mbtn[aria-expanded="true"]{background:var(--dt-hover)!important;color:var(--dt-fg)}
.dt-filtered .dt-mbtn{color:var(--dt-accent)}
.dt-f{width:100%;min-width:60px;font:inherit;font-weight:400;padding:3px 6px;border:1px solid var(--dt-line);border-radius:4px;background:var(--dt-bg);color:var(--dt-fg)}
.dt-f:focus{outline:2px solid var(--dt-accent);outline-offset:-1px}
.dt-filtered .dt-f{border-color:var(--dt-accent);background:var(--dt-accent-soft)}
.dt td{padding:5px 8px;border-bottom:1px solid var(--dt-line);white-space:nowrap}
.dt .dt-n{text-align:right;font-variant-numeric:tabular-nums}
.dt tr.dt-leaf{cursor:pointer}
.dt tr.dt-leaf:hover td{background:var(--dt-hover)}
.dt tr.dt-sel td{background:var(--dt-accent-soft)!important}
.dt tr.dt-grp td{background:var(--dt-group);font-weight:600;cursor:pointer}
.dt tr.dt-grp:hover td{background:var(--dt-hover)}
.dt tr:focus-visible{outline:2px solid var(--dt-accent);outline-offset:-2px}
.dt-gl{display:flex;align-items:center;gap:6px}
.dt-caret{display:inline-block;width:12px;font-size:10px;transition:transform .12s;color:var(--dt-muted)}
.dt-open .dt-caret{transform:rotate(90deg)}
.dt-gk{color:var(--dt-muted);font-weight:400}
.dt-badge{font-weight:500;font-size:11px;color:var(--dt-muted);background:var(--dt-bg);border:1px solid var(--dt-line);border-radius:999px;padding:0 6px}
.dt .dt-drill{margin-left:auto;font-weight:500;font-size:12px;color:var(--dt-accent);padding:1px 6px;border-radius:4px;opacity:.55}
.dt tr.dt-grp:hover .dt-drill,.dt tr.dt-grp:focus .dt-drill,.dt .dt-drill:focus{opacity:1}
.dt .dt-drill:hover{background:var(--dt-accent-soft)}
.dt tfoot td{position:sticky;bottom:0;z-index:1;background:var(--dt-head);font-weight:700;border-top:1px solid var(--dt-line);border-bottom:0}
.dt-more td{text-align:center}
.dt-more button,.dt-empty button{color:var(--dt-accent);font-weight:600}
.dt-empty td{text-align:center;color:var(--dt-muted);padding:24px}
.dt-pop{position:fixed;z-index:1000;width:260px;background:var(--dt-bg);color:var(--dt-fg);border:1px solid var(--dt-line);border-radius:8px;box-shadow:var(--dt-shadow);padding:4px;font:${FONT}}
.dt-mi{display:block;width:100%;text-align:left;padding:5px 8px!important;border-radius:4px}
.dt-mi:hover{background:var(--dt-hover)!important}
.dt-pop hr{border:0;border-top:1px solid var(--dt-line);margin:4px 0}
.dt-pop .dt-f{margin:2px 0}
.dt-vals{max-height:220px;overflow:auto}
.dt-vals label{display:flex;align-items:center;gap:6px;padding:2px 6px;border-radius:4px;cursor:pointer}
.dt-vals label:hover{background:var(--dt-hover)}
.dt-v{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dt-c{margin-left:auto;color:var(--dt-muted);font-size:11px;font-variant-numeric:tabular-nums}
.dt-note{color:var(--dt-muted);font-size:11px;padding:2px 6px}
.dt-panel{position:fixed;z-index:999;top:0;right:0;bottom:0;width:min(420px,100vw);background:var(--dt-bg);color:var(--dt-fg);border-left:1px solid var(--dt-line);box-shadow:var(--dt-shadow);display:flex;flex-direction:column;font:${FONT}}
.dt-ph{display:flex;align-items:center;gap:6px;padding:10px 12px;border-bottom:1px solid var(--dt-line)}
.dt-ph h3{margin:0;font-size:15px;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dt-pb{overflow:auto;padding:4px 12px 16px}
.dt-pb dl{margin:0;display:grid;grid-template-columns:minmax(90px,38%) 1fr}
.dt-pb dt,.dt-pb dd{margin:0;padding:7px 0;border-bottom:1px solid var(--dt-line)}
.dt-pb dt{color:var(--dt-muted);padding-right:8px}
.dt-pb dd{display:flex;align-items:center;gap:6px;word-break:break-word}
.dt-pb dd button{margin-left:auto;color:var(--dt-accent);font-size:12px;padding:0 4px;white-space:nowrap;opacity:.55}
.dt-pb dd:hover button,.dt-pb dd button:focus{opacity:1}
.dt-extra{margin-top:12px}
`;

  function injectCss() {
    if (document.getElementById('tabela-js-css')) return;
    const s = document.createElement('style');
    s.id = 'tabela-js-css';
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  // ---------- utilidades ----------
  const collator = new Intl.Collator('pt-BR', { numeric: true, sensitivity: 'base' });
  const NUMERIC = { number: 1, integer: 1, currency: 1, percent: 1 };
  const isNum = (t) => NUMERIC[t] === 1;
  const PARTS = { ano: 'ano', mes: 'mês', dia: 'dia' };
  const EMPTY_KEY = ' ';
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const norm = (s) => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const fmtInt = (n) => Number(n).toLocaleString('pt-BR');
  const isEmpty = (v) => v == null || v === '' || (typeof v === 'number' && isNaN(v));

  function parseNum(s) {
    if (typeof s === 'number') return s;
    s = String(s).trim().replace(/\s|R\$|%/g, '');
    if (!s) return NaN;
    if (s.includes(',')) s = s.replace(/\./g, '').replace(',', '.');
    else if (/^-?\d{1,3}(\.\d{3})+$/.test(s)) s = s.replace(/\./g, '');
    return Number(s);
  }
  function calendarDate(y, m, day) {
    const d = new Date(0);
    d.setFullYear(y, m - 1, day);
    d.setHours(0, 0, 0, 0);
    return d.getFullYear() === y && d.getMonth() === m - 1 && d.getDate() === day ? d : null;
  }
  function toDate(v) {
    if (v instanceof Date) return isNaN(v) ? null : v;
    if (typeof v === 'number') return new Date(v);
    const s = String(v);
    const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) return calendarDate(+m[1], +m[2], +m[3]);
    const b = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
    if (b) return calendarDate(+b[3], +b[2], +b[1]);
    const d = new Date(s);
    return isNaN(d) ? null : d;
  }
  function dayStart(ts) { const d = new Date(ts); d.setHours(0, 0, 0, 0); return d.getTime(); }
  function parseDateInput(s) {
    s = String(s).trim();
    if (!/^(\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2})$/.test(s)) return NaN;
    const d = toDate(s);
    return d ? d.getTime() : NaN;
  }
  const cmp = (a, b) => (typeof a === 'number' && typeof b === 'number' ? a - b : collator.compare(String(a), String(b)));
  const prettify = (k) => String(k).replace(/[_-]+/g, ' ').replace(/([a-z])([A-Z])/g, '$1 $2').replace(/^./, (c) => c.toUpperCase());

  function inferType(key, values) {
    const s = values.filter((v) => !isEmpty(v)).slice(0, 200);
    if (!s.length) return 'text';
    if (s.every((v) => v instanceof Date || (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}/.test(v)))) return 'date';
    if (s.every((v) => typeof v === 'number')) {
      if (/(^|[_\s])(id|cod|codigo|ano|year|cep|cpf|cnpj|telefone|numero|nf)$/i.test(key) || /[a-z]Id$/.test(key)) return 'text';
      return s.every(Number.isInteger) ? 'integer' : 'number';
    }
    return 'text';
  }

  // ---------- componente ----------
  function create(target, options) {
    injectCss();
    const root = typeof target === 'string' ? document.querySelector(target) : target;
    if (!root) throw new Error('Tabela: container não encontrado');
    const opts = Object.assign({ rows: [], columns: null, groupBy: [], sort: [], pageSize: 200, maxHeight: '70vh', expandLevels: 0, rowTitle: null, rowKey: 'id', detail: null }, options);

    let data = [], rowIdx = new Map(), cols = [], colMap = {};
    let current = [], tree = null, groupIndex = new Map(), pendingExpand = opts.expandLevels > 0;
    const st = { sort: [], filters: {}, values: {}, groupBy: [], focus: [], open: new Set(), limits: {}, sel: null, trail: [] };
    const specCache = new Map();

    // --- colunas e especificações de agrupamento ---
    function setData(rows) {
      data = rows || [];
      rowIdx = new Map(data.map((r, i) => [r, i]));
      // Uma resposta vazia transitória preserva o esquema e o contexto da tabela.
      const src = opts.columns || (data.length ? [...new Set(data.slice(0, 50).flatMap((r) => Object.keys(r)))] : cols);
      cols = src.map((c) => {
        c = typeof c === 'string' ? { key: c } : Object.assign({}, c);
        c.label = c.label || prettify(c.key);
        c.type = c.type || inferType(c.key, data.slice(0, 200).map((r) => r[c.key]));
        if (c.agg === undefined) c.agg = null; // Agregação exige regra explícita do domínio.
        return c;
      });
      colMap = {};
      cols.forEach((c) => (colMap[c.key] = c));
      specCache.clear();
      st.groupBy = st.groupBy.filter((id) => gspec(id));
      if (st.focus.some((f) => !gspec(f.spec))) st.trail = [];
      st.focus = st.focus.filter((f) => gspec(f.spec));
      st.sort = st.sort.filter((s) => colMap[s.key]);
      for (const state of [st.filters, st.values]) {
        for (const key of Object.keys(state)) if (!colMap[key]) Reflect.deleteProperty(state, key);
      }
    }
    const vis = () => cols.filter((c) => !c.hidden);
    const raw = (c, r) => (c.value ? c.value(r) : r[c.key]);

    function gspec(id) {
      if (specCache.has(id)) return specCache.get(id);
      let key = id, part;
      const i = id.lastIndexOf(':');
      if (i > 0 && PARTS[id.slice(i + 1)] && colMap[id.slice(0, i)] && colMap[id.slice(0, i)].type === 'date') { key = id.slice(0, i); part = id.slice(i + 1); }
      const col = colMap[key];
      const spec = col ? { id, col, part, label: col.label + (part ? ` (${PARTS[part]})` : '') } : null;
      specCache.set(id, spec);
      return spec;
    }

    function fmtVal(c, v, row) {
      if (isEmpty(v)) return '';
      if (c.format) return String(c.format(v, row));
      const n = typeof v === 'number' ? v : parseNum(v);
      switch (c.type) {
        case 'currency': return isNaN(n) ? String(v) : n.toLocaleString('pt-BR', { style: 'currency', currency: c.currency || 'BRL' });
        case 'percent': return isNaN(n) ? String(v) : n.toLocaleString('pt-BR', { style: 'percent', minimumFractionDigits: c.decimals ?? 1, maximumFractionDigits: c.decimals ?? 1 });
        case 'integer': return isNaN(n) ? String(v) : n.toLocaleString('pt-BR', { maximumFractionDigits: 0 });
        case 'number': return isNaN(n) ? String(v) : n.toLocaleString('pt-BR', { maximumFractionDigits: c.decimals ?? 2 });
        case 'date': { const d = toDate(v); return d ? d.toLocaleDateString('pt-BR') : String(v); }
        default: return String(v);
      }
    }
    const fmt = (c, r) => fmtVal(c, raw(c, r), r);
    const fmtAgg = (c, v) => (v == null ? '' : c.agg === 'count' ? fmtInt(v) : fmtVal(c, v));
    function sortVal(c, r) {
      const v = raw(c, r);
      if (isEmpty(v)) return null;
      if (isNum(c.type)) { const n = parseNum(v); return isNaN(n) ? null : n; }
      if (c.type === 'date') { const d = toDate(v); return d ? d.getTime() : null; }
      return String(v);
    }
    function groupOf(g, r) {
      const v = raw(g.col, r);
      if (isEmpty(v)) return { key: EMPTY_KEY, label: '(vazio)', sort: null };
      if (g.col.type === 'date') {
        const d = toDate(v);
        if (!d) return { key: String(v), label: String(v), sort: String(v) };
        const y = d.getFullYear(), m = d.getMonth();
        if (g.part === 'ano') return { key: String(y), label: String(y), sort: y };
        if (g.part === 'mes') return { key: y + '-' + m, label: d.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' }), sort: y * 12 + m };
        const t = dayStart(d.getTime());
        return { key: String(t), label: d.toLocaleDateString('pt-BR'), sort: t };
      }
      return { key: String(v), label: fmt(g.col, r), sort: sortVal(g.col, r) };
    }
    function aggregate(c, rows) {
      if (!c.agg) return null;
      if (typeof c.agg === 'function') return c.agg(rows);
      if (c.agg === 'count') return rows.length;
      let n = 0, sum = 0, min = Infinity, max = -Infinity;
      for (const r of rows) {
        const v = sortVal(c, r);
        if (v == null) continue;
        n++; sum += v; if (v < min) min = v; if (v > max) max = v;
      }
      if (!n) return null;
      return c.agg === 'sum' ? sum : c.agg === 'avg' ? sum / n : c.agg === 'min' ? min : c.agg === 'max' ? max : null;
    }

    // --- filtros ---
    function compileOne(c, t) {
      if (t === '∅' || norm(t) === '(vazio)') return (r) => isEmpty(raw(c, r));
      const typed = isNum(c.type)
        ? { parse: c.type === 'percent' ? (s) => parseNum(s) / 100 : parseNum, get: (r) => sortVal(c, r) }
        : c.type === 'date' ? { parse: parseDateInput, get: (r) => { const v = sortVal(c, r); return v == null ? null : dayStart(v); } } : null;
      if (typed) {
        let m = t.match(/^(.+?)\.\.(.+)$/);
        if (m) {
          const a = typed.parse(m[1]), b = typed.parse(m[2]);
          if (c.type === 'date' && (isNaN(a) || isNaN(b))) return () => false;
          if (!isNaN(a) && !isNaN(b)) return (r) => { const v = typed.get(r); return v != null && v >= a && v <= b; };
        }
        m = t.match(/^(>=|<=|!=|<>|>|<|=)\s*(.+)$/);
        if (m) {
          const x = typed.parse(m[2]), op = m[1];
          if (c.type === 'date' && isNaN(x)) return () => false;
          if (!isNaN(x)) return (r) => {
            const v = typed.get(r);
            if (v == null) return op === '!=' || op === '<>';
            switch (op) { case '>': return v > x; case '<': return v < x; case '>=': return v >= x; case '<=': return v <= x; case '=': return Math.abs(v - x) < 1e-9; default: return Math.abs(v - x) >= 1e-9; }
          };
        }
      }
      if (t.startsWith('!')) { const q = norm(t.slice(1)); return q ? (r) => !norm(fmt(c, r)).includes(q) : () => true; }
      if (t.startsWith('=')) { const q = norm(t.slice(1)); return (r) => norm(fmt(c, r)) === q; }
      const q = norm(t);
      return (r) => norm(fmt(c, r)).includes(q) || norm(raw(c, r) ?? '').includes(q);
    }
    function compileFilter(c, text) {
      const parts = String(text || '').split('|').map((s) => s.trim()).filter(Boolean);
      if (!parts.length) return null;
      const tests = parts.map((p) => compileOne(c, p));
      return (r) => tests.some((f) => f(r));
    }

    function compute(exceptKey) {
      const m = [];
      for (const k in st.filters) if (k !== exceptKey && colMap[k]) { const f = compileFilter(colMap[k], st.filters[k]); if (f) m.push(f); }
      for (const k in st.values) if (k !== exceptKey && colMap[k] && st.values[k]) { const g = gspec(k), set = st.values[k]; m.push((r) => set.has(groupOf(g, r).key)); }
      for (const f of st.focus) { const g = gspec(f.spec); if (g) m.push((r) => groupOf(g, r).key === f.key); }
      let rows = m.length ? data.filter((r) => m.every((f) => f(r))) : data.slice();
      if (exceptKey !== undefined) return rows;
      const ss = st.sort.map((s) => ({ c: colMap[s.key], dir: s.dir })).filter((s) => s.c);
      if (ss.length) {
        const keyed = rows.map((r) => ({ r, v: ss.map((s) => sortVal(s.c, r)) }));
        keyed.sort((a, b) => {
          for (let i = 0; i < ss.length; i++) {
            const x = a.v[i], y = b.v[i];
            if (x == null || y == null) { if (x == null && y == null) continue; return x == null ? 1 : -1; }
            const d = cmp(x, y) * ss[i].dir;
            if (d) return d;
          }
          return 0;
        });
        rows = keyed.map((k) => k.r);
      }
      return rows;
    }

    // --- agrupamento ---
    const effectiveGroups = () => st.groupBy.filter((s) => !st.focus.some((f) => f.spec === s)).map(gspec).filter(Boolean);
    function buildGroups(rows, specs, depth, path, labels) {
      const g = specs[depth], map = new Map();
      for (const r of rows) {
        const gv = groupOf(g, r);
        let e = map.get(gv.key);
        if (!e) map.set(gv.key, (e = Object.assign(gv, { rows: [] })));
        e.rows.push(r);
      }
      const list = [...map.values()];
      for (const e of list) {
        e.spec = g; e.depth = depth;
        e.path = path.concat([[g.id, e.key]]);
        e.labels = labels.concat(e.label);
        e.id = JSON.stringify(e.path);
        e.aggs = {};
        for (const c of cols) if (c.agg) e.aggs[c.key] = aggregate(c, e.rows);
        e.children = depth + 1 < specs.length ? buildGroups(e.rows, specs, depth + 1, e.path, e.labels) : null;
      }
      const s = st.sort[0], sc = s && colMap[s.key];
      const by = sc && sc === g.col ? (e) => e.sort : sc && sc.agg ? (e) => e.aggs[sc.key] : (e) => e.sort;
      const dir = sc && (sc === g.col || sc.agg) ? s.dir : 1;
      list.sort((a, b) => {
        const x = by(a), y = by(b);
        if (x == null || y == null) return x == null && y == null ? 0 : x == null ? 1 : -1;
        return cmp(x, y) * dir;
      });
      return list;
    }
    function walk(list, fn) { if (list) for (const g of list) { fn(g); walk(g.children, fn); } }

    // --- DOM ---
    root.classList.add('dt');
    root.innerHTML = `
      <div class="dt-bar">
        <div class="dt-zone" data-zone aria-label="Agrupamentos"></div>
        <select class="dt-add" data-add aria-label="Agrupar por coluna"></select>
        <button class="dt-btn" data-act="expand">Expandir tudo</button>
        <button class="dt-btn" data-act="collapse">Recolher tudo</button>
        <button class="dt-btn" data-act="clear">Limpar filtros</button>
        <span class="dt-count" data-count aria-live="polite"></span>
      </div>
      <div class="dt-crumbs" data-crumbs hidden></div>
      <div class="dt-scroll"><table><thead></thead><tbody></tbody><tfoot></tfoot></table></div>`;
    const $ = (s) => root.querySelector(s);
    const zone = $('[data-zone]'), addSel = $('[data-add]'), countEl = $('[data-count]'), crumbs = $('[data-crumbs]'), scroller = $('.dt-scroll');
    const thead = $('thead'), tbody = $('tbody'), tfoot = $('tfoot');
    scroller.style.setProperty('--dt-max-height', opts.maxHeight);

    function placeholder(c) {
      if (isNum(c.type)) return '>1000 · 10..50';
      if (c.type === 'date') return '>=01/01/2025';
      return 'Filtrar…';
    }
    const HELP = 'Filtro: texto contém · =exato · !não contém · a|b (ou) · ∅ vazios · números/datas: >, <, >=, <=, !=, a..b';

    function renderHead() {
      thead.innerHTML = '<tr>' + vis().map((c) => `
        <th data-k="${esc(c.key)}"${c.width ? ` style="min-width:${esc(c.width)}"` : ''}>
          <div class="dt-h">
            <span class="dt-sort" role="button" tabindex="0" data-sort title="Clique para ordenar · Shift+clique: ordenação múltipla · arraste para agrupar"><span class="dt-lbl" draggable="true">${esc(c.label)}</span><span class="dt-arrow"></span></span>
            <button class="dt-mbtn" data-menu aria-haspopup="dialog" aria-expanded="false" aria-label="Opções de ${esc(c.label)}">▾</button>
          </div>
          <input class="dt-f" data-f type="search" autocomplete="off" placeholder="${esc(placeholder(c))}" title="${esc(HELP)}" aria-label="Filtrar ${esc(c.label)}">
        </th>`).join('') + '</tr>';
      syncHead();
    }
    function syncHead() {
      for (const th of thead.querySelectorAll('th')) {
        const k = th.dataset.k, i = st.sort.findIndex((s) => s.key === k), s = st.sort[i];
        th.classList.toggle('dt-sorted', !!s);
        th.setAttribute('aria-sort', s ? (s.dir > 0 ? 'ascending' : 'descending') : 'none');
        th.querySelector('.dt-arrow').textContent = s ? (s.dir > 0 ? '▲' : '▼') + (st.sort.length > 1 ? i + 1 : '') : '⇅';
        th.classList.toggle('dt-filtered', !!(st.filters[k] && st.filters[k].trim()) || !!st.values[k]);
        const inp = th.querySelector('.dt-f'), want = st.filters[k] || '';
        if (document.activeElement !== inp && inp.value !== want) inp.value = want;
      }
    }

    function renderZone() {
      zone.innerHTML = st.groupBy.length
        ? st.groupBy.map((s, i) => `${i ? '<span class="dt-sep">›</span>' : ''}<span class="dt-chip" draggable="true" data-gi="${i}" title="Arraste para reordenar">${esc(gspec(s).label)}<button data-ungroup="${i}" aria-label="Remover agrupamento ${esc(gspec(s).label)}">×</button></span>`).join('')
        : '<span>Arraste um cabeçalho aqui para agrupar</span>';
      let o = '<option value="">+ Agrupar por…</option>';
      for (const c of cols) {
        const ids = c.type === 'date' ? ['ano', 'mes', 'dia'].map((p) => c.key + ':' + p) : [c.key];
        for (const id of ids) if (!st.groupBy.includes(id)) o += `<option value="${esc(id)}">${esc(gspec(id).label)}</option>`;
      }
      addSel.innerHTML = o;
      const grouped = effectiveGroups().length > 0;
      $('[data-act="expand"]').hidden = $('[data-act="collapse"]').hidden = !grouped;
      $('[data-act="clear"]').disabled = !Object.keys(st.filters).some((k) => st.filters[k]) && !Object.keys(st.values).length && !st.focus.length;
    }

    function renderCrumbs() {
      crumbs.hidden = !st.focus.length;
      if (!st.focus.length) return;
      crumbs.innerHTML = '<button data-crumb="0">Todos</button>' + st.focus.map((f, i) => {
        const txt = `${esc(gspec(f.spec).label)}: ${esc(f.label)}`;
        return '<span class="dt-sep">›</span>' + (i === st.focus.length - 1 ? `<span class="dt-cur">${txt}</span>` : `<button data-crumb="${i + 1}">${txt}</button>`);
      }).join('') + `<button class="dt-btn dt-back" data-crumb="${st.focus.length - 1}">← Voltar</button>`;
    }

    function renderLeaves(rows, depth, pid, V) {
      const lim = st.limits[pid] || opts.pageSize, n = Math.min(rows.length, lim);
      const pad = depth ? ` style="padding-left:${8 + depth * 20 + 18}px"` : '';
      let h = '';
      for (let i = 0; i < n; i++) {
        const r = rows[i], idx = rowIdx.get(r);
        h += `<tr class="dt-leaf${st.sel === idx ? ' dt-sel' : ''}" tabindex="0" data-i="${idx}">` +
          V.map((c, j) => `<td${isNum(c.type) ? ' class="dt-n"' : ''}${j === 0 ? pad : ''}>${c.render ? c.render(raw(c, r), r) : esc(fmt(c, r))}</td>`).join('') + '</tr>';
      }
      if (rows.length > n) h += `<tr class="dt-more"><td colspan="${V.length}"><button data-more="${esc(pid)}">Mostrar mais ${fmtInt(Math.min(opts.pageSize, rows.length - n))} (${fmtInt(rows.length - n)} restantes)</button></td></tr>`;
      return h;
    }
    function renderGroups(list, V) {
      const firstAgg = V.findIndex((c) => c.agg);
      const span = firstAgg < 0 ? V.length : Math.max(1, firstAgg);
      let h = '';
      for (const g of list) {
        groupIndex.set(g.id, g);
        const open = st.open.has(g.id);
        h += `<tr class="dt-grp${open ? ' dt-open' : ''}" tabindex="0" data-g="${esc(g.id)}" aria-expanded="${open}">` +
          `<td colspan="${span}" style="padding-left:${8 + g.depth * 20}px"><div class="dt-gl"><span class="dt-caret">▶</span><span class="dt-gk">${esc(g.spec.label)}:</span><span>${esc(g.label)}</span><span class="dt-badge" title="linhas">${fmtInt(g.rows.length)}</span><button class="dt-drill" data-drill title="Abrir somente este grupo (duplo clique)">Detalhar ›</button></div>${firstAgg === 0 ? `<div class="dt-n">${esc(fmtAgg(V[0], g.aggs[V[0].key]))}</div>` : ''}</td>` +
          V.slice(span).map((c) => `<td${isNum(c.type) ? ' class="dt-n"' : ''}>${c.agg ? esc(fmtAgg(c, g.aggs[c.key])) : ''}</td>`).join('') + '</tr>';
        if (open) h += g.children ? renderGroups(g.children, V) : renderLeaves(g.rows, g.depth + 1, g.id, V);
      }
      return h;
    }

    function renderBody() {
      const V = vis();
      current = compute();
      groupIndex = new Map();
      const specs = effectiveGroups();
      tree = specs.length && current.length ? buildGroups(current, specs, 0, [], []) : null;
      if (pendingExpand && tree) { walk(tree, (g) => { if (g.depth < opts.expandLevels) st.open.add(g.id); }); pendingExpand = false; }
      tbody.innerHTML = !current.length
        ? `<tr class="dt-empty"><td colspan="${V.length}">Nenhuma linha corresponde aos filtros. <button data-act="clear">Limpar filtros</button></td></tr>`
        : tree ? renderGroups(tree, V) : renderLeaves(current, 0, '', V);
      tfoot.innerHTML = current.length && V.some((c) => c.agg)
        ? '<tr>' + V.map((c, i) => `<td${isNum(c.type) ? ' class="dt-n"' : ''}>${c.agg ? esc(fmtAgg(c, aggregate(c, current))) : i === 0 ? 'Total' : ''}</td>`).join('') + '</tr>'
        : '';
      countEl.textContent = current.length === data.length ? `${fmtInt(data.length)} linhas` : `${fmtInt(current.length)} de ${fmtInt(data.length)} linhas`;
      syncHead(); renderZone(); renderCrumbs();
      if (panel && st.sel != null) openPanel(st.sel, true);
    }
    function refocus(sel) {
      const tr = [...tbody.rows].find((t) => (sel.g != null && t.dataset.g === sel.g) || (sel.i != null && t.dataset.i === String(sel.i)));
      if (tr) tr.focus();
    }

    // --- ações ---
    function toggleSort(key, multi, dir) {
      const i = st.sort.findIndex((s) => s.key === key);
      if (dir !== undefined) {
        if (!dir) { if (i >= 0) st.sort.splice(i, 1); }
        else if (multi) { if (i >= 0) st.sort[i].dir = dir; else st.sort.push({ key, dir }); }
        else st.sort = [{ key, dir }];
      } else if (!multi) {
        st.sort = i < 0 ? [{ key, dir: 1 }] : st.sort[i].dir === 1 ? [{ key, dir: -1 }] : [];
      } else if (i < 0) st.sort.push({ key, dir: 1 });
      else if (st.sort[i].dir === 1) st.sort[i].dir = -1;
      else st.sort.splice(i, 1);
      renderBody();
    }
    function addGroup(id, at) {
      if (!gspec(id)) return;
      const cur = st.groupBy.indexOf(id);
      if (cur >= 0) st.groupBy.splice(cur, 1);
      st.groupBy.splice(at == null ? st.groupBy.length : at, 0, id);
      st.limits = {};
      renderBody();
    }
    const defaultSpec = (key) => (colMap[key] && colMap[key].type === 'date' ? key + ':ano' : key);
    function drill(id) {
      const g = groupIndex.get(id);
      if (!g) return;
      st.trail[st.focus.length] = new Set(st.open);
      st.focus = st.focus.concat(g.path.map(([spec, key], i) => ({ spec, key, label: g.labels[i] })));
      st.open.clear(); st.limits = {};
      renderBody();
      scroller.scrollTop = 0;
      const first = tbody.querySelector('tr[tabindex]');
      if (first) first.focus();
    }
    function addFocus(spec, key, label) {
      if (st.focus.some((f) => f.spec === spec)) st.focus = st.focus.filter((f) => f.spec !== spec);
      st.trail[st.focus.length] = new Set(st.open);
      st.focus.push({ spec, key, label });
      st.open.clear(); st.limits = {};
      renderBody();
    }
    function goCrumb(n) {
      st.focus = st.focus.slice(0, n);
      st.open = st.trail[n] || new Set();
      st.trail.length = n; st.limits = {};
      renderBody();
    }
    function clearFilters() {
      st.filters = {}; st.values = {}; st.focus = []; st.trail = []; st.limits = {};
      renderBody();
    }

    // --- menu da coluna ---
    let pop = null, popBtn = null;
    function closeMenu() {
      if (!pop) return;
      pop.remove(); pop = null;
      if (popBtn) { popBtn.setAttribute('aria-expanded', 'false'); popBtn = null; }
      document.removeEventListener('mousedown', onOutside, true);
      window.removeEventListener('scroll', onScroll, true);
      window.removeEventListener('resize', closeMenu);
    }
    const onOutside = (e) => { if (pop && !pop.contains(e.target) && e.target !== popBtn) closeMenu(); };
    const onScroll = (e) => { if (pop && !pop.contains(e.target)) closeMenu(); };
    function openMenu(btn, key) {
      if (pop && pop.dataset.k === key) return closeMenu();
      closeMenu();
      const c = colMap[key], sorted = st.sort.some((s) => s.key === key);
      pop = document.createElement('div');
      pop.className = 'dt-pop'; pop.dataset.k = key;
      pop.setAttribute('role', 'dialog'); pop.setAttribute('aria-label', 'Opções de ' + c.label);
      const grp = c.type === 'date'
        ? [['ano', 'Agrupar por ano'], ['mes', 'Agrupar por mês'], ['dia', 'Agrupar por dia']].map(([p, l]) => `<button class="dt-mi" data-gp="${esc(key + ':' + p)}">⊞ ${l}</button>`).join('')
        : `<button class="dt-mi" data-gp="${esc(key)}">⊞ Agrupar por esta coluna</button>`;
      pop.innerHTML = `<button class="dt-mi" data-s="1">▲ Ordenar crescente</button><button class="dt-mi" data-s="-1">▼ Ordenar decrescente</button>${sorted ? '<button class="dt-mi" data-s="0">Remover ordenação</button>' : ''}<hr>${grp}<hr>` +
        `<input class="dt-f" data-vs type="search" placeholder="Buscar valores…" aria-label="Buscar valores"><div class="dt-vals"></div><hr><button class="dt-mi" data-clr>Limpar filtro desta coluna</button>`;
      document.body.appendChild(pop);

      const g = gspec(key), counts = new Map();
      for (const r of compute(key)) {
        const gv = groupOf(g, r);
        const e = counts.get(gv.key);
        if (e) e.n++; else counts.set(gv.key, { key: gv.key, label: gv.label, sort: gv.sort, n: 1 });
      }
      const universe = [...counts.values()].sort((a, b) => (a.sort == null ? 1 : b.sort == null ? -1 : cmp(a.sort, b.sort)));
      const valsEl = pop.querySelector('.dt-vals'), search = pop.querySelector('[data-vs]');
      let shown = [], matched = [];
      function drawVals() {
        const q = norm(search.value.trim()), set = st.values[key];
        const match = q ? universe.filter((u) => norm(u.label).includes(q)) : universe;
        matched = match;
        shown = match.slice(0, 500);
        const all = matched.length > 0 && matched.every((u) => !set || set.has(u.key));
        valsEl.innerHTML = `<label><input type="checkbox" data-all ${all ? 'checked' : ''}><span class="dt-v"><b>(Selecionar ${q ? 'resultados' : 'tudo'})</b></span></label>` +
          shown.map((u, i) => `<label><input type="checkbox" data-vi="${i}" ${!set || set.has(u.key) ? 'checked' : ''}><span class="dt-v">${esc(u.label)}</span><span class="dt-c">${fmtInt(u.n)}</span></label>`).join('') +
          (match.length > shown.length ? `<div class="dt-note">+${fmtInt(match.length - shown.length)} valores — refine a busca</div>` : '') +
          (!match.length ? '<div class="dt-note">Nenhum valor</div>' : '');
      }
      drawVals();
      search.addEventListener('input', drawVals);
      valsEl.addEventListener('change', (e) => {
        let set = st.values[key] || new Set(universe.map((u) => u.key));
        if (e.target.hasAttribute('data-all')) matched.forEach((u) => (e.target.checked ? set.add(u.key) : set.delete(u.key)));
        else { const u = shown[+e.target.dataset.vi]; if (e.target.checked) set.add(u.key); else set.delete(u.key); }
        if (universe.every((u) => set.has(u.key))) Reflect.deleteProperty(st.values, key); else st.values[key] = set;
        st.limits = {};
        renderBody(); drawVals();
      });
      pop.addEventListener('click', (e) => {
        const b = e.target.closest('button');
        if (!b) return;
        if (b.dataset.s !== undefined) { closeMenu(); toggleSort(key, e.shiftKey, +b.dataset.s); }
        else if (b.dataset.gp) { closeMenu(); addGroup(b.dataset.gp); }
        else if (b.hasAttribute('data-clr')) { Reflect.deleteProperty(st.filters, key); Reflect.deleteProperty(st.values, key); closeMenu(); renderBody(); }
      });

      const rect = btn.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
      pop.style.left = Math.max(8, Math.min(rect.right - w, innerWidth - w - 8)) + 'px';
      pop.style.top = (rect.bottom + 4 + h > innerHeight ? Math.max(8, rect.top - h - 4) : rect.bottom + 4) + 'px';
      popBtn = btn; btn.setAttribute('aria-expanded', 'true');
      document.addEventListener('mousedown', onOutside, true);
      window.addEventListener('scroll', onScroll, true);
      window.addEventListener('resize', closeMenu);
      search.focus();
    }

    // --- painel de detalhe ---
    let panel = null;
    function openPanel(idx, silent) {
      const r = data[idx];
      if (!r) return closePanel();
      st.sel = idx;
      for (const tr of tbody.rows) tr.classList.toggle('dt-sel', tr.dataset.i === String(idx));
      if (!panel) {
        panel = document.createElement('aside');
        panel.className = 'dt-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'Detalhe da linha');
        document.body.appendChild(panel);
        panel.addEventListener('click', onPanelClick);
      }
      const pos = current.indexOf(r);
      const tcol = cols.find((c) => c.type === 'text') || cols[0];
      const title = opts.rowTitle ? opts.rowTitle(r) : tcol ? fmt(tcol, r) : 'Detalhe';
      panel.innerHTML = `<div class="dt-ph"><h3 title="${esc(title)}">${esc(title)}</h3><span class="dt-count">${pos >= 0 ? `${fmtInt(pos + 1)} de ${fmtInt(current.length)}` : 'fora do filtro'}</span>` +
        `<button class="dt-btn" data-nav="-1" ${pos <= 0 ? 'disabled' : ''} aria-label="Linha anterior" title="Anterior (↑)">↑</button><button class="dt-btn" data-nav="1" ${pos < 0 || pos >= current.length - 1 ? 'disabled' : ''} aria-label="Próxima linha" title="Próxima (↓)">↓</button><button class="dt-btn" data-close aria-label="Fechar" title="Fechar (Esc)">✕</button></div>` +
        `<div class="dt-pb"><dl>${cols.map((c) => {
          const v = raw(c, r);
          return `<dt>${esc(c.label)}</dt><dd><span>${c.render ? c.render(v, r) : isEmpty(v) ? '<span class="dt-gk">—</span>' : esc(fmt(c, r))}</span>${isEmpty(v) ? '' : `<button data-fk="${esc(c.key)}" title="Mostrar somente linhas com este valor">Filtrar por este</button>`}</dd>`;
        }).join('')}</dl>${opts.detail ? `<div class="dt-extra">${opts.detail(r)}</div>` : ''}</div>`;
      if (!silent) {
        const tr = [...tbody.rows].find((t) => t.dataset.i === String(idx));
        if (tr) tr.scrollIntoView({ block: 'nearest' });
        panel.querySelector('[data-close]').focus();
      }
    }
    function closePanel() {
      if (panel) { panel.remove(); panel = null; }
      const prev = st.sel;
      st.sel = null;
      for (const tr of tbody.querySelectorAll('.dt-sel')) tr.classList.remove('dt-sel');
      if (prev != null) refocus({ i: prev });
    }
    function navPanel(d) {
      const pos = current.indexOf(data[st.sel]), next = current[pos + d];
      if (pos >= 0 && next) {
        const idx = rowIdx.get(next);
        openPanel(idx);
        panel.querySelector(`[data-nav="${d}"]:not(:disabled)`)?.focus();
      }
    }
    function onPanelClick(e) {
      const b = e.target.closest('button');
      if (!b) return;
      if (b.hasAttribute('data-close')) closePanel();
      else if (b.dataset.nav) navPanel(+b.dataset.nav);
      else if (b.dataset.fk) { const r = data[st.sel], g = gspec(b.dataset.fk), gv = groupOf(g, r); addFocus(g.id, gv.key, gv.label); }
    }

    // --- eventos ---
    let debounce = null, drag = null;
    thead.addEventListener('click', (e) => {
      const th = e.target.closest('th');
      if (!th) return;
      if (e.target.closest('[data-menu]')) openMenu(e.target.closest('[data-menu]'), th.dataset.k);
      else if (e.target.closest('[data-sort]')) toggleSort(th.dataset.k, e.shiftKey);
    });
    thead.addEventListener('keydown', (e) => {
      const s = e.target.closest('[data-sort]');
      if (s && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); toggleSort(s.closest('th').dataset.k, e.shiftKey); }
    });
    thead.addEventListener('input', (e) => {
      if (!e.target.matches('[data-f]')) return;
      const k = e.target.closest('th').dataset.k;
      st.filters[k] = e.target.value;
      clearTimeout(debounce);
      debounce = setTimeout(() => { st.limits = {}; renderBody(); }, 120);
    });
    thead.addEventListener('dragstart', (e) => {
      const th = e.target.closest && e.target.closest('th');
      if (!th) return;
      drag = { col: th.dataset.k };
      e.dataTransfer.effectAllowed = 'copyMove';
      e.dataTransfer.setData('text/plain', th.dataset.k);
    });
    zone.addEventListener('dragstart', (e) => {
      const chip = e.target.closest('[data-gi]');
      if (!chip) return;
      drag = { chip: +chip.dataset.gi };
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', 'chip');
    });
    const onDragEnd = () => { drag = null; zone.classList.remove('dt-over'); };
    document.addEventListener('dragend', onDragEnd);
    zone.addEventListener('dragover', (e) => { if (drag) { e.preventDefault(); zone.classList.add('dt-over'); } });
    zone.addEventListener('dragleave', (e) => { if (!zone.contains(e.relatedTarget)) zone.classList.remove('dt-over'); });
    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('dt-over');
      if (!drag) return;
      const on = e.target.closest('[data-gi]'), at = on ? +on.dataset.gi : null;
      if (drag.col) addGroup(defaultSpec(drag.col), at);
      else if (drag.chip != null) addGroup(st.groupBy[drag.chip], at);
      drag = null;
    });
    zone.addEventListener('click', (e) => {
      const b = e.target.closest('[data-ungroup]');
      if (b) { st.groupBy.splice(+b.dataset.ungroup, 1); st.limits = {}; renderBody(); }
    });
    addSel.addEventListener('change', () => { if (addSel.value) addGroup(addSel.value); });
    const onRootClick = (e) => {
      const a = e.target.closest('[data-act]');
      if (!a) return;
      if (a.dataset.act === 'clear') clearFilters();
      else if (a.dataset.act === 'expand') { walk(tree, (g) => st.open.add(g.id)); renderBody(); }
      else if (a.dataset.act === 'collapse') { st.open.clear(); st.limits = {}; renderBody(); }
    };
    root.addEventListener('click', onRootClick);
    crumbs.addEventListener('click', (e) => { const b = e.target.closest('[data-crumb]'); if (b) goCrumb(+b.dataset.crumb); });

    tbody.addEventListener('click', (e) => {
      if (e.target.closest('[data-act]')) return;
      const more = e.target.closest('[data-more]');
      if (more) { const pid = more.dataset.more; st.limits[pid] = (st.limits[pid] || opts.pageSize) + opts.pageSize; renderBody(); return; }
      const tr = e.target.closest('tr');
      if (!tr) return;
      if (tr.dataset.g) {
        if (e.target.closest('[data-drill]')) drill(tr.dataset.g);
        else toggleGroup(tr.dataset.g);
      } else if (tr.dataset.i) openPanel(+tr.dataset.i);
    });
    tbody.addEventListener('dblclick', (e) => {
      const tr = e.target.closest('tr.dt-grp');
      if (tr && !e.target.closest('[data-drill]')) { window.getSelection()?.removeAllRanges(); drill(tr.dataset.g); }
    });
    function toggleGroup(id, force) {
      const open = force ?? !st.open.has(id);
      if (open === st.open.has(id)) return;
      if (open) st.open.add(id); else st.open.delete(id);
      renderBody();
      refocus({ g: id });
    }
    tbody.addEventListener('keydown', (e) => {
      const tr = e.target;
      if (tr.tagName !== 'TR') return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        let n = tr;
        do n = e.key === 'ArrowDown' ? n.nextElementSibling : n.previousElementSibling; while (n && !n.hasAttribute('tabindex'));
        if (n) n.focus();
      } else if (tr.dataset.g) {
        if (e.key === 'Enter' && e.shiftKey) { e.preventDefault(); drill(tr.dataset.g); }
        else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleGroup(tr.dataset.g); }
        else if (e.key === 'ArrowRight') toggleGroup(tr.dataset.g, true);
        else if (e.key === 'ArrowLeft') toggleGroup(tr.dataset.g, false);
      } else if (tr.dataset.i && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openPanel(+tr.dataset.i); }
    });
    const onDocKey = (e) => {
      if (e.key === 'Escape') { if (pop) closeMenu(); else if (panel) closePanel(); }
      else if (panel && panel.contains(document.activeElement) && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) { e.preventDefault(); navPanel(e.key === 'ArrowDown' ? 1 : -1); }
    };
    document.addEventListener('keydown', onDocKey);

    // --- inicialização ---
    setData(opts.rows);
    st.sort = (opts.sort || []).map((s) => (typeof s === 'string' ? { key: s.replace(/^-/, ''), dir: s.startsWith('-') ? -1 : 1 } : s)).filter((s) => colMap[s.key]);
    st.groupBy = (opts.groupBy || []).filter((id) => gspec(id));
    renderHead();
    renderBody();

    return {
      setRows(rows) {
        const selected = st.sel == null ? null : data[st.sel];
        const identity = (row) => typeof opts.rowKey === 'function' ? opts.rowKey(row) : row?.[opts.rowKey];
        const key = selected && identity(selected);
        const active = document.activeElement;
        const panelFocus = panel?.contains(active);
        const focusAttr = panelFocus && ['data-close', 'data-nav', 'data-fk', 'id', 'name'].find((attr) => active.hasAttribute(attr));
        const focusValue = focusAttr && active.getAttribute(focusAttr);
        const scroll = panel?.querySelector('.dt-pb').scrollTop;
        closeMenu(); setData(rows);
        const matches = selected ? data.map((row, i) => ({ row, i })).filter(({ row }) => key == null ? row === selected : identity(row) === key) : [];
        if (matches.length === 1) st.sel = matches[0].i;
        else closePanel();
        if (!opts.columns) renderHead();
        renderBody();
        if (panel && panelFocus) {
          const next = focusAttr && [...panel.querySelectorAll('[' + focusAttr + ']')].find((el) => el.getAttribute(focusAttr) === focusValue && !el.disabled);
          (next || panel.querySelector('[data-close]')).focus();
          panel.querySelector('.dt-pb').scrollTop = scroll;
        }
      },
      groupBy(ids) { st.groupBy = (ids || []).filter((id) => gspec(id)); st.limits = {}; renderBody(); },
      filter(key, text) { st.filters[key] = text || ''; renderBody(); },
      sort(key, dir) { toggleSort(key, false, dir); },
      drillTo(focus) { st.focus = (focus || []).filter((f) => gspec(f.spec)).map((f) => ({ spec: f.spec, key: String(f.key), label: f.label ?? String(f.key) })); st.open.clear(); renderBody(); },
      clearFilters,
      getRows: () => current.slice(),
      getState: () => ({ sort: st.sort.slice(), filters: Object.assign({}, st.filters), groupBy: st.groupBy.slice(), focus: st.focus.slice() }),
      destroy() { closeMenu(); closePanel(); document.removeEventListener('keydown', onDocKey); document.removeEventListener('dragend', onDragEnd); root.removeEventListener('click', onRootClick); root.innerHTML = ''; root.classList.remove('dt'); },
    };
  }

  global.Tabela = { create };
})(typeof window !== 'undefined' ? window : this);
