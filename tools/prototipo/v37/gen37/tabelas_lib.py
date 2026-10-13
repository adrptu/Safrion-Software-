# -*- coding: utf-8 -*-
"""Apoio dos testes TABELAS-FOCO de Cadastros e Irrigação (tabelas_cad_test.py, tabelas_irr_test.py): lê a i-ésima grade G2 visível
(cabeçalhos com data-un, células por coluna), abre o menu de filtro da coluna (valores, marcar, ordenar) e confere a unidade junto do
valor e a ordem por número ou por data. Mesmo desenho dos auxiliares de tabelas_est_test.py (filtro pelo menu, OK, Limpar filtros)."""
import re, json, time

TBS = "[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent)"
NUM = r'[+−-]?≈?[\d.]+(?:,\d+)?'


def T(i):
    return f"({TBS})[{i}]"


class Grade:
    """i-ésima grade visível da página (J = Chrome.js)."""
    def __init__(self, J, i=0):
        self.J, self.i = J, i

    def heads(self):
        # textContent: o texto do rótulo sem a caixa alta de CSS (as telas da Irrigação mostram o cabeçalho em maiúsculas)
        return self.J(f"[...{T(self.i)}.querySelectorAll('[role=columnheader]')].map(h=>[h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,''),h.dataset.un||''])") or []

    def labels(self):
        return [h for h, _ in self.heads()]

    def linhas(self, so_folhas=False):
        """células (texto) de cada linha visível; so_folhas: só linhas sem seta de grupo."""
        f = "&&!r.querySelector('button[aria-label^=\"Expandir\"],button[aria-label^=\"Recolher\"]')" if so_folhas else ''
        return self.J(f"[...{T(self.i)}.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]'){f}).map(r=>[...r.querySelectorAll('[role=cell]')].map(x=>x.innerText.replace(/\\s+/g,' ').replace(/^[▸▾]\\s*/,'').trim()))") or []

    def dicts(self, so_folhas=False):
        hs = self.labels()
        return [dict(zip(hs, r)) for r in self.linhas(so_folhas)]

    def col(self, nome, so_folhas=False):
        return [d.get(nome, '') for d in self.dicts(so_folhas)]

    def chips(self, nome):
        """por linha: a célula da coluna tem chip (pílula com border-radius ≥ 999px)?"""
        return self.J(f"""(()=>{{const t={T(self.i)}; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim());
          const k=hs.indexOf({json.dumps(nome)}); return [...t.querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>{{const c=r.querySelectorAll('[role=cell]')[k];
          if(!c||!c.innerText.trim()) return null; return [...c.querySelectorAll('span')].some(s=>parseFloat(getComputedStyle(s).borderTopLeftRadius)>=99&&s.innerText.trim());}});}})()""") or []

    def _menu(self, col):
        r = self.J(f"(()=>{{const b={T(self.i)}.querySelector('button[aria-label=\"Filtrar {col}\"]'); if(!b) return false; b.click(); return true;}})()")
        time.sleep(.4)
        return r

    def rotulos(self, col):
        """valores que o menu de filtro da coluna oferece (sem a contagem)."""
        if not self._menu(col): return None
        r = self.J("[...document.querySelectorAll('[role=dialog] label')].map(l=>l.innerText.replace(/\\s+\\d+$/,'').trim())") or []
        self.J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
        return r

    def filtra(self, col, vals):
        if not self._menu(col): return False
        self.J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
        for v in vals:
            self.J(f"(()=>{{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(v)}); l&&l.querySelector('input').click();}})()"); time.sleep(.15)
        self.J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
        return True

    def ordena(self, col, desc=False):
        if not self._menu(col): return False
        self.J(f"[...document.querySelectorAll('[role=dialog] button.g2fi')][{1 if desc else 0}].click()"); time.sleep(.5)
        return True

    def cabecalho_ordena(self, col):
        """clique no título (ciclo crescente → decrescente → sem ordem)."""
        self.J(f"(()=>{{const b={T(self.i)}.querySelector('button[aria-label=\"Ordenar por {col}\"]'); b&&b.click();}})()"); time.sleep(.45)

    def com_menu(self):
        """colunas com botão de filtro (menu ▾) e com botão de ordenar no título."""
        return self.J(f"[...{T(self.i)}.querySelectorAll('[role=columnheader]')].map(h=>!!h.querySelector('button.g2fb')&&!!h.querySelector('button.g2hb'))") or []

    def desalinhadas(self):
        """linhas (o cabeçalho conta como uma) fora da trilha do grid: cabeçalhos que quebram para outra linha ou se empilham (a borda esquerda
        não cresce da esquerda para a direita) e linhas cujas células não ficam sob os cabeçalhos. Com a trilha menor que as colunas (colunas que
        entram e saem sem o nº de colunas acompanhar), cabeçalho e células quebram juntos e ficam "alinhados" pela borda esquerda: só a ordem
        das bordas mostra o defeito (sonda da revisão TABR, 10/10/2026: CD-05 Clientes com repeat(8) para 10 colunas)."""
        return self.J(f"""(()=>{{const t={T(self.i)}; const hs=[...t.querySelectorAll('[role=columnheader]')]; const hl=hs.map(h=>Math.round(h.getBoundingClientRect().left));
          const cab=hl.some((x,i)=>i>0&&x<=hl[i-1])?1:0;
          return cab+[...t.querySelectorAll('[role=row]')].filter(r=>r.querySelector('[role=cell]')).filter(r=>{{const cs=[...r.querySelectorAll('[role=cell]')]; return cs.length!==hs.length||cs.some((c,i)=>Math.abs(Math.round(c.getBoundingClientRect().left)-hl[i])>1);}}).length;}})()""")

    def rola_dentro(self):
        """390 px: a página não rola de lado; a grade cabe na caixa ou rola dentro dela; a 1ª coluna fica à vista."""
        return self.J(f"""(()=>{{const t={T(self.i)}; const sc=t.closest('.g2rola'); const R=sc.getBoundingClientRect(); const h=t.querySelector('[role=columnheader]').getBoundingClientRect();
          const ox=getComputedStyle(sc).overflowX; const cabe=sc.scrollWidth<=sc.clientWidth+1;
          return {{pagina:document.documentElement.scrollWidth<=innerWidth+1, cabe, rola:!cabe&&(ox==='auto'||ox==='scroll'), c0:h.left>=R.left-1&&h.right<=R.right+1}};}})()""") or {}


