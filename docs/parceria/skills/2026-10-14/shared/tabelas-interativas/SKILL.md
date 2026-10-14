---
name: tabelas-interativas
description: Crie e revise tabelas de gestão com filtro e ordenação no cabeçalho, agrupamento por coluna e drill-down. Use em listagens, relatórios web e planilhas; adapte aos recursos do formato e à semântica dos dados.
---

# Tabelas interativas

## Universo, agregação e continuidade

Filtro, grupo, total, contador e drill-down precisam se referir ao mesmo universo autorizado. Declare se o valor representa página, recorte ou total global. Mantenha valores tipados separados da apresentação; ausentes permanecem distintos de zero e sua posição na ordenação deve ser explícita e consistente nos dois sentidos.

Agregação é regra de domínio, não consequência do formato da coluna: moeda pode representar preço unitário, percentual pode exigir razão ponderada. Some apenas grandezas aditivas compatíveis; taxas e custos/ha não se somam. Faça o resumo pela fonte canônica e exponha parcialidade quando faltar dado. Exemplos de assets não definem regra de negócio. O asset usa `agg: null` por padrão. Ative agregação somente com regra validada do domínio.

Ao detalhar e voltar, preserve busca, filtros, ordem, grupos abertos, página/posição e foco. Recorte recebido de painel/mapa tem contexto explícito e recuperação, sem ser silenciosamente limitado por busca antiga ou sobrescrever preferências persistidas. Alternâncias tabela/raias/calendário conservam entidade, permissão e semântica de contagem.


Listagens interativas de gestão seguem os **quatro recursos** abaixo. Adapte a semântica e os controles ao formato e ao conjunto; uma tabela curta de comparação em texto não exige construir uma aplicação.

## 1. Ordenação no cabeçalho
- Clicar no título da coluna ordena: crescente → decrescente → sem ordenação.
- Shift+clique adiciona ordenação secundária (mostra ▲1 ▼2).
- Indicador sempre visível (⇅ neutro, ▲/▼ destacado quando ativo). `aria-sort` no `<th>`.
- Vazios sempre no fim, independente da direção. Ordenação numérica/data por valor real, texto com collator `pt-BR` (acentos e números naturais).

## 2. Filtro no cabeçalho
- O campo de filtro fica **dentro da mesma célula `<th>`**, logo abaixo do título — nada de linha extra de filtros, painel lateral ou modal.
- Sintaxe (dica no `title`/placeholder):
  - texto: contém (sem acento/caixa) · `=exato` · `!não contém` · `a|b` (ou) · `∅` vazios
  - números e datas: `>1000`, `<=50`, `!=0`, `10..50`, `>=01/01/2025`, `01/01/2025..31/03/2025`
- Menu ▾ da coluna: ordenar ↑/↓, agrupar por esta coluna, **lista de valores com checkbox e contagem** (estilo Excel, com busca) e "limpar filtro desta coluna".
- Coluna filtrada fica visualmente destacada. Contador "X de Y linhas" sempre visível.

## 3. Agrupamento fácil e rápido por qualquer coluna
- Agrupar por qualquer coluna com ação simples no cabeçalho; oferecer acesso por teclado e toque. Arraste e seletor são alternativas quando úteis, não três controles obrigatórios para a mesma tarefa.
- Multinível (Região › UF › Vendedor), chips removíveis (×) e reordenáveis por arraste.
- Datas agrupam por **ano / mês / dia**.
- Linha de grupo mostra rótulo, contagem e agregados pertinentes, alinhados. Somar apenas grandezas com unidades compatíveis. Percentuais, doses, preços e produtividade usam fórmula do domínio (frequentemente razão de totais/média ponderada), nunca média simples por padrão. Totais devem declarar se abrangem o conjunto filtrado ou só a página carregada.
- Grupos ordenam pela coluna ordenada (se for a do grupo ou uma coluna agregada, ex.: regiões por maior valor).
- Botões "Expandir tudo / Recolher tudo".

