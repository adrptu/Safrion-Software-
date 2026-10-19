# EX-53 F1b-D11 — metas explícitas (Codex)

Base: 262662affd0fe6197f3c42ad88a9186d8b350cfa. Contrato 6259133161/6259208739; crítica Claude 6259281115 incorporada, recibo 6259301893. Revisor/integrador: Claude.

Configurações → Metas e limites (CF-06) → detalhe/versões. Quatro medidas: KPI-PCM-05, custo-desvio (KPI-CUS-03), venda-referencia e compra-referencia (sem KPI PRD específico). Meta de produtividade continua no cultivo. Ativos liberados foi excluído conforme crítica: não é disponibilidade técnica.

Leitor puro `metaDe(c,id)`; classificador `metaAvaliar(c,id,valor,un,parcial)`; rastreio `metaDica(c,id)`. Somente escopo organizacao. Unidade %, não fração; custo/compra menor é melhor; venda/cumprimento maior é melhor. Alvo incluso no verde e limiar incluso no amarelo; limiares iguais não criam faixa amarela. Ausência, unidade incompatível ou base parcial ficam cinza. Sem padrões de meta. A meta vigente se aplica também a períodos passados (explicado na tela/dica).

Comando `metaGravar` dentro de `cenMudar` estrito: papel gestor ativo revalidado, motivo obrigatório, versão por medida, recibo idempotente e trilha com antes/depois. Retirada preserva versão (ABA). Falha ao gravar não confirma sucesso. Rascunho e foco preservados ao fechar/reabrir; conflito exige comparar vigente e atualizar versão explicitamente antes de salvar novamente.

## Provas executadas pelo Codex, 19/10/2026

- `node metas_unit_test.js`: fronteiras, zero, ausências, retirada, inválidos, escopo/unidade e imutabilidade PASS.
- `python3 metas_comando_test.py`: funções reais de cenário/configuração; gestor/recusa, motivo, replay, conflito, versão após retirada, autoria e quota sem efeito PASS.
- `python3 config_unit_test.py`: 226/226, sem alteração de regras anteriores.
- `python3 inteligencia_unit_test.py`: 35/35.
- `python3 ex53_metas_test.py`, `ex53_m5_cartao_test.py`, `ex53_f1c_test.py`: PASS, incluindo meta M5 vermelha/retirada e custo com sinal/base parcial. Contraprovas antigas preservadas.
- Build: 147 artboards, 67 no menu. Primeira tentativa falhou por Node fora do PATH; execução válida usa o Node instalado. Compilação inicial tentou cache Python fora do sandbox; redirecionada a /private/tmp. Essas falhas de preparo não contam como teste aprovado.
- CUA, localhost:8936, perfil sintético Ana, largura desktop observada 1280: criação 90/80; ausência de motivo rejeitada com campos preservados; Escape devolve foco à linha, Enter reabre com rascunho; salvar dá recibo CFG-0016, M5 0%/0 de 3 fica Fora da meta, estilo vermelho #B42318; retirar com motivo dá CFG-0017, M5 volta Meta não configurada. Versões/autoria/data/motivo visíveis.
- CUA IV: meta venda alvo0/atenção−2; Mamão −1,6% permanece Abaixo da referência e recebe Atenção à meta; saca a conferir recebe Base parcial. Não muda a contagem matemática de produtos abaixo da referência.

## Pendências explícitas de liberação

Claude: crítica do HEAD, browser 390/teclado completo, revalidação de papel e consumidores IC/Mapa afetados. Codex não afirma teste móvel executado: viewport local já mostrou limitação em rodada anterior. Alavancas/pgCor pertencem ao Claude e serão ligados aos mesmos IDs; não foram editados aqui. Sem publicação/merge/main/produção por este PR. Nenhuma auditoria integral disparada.

Aplicado: listagem/detalhe/versões, contexto de organização, retorno e recuperação, unidades e estados explícitos. Fora: calendário/capacidade/janela de reincidência e D1–D4, aprovação operacional, produtividade duplicada. Cortado: seletor de sentido incoerente com domínio, metas padrão e cor de Ativos liberados.

Contraprova adicional CUA em duas abas: rascunho custo0/5 contra gravação20/25 na outra aba. Salvar antigo foi rejeitado com versão/valores vigentes visíveis e rascunho intacto. Atualizar versão não gravou automaticamente; segundo Salvar explícito produziu v2/CFG-0020. Foco após atualizar versão foi ajustado para o campo Valor, pois o botão desaparece.
