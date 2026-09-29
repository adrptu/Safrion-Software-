# Planejamento remoto da HML

`infra-hml.yml` prepara **somente o plano da primeira fase** (banco, registro e contêineres de segredos).
Não contém `apply`, publicação, criação de usuário ou valor de segredo. Depende do bootstrap aplicado e conferido;
o código integrado por si só não comprova execução remota nem homologação disponível.

## Preparar uma vez

1. Seguir [bootstrap](../../infra/terraform/bootstrap/README.md) e [operação](../../docs/OPERACAO.md).
   Confirmar backend remoto separado, IAM efetivo, federação e autorização de gasto. A conta da CI não pode ler o
   bucket do bootstrap. O state HML fica em `gs://safrion-hml-1390827288-tfstate-hml/hml`.
2. Configurar o environment `hml-infra` para a main e sua variável `HML_PROJECT_NUMBER`, com o número real do projeto
   `safrion-hml-1390827288`. Ambos os jobs usam esse environment; só o segundo recebe `id-token: write`.
   A disponibilidade das regras do environment depende do plano GitHub. Não alegar revisão humana obrigatória
   sem comprová-la; o gate de aplicação ainda será entregue separadamente.
3. Guardar um JSON UTF-8 **privado**, fora do Git, em `config/hml.tfvars.json` no bucket HML. Usar as cinco saídas
   do bootstrap/destino (`projeto_id`, `projeto_numero`, `rede_self_link`, `subrede_self_link`, `faixa_psa_nome`)
   e `operador` no formato `user:e-mail`. Região fixa em São Paulo. `criar_cloud_run=false`; demais valores da
   segunda fase ausentes ou nos defaults vazios. Não incluir segredos. Registrar geração GCS e SHA256 dos bytes
   conferidos; as entradas do workflow são somente esses dois identificadores, sem HCL/argumentos livres.

## Executar e revisar

Disparar manualmente **HML — planejar infraestrutura**, selecionando `main` e os dois identificadores revisados.
A validação da origem ocorre antes da autenticação. O checkout é o SHA do evento; não segue outra branch durante
a execução. Terraform 1.16.3 e gcloud 586.0.0 são fixados; actions usam SHA completo.

O helper recusa configuração duplicada/desconhecida, outro destino, fase 2, plano destrutivo, guard reprovado e
readback divergente. Executa `init` com lockfile somente leitura, `plan` com lock e `show` privado. Não recebe
`TF_VAR_*`, `TF_CLI_ARGS` ou `TF_LOG` herdados; arquivo CLI vazio impede carregar `~/.terraformrc`.
Exemplo `.tfvars.example` não é configuração automática. O arquivo temporário de credenciais criado pela action
`auth` fica no checkout até sua limpeza final: nenhum passo deste job deve enviar o workspace como artefato.

Binário, hash e `recibo.json` ficam privados em `planos/<run_id>/<tentativa>/`, com escrita condicionada à ausência
do objeto e expiração de 30 dias. O recibo de origem só é gravado depois de conferir o binário e seu hash; é relido
pela geração e comparado byte a byte antes de anunciar sucesso. Contém apenas `repositorio`, `workflow`, `evento`,
`ref`, `head_sha`, `run_id`, `tentativa`, `config_generation`, `config_sha256`, `plan_sha256`, `plan_generation` e
`escopo` (`fase1`). Não é uma assinatura criptográfica: o consumidor ainda precisa conferir a execução oficial
bem-sucedida na API do GitHub, a main atual e a geração/hash do plano antes de aplicar.

O resumo humano no summary preserva commit, hash/geração da configuração e do plano, contagens, drift, resultado
das travas e o aviso de que só houve PLAN. Acrescenta objeto, geração e SHA256 do recibo de origem. Nenhum endereço
de recurso do plano, e-mail, valor ou JSON bruto do plano é publicado.
Revisores autorizados devem conferir o binário privado pela geração e compará-lo ao hash do recibo externo;
o resumo por contagens não substitui essa revisão. Produção segue o aceite explícito da candidata.

Uma falha retorna um código sem ecoar saída privada. Arquivos temporários são removidos ao sair normalmente,
inclusive por exceção; encerramento abrupto depende do descarte do runner efêmero. Upload parcial pode permanecer
privado até expirar; não gera recibo de sucesso. A identidade atual tem poderes de administração da HML:
PLAN é uma restrição deste workflow, **não IAM somente leitura**. `objectAdmin` pode alterar objetos; geração e hash
externo detectam divergência, não tornam o bucket imutável nem protegem contra administradores de ambas as contas.
Timeout tenta interromper a CLI cooperativamente e encerra o grupo de processos antes de remover temporários.
Interrupção abrupta ainda pode deixar um lock remoto; conferir execução e lock com a equipe antes de desbloquear,
sem `force-unlock` automático.

Os testes locais de contrato e orquestração estão em `tools/ci/test_hml_plan.py`, executados pelo check existente
de documentação/CI. Usam dados sintéticos e ferramentas simuladas; não comprovam WIF, IAM ou Terraform real.
Contribuição do Gemini Pro/HIGH no desenho: JSON estrito, ambiente por lista permitida e contraprovas de vazamento.
