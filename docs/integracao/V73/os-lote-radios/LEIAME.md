# OS-LOTE (PR #88) na composição e correção dos rádios de papel (achado do app 6227866897)

## Composição

- `d995ded` = `47ccc1d` + merge do PR #88 (OS-LOTE-F1, HEAD `703d9a1`).
- A integração foi feita pelo Claude como revisor, com o parecer 6227950030 (DEC-0910-02).
- O `cf01_703d9a1_pr88.log` é o bruto do `config_test.py cf01` rodado no HEAD do PR #88: **39/39**. Era o bruto que o Codex pediu em 6228059563.

## Correção dos rádios

O achado é o 6227866897 (P2), aberto pelo app do Codex no PR #47. Em Configurações › CF-01, no painel da alçada, as opções de "Papel que decide" (`cf1_aopc`, `areas/configuracoes.py`) tinham cada uma o seu ponto de Tab. Pelo padrão de grupo de rádios, o grupo deve ter um ponto de Tab só, na opção marcada, e as setas trocam a opção.

**A correção:** agora só a opção marcada tem `tabindex=0`; as demais ficam com `-1`. Sem opção marcada, quem recebe o ponto de Tab é a primeira. É o mesmo padrão do `cf1_acand`.

**Teste novo, no `cf01` do `config_test.py`:**
- ao abrir o painel, existe um só ponto de Tab, na opção vigente;
- ao escolher PCP, o ponto de Tab vai junto e continua sendo um só.

**Execução:**

| Execução | Render | Resultado | Bruto |
|---|---|---|---|
| Com a correção | `d995ded` + correção, 156 páginas | **41/41** | `cf01_correcao_radios.log` |
| Contraprova, sem a correção | versão publicada v110 (render `05947ad`) | **38/41**: os 2 checks novos **FALHAM**, com 3 opções com `tabIndex=0` (`['Gestor (vigente)', 'PCP', 'Agrônomo']`) | `cf01_contraprova_v110.log` |

Na contraprova, a v110 não tem as origens de demonstração do OS-LOTE. Por isso o check do painel da AL-01, que conta as ordens em "A liberar", também difere. Essa diferença não vem desta correção.

Todos os dados são sintéticos.
