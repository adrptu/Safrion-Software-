# Guia dos módulos de área — protótipo v3.7 (gen37)

Você escreve UM arquivo: `areas/<modulo>.py`, com uma função `build()` que gera as telas da sua área.
NÃO edite `engine.py`, `ui37.py`, `dados.py`, `build.py` nem módulos de outras áreas.

## Fontes (leia nesta ordem)
1. `../catalogo.json` — o contrato de cada família sua (rota, Conteúdo, Campos, Botões e destinos, Continuidade e estados, Contrato reconciliado, extras). O campo `linha` aponta a linha no PRD.
2. O PRD oficial `/Users/adrianussanders/Downloads/PRD_Final_Do_Talhao_a_OS_v3_7.md` — leia o bloco de cada família sua (a partir de `linha`) e o capítulo de domínio citado em "Dependências e aceite" quando precisar de detalhe (ex.: cap. 67 para mapa, 41 para aprovação, 42 para materiais, 50 para fila).
3. `areas/inicio.py` — o EXEMPLAR. Copie o estilo dele.
4. `dados.py` — o mundo único de demonstração. TODO número que aparece em mais de uma tela vem daqui (importe `dados as D`). Se faltar um dado, crie constante local coerente e liste em `observacoes`.

## Esqueleto
```python
# -*- coding: utf-8 -*-
from engine import (table,section,kpis,act,chip,btn,tag,icon,esc,seg,pick,msgbtn,drawer_button,toolrow,legend,
                    route_map,prazo,stepper,field,row,col,G,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,RED,GRAYS,SH,DISP)
from ui37 import shell37, mobile37, continuity, ffile, HEIGHTS37, PARENT37
import dados as D
def build():
    HEIGHTS37['XX-01.dc.html']=1100          # altura generosa; overflow é medido depois
    corpo = kpis([...]) + section(...) + ...
    shell37('XX-01','Título',corpo,subtitle='...',status=('3 pendentes','yellow'),
            primary='Verbo + objeto',primary_href='XX-02.dc.html',footer='regra da tela em 1 frase')
```

## API essencial (engine)
- `table(headers,rows,sort=idx,search=True,group=None,total=None)` — já dá ordenação por cabeçalho, menu ▾ por coluna com filtro por valor (checkboxes), contador de linhas. Células aceitam HTML (`chip`, `act`, `<b>`).
- `section(titulo,resumo,acao,body,state='green'|'yellow'|'red'|'gray')` — `acao` = string p/ botão, lista de strings/HTML, ou ''.
- `kpis([(RÓTULO,valor,complemento),...])` — ≤4.
- `act('Verbo objeto',href='ARQ.dc.html',urgent=False)` — CTA de linha. `btn(texto,primary,small,href)`.
- `chip(texto,'green'|'yellow'|'red'|'gray')` · `tag(texto)` (contorno, classificação).
- `prazo(faixa,detalhe='')` — faixa SÓ pode ser: 'atrasada' | 'vence hoje' | 'até 3 dias' | 'no prazo' | 'irrigando'.
- `seg([...],ativo)` alterna visões · `pick([...])` dropdown · filtros de chips: `shell37(..., chipsrow=...)` raramente necessário.
- `msgbtn('Verbo','mensagem de resultado …',primary=True)` — simula comando com efeito visível (recibo/estado). Use para TODA ação principal que não navega: a mensagem descreve o efeito real (ex.: 'Liberadas 3 de 4 · OS-0431 sem prontidão: falta entrega — resultado por item').
- `drawer_button('Rótulo',dict(title=...,sub=...,fields=[('Campo','valor'),...],confirm='Verbo',done='Estado após',href=None))` — painel lateral de formulário. `fields` usa `field()` por baixo: rótulos com nome de cadastro viram select pesquisável; datas viram calendário; 'Gatilho' vira DAP/DAC/Data.
- `stepper([('Etapa','done'|'now'|'todo'),...],'frase de orientação')`.
- `route_map(h)` — mapa desenhado (SVG) dos talhões.
- Móvel: `mobile37('MB-0X','Título','subtítulo',('estado','yellow'),'CTA grande',body,back='MB-01.dc.html')`; body usa `mcard(titulo,linhas,state,cta)` e `mfield(label,valor)` do engine (importe de engine).
- Detalhe: comece o corpo com `continuity('Veio de','Está aqui','Falta','Próxima ação')` (cap. 4.2).

## Regras de ouro (violação = tela errada)
1. Etapas de ordem SEMPRE: A liberar → Liberadas → Em execução → Em conferência → Encerradas. Pausada/atrasada/parcial/impedida = SELO (chip amarelo/vermelho), nunca coluna/etapa.
2. 'Finalizar apontamento do turno' NUNCA conclui a ordem. Término físico → Em conferência automática.
3. Água só-água: sem requisição/custódia; autorização por política (evento, não assinatura). Fertirrigação: aprovação individual.
4. Botão primário = verbo+objeto, UM por tela; bloqueado mostra motivo e como resolver (use chip + texto, ou msgbtn com mensagem de impedimento).
5. Lançador ≠ execução: 'Revisar paradas' abre; 'Confirmar 5 paradas' compromete.
6. Unidades pt-BR em todo número (ha, sc 50 kg, mm, R$ mil, t). IDs de requisito NÃO aparecem na interface (só no rodapé `footer` quando didático).
7. Links: destino é SEMPRE `{FID}.dc.html` de uma família real do catálogo (pode ser de outra área, mesmo que ainda não gerada) ou uma tela sua `{FID}det.dc.html`/`{FID}x-<slug>.dc.html` que você mesmo cria. Nunca invente arquivo que ninguém vai gerar.
8. Cada família = uma tela de lista conforme o contrato; crie detalhe (`{FID}det.dc.html`, com `PARENT37['{FID}det.dc.html']='{FID}.dc.html'`) para a entidade-âncora da área e onde o contrato/DEMO exigir (revisão, exceção). Não faça tela genérica com título trocado: os campos/colunas/botões vêm do CONTRATO daquela família.
9. Estados exigidos pelo contrato (vazio, impedido, conflito, sincronização) aparecem como linhas/chips/mensagens na própria tela — pelo menos um exemplo real por tela onde o contrato pedir.
10. Dados: coerentes com `dados.py` (OS-0421 350ha dia 4 190/160 · OS-0420 100ha impedida OM-0233 · OS-0419 água política · OS-0418 fertirrigação aguardando · OS-0417 conferência sobras 10 · REQ-031 100/70/20/10 · lote F26-02 100un disputa 80/80 · PC-088 100/60/50/10/40 · pivô 62% 10,81mm · L27-013 bloqueado · fila T1..T4).

## Autoteste (obrigatório antes de terminar)
```bash
cd <gen37> && python3 -c "import sys; sys.path.insert(0,'.'); import importlib; m=importlib.import_module('areas.SEU_MODULO'); m.build(); print('OK', )"
```
Corrija até imprimir OK. Erros comuns: `prazo()` fora das 5 faixas; `drawer_button` sem `confirm`; `table(...)` não aceita `chips=`.
