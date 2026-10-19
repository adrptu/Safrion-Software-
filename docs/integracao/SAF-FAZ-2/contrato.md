# SAF-FAZ-2 · safra com várias fazendas · contrato do domínio

Pedido do proprietário (14/10/2026): "E se planejar safra puder selecionar mais de 1 fazenda e os talhoes de cada fazenda?"
Acordo 6173544970 e ajustes do Codex 6173977617. Autor / revisor / integrador: Claude / Codex / Codex.

## Modelo
- Cada fazenda tem a própria **sub-safra**, que é a linha de safra de hoje: `{id, nome, ini, fim, faz, estado, ro}`.
- A safra de várias fazendas liga as sub-safras pelo campo `mae`. Safra de uma fazenda não tem `mae` e fica igual à de hoje.
- Talhões, ocupação, capacidade, demanda e solicitação de compra continuam **por sub-safra**, com os cálculos já testados. A mãe só reúne a leitura.
- **Danos evitados:**
  - recurso ou insumo de uma fazenda cobrir a falta de outra;
  - remoção de fazenda deixar órfãos cultivo, SOL, O.S., plano ou orçamento;
  - fazenda nova herdar estado ou aprovação;
  - repetição duplicar sub-safra ou compra;
  - soma de unidades diferentes;
  - falta de dado virar zero.

## API (`tools/prototipo/v37/gen37/safra_grupo.js`, funções puras, sem DOM)

| Função | Entrada | Saída e regras |
|---|---|---|
| `sgMaeDe(safs, id)` | id de sub-safra ou da mãe | id da mãe, ou `null` (safra de uma fazenda) |
| `sgGrupo(safs, id)` | idem | `{mae, nome, ini, fim, subs}`, com as subs na ordem da lista; `null` se não existe |
| `sgImpedeRemover(sub, dep)` | `dep = {cultivos, sol:{id,estado}\|null, os:[ids], plano_aprovado, orcamento_aprovado}` | `[{t, destino}]`; lista vazia = pode tirar |
| `sgCompor(safs, ped, op)` | `ped = {chave, nome, ini, fim, fazendas:[...], saf?}` (com `saf`, edita o grupo dessa sub-safra); `op = {rec, deps(saf), novoId(tipo, faz, i)}` | `{ok, erros?, bloqueios?, safs, mae, recibo, repetido}` (regras abaixo) |
| `sgLeitura(grupo, info)` | `info[saf] = {area_ha\|null, cultivos, estado, plano?, orcamento?, demanda:[{insumo,un,qtd,talhao,ciclo,destino}]\|null, sol\|null}` | `{fazendas, area:{ha, completa, faltam}, estados, planos, orcamentos, sol:{enviadas, de}, parcial, demanda:{linhas, porInsumo, incompleta}}` (regras abaixo) |
| `sgEnviar(grupo, chave, rec, enviarUm)` | `enviarUm(saf) => {ok, recibo?, erro?}` (o comando de envio que já existe, por sub-safra) | `{ok, parcial, recibos:[{faz,saf,recibo,repetido}], falhas:[{faz,saf,erro}]}` (regras abaixo) |

**Regras de `sgCompor`**
- A recusa é atômica: com qualquer erro ou bloqueio, `safs` volta igual.
- A mesma `chave` devolve o recibo gravado com `repetido: true` e não muda nada.
- A sub-safra que fica conserva ID, estado e o resto.
- A que entra nasce em `Rascunho`.
- A que sai e está vazia empresta o ID à fazenda que entra (`acao: 'trocada'`) e volta a `Rascunho`.
- Com 1 fazenda, a safra fica sem `mae`.
- Safra encerrada (`ro`) recusa a edição.

**Regras de `sgLeitura`**
- Não existe estado ou aprovação geral: a leitura traz a contagem por estado e marca `parcial`.
- A área total soma só o que é conhecido. Se faltar alguma área, `completa` fica falso e `faltam` lista as fazendas.
- `porInsumo` soma por (insumo, unidade); unidades diferentes ficam separadas.
- Cada linha conserva fazenda, talhão, ciclo e destino.

**Regras de `sgEnviar`**
- O que deu certo fica gravado em `rec[chave|saf]`.
- Repetir com a mesma chave só tenta o que falhou.
- Falha parcial dá `ok: false, parcial: true`.
- Sem chave, tudo é recusado sem chamar o envio.

## Fixtures
`safra_grupo_fixtures.json`, com dados sintéticos:
- as 4 safras do cenário;
- `deps` por safra (S2627 tem 9 cultivos, SOL-2026-07, OS-0417 e OS-0420);
- os pedidos: uma fazenda, duas, fazenda repetida, sem fazenda e período invertido;
- a leitura "uma aprovada, outra pendente", com Glifosato em L nas duas fazendas e em kg numa só;
- a leitura com área desconhecida.

## Testes
- **Autor (Claude):** `node safra_grupo_unit.js` dá 19/19.
- **Contraprova:** um mutante com 5 defeitos (remoção sem bloqueio, estado herdado, reenvio de tudo, soma binária, soma entre unidades) dá 12/19.
- **Revisor (Codex):** `safra_grupo_contrato_test.js`, arquivo próprio e de autoria do Codex. Carrega o domínio como o teste do autor (`new Function` sobre o arquivo) e usa as fixtures.
- **Contraprovas pedidas em 6173977617:**
  - safra de uma fazenda preservada (G1);
  - adicionar e remover fazenda antes e depois de vínculo (G5 a G8);
  - uma fazenda aprovada e outra pendente (G9 e G10);
  - a mesma demanda em duas fazendas com destinos distintos (G10c);
  - falha no segundo envio seguida de nova tentativa (G12, G12b e G12c);
  - voltar ou trocar mantendo rascunho e foco, a 390 px e com teclado: fica para o teste de navegador da tela (a seguir).

## Tela (próximo passo, mesmo autor)
- **Nova safra / Editar:** o campo "Fazendas" passa a ser de escolha múltipla. Remover uma fazenda com vínculo mostra o motivo e o destino.
- **Escolha da safra:** as sub-safras da mesma safra ficam juntas, com "N fazendas" no nome.
- **Faixa "Trabalhando em":** chips das fazendas da safra para trocar de fazenda na mesma etapa. O rascunho e o filtro ficam com cada sub-safra.
- **Demanda (etapa 4):** resumo por insumo e unidade das fazendas da safra e "Enviar as N fazendas" (`sgEnviar`), com recibo por fazenda.
