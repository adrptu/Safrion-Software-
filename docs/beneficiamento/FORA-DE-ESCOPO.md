# Beneficiamento · v2 · Fora de escopo

Complemento de `ESPECIFICACAO.md` (era o §13 do v1). Rótulo: especificado. Cada item diz por que fica fora e quando volta. O que já tem bloco (BEN-2 a BEN-8 e a trava do ativo) está numa fonte só, ESPECIFICACAO.md §11.8, com a dependência do PCM no §8; aqui fica só o que não entra em bloco nenhum ou depende de uma decisão.

## 1. Depende de decisão do proprietário ou de dado real

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Valores reais da alçada de diferença (% e teto em kg por rota) e quem é "a gestão" | Política da organização (CF-02 l.1818; l.195). O padrão sintético é parâmetro com rótulo (RN-043 l.245) | O proprietário definir a política CF-02 da fazenda (DECISOES.md §3) |
| Umidades de referência, incerteza do medidor, hipótese de matéria seca por rota, capacidades de secador e terreiro, vida útil reais | Parâmetro técnico sem fonte vira número inventado (l.4177; PRD 45.7 l.7572) | O responsável técnico entregar protocolo com fonte, por espécie e finalidade (BEN-02 l.7560) |
| Padrão oficial de classificação por produto (MAPA) | Item e vigência não verificados; nenhuma norma é embutida (R-G02) | Item e vigência verificados e registrados; o padrão entra cadastrado e versionado |
| Liberação por concessão do cliente (lote fora do padrão aceito por um cliente específico) | Não é exceção expressa do PRD; seria política comercial sem dono | O proprietário definir a política, com proposta à v3.10 |
| Reserva por "classe X ou melhor" | Exige hierarquia de classes com fonte; hoje a regra é igualdade (R-E05) | BEN-6, com a hierarquia publicada |
| Saca ou litro para fruto e coco de café (convenção regional) | Sem fator nem fonte; a R-B05 deixa vazio | O proprietário pedir, com fator e fonte por item |
| Equivalente a 14 % do grão úmido | Não pedido; seria número estimado ao lado do físico | O proprietário pedir; entra rotulado "equivalente (estimado)" pela `benEst`, sem coluna nova |
| Horas disponíveis da linha por dia ou turno | Sem dado; o I16 precisa dos dois lados da conta | BEN-5, com o parâmetro definido pelo dono |
| Correção da plausibilidade do L27-013 (cerca de 97 sc/ha contra 38 sc/ha) | Mexe em seis arquivos fora da BEN (ESPECIFICACAO.md §10.7) | O Codex decidir corrigir o mundo de demonstração |

## 2. Software real, legal ou fiscal

| Item | Por que fica fora | Volta quando |
|---|---|---|
| CMD-06, CMD-23, CMD-24 e CMD-42 no servidor; idempotência no servidor; outbox; movimento imutável com a versão da conversão | Software real exige comando do proprietário (AGENTS §2; ADR 0001, 0003, 0004) | Etapa de software real autorizada, depois da fatia de protótipo aceita |
| Integração com ERP (escritor oficial de estoque e custo) | Idem | Idem |
| Tabela oficial de classificação embutida no código | Nunca: o padrão é cadastrado e versionado (R-G02) | Não volta |
| Torrefação e moagem | Fora do módulo (PRD 45.4 l.7508) | Não volta neste módulo |
| Contrato de registro de câmara fria | O PRD não tem | Proposta à v3.10 aprovada (DECISOES.md §6) |

## 3. Sem dado, sem pedido ou sem dono

| Item | Por que fica fora | Volta quando |
|---|---|---|
| Unificar as cópias de `bloco` e `kline` (onze arquivos) e o Kanban estático de `areas/campo.py:122` | Muda cabeçalho e espaçamento de telas fora da BEN; o 1a exige HTML idêntico | Tarefa própria, com diff de render por tela |
| Links antigos para o EST adotarem `#sec=` (`areas/processo_os.py:291`; `areas/inicio.py:41, 127, 645, 1370, 1405`) | Não é necessário ao BEN-1 | Tarefa própria, quando o dono das telas pedir |
| O.S. agrícola sem registro da autorização (CMD-42) no `osc_liberar` (`areas/processo_os.py:300-311`); decisão "O.S. sem revisão" de 01/10 fora de `docs/DECISIONS.md` | Mesma lacuna que a BEN corrige para a OB (BEN-PRD-08), mas em outro módulo | O Codex registrar a pendência e abrir a tarefa |
| Escala do insumo (2 casas, `quantidade.py:1-9`) e da área (2 casas) diferente do PRD 10.0 | Fora da BEN; a BEN segue o PRD 10.0 | O Codex registrar exceção versionada (l.4191) ou alinhar |
| "Marta (conferente)" no SU-09 oculto (`areas/suprimentos.py:1037, 1047`) | Tela oculta; a Marta da BEN é a Qualidade | O SU-09 voltar ao menu: trocar o contador ou dar a ela a habilidade "Conferir" |
| a13 no "Armazém Sede" no CD-03 (`dados_cad.py:56`; `areas/cadastros.py:506`) | S4; a BEN mostra o local do lote (Packing) | Revisão do CD-03 ou ativo movido pelo PCM |
| MA-02 cita "OB-0104 · Packing linha 1" (`areas/maquinas.py:254`) | Arquivo do PCM | Pedido de texto ao autor do PCM |
| `verif_os.py:64` (Todas 8 ≠ 11) | Falha antiga, já em `0cf6f90` | Quem cuidar da O.S. corrigir; fica fora do aceite da BEN |
| Rótulo "O.S." para a OB nas linhas do EST | S4 | BEN-6 (rótulo "Ordem") |

## 4. Fora do BEN-1 e sem bloco

| Item | Condição de volta |
|---|---|
| Visão Mapa do CO-05 (l.2841) | As instalações terem coordenadas no CD-03 |
| Ordem contínua com estoque em processo inicial (EP₀ da CAL-16, l.4423) | Existir ordem que herda estoque em processo de outra |
| Colunas configuráveis na G2 | TABELAS-FOCO 2e (portão P6), quando o Codex abrir o incremento; sem ele, vale o plano B e o desvio do PRD 4.3 (l.287) fica registrado aqui |
