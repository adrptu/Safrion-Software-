# Composição com o PR #110 (EX-50(a) / LO-02det), 17/10/2026

- **Base:** `0c4b048`. O PR #110 do Codex (HEAD `831e63a`) foi integrado em `ed818ec`.
- **Composição e ajustes do integrador** (`ce7b90e`):
  - **Corpo e cabeçalho (parte do Claude):**
    - saem as etapas fictícias, a continuidade "Fila de expedição · T2", a nota de frete e o link da viagem VG-118;
    - o título passa a "Conferir carga", e a trilha mostra a RM (`lo_contexto`);
    - o selo do estado tem cor: amarelo para Programada, verde para Entregue ou Em trânsito, cinza para nenhuma carga;
    - a primária "Confirmar saída" passa a "Abrir Expedição" depois da saída;
    - há um link "Abrir Expedição" para a carga.
  - **Patch nos handlers do Codex, com aviso no PR:**
    - **A1:** a coluna Saída mostrava "undefined kg" (`l.kg` não existe). Agora soma os movimentos oficiais do lote nessa RM.
    - **A2:** a consulta de uma RM já saída dizia "sem permissão". Agora diz "Saída já confirmada por … ; correção é estorno no Estoque".
    - **A3:** depois da saída, o endereço guarda `#rm=`, e o F5 reabre a mesma carga.
    - Sem carga programada, o botão leva à Expedição; antes só avisava.
- **Testes pelo impacto** (executados; os brutos estão nesta pasta):

  | Teste | Resultado |
  |---|---|
  | logistica_saida | 13/13 (3 novos) |
  | textos_soltos | 266/267 |
  | links_ocultos | 16/16 |
  | acao_unica | 10/10 |
  | componentes | 3/3 |
  | paginas_scan | 5/5 (148 páginas) |

  - **Contraprova de logistica_saida:** com o JS do PR, o executor para no primeiro teste novo (A1, "undefined kg").
  - **textos_soltos:** a falha `D CA-01det` já existe na base. Os oráculos de LO-02det foram ajustados: a frase da retirada T2 foi apagada, e o que fica à vista é "Nenhuma carga programada".
- **Sonda no navegador, no HEAD do PR** (`sonda_lo02det_pr_head.log`), com a RM-0002 do PV-030 programada por Ana:
  - Caio é recusado;
  - tara maior que o bruto é barrada no campo;
  - Rui confirma 52.000 − 15.000 = 37.000 kg, com um único movimento MP-1020;
  - achados: A1 ("undefined kg"); A2 ("sem permissão"); A3 (depois de recarregar, o detalhe volta vazio).
- **Sonda no navegador, na composição** (`sonda_lo02det.log`):
  - sem carga programada, o cabeçalho diz "Nenhuma carga programada", e a primária é "Abrir Expedição";
  - com a RM programada, a trilha mostra "RM-0002 · PV-030 · Coop Grão Sul" e o selo amarelo diz Programada;
  - o Enter na primária abre "Confirmar saída · RM-0002";
  - depois da saída, o selo diz Entregue, o endereço tem `#rm=RM-0002`, e o F5 mantém a carga com 1 movimento;
  - a coluna Saída mostra 37000 kg;
  - a consulta explica "Saída já confirmada por Rui";
  - a 390 não há rolagem horizontal;
  - nenhum erro de JS.
- **Limite conhecido (motor comum, não vem deste PR):** o formulário do g2 não leva o foco para dentro do diálogo e não fecha com Esc. Isso vale para todos os formulários do protótipo e fica no backlog de acessibilidade do motor.
- **Páginas que mudam em relação ao publicado:** só `LO-02det.dc.html`.