def limpa(J):
    J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^Limpar filtros/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)


def num(t):
    m = re.search(NUM, t or '')
    if not m: return None
    s = m.group(0).replace('≈', '').replace('−', '-').replace('.', '').replace(',', '.')
    try: return float(s)
    except ValueError: return None


def un_ok(cel, un, extra=()):
    """célula de coluna com data-un: '—', vazia, texto previsto (extra) ou número com a unidade junto ("160,0 ha", "R$ 14,49/ha")."""
    if cel in ('', '—') or cel in extra: return True
    if un.startswith('R$'):
        return bool(re.fullmatch(r'−?R\$ [\d.]+(,\d+)?' + re.escape(un[2:]), cel))
    return bool(re.fullmatch(NUM + ' ' + re.escape(un), cel))


DIAS = {'ontem': -1, 'hoje': 0, 'amanhã': 1}


def instante(t):
    """'hoje 20:00', '25/09 11:15', '15/10/2026' → chave ordenável (ano, mês, dia, minuto) para conferir a ordem por data."""
    t = (t or '').strip()
    m = re.match(r'^(ontem|hoje|amanhã) (\d{2}):(\d{2})$', t)
    if m: return (2026, 9, 23 + DIAS[m.group(1)], int(m.group(2)) * 60 + int(m.group(3)))
    m = re.match(r'^(\d{2})/(\d{2}) (\d{2}):(\d{2})$', t)
    if m: return (2026, int(m.group(2)), int(m.group(1)), int(m.group(3)) * 60 + int(m.group(4)))
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', t)
    if m: return (int(m.group(3)), int(m.group(2)), int(m.group(1)), 0)
    return None


def crescente(xs, desc=False):
    xs = [x for x in xs if x is not None]
    return len(xs) > 1 and xs == sorted(xs, reverse=desc)
