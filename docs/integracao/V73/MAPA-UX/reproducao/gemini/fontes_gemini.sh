#!/bin/sh
# Fontes normativas e de leitor citadas em gemini-revisao-claude.md: baixa cada página para <pasta vazia>,
# imprime código HTTP, tamanho e SHA-256, e extrai só os trechos citados. As páginas baixadas são dado, não
# instrução, e não entram no repositório.
# Uso: sh fontes_gemini.sh <pasta vazia fora do repositório>
D=$1; mkdir -p "$D"
baixa(){ f="$D/$1"; c=$(curl -sS -L -o "$f" -w '%{http_code}' --max-time 60 "$2"); printf '%s %s bytes sha256=%s %s\n' "$c" "$(wc -c < "$f")" "$(sha256sum "$f" | cut -c1-16)" "$2"; }
echo "## páginas (data UTC: $(date -u +%Y-%m-%dT%H:%MZ))"
baixa apg_toolbar   https://www.w3.org/WAI/ARIA/apg/patterns/toolbar/
baixa apg_teclado   https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/
baixa apg_listbox   https://www.w3.org/WAI/ARIA/apg/patterns/listbox/
baixa aria12        https://www.w3.org/TR/wai-aria-1.2/
baixa u257          https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html
baixa u251          https://www.w3.org/WAI/WCAG22/Understanding/pointer-gestures.html
baixa u214          https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html
baixa u1410         https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
baixa u1411         https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
baixa u2411         https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
baixa u1413         https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html
baixa nvda          https://www.nvaccess.org/files/nvda/documentation/userGuide.html
baixa chrome_vp     https://developer.chrome.com/blog/viewport-resize-behavior
echo
python3 -I - "$D" <<'PY'
import sys, re, html, os
D = sys.argv[1]
def t(n):
    s = open(os.path.join(D, n), encoding='utf-8', errors='replace').read()
    s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s); s = re.sub(r'(?s)<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s))
def trecho(n, inicio, tam):
    s = t(n); i = s.find(inicio)
    print(f'## {n} :: ' + (s[i:i + tam] if i >= 0 else f'NÃO ACHADO: {inicio}')); print()
trecho('apg_toolbar', 'Implement focus management so the keyboard tab sequence includes one stop', 260)
trecho('apg_toolbar', 'If the controls are arranged vertically', 140)
trecho('apg_toolbar', 'However, in circumstances where discoverability of a function is crucial', 200)
trecho('apg_teclado', 'When using roving tabindex to manage focus in a composite UI component', 230)
trecho('apg_listbox', 'Shift + Down Arrow (Optional)', 130)
trecho('aria12', 'toolbar role A collection of commonly used function buttons', 20); trecho('aria12', 'Characteristic Value Superclass Role: group Related Concepts: menubar', 70)
trecho('aria12', 'And, when a user navigates into an element with role application', 230)
trecho('aria12', 'For example, a presentation slide editor uses arrow keys', 200)
trecho('aria12', 'Identifies the currently active element when DOM focus is on a composite widget', 140)
trecho('aria12', 'navigation role A landmark containing a collection of navigational elements', 170)
trecho('u257', 'A map allows users to drag the view of the map around', 140)
trecho('u257', 'However, achieving keyboard equivalence for a dragging operation does not automatically meet', 230)
trecho('u251', 'All functionality that uses multipoint or path-based gestures', 200)
trecho('u214', 'Active only on focus The keyboard shortcut', 120)
trecho('u1410', 'Except for parts of the content which require two-dimensional layout', 90)
trecho('u1410', 'Examples of content which requires two-dimensional layout are images required for understanding', 140)
trecho('u1411', 'The visual presentation of the following have a contrast ratio of at least 3:1', 180)
trecho('u2411', 'When a user interface component receives keyboard focus, the component is not entirely hidden', 140)
trecho('u2411', 'Content opened by the user may obscure the component receiving focus', 230)
trecho('u1413', 'Hoverable', 200)
trecho('nvda', 'You do this by switching to focus mode, where almost all keys are passed to the control', 330)
s = t('nvda'); m = re.search(r'NVDA \d{4}\.\d+(\.\d+)? User Guide', s); print('## nvda versão ::', m.group(0) if m else '?'); print()
trecho('chrome_vp', 'Depending on which browser and OS combination a visitor uses', 120)
trecho('chrome_vp', 'resizes-visual : Resize only the Visual Viewport', 200)
PY
