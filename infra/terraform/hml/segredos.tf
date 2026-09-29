# Segredos sem versão: os valores entram por stdin ou pelo console, fora do Terraform (senão iriam para o state e o plan).
# Apagar um segredo apaga todas as versões: prevent_destroy e deletion_protection.

locals {
  segredos = toset([
    "hml-db-admin-senha",
    "hml-db-migrator-senha",
    "hml-db-app-runtime-senha",
    "hml-oidc-client-secret",
  ])

  # secretAccessor no nível do segredo, nunca no projeto, e só para contas de serviço. O operador não lê senha
  # nenhuma: sem IP público ele não conecta ao banco (ADR 0006), e o job de preparo lê a do admin pela sa-preparo.
  leitores = {
    web     = { membro = "serviceAccount:${local.sa.web}", segredos = ["hml-db-app-runtime-senha", "hml-oidc-client-secret"] }
    preparo = { membro = "serviceAccount:${local.sa.preparo}", segredos = ["hml-db-admin-senha", "hml-db-migrator-senha", "hml-db-app-runtime-senha"] }
    demo    = { membro = "serviceAccount:${local.sa.demo}", segredos = ["hml-db-app-runtime-senha"] }
  }

  acesso_segredos = merge([
    for quem, l in local.leitores : {
      for s in l.segredos : "${quem}/${s}" => { membro = l.membro, segredo = s }
    }
  ]...)

  # Versão fixa de cada segredo (R-006, F40). Vazio enquanto criar_cloud_run = false.
  # Só o Terraform troca a versão: sem gcloud --update-secrets, o apply seguinte não volta à antiga.
  versao = var.versoes_segredos == null ? {} : {
    "hml-db-admin-senha"       = tostring(var.versoes_segredos.admin)
    "hml-db-migrator-senha"    = tostring(var.versoes_segredos.migrator)
    "hml-db-app-runtime-senha" = tostring(var.versoes_segredos.app_runtime)
    "hml-oidc-client-secret"   = tostring(var.versoes_segredos.oidc)
  }
}

resource "google_secret_manager_secret" "hml" {
  for_each = local.segredos

  secret_id           = each.value
  deletion_protection = true

  # Destruir uma versão só a desativa; a destruição real vem 7 dias depois (R-006, rotação passo 6).
  version_destroy_ttl = "604800s"

  replication {
    user_managed {
      replicas {
        location = var.regiao
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_secret_manager_secret_iam_member" "acesso" {
  for_each = local.acesso_segredos

  secret_id = google_secret_manager_secret.hml[each.value.segredo].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = each.value.membro
}

# Pedido de vínculo: cada versão é um pedido de uso único, com o código de referência. Fora de local.segredos e SEM
# version_destroy_ttl: com o atraso, destruir só desativaria a versão, e o pedido seguiria recuperável e cobrado por
# 7 dias (R-006 3b). Assim, a destruição pelo job é imediata. checar_travas.py recusa o campo aqui.
resource "google_secret_manager_secret" "vinculo_pedido" {
  secret_id           = "hml-vinculo-pedido"
  deletion_protection = true

  replication {
    user_managed {
      replicas {
        location = var.regiao
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

# IAM só no hml-vinculo-pedido (R-006 §3c), em dois vínculos explícitos que o checar_travas.py confere.
# Operador: grava versão (secretVersionAdder), sem ler, desativar nem destruir.
resource "google_secret_manager_secret_iam_member" "pedido_operador" {
  secret_id = google_secret_manager_secret.vinculo_pedido.secret_id
  role      = "roles/secretmanager.secretVersionAdder"
  member    = var.operador
}

# Job (sa-preparo): o papel safrionVinculoPedido do bootstrap (versions.list, get, access, disable e destroy), no lugar
# de secretAccessor + secretVersionManager. Sem add, enable nem rotate: a conta do job não grava pedido nem reativa
# versão desativada. Resta: lê pedidos ENABLED e destrói versões. Não isola os dois jobs que usam a sa-preparo nem
# código alterado por quem tem run.developer. O bootstrap cria o papel antes do apply do hml.
resource "google_secret_manager_secret_iam_member" "pedido_fila" {
  secret_id = google_secret_manager_secret.vinculo_pedido.secret_id
  role      = "projects/${var.projeto_id}/roles/safrionVinculoPedido"
  member    = "serviceAccount:${local.sa.preparo}"
}
