# Fora de escopo · Planejar safra, etapa única (v2)

Companheiro de [ESPECIFICACAO.md](ESPECIFICACAO.md). Cada item tem o motivo de ficar fora e a condição de retorno. Os itens marcados "limitação" vão na lista de limitações entregue com a candidata em homologação (§10).

| Item | Por que fica fora | Volta quando |
|---|---|---|
| **Realizado das O.S. na capacidade e na projeção** (PRD 44.1, "projeção = realizado + saldo futuro", PRD.md:7150). **Limitação.** | Hoje a capacidade, as horas e o custo são do plano inteiro, pela data do plano. A OS-0421 já executou 190 ha (dados.py:94), e as horas dela continuam contando em nov/26 e dez/26 | fatia do CONTROLE-01 (`pce/verificada.md:229`): depois do PR 5, ou antes da homologação se o item 10 for S2 (§10) |
| **Publicar versão de referência ao fim do planejamento** (RN-031, PRD.md:233; FL-AG-08 passo 4, PRD.md:7220; UX-01 "versões rastreáveis", PRD.md:11734) | Exige base, revisão e realizado coexistindo, que é o tema do CONTROLE-01 | fatia do CONTROLE-01 (`pce/verificada.md:227, :238`), sem trazer o realizado para a etapa 3 e sem uma segunda primária (PRD 4.2). O passo "Publique plano" fica pendente na DEC, não removido |
| **Regra A:** ocorrências antes do início, depois do fim ou fora do calendário fora dos totais. **Limitação.** | Muda totais e o custo de implantação de perene. Hoje elas ganham etiqueta, ficam nos totais com qualificador e não contam na capacidade (PRD 44.1, 44.5) | o Codex decidir severidade e regra. Não depende de existirem dias úteis por safra |
| **Calendário por safra** (hoje set/26–ago/27 fixo) | Só a S2526 cai fora dele. Na LG2627, as 75 ocorrências estão antes do início da própria safra, e um calendário por safra não mudaria nada | existirem dias úteis por safra |
| **Recursos por fazenda, herdados do CD-03/MA-01** (PRD 53.1). **Limitação.** | Cadastro único no protótipo. A conta soma só as safras abertas da mesma fazenda (P3, padrão) | incremento D4/ALOC (`058eb147`) ou resposta de P3 |
| **Pessoas por função** (PRD 44.4, KPI-PCP-06) | "Operadores e equipe" é um pool só | as habilidades do CD-04 entrarem no cálculo |
| **Déficit com prazo, responsável e alternativas** (PL-03, PRD 44.6) | O veredito dá a primeira data e quanto falta, não o plano de atendimento | fatia própria do PL-03 |
| **Conflito por semana e turno** | Já está em O.S. › Recursos (DEC-2609-09); a etapa é estimativa mensal | — (fica na O.S.) |
| **Prévia antes de salvar no formulário Rendimento** (`repartir` sobre o rascunho) | A prévia do recurso (§4.2) já recalcula; falta medir no navegador. O `ocorr` da LG2627 leva 9,8 ms no node (executado, v2calc) | prévia do recurso medida no navegador em até 100 ms por tecla; o mesmo mecanismo vale aqui |
| **Custo por mês (caixa)** | PEND-SAF-02 (P1); continua exigido no orçamento (PRD 44.5 e 44.6) | resposta do proprietário; se "manter", desenho próprio |
| **Colunas Largura · velocidade · eficiência, custo/h e R$/kg na tabela** | PEND-SAF-01 (P2) | resposta "Manter na tabela": fatia própria com colunas configuráveis (componente G2 novo) |
| **Cenário adverso de clima** (PRD 44.4) | Sem fonte de dados | houver fonte e decisão do Codex |
| **Janela em datas**, como no Farmbox | A entrada em horas é o oráculo do D-01 | teste de regressão do D-01 para mudar a entrada |
| **Copiar a janela no "Todas"** | Sobrescreveria, sem aviso, as janelas próprias das outras atividades. A regra é do D-01 | decisão do Codex, dono do oráculo D-01 |
| **"Nova configuração" para atividade sem nenhuma** | O `rendAfter` exige `_novaCfg` (safra.js:440-441) | o `rendAfter` aceitar inclusão sem ele |
| **Cartões no lugar de tabela no celular** (PRD 4.3) | Componente G2 novo | componente pronto e testado |
| **Diesel como item de demanda** (D2) | Quem fornece o combustível não está definido | a fazenda definir quem fornece |
| **PL-03 oculto com números fixos** que contradizem a etapa 5 (planejamento.py:312-379) | Outra tela | tarefa própria: derivar da etapa 3 ou remover |
| **Navegação por setas na `g_cap`** (tabindex móvel) | Com a grade recolhida e "—" inerte, as paradas de Tab caem; ainda são uma por célula com demanda | o G2 ganhar navegação por setas |
| **Espelho `_ocorr_py` sem conferir cultura nem ajustes '-' e '+'** (dados2.py:130-138) | Corrigir mexe no espelho da demanda; `resumo_cultura` usa o laço do `plano_op` | tarefa própria, com a paridade da demanda verde |
| **`aj` sem uso** depois da Origem calculada (inclusive na atividade dividida, safra.js:465-466) | O selo sai da linha e a Origem não lê `aj` | limpeza à parte, sem mudar comportamento |
