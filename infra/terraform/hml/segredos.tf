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

  # IAM só no hml-vinculo-pedido (R-006 3c). Operador: grava versão, sem ler nem destruir. sa-preparo (o job): lista,
  # lê, desativa e destrói. O secretVersionManager também dá versions.add, versions.enable e secrets.rotate (sem
  # access): com o secretAccessor, quem roda como sa-preparo reativa e lê uma versão desativada, que ainda tem o código,
  # e grava pedidos. Não amplia o que ela já pode, porque lê a senha do admin do banco.
  # Chave sem e-mail: o endereço vai para o log do plan.
  acesso_pedido = {
    "operador/versionAdder"  = { membro = var.operador, papel = "roles/secretmanager.secretVersionAdder" }
    "preparo/accessor"       = { membro = "serviceAccount:${local.sa.preparo}", papel = "roles/secretmanager.secretAccessor" }
    "preparo/versionManager" = { membro = "serviceAccount:${local.sa.preparo}", papel = "roles/secretmanager.secretVersionManager" }
  }

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

resource "google_secret_manager_secret_iam_member" "vinculo_pedido" {
  for_each = local.acesso_pedido

  secret_id = google_secret_manager_secret.vinculo_pedido.secret_id
  role      = each.value.papel
  member    = each.value.membro
}
