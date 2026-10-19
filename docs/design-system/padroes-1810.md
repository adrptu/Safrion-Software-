# Padrões de 18/10/2026

Pedidos do proprietário em 18/10, transformados em padrão pelo método da skill `padrao-safrion`.

- **Valem para todas as telas do mesmo tipo**, no protótipo e no software real.

## VIS-08 · Modo de visão pelo ícone em toda tela

> "O modo de visão em mapa em planejar safra tem que ser pelo ícone igual os demais que você fez"

**Referência:** Ordens de serviço, Pragas e doenças e Irrigação. O seletor de visões da VISOES-1 é um trilho com um botão por visão, só ícone. O nome "Ver em …" vai no aria-label e na dica, e a visão aberta fica marcada.

**Regra:** toda troca de modo de ver a mesma lista ou o mesmo painel (Tabela, Cartões, Kanban, Calendário, Mapa, Carga, Frentes) usa esse seletor. O botão de texto ("Lista | Mapa", "Tabela · Mapa") fica proibido. As visões de cada tela vêm do registro único (`visoes.REGISTRO`).
- **Listagem da tela:** `engine.visoes`, com `?view` e preferência por perfil.
- **Painel ou visão que é estado da tela:** `engine.visoes_locais`. É o mesmo desenho, sem `?view` (ex.: o painel "Editar talhões…").
- **Código único:** as duas funções e o `modos_html` saem da mesma função do motor (`engine._seletor_icones`). Nenhuma tela copia o desenho.

**Telas corrigidas:**

| Tela | Antes | Depois |
|---|---|---|
| Planejar safra › Editar talhões… | "Tabela · Mapa" em texto | Ver em tabela · Ver em mapa (`visoes_locais`, entidade `saf_tal`) |
| Cadastros › Fazendas e talhões (CD-01) | "Lista \| Mapa" em texto, mais Tabela \| Cartões em ícone | Um seletor só: Tabela · Cartões · Mapa (`visoes`, entidade `tal`, com `?view`) |
| Agrícola › Beneficiamento | "Lista \| Cartões \| Kanban" em texto | Ver em tabela · cartões · kanban (`visoes_locais`, entidade `ben`) |
| Manutenção › Ordens | ícones numa cópia própria da barra, com outro ícone de Tabela | O seletor comum (`visoes_locais`, entidade `ma_om`), com o mesmo ícone de Tabela das outras telas |

**Fora, com o motivo:**
- **Colheita:** "Por talhão | Por semana" são duas análises diferentes, não dois modos de ver a mesma lista.
- **Manutenção:** "Sem ordem | Ordens | Ativos | Planos" são os subitens do menu (DS-MAN), não modos de visão.
- **CA-01 (campo):** "Lista | Kanban | Mapa" fica numa tela oculta, fora do menu, na fila de exclusão do EX-50.

**Dano evitado:** a mesma ação com duas aparências. A pessoa procura o ícone que aprendeu na O.S. e não acha o mapa na tela seguinte.

**Teste:**
- `visao_icone_test.py`: varredura estática das telas do menu. Todo grupo "Visão…" ou "Visualização…" tem só botões de ícone; as exceções acima ficam listadas com o motivo.
- `visoes_unit_test.py`: B1 (CD-01 com o seletor) e B1c (Planejar safra só com ícone).
- `saf_mapa_test.py`, `cadf_fix_lista_test.py`, `ben_fluxo_test.py`, `cartoes_test.py` e `man_limpa_test.py`: telas abertas no navegador.
- **Contraprova:** a `visao_icone_test.py` no render da v138 reprova no Planejar safra, na CD-01 (2 grupos) e no Beneficiamento.

**Oráculos ajustados, com o motivo:**
- Seletores dos testes de navegador: o clique vai no botão `[data-visao=…]` do seletor comum, no lugar do texto antigo ("Mapa", "Kanban"). Isso vale para `saf_mapa`, `cadf_fix_lista`, `ben_fluxo` e `cartoes` (M7b). A `man_limpa` (L6) passa a esperar os nomes comuns "Ver em tabela", "Ver em cartões" e "Ver em kanban". A `ma_unica` (AC-PCM-04) e a `ma_rastreio` (F58 a F61) abrem o Kanban pelo nome "Ver em kanban", porque o botão não tem texto visível.
- `cadastros_padrao` P4: na tela com o seletor de visões (a CD-01, como a IR-01), o Tabela | Cartões fica no seletor acima da lista, e a barra da tabela termina no Colunas. O teste reprova se a barra repetir os modos.
- `cadf_test` e `cadf_fix_lista_test`: a árvore abre recolhida desde a v129 (DRILL-RECOLHIDO), então o talhão só aparece depois do "Expandir tudo" da tabela. Os dois já falhavam na v138 pelo mesmo motivo, antes da VIS-08.

**Prova visual (executada em 19/10):** fotos das 4 telas em 1440 e 390 px, conferidas uma a uma. Em 390 px, na Manutenção › Ordens, o seletor fica no fim da linha dos filtros de fase, que rola na horizontal. Isso já era assim antes da VIS-08 e fica para a revisão do celular da Manutenção.
