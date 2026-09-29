import { Duplex } from 'node:stream';

/** Mensagem do protocolo do PostgreSQL: tipo, tamanho (com ele mesmo) e corpo. */
function quadro(tipo: string, corpo: Buffer): Buffer {
  const b = Buffer.alloc(corpo.length + 5);
  b.write(tipo, 0);
  b.writeInt32BE(corpo.length + 4, 1);
  corpo.copy(b, 5);
  return b;
}

/**
 * Transporte PostgreSQL em memória, para o driver pg real sem rede (modelo do harness da revisão do Codex, CONEXAO-01):
 * aceita a autenticação (AuthenticationOk e ReadyForQuery), responde a cada consulta simples com CommandComplete e
 * ReadyForQuery quando `responde` e fecha no Terminate. Sem resposta, é a perda de resposta depois da autenticação: o
 * SELECT 1 fica pendente até alguém destruir o transporte.
 */
export class TransportePg extends Duplex {
  private inicio = true;
  consultas = 0;

  constructor(private readonly responde: boolean) {
    super();
  }

  setNoDelay() {
    return this;
  }

  setKeepAlive() {
    return this;
  }

  connect() {
    queueMicrotask(() => this.emit('connect'));
    return this;
  }

  override _read() {
    // As respostas entram por push; não há o que ler sob demanda.
  }

  override _write(bytes: Buffer, _codificacao: BufferEncoding, pronto: (erro?: Error | null) => void) {
    if (this.inicio) {
      this.inicio = false;
      queueMicrotask(() =>
        this.push(Buffer.concat([quadro('R', Buffer.alloc(4)), quadro('Z', Buffer.from('I'))])),
      );
    } else if (bytes[0] === 0x51) {
      this.consultas++;
      if (this.responde) {
        queueMicrotask(() =>
          this.push(Buffer.concat([quadro('C', Buffer.from('SELECT 1\0')), quadro('Z', Buffer.from('I'))])),
        );
      }
    } else if (bytes[0] === 0x58) {
      queueMicrotask(() => this.destroy());
    }
    pronto();
  }
}
