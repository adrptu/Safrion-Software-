# BASE-QTD — Codex — 17/10/2026

Contrato PR47/6229608079; Claude revisor/integrador. PR empilhado sobre PR94 (2f0a1f0), preservando sua verificação9. Ambiente de prova: fontes adca8ba recuperadas por SHA de blob, mais delta comportamental de agronomia do PR94. Não foi renderização ou navegador.

## Diagnóstico
Teste obsoleto. Dois cenários chamavam irrTerminar logo depois de iniciar e com volume null. A trava de término antecipado interrompia a bateria; depois dela, a exigência legítima de hidrômetro também impediria o fluxo. Nenhuma alteração no código do produto.
A fixture agora avança o relógio sintético ao fim previsto e fornece medição sintética explícita (não dados reais). Teste15 verifica que término cedo e ausência de medição continuam recusados, sem mudança de estado.
Após remover esse bloqueio apareceu verificação10 obsoleta: seis ocorrências de custo/preparo, sem baixa de custódia. Cinco linhas exatas inspecionadas foram documentadas como exceções; não liberam toda ocorrência futura da expressão no arquivo.
O executor JSC emitia erro em stdout, enquanto o wrapper mostrava apenas stderr; diagnóstico agora mostra stderr ou stdout. Node foi usado para identificar o erro e JSC padrão para confirmação.

## Executado
- Base original: aborta Antes do fim previsto (Node identifica stack).
- Candidata com delta94: 15/15 em Node e JSC (inclui7777 comparações Python/JS).
- Mutante removendo guarda temporal: falha15, exit1.
- Mutante adicionando x.dose*area noutra linha de cenario.js: falha10, exit1; exceção não mascara nova ocorrência.
- Sem UI, sem publicação. Claude deve revisar as exceções e reproduzir a composição antes de integrar. A versão adca8ba isolada não contém a abertura vazia de94; por isso a prova15/15 inclui94.