## 4. Drill-down assertivo e intuitivo
- **Clique no grupo** → expande/recolhe (▶ gira).
- **"Detalhar ›" ou duplo clique no grupo** → entra no grupo: vira filtro, aparece trilha **"Todos › Região: Sul › UF: RS"** e o próximo nível de agrupamento assume. "← Voltar" e cada migalha restauram o estado anterior (inclusive grupos que estavam abertos).
- **Clique na linha** → painel lateral de detalhe com **todos** os campos (inclusive colunas ocultas), posição "12 de 142", navegação ↑/↓ e botão **"Filtrar por este"** em cada valor (entra direto no drill por aquele valor).
- Teclado: ↑/↓ entre linhas, → / ← abre/fecha grupo, Enter abre, Shift+Enter detalha, Esc fecha.
- Nunca perder o contexto: filtros, ordenação e trilha continuam visíveis; estado vazio mostra "Nenhuma linha corresponde aos filtros · Limpar filtros".

---

## Tabela editável

- Edição na linha ou no painel lateral da linha, conforme o projeto; campos relacionados formam uma operação contínua, com rascunho e erros junto do campo/item, sem confirmações por célula.
- Atualizar totais dependentes sem reordenar linhas, retirar foco ou mover o que a pessoa está digitando. Ordenação/filtro durante edição preserva o rascunho e deixa claro onde ele permanece.
- Em lote com sucesso parcial permitido, mostrar quais itens concluíram, falharam ou aguardam; repetir somente os pendentes com idempotência. Itens interdependentes não podem ficar parcialmente confirmados.
- Fluxo, ação primária e retorno seguem `master-detail-ux`; preenchimento e estados visuais seguem `ux-essencial`.

## Como implementar

### HTML, artifact, relatório web (padrão)
O componente [assets/tabela.js](assets/tabela.js) e [assets/exemplo.html](assets/exemplo.html) são referências a inspecionar e testar; não presumir conformidade, segurança ou agregação correta. Prefira o componente existente do projeto quando ele atende ao contrato. Para grandes bases, filtro/ordenação/agrupamento devem operar no conjunto autorizado no servidor, sem fingir totais globais sobre uma página local.

1. Somente se o asset for a solução escolhida, inspecione `assets/tabela.js` e integre conforme build/CSP do projeto; não copie o componente inteiro para substituir um componente existente adequado.
2. Crie a tabela:

```html
<div id="vendas"></div>
<script>/* conteúdo de tabela.js */</script>
<script>
  Tabela.create('#vendas', {
    rows: dados,                       // array de objetos
    columns: [
      { key: 'pedido', label: 'Pedido', type: 'text' },
      { key: 'data', label: 'Data', type: 'date' },          // 'AAAA-MM-DD', dd/mm/aaaa ou Date
      { key: 'regiao', label: 'Região' },
      { key: 'valor', label: 'Valor total', type: 'currency', agg: 'sum' }, // valores aditivos do exemplo
      { key: 'margem', label: 'Margem', type: 'percent', agg: null }, // resumo exige razão de totais do domínio
      { key: 'obs', label: 'Observação', hidden: true },     // só no painel de detalhe
    ],
    groupBy: ['regiao'],        // agrupamento inicial opcional; datas: 'data:ano' | 'data:mes' | 'data:dia'
    sort: ['-valor'],           // '-' = decrescente
    expandLevels: 0,            // quantos níveis abrir de início
    rowTitle: (r) => `Pedido ${r.pedido}`,   // título do painel de detalhe
    detail: (r) => '',          // HTML extra no painel (gráfico, links) — opcional
  });
</script>
```

Opções de coluna: `key`, `label`, `type` (`text` | `integer` | `number` | `currency` | `percent` | `date`), `agg` (`sum` | `avg` | `min` | `max` | `count` | função `(rows)=>valor` | `null`), `decimals`, `currency` (padrão `BRL`), `format(v,row)`, `render(v,row)` (retorna HTML — escape você mesmo), `value(row)` (coluna calculada), `width`, `hidden`.

Defina tipos explicitamente: ID, CPF, CEP e nº de pedido são códigos, não medidas. Use `agg: null` quando não houver agregado válido; preços/percentuais exigem regra explícita e denominador conhecido, sem inferir soma ou média pelo formato da coluna.

