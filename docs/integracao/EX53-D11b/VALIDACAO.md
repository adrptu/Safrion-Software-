# EX-53 D11b — dedicação por pessoa

Autor Codex; revisor/integrador Claude. Base bb039eb9b89a6412f5b36dbe1f1c9d41549277a7. Contrato PR47: 6259720920, 6260267589; crítica solicitada 6260476136. Protótipo local, sem banco/autorização de servidor ou publicação.

## Comportamento

CD-04 persiste pessoas/equipes no cenário compartilhado, separado dos usuários e alçadas. CF-06 configura dedicação explícita por pessoa/especialidade com motivo, versão e recibo. A soma cabe no teto nominal do calendário; não se pressupõe dedicação total, habilitação ou jornada semanal para ciclo 6×2 sem âncora.

`capacidadeDe(c, especialidade)` retorna `{hhSemana,pessoas,fonte}` ou `null`. Uma partilha obsoleta ativa suspende o total da especialidade; inativas e retiradas são excluídas. Fonte, situação, vigência contratual e calendário são revalidados. Calendário/contrato alterado exige nova conferência, sem ratear horas automaticamente. Exclusão de equipe sem ativos preserva o cadastro inativo.

## Executado por Codex em 19/10/2026

- Node `capacidade_unit_test.js`: teto, ciclo incerto, limite inclusivo, dupla contagem, redução da jornada, agregação por pessoa, obsolescência, inativação e retirada — PASS.
- Node `pessoas_estado_unit_test.js`: revisão otimista, cópia defensiva, ator, repetição, conflito de chave, rename, remoção/recriação ABA, duplicidade, equipe, comandos de dedicação, contrato vencido, papel gestor revogado, versão da fonte — PASS. O primeiro ensaio de permissão revelou helper ausente no fixture (`g2papT`); fixture corrigido e mesma asserção executada com sucesso.
- Build completo com Node no PATH: 147 artboards, 67 no menu, 80 ocultos; saída 0. Primeiro ensaio sem Node no PATH falhou por ambiente; não contado como sucesso.
- Compilação sintática por `new Function` de 154 scripts inline gerados — PASS.
- CUA, navegador real, dados sintéticos em localhost8937: Zé 30+21h/50 recusado mantendo rascunho; 30+20h salvo CFG-0015, persistência após reload; calendário Oficina alterado na CD-04 para 6×2, retorno à CF-06 mostra Rever dedicação. No detalhe final: semana sem base definida e Rever dedicação (não Vigente).
- CUA com iframe de viewport 390×844: foco de Fechar para primeiro campo, percurso Tab pelas quatro especialidades/motivo/Salvar; Enter grava Ana5h e retorna foco à linha, CFG-0017. Não equivale a teste de aparelho/teclado virtual físico.
- CUA concorrência duas abas: A abre v1; B grava6h CFG-0018; A tenta7h, recebe conflito, mantém7h/motivo, mostra vigente6h/v2; Atualizar versão e manter rascunho restaura foco ao primeiro campo; novo clique Salvar grava CFG-0019.
- `git diff --check` sem erros.

## Revisão e composição pendentes

Claude revisa este HEAD e integra; Codex não integra o próprio PR. Consumidores manBacklog/pgBacklog são de autoria Claude e ainda não estão nesta entrega. Não há aceite integral EX53 nem gatilho de auditoria integral/PRD/Next. Revisor deve reproduzir fonte CD04 e impactos na composição, inclusive cenários de cadastro concorrente; proteção real permanece responsabilidade da aplicação futura.

Aplicado: lista/detalhe, estado, horas explícitas, motivo/recibo, recuperação com rascunho e foco. Fora: consumidor do painel/manutenção, por autoria separada. Cortado: valor semanal presumido e dedicação automática; ausência permanece desconhecida.

## Contraprova adicional do cadastro

Node `pessoas_concorrencia_test.cjs` executa c4fonte/c4grava e g2persiste extraídos das fontes: edição externa com formulário aberto não apaga rascunho; salvar versão antiga recusa, restaura formulário e preserva o valor externo; fechar permite atualizar a fonte. PASS. cenMudar e setState adaptados explicitamente: não é teste de UI. A conferência adicional de navegador desta retomada não ocorreu: a interface informou Mac bloqueado após timeout. Nenhum controle foi contornado.
