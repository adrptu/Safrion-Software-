# v55 · vermelhos base × candidata (executado)

- **Base:** 7d38e5d (cópia local de 7d38e5d), rodada em 10/10 às 01:54 e às 02:42 UTC.
- **Candidata:** `int/comp` @ 47ff754, rodada em 10/10 às 02:41 UTC (`final2nav`).
- **Brutos:** `brutos/base-7d38e5d_<teste>.log` e `brutos/cand-47ff754_<teste>.log`.
- **Comparação:** as linhas FALHA/FALHOU foram comparadas com `diff`, sem a duração do teste. **As falhas são idênticas nos quatro testes.**

| Teste | Base | Candidata | Asserção que falha (texto do teste) | Jornada que toca |
|---|---|---|---|---|
| `ostest.py` | 32 ok · 1 falha | 32 ok · 1 falha | "painel da nova ordem A liberar: Liberar para execução e Ajustar antes de liberar, sem selo de agrônomo" (OS-0440 · Pulverização · Fungicida 2ª aplicação + inseticida) | O.S. › painel A liberar. Causa, lida no relato do CTL-1/CTL-5: na OS-0440 o Inseticida B está em L/ha e a bula em kg/ha, então a trava de unidade bloqueia a liberação. Não é uma das 4 mudanças da v55 |
| `osacoes.py` | 40 ok · 5 falhas | 40 ok · 5 falhas | (1) "lista mostra percentual: 190 / 350 ha · 54 % · saldo 160 ha" (OS-0421); (2) "OS-0430 A liberar com dono Ana (agrônoma), sem selo de agrônomo"; (3) "lista cabe sem rolagem horizontal · [2150, 1116]"; (4) "recusa não muda o saldo (70 ha)" (OS-0420); (5) "lista: saldo 120 ha e dispensado 40 ha" (OS-0421) | Lista de O.S. Os textos esperados são anteriores às colunas da TABELAS (o saldo e o dispensado aparecem em colunas próprias). O item (3) é uma lista de O.S. mais larga que 1116 px |
| `acao_unica_test.py responsivo` | 1 ok · 2 falhas | 1 ok · 2 falhas | 17 "matriz RESPONSIVIDADE (7 dimensões × SAF etapa 6 e CMP etapa 3)"; 18 "teclado virtual aberto (360×420) · a busca focada continua visível e livre; a área de ações volta ao fluxo (static)…" | **Planejar safra, etapa 6**, e Compras, etapa 3, em telas baixas (800×360) e com o teclado virtual. Toca uma das jornadas da v55 (Planejar safra), em dimensões extremas |
| `partest.py` | 46 ok · 1 falha | 46 ok · 1 falha | "T1-C copia ajuste do T1-B" | Parcelas e talhões (cópia de ajuste entre parcelas). Pode tocar Planejar safra › Dividir: o Codex confere |

Nada aqui foi corrigido ou escondido. O Codex decide se algum desses casos atinge uma das 4 jornadas publicadas ou um controle essencial; os candidatos a essa leitura são o `acao_unica responsivo` (SAF etapa 6) e o `partest` T1-C.
