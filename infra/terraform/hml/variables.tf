variable "projeto_id" {
  description = "ID do projeto Google Cloud da HML."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.projeto_id))
    error_message = "ID de projeto inválido: 6 a 30 caracteres, minúsculas, dígitos e hífen."
  }
}

variable "projeto_numero" {
  description = "Número do projeto (agente de serviço do IAP e URL padrão do Cloud Run)."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.projeto_numero))
    error_message = "O número do projeto é só numérico."
  }
}

variable "regiao" {
  description = "Região da HML (ADR 0005)."
  type        = string
  default     = "southamerica-east1"

  validation {
    condition     = var.regiao == "southamerica-east1"
    error_message = "A HML fica em southamerica-east1 (ADR 0005). Outra região exige ADR nova."
  }
}

variable "criar_cloud_run" {
  description = "false na 1ª aplicação (banco, segredos, registro). true depois que as versões dos segredos existirem."
  type        = bool
  default     = false
}

variable "versoes_segredos" {
  description = "Número fixo da versão de cada segredo, nunca latest. Obrigatório com criar_cloud_run = true."
  type = object({
    admin       = number
    migrator    = number
    app_runtime = number
    oidc        = number
  })
  default = null

  validation {
    condition     = var.versoes_segredos == null || try(alltrue([for v in values(var.versoes_segredos) : v >= 1 && floor(v) == v]), false)
    error_message = "Cada versão é um inteiro maior ou igual a 1."
  }

  validation {
    condition     = !var.criar_cloud_run || var.versoes_segredos != null
    error_message = "Com criar_cloud_run = true, informe versoes_segredos."
  }
}

variable "url_controlada" {
  description = "iap (padrão): IAP no serviço web, sem allUsers. publico: allUsers com run.invoker só na web (exceção ENG-005 aprovada)."
  type        = string
  default     = "iap"

  validation {
    condition     = contains(["iap", "publico"], var.url_controlada)
    error_message = "Use iap ou publico."
  }
}

variable "iap_permitidos" {
  description = "Quem passa pelo IAP (roles/iap.httpsResourceAccessor): o grupo Google dos testadores e a conta do teste de /saude. E-mail de pessoa não entra: iria para o plan e o state."
  type        = list(string)
  default     = []

  validation {
    condition     = alltrue([for m in var.iap_permitidos : can(regex("^(group|serviceAccount):[^@\\s]+@[^@\\s]+$", m))])
    error_message = "Cada item usa group: ou serviceAccount: seguido do e-mail. Testadores entram no grupo, fora do Terraform."
  }
}

variable "operador" {
  description = "Operador humano (o Adrianus, nunca um agente), no formato user:e-mail."
  type        = string

  validation {
    condition     = can(regex("^user:[^@\\s]+@[^@\\s]+$", var.operador))
    error_message = "Use user:e-mail."
  }
}

variable "oidc_client_id" {
  description = "Client ID do cliente OAuth da HML (Google Auth Platform). Só a web usa: vazio na fase 1."
  type        = string
  default     = ""

  validation {
    condition     = !var.criar_cloud_run || length(trimspace(var.oidc_client_id)) > 0
    error_message = "Com criar_cloud_run = true, informe o client ID."
  }
}

variable "origem" {
  description = "SAFRION_ORIGEM. Vazio: https://safrion-web-<número do projeto>.<região>.run.app."
  type        = string
  default     = null

  validation {
    condition     = var.origem == null ? true : can(regex("^https://[^/\\s]+$", var.origem))
    error_message = "Use https://host, sem barra no fim."
  }
}

# Rede privada (ADR 0006), das saídas do bootstrap. Por variável, e não por bloco data, que o checar_travas.py recusa.
# O bootstrap precisa ser aplicado antes: a instância só aceita a faixa na criação.
variable "rede_self_link" {
  description = "self_link da rede da HML (saída rede_self_link do bootstrap)."
  type        = string

  validation {
    condition     = can(regex("^https://www\\.googleapis\\.com/compute/v1/projects/[a-z][a-z0-9-]{4,28}[a-z0-9]/global/networks/[a-z]([-a-z0-9]{0,61}[a-z0-9])?$", var.rede_self_link)) && startswith(var.rede_self_link, "https://www.googleapis.com/compute/v1/projects/${var.projeto_id}/")
    error_message = "Use a saída rede_self_link do bootstrap deste projeto."
  }
}

variable "subrede_self_link" {
  description = "self_link da sub-rede do Direct VPC egress (saída subrede_self_link do bootstrap)."
  type        = string

  validation {
    condition     = can(regex("^https://www\\.googleapis\\.com/compute/v1/projects/[a-z][a-z0-9-]{4,28}[a-z0-9]/regions/[a-z0-9-]+/subnetworks/[a-z]([-a-z0-9]{0,61}[a-z0-9])?$", var.subrede_self_link)) && startswith(var.subrede_self_link, "https://www.googleapis.com/compute/v1/projects/${var.projeto_id}/regions/${var.regiao}/")
    error_message = "Use a saída subrede_self_link do bootstrap deste projeto, na região da HML."
  }
}

variable "faixa_psa_nome" {
  description = "Nome da faixa do Private Service Access (saída faixa_psa_nome do bootstrap)."
  type        = string

  validation {
    condition     = can(regex("^[a-z]([-a-z0-9]{0,61}[a-z0-9])?$", var.faixa_psa_nome))
    error_message = "Use a saída faixa_psa_nome do bootstrap."
  }
}
