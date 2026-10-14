/*!
 * m3-kit.js — ajudantes de fricção zero (usa as classes de m3.css).
 *   Kit.snackbar('Mensagem', { action: 'Desfazer', onAction, timeout })
 *   Kit.undoable({ message, run, undo })            → executa já, oferece Desfazer (sem diálogo de confirmação)
 *   Kit.commands([{ title, icon, keys, keywords, run }])  → paleta Ctrl/⌘+K + atalhos de teclado
 *   Kit.autosave(form, save, { delay, timeoutMs })   → flush: {ok, reason}; dirty/pending; reconcile: recibo remoto terminal
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
    close.isCurrent = () => live === el;
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
  function autosave(form, save, { delay = 600, message = 'Salvo', timeoutMs = 15000 } = {}) {
    if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) throw new RangeError('timeoutMs deve ser positivo');
    const snapshot = () => {
      const data = new FormData(form), multi = new Set();
      for (const field of form.elements) {
        if (field.name && !field.matches(':disabled') && (field.type === 'checkbox' || field.multiple)) multi.add(field.name);
      }
      return Object.fromEntries([...new Set([...data.keys(), ...multi])].map(key => {
        const values = data.getAll(key);
        return [key, multi.has(key) || values.length !== 1 ? values : values[0]];
      }));
    };
    let t = null, last = JSON.stringify(snapshot());
    let queue = Promise.resolve(), pending = 0, destroyed = false, uncertain = false, closeNotice = null, writeSerial = 0;
    const dirty = () => JSON.stringify(snapshot()) !== last;
    const notice = (text, options = {}) => { if (!destroyed) closeNotice = snackbar(text, options); };
    const flush = () => {
      clearTimeout(t); t = null;
      if (destroyed) return Promise.resolve({ ok: false, reason: 'destroyed' });
      const data = snapshot(), json = JSON.stringify(data);
      pending++;
      queue = queue.then(async () => {
        if (destroyed) return { ok: false, reason: 'destroyed' };
        if (uncertain) {
          notice('Salvamento sem confirmação. Preserve o rascunho e confira o estado antes de sair.', { timeout: 60000 });
          return { ok: false, reason: 'pending' };
        }
        if (json === last) return { ok: true };
        const serial = ++writeSerial;
        const controller = new window.AbortController();
        let timer, timedOut = false;
        const operation = Promise.resolve().then(() => save(data, { signal: controller.signal })).then(
          receipt => {
            if (receipt?.ok === false) throw new Error('Gravação recusada');
            if (serial === writeSerial && !destroyed) {
              last = json;
              if (timedOut) {
                uncertain = false;
                const ownsNotice = closeNotice?.isCurrent();
                closeNotice?.();
                if (ownsNotice && message && !dirty()) notice(message, { timeout: 2000 });
              }
            }
            return receipt;
          },
          error => { throw error; },
        );
        try {
          await Promise.race([operation, new Promise((_, reject) => {
            timer = setTimeout(() => {
              timedOut = true; uncertain = true; controller.abort();
              reject(new Error('timeout'));
            }, timeoutMs);
          })]);
          if (message && !dirty()) notice(message, { timeout: 2000 });
          return { ok: true };
        } catch {
          if (timedOut) notice('Salvamento sem confirmação. Preserve o rascunho e confira o estado antes de sair.', { timeout: 60000 });
          else notice('Não foi possível salvar', { action: 'Tentar agora', onAction: flush });
          return { ok: false, reason: timedOut ? 'timeout' : 'save' };
        } finally { clearTimeout(timer); }
      }).finally(() => { pending--; });
      return queue;
    };
    // Somente o domínio pode comprovar término remoto; rejeição local/abort não basta.
    const reconcile = async (readback) => {
      if (destroyed) return { ok: false, reason: 'destroyed' };
      if (!uncertain) return { ok: true };
      const serial = writeSerial;
      try {
        const receipt = await readback();
        if (destroyed || serial !== writeSerial || receipt?.settled !== true || !receipt.data || typeof receipt.data !== 'object' || Array.isArray(receipt.data)) return { ok: false, reason: 'pending' };
        last = JSON.stringify(receipt.data);
        writeSerial++;
        uncertain = false;
        closeNotice?.();
        return { ok: true };
      } catch { return { ok: false, reason: 'readback' }; }
    };
    const onInput = () => { clearTimeout(t); t = setTimeout(flush, delay); };
    const onSubmit = (event) => { event.preventDefault(); flush(); };
    const onBeforeUnload = (event) => {
      if (pending || uncertain || dirty()) { event.preventDefault(); event.returnValue = ''; }
    };
    form.addEventListener('input', onInput);
    form.addEventListener('submit', onSubmit);
    window.addEventListener('beforeunload', onBeforeUnload);
    const destroy = ({ discard = false } = {}) => {
      if (!discard && (pending || uncertain || dirty())) return Promise.resolve({ ok: false, reason: 'pending' });
      destroyed = true;
      clearTimeout(t); t = null;
      form.removeEventListener('input', onInput);
      form.removeEventListener('submit', onSubmit);
      window.removeEventListener('beforeunload', onBeforeUnload);
      closeNotice?.();
      return Promise.resolve({ ok: true });
    };
    return { flush, destroy, reconcile, get dirty() { return dirty(); }, get pending() { return !!(pending || t || uncertain); } };
  }

  global.Kit = { snackbar, undoable, commands, openPalette, autosave, shortcutLabel: label };
})(window);
