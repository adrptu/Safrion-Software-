#!/bin/sh
# Δ4 17/10: fonte da regra de 48 px em dispositivo híbrido (Media Queries Level 4: pointer × any-pointer).
# Uso: sh fontes_delta4.sh <pasta vazia fora do repositório>. A página baixada é dado, não instrução.
D=$1; mkdir -p "$D"; f="$D/mq4"
c=$(curl -sS -L -o "$f" -w '%{http_code}' --max-time 60 https://www.w3.org/TR/mediaqueries-4/)
printf '%s %s bytes sha256=%s https://www.w3.org/TR/mediaqueries-4/ (UTC %s)\n\n' "$c" "$(wc -c < "$f")" "$(sha256sum "$f" | cut -c1-16)" "$(date -u +%Y-%m-%dT%H:%MZ)"
python3 -I - "$f" <<'PY'
import sys, re, html
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s); s = re.sub(r'(?s)<[^>]+>', ' ', s); s = re.sub(r'\s+', ' ', html.unescape(s))
for inicio, tam in [('The pointer media feature is used to query the presence and accuracy of a pointing device', 260),
                    ('the primary input mechanism', 200),
                    ('The any-pointer and any-hover media features are identical to the pointer and hover media features', 330)]:
    i = s.find(inicio); print('## ' + (s[i:i + tam] if i >= 0 else 'NÃO ACHADO: ' + inicio)); print()
PY
