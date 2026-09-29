variable "projeto_id" {
  description = "ID do projeto Google Cloud da HML (criado pelo Adrianus)."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.projeto_id))
    error_message = "ID de projeto inválido: 6 a 30 caracteres, minúsculas, dígitos e hífen."
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

variable "github_repositorio" {
  description = "Repositório no formato dono/nome, usado na condição de workflow_ref."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repositorio))
    error_message = "Use o formato dono/nome."
  }
}

variable "github_repository_id" {
  description = "ID numérico do repositório no GitHub (claim repository_id)."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.github_repository_id))
    error_message = "O ID do repositório é só numérico."
  }
}

variable "github_owner_id" {
  description = "ID numérico do dono do repositório no GitHub (claim repository_owner_id)."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.github_owner_id))
    error_message = "O ID do dono é só numérico."
  }
}

variable "habilitar_iap" {
  description = "Liga a API do IAP e o papel iap.admin da conta de infraestrutura (URL controlada por IAP)."
  type        = bool
  default     = true
}

variable "operador" {
  description = "Operador humano (o Adrianus, nunca um agente), no formato user:e-mail."
  type        = string

  validation {
    condition     = can(regex("^user:[^@\\s]+@[^@\\s]+$", var.operador))
    error_message = "Use user:e-mail."
  }
}

variable "agentes" {
  description = "Conta Google própria dos agentes (user:e-mail), com tokenCreator na sa-agentes-leitura. Pode ficar vazia."
  type        = list(string)
  default     = []

  validation {
    condition     = alltrue([for m in var.agentes : can(regex("^user:[^@\\s]+@[^@\\s]+$", m))])
    error_message = "Cada item usa user:e-mail."
  }
}

variable "criar_sa_vertex" {
  description = "Cria a sa-vertex (aiplatform.user) para o Gemini via Vertex. A API aiplatform não é ligada aqui: gera custo e é decisão do Adrianus."
  type        = bool
  default     = false
}

# Rede privada (ADR 0006). Os dois blocos ficam em RFC 1918: o PRIVATE_RANGES_ONLY só leva à VPC destinos RFC 1918, e o
# Cloud SQL só autoriza sozinho origens RFC 1918. Mudar depois do apply recria a sub-rede ou a faixa, que a instância usa.
variable "subrede_cidr" {
  description = "Sub-rede do Direct VPC egress do Cloud Run: bloco /24 alinhado, em RFC 1918."
  type        = string
  default     = "10.10.0.0/24"

  validation {
    condition     = try(endswith(var.subrede_cidr, "/24") && cidrhost(var.subrede_cidr, 0) == split("/", var.subrede_cidr)[0], false)
    error_message = "Use um bloco /24 alinhado, como 10.10.0.0/24."
  }

  validation {
    condition     = can(regex("^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)", var.subrede_cidr))
    error_message = "A sub-rede fica em RFC 1918 (10.0.0.0/8, 172.16.0.0/12 ou 192.168.0.0/16)."
  }
}

variable "faixa_psa_cidr" {
  description = "Faixa do Private Service Access, onde o Cloud SQL recebe o IP privado: bloco /20 alinhado, em RFC 1918, sem conter a sub-rede."
  type        = string
  default     = "10.20.0.0/20"

  validation {
    condition     = try(endswith(var.faixa_psa_cidr, "/20") && cidrhost(var.faixa_psa_cidr, 0) == split("/", var.faixa_psa_cidr)[0], false)
    error_message = "Use um bloco /20 alinhado, como 10.20.0.0/20."
  }

  validation {
    condition     = can(regex("^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)", var.faixa_psa_cidr))
    error_message = "A faixa fica em RFC 1918 (10.0.0.0/8, 172.16.0.0/12 ou 192.168.0.0/16)."
  }

  # Blocos alinhados só se sobrepõem quando um contém o outro; aqui, quando a /24 cai dentro da /20.
  validation {
    condition     = try(cidrhost(format("%s/20", split("/", var.subrede_cidr)[0]), 0) != split("/", var.faixa_psa_cidr)[0], false)
    error_message = "A faixa do PSA não pode conter a sub-rede (subrede_cidr)."
  }
}
