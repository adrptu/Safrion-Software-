# OS-LOTE R2 · crítica delimitada do Gemini

16/10/2026. Adaptador existente `work/gemini-team/gemini-consult.py`; modelo real gemini-3.1-pro-preview, HIGH, STOP, 6.438 tokens totais. Pacote mínimo sintético inspecionado (5.674bytes), hash ce1b1251f4e42bfdf573d71042b01d9dbac57a368f82722ab7f6445baa8e2807. Primeira tentativa no sandbox parou na autenticação, antes da API; execução com permissão concedida concluiu uma consulta. Não houve repetição paga nem fallback de modelo. Prompt e resposta bruta preservados ao lado.

O bruto abre com “revisada pelo Claude”; isso é impreciso: Claude aceitou a conciliação no recibo6220998887, não revisou a R2 final. Tampouco o Gemini executou o oráculo ou leu arquivos não enviados. Parecer textual não é aprovação de produto.

| Sugestão | Tratamento Codex / aceite de implementação |
|---|---|
|1.Conflito em parte da seleção|Adaptada. Envelope inclui versões de todas as origens e grupo; retorno identifica conflitos, conserva rascunho/seleção válidos. **Recusado** desmarcar C e reenviar automaticamente A/B com um clique sem nova prévia: seria mudar o conjunto confirmado. Testar outra aba alterando C entre prévia/confirmação; efeito do agrupamento zero e seleção recuperável.|
|2.Duração não cabe na interseção|Já coberta na R1 e no oráculo N6:6,75h>5h. Não acrescentada trava geral que impeça guardar composição tecnicamente válida só porque falta prontidão; impedir programação/liberação inválida, nomeando pendência. O critério original do modelo duplicava setup em um trecho; fórmula usa trabalho+deslocamento+setup uma vez.|
|3.Separação operacional preserva aprovação|Precisada conforme41.3/APROV-11: mesmaO.S./versão técnica/escopo preserva vínculo. **Recusado copiar carimbo para nova entidade**, proposto no checklist bruto: aprovação é porID/versão. Data fora da janela e máquina que altera método exigem nova revisão. Aprovadas continuam fora do atalho inicial.|
|4.Desfazer inviável|Adaptada: reler ao abrir e revalidar no comando; motivo persistente e link à origem, sem tooltip como única explicação e sem novo polling/WebSocket. Corrida após leitura recusa com rascunho preservado.|
|5.Parâmetro ausente|Aceita: excluir com motivo Definir parâmetro; não herdar perfil/restrição da âncora. Critério vale para todos os parâmetros pertinentes, não só quando a âncora tem valor.|

Crítica resolvida por contrato/contraexemplo, sem votação. Mudanças aplicadas naR2; testes de concorrência, UI e banco continuam especificados para implementação. Oráculo25/25 é cálculo independente, não evidência desses controles.
