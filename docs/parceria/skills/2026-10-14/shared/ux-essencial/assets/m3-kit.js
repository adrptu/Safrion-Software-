/*!
 * m3-kit.js — ajudantes de fricção zero (usa as classes de m3.css).
 *   Kit.snackbar('Mensagem', { action: 'Desfazer', onAction, timeout })
 *   Kit.undoable({ message, run, undo })            → executa já, oferece Desfazer (sem diálogo de confirmação)
 *   Kit.commands([{ title, icon, keys, keywords, run }])  → paleta Ctrl/⌘+K + atalhos de teclado
 *   Kit.autosave(form, save, { delay })              → salva sozinho, sem botão "Salvar"
 */
(function (global) {
  'use strict';

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const norm = (s) => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  const typing = (el) => el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));

  // ---------- snackbar ----------
  let live = null, timer = null;
  function snackbar(message, { action, onAction, timeout = 6000 } = {}) {
    if (live) live.remove();
    clearTimeout(timer);
    const el = document.createElement('div');
    el.className = 'snackbar';
    el.setAttribute('role', 'status');
    el.innerHTML = `<span>${esc(message)}</span>${action ? `<button class="btn btn-text">${esc(action)}</button>` : ''}<button class="icon-btn" aria-label="Fechar" style="color:inherit"><span class="icon">close</span></button>`;
    document.body.appendChild(el);
    live = el;
    requestAnimationFrame(() => el.classList.add('show'));
    const close = () => { el.classList.remove('show'); setTimeout(() => el.remove(), 250); if (live === el) live = null; };
    const [a, x] = action ? el.querySelectorAll('button') : [null, el.querySelector('button')];
    if (a) a.addEventListener('click', () => { close(); if (onAction) onAction(); });
    x.addEventListener('click', close);
    let remaining = timeout, started = Date.now();
    const arm = () => { started = Date.now(); timer = setTimeout(close, remaining); };
    el.addEventListener('mouseenter', () => { clearTimeout(timer); remaining -= Date.now() - started; });
    el.addEventListener('mouseleave', arm);
    arm();
    return close;
  }

  function undoable({ message, run, undo, action = 'Desfazer' }) {
    const result = run();
    snackbar(message, { action, onAction: () => undo(result) });
    return result;
  }

  // ---------- atalhos + paleta de comandos ----------
  const registry = [];
  function parseKeys(k) { return k.toLowerCase().split('+').map((p) => p.trim()); }
  function matches(e, keys) {
    const p = parseKeys(keys), key = p[p.length - 1];
    const mod = p.includes('mod'), shift = p.includes('shift'), alt = p.includes('alt');
    return e.key.toLowerCase() === key && (isMac ? e.metaKey : e.ctrlKey) === mod && e.shiftKey === shift && e.altKey === alt;
  }
  const label = (keys) => parseKeys(keys).map((p) => (p === 'mod' ? (isMac ? '⌘' : 'Ctrl') : p === 'shift' ? '⇧' : p === 'alt' ? (isMac ? '⌥' : 'Alt') : p.toUpperCase())).join(isMac ? '' : '+');

  function commands(list) {
    registry.push(...list);
    return { open: openPalette };
  }

  let scrim = null;
  function openPalette() {
    if (scrim) return;
    const back = document.activeElement;
    scrim = document.createElement('div');
    scrim.className = 'palette-scrim';
    scrim.innerHTML = `<div class="palette" role="dialog" aria-label="Comandos"><input type="text" placeholder="O que você quer fazer?" aria-label="Buscar comando" role="combobox" aria-expanded="true" aria-controls="kit-cmds"><ul id="kit-cmds" role="listbox"></ul></div>`;
    document.body.appendChild(scrim);
    const input = scrim.querySelector('input'), ul = scrim.querySelector('ul');
    let shown = [], sel = 0;
    const draw = () => {
      const q = norm(input.value.trim());
      shown = registry.filter((c) => !q || q.split(/\s+/).every((t) => norm(c.title + ' ' + (c.keywords || '')).includes(t)));
      sel = Math.min(sel, Math.max(0, shown.length - 1));
      ul.innerHTML = shown.length
        ? shown.map((c, i) => `<li role="option" data-i="${i}" aria-selected="${i === sel}"><span class="icon">${esc(c.icon || 'arrow_forward')}</span>${esc(c.title)}${c.keys ? `<span class="kbd">${esc(label(c.keys))}</span>` : ''}</li>`).join('')
        : '<div class="empty">Nenhum comando encontrado</div>';
      ul.querySelector('[aria-selected="true"]')?.scrollIntoView({ block: 'nearest' });
    };
    const close = () => { scrim.remove(); scrim = null; if (back && back.focus) back.focus(); };
    const exec = (c) => { close(); if (c) c.run(); };
    input.addEventListener('input', () => { sel = 0; draw(); });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(sel + 1, shown.length - 1); draw(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(sel - 1, 0); draw(); }
      else if (e.key === 'Enter') { e.preventDefault(); exec(shown[sel]); }
      else if (e.key === 'Escape') { e.preventDefault(); close(); }
    });
    ul.addEventListener('click', (e) => { const li = e.target.closest('li'); if (li) exec(shown[+li.dataset.i]); });
    scrim.addEventListener('mousedown', (e) => { if (e.target === scrim) close(); });
    draw();
    input.focus();
  }

  document.addEventListener('keydown', (e) => {
    if (matches(e, 'mod+k')) { e.preventDefault(); if (scrim) scrim.querySelector('input').focus(); else openPalette(); return; }
    if (scrim) return;
    for (const c of registry) {
      if (!c.keys) continue;
      const hasMod = /mod|alt/.test(c.keys);
      if (!hasMod && typing(document.activeElement)) continue;
      if (matches(e, c.keys)) { e.preventDefault(); c.run(); return; }
    }
  });

  // ---------- autosave ----------
  function autosave(form, save, { delay = 600, message = 'Salvo' } = {}) {
    const snapshot = () => {
      const data = new FormData(form);
      return Object.fromEntries([...new Set(data.keys())].map(key => {
        const values = data.getAll(key);
        return [key, values.length === 1 ? values[0] : values];
      }));
    };
    let t = null, last = JSON.stringify(snapshot());
    let queue = Promise.resolve(), pending = 0;
    const flush = () => {
      const data = snapshot(), json = JSON.stringify(data);
      // Capture cada versão, mas compare com o último recibo somente ao executar.
      // Assim B pendente seguido de retorno a A não perde a reversão.
      pending++;
      queue = queue.then(async () => {
        if (json === last) return;
        try {
          await save(data);
          last = json;
          if (message && JSON.stringify(snapshot()) === json) snackbar(message, { timeout: 2000 });
        } catch {
          last = null;
          snackbar('Não foi possível salvar', { action: 'Tentar agora', onAction: flush });
        }
      }).finally(() => { pending--; });
      return queue;
    };
    form.addEventListener('input', () => { clearTimeout(t); t = setTimeout(flush, delay); });
    form.addEventListener('submit', (e) => { e.preventDefault(); clearTimeout(t); flush(); });
    window.addEventListener('beforeunload', (event) => {
      // O navegador não aguarda save: peça confirmação de saída se houver edição sem recibo.
      if (pending || JSON.stringify(snapshot()) !== last) {
        event.preventDefault();
        event.returnValue = '';
      }
    });
    return { flush };
  }

  global.Kit = { snackbar, undoable, commands, openPalette, autosave, shortcutLabel: label };
})(window);
