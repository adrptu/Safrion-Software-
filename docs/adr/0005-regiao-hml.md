# ADR 0005: Hospedar a HML em southamerica-east1 (São Paulo)

- **Situação:** proposta
- **Data:** 2026-09-28
- **Autor:** Claude Code
- **Revisor:** Codex (pendente)
- **Requisitos do PRD afetados:** 28.1 (região em ADR), 27.4 (HML equivalente à produção), 30.5 (backup e PITR), ENG-061 a ENG-064

## Contexto
O PRD 28.1 pede a região primária definida em ADR, "próxima aos usuários do piloto", considerando latência, serviços disponíveis, residência de dados e recuperação. A HML guarda a identidade OIDC real dos testadores, que estão no Brasil. O custo e o desenho estão no [R-006, atualização de 28/09/2026](../parceria/rodadas/evidencias/R-006-hospedagem.md) (commit `090caf7`).

## Decisão
- Toda a HML em **`southamerica-east1`**: Cloud Run, Cloud SQL, backups, logs do PITR, Artifact Registry, réplica dos segredos e bucket do state.
- Local dos backups fixado na mesma região. Sem isso, eles vão para uma multirregião fora do Brasil.
- O Terraform recusa outra região (`validation` em `variables.tf`). Mudar exige ADR nova.
- **Custo Tier 2 proposto:** base de ≈ US$ 15,22/mês com preços de São Paulo (R-006). A franquia do Cloud Run é valorada a preço Tier 1 e abatida ao preço de São Paulo. O aceite do gasto é do Adrianus, em frase literal (R-006, orçamento); pendente.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| `us-central1` (Iowa) | Mais barata (preço Tier 1, R-006 F12), mas põe dados e backups fora do Brasil (transferência internacional pela LGPD; regras da ANPD não verificadas) e longe dos testadores (latência não medida) |
| `southamerica-west1` (Santiago) | Mais perto que os EUA, mas fora do Brasil, com o mesmo problema de residência; preços, serviços e latência não verificados nesta rodada |

## Consequências
- Mais fácil: residência dos dados no Brasil, menor distância dos testadores e preços de São Paulo já conferidos (R-006, F12, F13b, F38, F39).
- Mais difícil: preço acima de Tier 1 e franquia do Cloud Run que cobre menos horas (≈ 35,7 h/mês de web ativa com 1 vCPU).
- Recuperação: backups e PITR na mesma região atendem a HML. A produção precisa decidir a cópia fora da região (ENG-069) na ADR dela.
- Reversão: HML sem dado real pode ser recriada em outra região por ADR nova, novo apply e novo preparo do banco. Os backups não migram entre regiões por este Terraform.

## Verificação
- `validation` da variável `regiao` em `infra/terraform/bootstrap` e `infra/terraform/hml`.
- Revisão do plan: `location` e `region` de todos os recursos em `southamerica-east1`, inclusive `backup_configuration.location`.
- Na 1ª fatura, conferir o preço de São Paulo e a aplicação da franquia (R-006).
