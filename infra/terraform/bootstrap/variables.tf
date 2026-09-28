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