API retornada: `setRows(rows)`, `groupBy([...])`, `filter(key, texto)`, `sort(key, 1|-1|0)`, `drillTo([{spec, key, label}])`, `clearFilters()`, `getRows()`, `getState()`, `destroy()`.

Várias tabelas na mesma página: chame `Tabela.create` para cada container. Altura máxima com rolagem e cabeçalho fixo: opção `maxHeight` (padrão `70vh`).

### React / Next / Vue
Envolva o mesmo componente — o comportamento fica idêntico:

```jsx
function TabelaInterativa({ rows, columns, ...opts }) {
  const ref = useRef(null), api = useRef(null);
  useEffect(() => { api.current = Tabela.create(ref.current, { rows, columns, ...opts }); return () => api.current.destroy(); }, [columns]);
  useEffect(() => { api.current?.setRows(rows); }, [rows]);
  return <div ref={ref} />;
}
```
Se o projeto já usa TanStack Table/AG Grid/MUI DataGrid, pode usar a biblioteca, mas **cumpra o checklist abaixo item por item** (atenção: agrupamento no AG Grid e MUI é recurso pago — nesse caso, use `tabela.js`).

### Streamlit / Dash / Jupyter
Renderize o HTML com `tabela.js` inline: `st.components.v1.html(html, height=700, scrolling=True)`; em Dash, `html.Iframe(srcDoc=html)`; no Jupyter, `IPython.display.HTML`. Serialize os dados com `df.to_json(orient='records', date_format='iso')`.

### Excel (.xlsx)
Planilha não tem drill-down igual ao da web, então reproduza o equivalente nativo:
- Dados como **Tabela do Excel** (`openpyxl.worksheet.table.Table`) → botões de filtro/ordenação na linha de cabeçalho; `freeze_panes` abaixo do cabeçalho; formatos numéricos corretos.
- Aba **"Resumo"** agrupada pela dimensão principal (e subníveis) com `SUBTOTAL`/`SUMIFS` e **estrutura de tópicos** (`row_dimensions.group(..., outline_level=n)`) para expandir/recolher.
- Drill-down: cada linha do resumo com **hiperlink** para a aba de dados (ou aba de detalhe por grupo).
- Se o usuário usa Excel desktop, sugerir também uma Tabela Dinâmica sobre a Tabela.

### Terminal / chat em Markdown
Markdown não é interativo. Para tabelas pequenas (até ~15 linhas) mostre normalmente. Para dados maiores, ou quando o usuário for explorar, **gere a versão interativa** (artifact/HTML com `tabela.js`) e dê o link, somente com dados sintéticos ou explicitamente autorizados para esse destino. Se o projeto proibir dados reais em artefatos, mantenha-os no ambiente autorizado; autorização genérica de desenvolvimento não libera exportação.

---

## Checklist antes de entregar qualquer tabela
- [ ] Clique no cabeçalho ordena; Shift+clique ordena por várias colunas; indicador visível
- [ ] Campo de filtro dentro do `<th>` de cada coluna, com operadores para números/datas
- [ ] Menu ▾ com lista de valores (checkbox + contagem + busca)
- [ ] Agrupar por qualquer coluna em 1 gesto (arrastar, menu ou seletor), multinível, datas por ano/mês/dia
- [ ] Linhas de grupo com contagem e agregados alinhados; total no rodapé
- [ ] Drill-down: expandir grupo, "Detalhar" com trilha e Voltar, painel de detalhe da linha com "Filtrar por este"
- [ ] Contador "X de Y linhas", filtros ativos destacados, estado vazio com "Limpar filtros"
- [ ] Tipos corretos (códigos como texto, moeda BRL, percentuais, datas pt-BR)
- [ ] Funciona com teclado e nos temas adotados pelo projeto

O asset `Tabela.create` aceita `rowKey` (nome de campo ou função; padrão `id`) para preservar o detalhe em `setRows` com objetos novos. Use uma identidade estável e única. Sem chave, somente o mesmo objeto pode manter seleção; registro removido ou chave duplicada fecha o detalhe, sem escolher outro registro. Atualização conserva grupos expandidos e contexto ainda válido.
