import { useState } from "react";
import { useRouter } from "@tanstack/react-router";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Chip, Tag } from "@/components/ui/chip";
import { Input, Textarea } from "@/components/ui/field";
import { Continuity, NextStep } from "@/components/ui/steps";
import { formatArea, formatQty } from "@/lib/format";
import { nextAction, osTitle, phaseLabel, phaseTone } from "@/lib/os";
import { PLOTS, PRODUCTS, MACHINES, PEOPLE, PHASES } from "@/lib/seed";
import { useApp, classificarFila, novaChaveApontamento, saldoEfetivo, decidirChave, dataDoItem } from "@/lib/store";
import type { WorkOrder } from "@/lib/types";

type OsDraft = { ha: string; hours: string; reason: string; review: boolean; chave?: string };

const sessionDrafts = new Map<string, OsDraft>();

export function osDraftKey(ctx: {
  farmId: string;
  seasonId: string;
  osSeasonId: string;
  osId: string;
  version: number;
  role: string;
}) {
  return [ctx.farmId, ctx.seasonId, ctx.osSeasonId, ctx.osId, String(ctx.version), ctx.role].join("|");
}

export function readOsDraft(key: string) {
  return sessionDrafts.get(key);
}

export function writeOsDraft(key: string, draft: OsDraft) {
  sessionDrafts.set(key, draft);
}

export function dropOsDraft(key: string) {
  sessionDrafts.delete(key);
}

export function invalidateOtherVersions(key: string) {
  const parts = key.split("|");
  if (parts.length !== 6) return;
  const version = parts[4];
  const head = `${parts.slice(0, 4).join("|")}|`;
  const tail = `|${parts[5]}`;
  for (const stored of [...sessionDrafts.keys()]) {
    const bits = stored.split("|");
    if (stored.startsWith(head) && stored.endsWith(tail) && bits[4] !== version) sessionDrafts.delete(stored);
  }
}

function blankDraft(): OsDraft {
  return { ha: "", hours: "2,4", reason: "", review: false };
}

export function confirmedProgressId(
  beforeIds: string[],
  beforeDoneHa: number,
  after: { id: string; osId: string; ha: number; sync: string }[],
  afterDoneHa: number | undefined,
  osId: string,
  ha: number,
): string | null {
  if (afterDoneHa === undefined || !Number.isFinite(ha) || !Number.isFinite(beforeDoneHa) || !Number.isFinite(afterDoneHa)) return null;
  const created = after.filter((a) => a.osId === osId && !beforeIds.includes(a.id));
  if (created.length !== 1) return null;
  const rec = created[0];
  if (!Number.isFinite(rec.ha) || rec.sync !== "sincronizado") return null;
  if (Math.abs(rec.ha - ha) > 1e-6) return null;
  if (Math.abs(afterDoneHa - (beforeDoneHa + ha)) > 1e-6) return null;
  return rec.id;
}

export function ambiguousDecimal(raw: string) {
  return /^\d+\.\d{3}$/.test(raw.trim());
}

export function parseDecimal(raw: string): number | null {
  const text = raw.trim();
  if (ambiguousDecimal(text) || !/^\d+(?:[.,]\d+)?$/.test(text)) return null;
  const value = Number(text.replace(",", "."));
  return Number.isFinite(value) ? value : null;
}

const DECIMAL_HELP = "Use 1,5 ou 1.5, sem separador de milhar.";
const AMBIGUOUS_HELP = "Valor ambíguo: use vírgula para decimais ou retire o ponto para milhar.";

export function WorkPanel({ os, onClose }: { os: WorkOrder; onClose: () => void }) {
  const farmId = useApp((s) => s.farmId);
  const seasonId = useApp((s) => s.seasonId);
  const role = useApp((s) => s.role);
  const draftKey = osDraftKey({
    farmId,
    seasonId,
    osSeasonId: os.seasonId,
    osId: os.id,
    version: os.version,
    role,
  });
  return <WorkPanelBody key={draftKey} os={os} onClose={onClose} draftKey={draftKey} />;
}

function WorkPanelBody({ os, onClose, draftKey }: { os: WorkOrder; onClose: () => void; draftKey: string }) {
  const s = useApp();
  const router = useRouter();
  const nxt = nextAction(os, s);
  const [reason, setReason] = useState(() => (readOsDraft(draftKey) ?? blankDraft()).reason);
  const [review, setReview] = useState(() => (readOsDraft(draftKey) ?? blankDraft()).review);
  const [ha, setHa] = useState(() => (readOsDraft(draftKey) ?? blankDraft()).ha);
  const [hours, setHours] = useState(() => (readOsDraft(draftKey) ?? blankDraft()).hours);
  const [haError, setHaError] = useState<string | null>(null);
  const [hoursError, setHoursError] = useState<string | null>(null);

  function remember(patch: Partial<OsDraft>) {
    const current = readOsDraft(draftKey) ?? blankDraft();
    writeOsDraft(draftKey, { ...current, ...patch });
  }
  const fila = classificarFila(s, os.id);
  const pendenteHa = fila.pendentes.reduce((sum, item) => sum + Number(item.payload.ha), 0);
  const saldo = saldoEfetivo(os.areaHa, os.doneHa, pendenteHa);
  const aps = s.apontamentos.filter((a) => a.osId === os.id);
  const cobrir = saldo <= 1e-6 && pendenteHa > 0;
  const passo = cobrir
    ? {
        tone: "warn" as const,
        cause: s.offline
          ? `Aguardando envio de ${formatArea(pendenteHa)} · sincronize quando houver sinal`
          : `Aguardando envio de ${formatArea(pendenteHa)} · sincronize`,
        owner: undefined,
        due: undefined,
        label: undefined,
        blocked: true,
        shortcut: undefined,
        shortcutHref: undefined,
      }
    : nxt;

  function run() {
    switch (nxt.cmd) {
      case "approve":
        setReview(true);
        remember({ review: true });
        return;
      case "release":
        s.releaseOrder(os.id);
        return;
      case "start":
        s.startOrder(os.id);
        return;
      case "deliver":
        s.deliverInputs(os.id);
        return;
      case "confirm":
        s.confirmReceipt(os.id);
        return;
      case "conference":
        s.sendToConference(os.id);
        return;
      case "close":
        s.closeOrder(os.id);
        return;
      case "window":
        s.setIrrigationWindow(os.id, "24/09 14:00–22:00");
        return;
      case "reprogram":
        s.reprogramOrder(os.id);
        return;
      case "record": {
        const submitted = parseDecimal(ha);
        const submittedHours = parseDecimal(hours);
        if (submitted === null || submitted <= 0 || submittedHours === null) {
          setHaError(submitted !== null && submitted > 0 ? null : ambiguousDecimal(ha) ? AMBIGUOUS_HELP : DECIMAL_HELP);
          setHoursError(submittedHours !== null ? null : ambiguousDecimal(hours) ? AMBIGUOUS_HELP : DECIMAL_HELP);
          return;
        }
        setHaError(null);
        setHoursError(null);
        const stored = readOsDraft(draftKey);
        const chave = stored?.chave ?? novaChaveApontamento(os.id);
        remember({ chave });
        const live = useApp.getState();
        live.recordProgress(os.id, submitted, submittedHours, chave);
        const after = useApp.getState();
        if (after.hydration !== "ready") return;
        if (decidirChave(after, os.id, chave, submitted, submittedHours).tipo === "repetida") {
          dropOsDraft(draftKey);
          setHa("");
          setHours("2,4");
          setHaError(null);
          setHoursError(null);
        }
        return;
      }
    }
  }

  return (
    <aside
      className="flex h-full w-full max-w-[460px] flex-col border-l border-line bg-surface shadow-panel"
      role="dialog"
      aria-label={osTitle(os)}
      data-os-id={os.id}
    >
      <header className="flex items-start justify-between gap-3 px-6 pt-6 pb-3">
        <div>
          <p className="font-display text-[19px] font-bold leading-tight">{osTitle(os)}</p>
          <p className="mt-1 text-[13px] font-semibold text-muted">
            {os.plotIds.join(" · ")} · {formatArea(os.areaHa)} · v{os.version}
          </p>
        </div>
        <Button variant="ghost" size="icon-sm" onClick={onClose} aria-label="Fechar">
          <X className="size-5" />
        </Button>
      </header>

      <div className="flex-1 overflow-y-auto px-6 pb-8">
        <ol className="mb-4 flex gap-1">
          {PHASES.map((p) => {
            const i = PHASES.findIndex((x) => x.id === os.phase);
            const pi = PHASES.findIndex((x) => x.id === p.id);
            const active = p.id === os.phase;
            return (
              <li key={p.id} className="flex-1">
                <div
                  className={
                    active
                      ? "h-1.5 rounded-full bg-primary"
                      : pi < i
                        ? "h-1.5 rounded-full bg-done"
                        : "h-1.5 rounded-full bg-line"
                  }
                />
                <p className={active ? "mt-1 text-[11px] font-extrabold" : "mt-1 text-[11px] font-semibold text-muted"}>
                  {p.label}
                </p>
              </li>
            );
          })}
        </ol>

        <div className="mb-3 flex flex-wrap gap-1.5">
          <Chip tone={phaseTone(os.phase)}>{phaseLabel(os.phase)}</Chip>
          {os.approved ? <Chip tone="sucesso">Aprovada pelo agrônomo</Chip> : os.awaitingAgronomist ? <Chip tone="atencao">Aguardando agrônomo</Chip> : null}
          {os.paused ? <Chip tone="atencao">Pausada</Chip> : null}
          {os.irrigation?.waterOnly ? <Chip tone="informacao">Liberada pela prontidão</Chip> : null}
          {os.irrigation?.estimated ? <Chip tone="neutro">Estimativa por ET</Chip> : null}
        </div>

        <Continuity
          from={os.origin}
          here={phaseLabel(os.phase)}
          missing={os.impediment?.cause ?? (saldo > 0 ? `Saldo ${formatArea(saldo)}` : "Nada")}
          next={passo.label ?? passo.cause}
        />

        <div className="mt-4">
          <NextStep
            tone={passo.tone}
            cause={passo.cause}
            owner={passo.owner}
            due={passo.due}
            actionLabel={passo.label}
            onAction={passo.label ? run : undefined}
            blocked={passo.blocked}
            shortcut={passo.shortcut}
            onShortcut={
              passo.shortcutHref
                ? () => {
                    router.history.push(passo.shortcutHref!);
                  }
                : undefined
            }
          />
        </div>

        {review && (
          <div className="mt-3 rounded-2xl border border-line p-3">
            <p className="text-[13px] font-bold">Revisar versão</p>
            <p className="mt-1 text-[12px] text-muted">Aprovar não libera. Rejeitar não cancela.</p>
            <Textarea
              className="mt-2"
              placeholder="Motivo obrigatório para devolver ou rejeitar"
              value={reason}
              onChange={(e) => {
                setReason(e.target.value);
                remember({ reason: e.target.value });
              }}
            />
            <div className="mt-2 flex flex-wrap gap-2">
              <Button size="sm" onClick={() => { s.approveVersion(os.id); setReview(false); }}>
                Aprovar versão
              </Button>
              <Button size="sm" variant="secondary" onClick={() => s.returnVersion(os.id, reason)}>
                Devolver para ajuste
              </Button>
              <Button size="sm" variant="danger-outline" onClick={() => s.rejectVersion(os.id, reason)}>
                Rejeitar
              </Button>
            </div>
          </div>
        )}

        {nxt.cmd === "record" && !cobrir && (
          <div className="mt-3 grid grid-cols-2 gap-2">
            <label className="text-[12px] font-semibold text-muted">
              Área feita (máx. {formatArea(saldo)})
              <Input
                className="mt-1"
                inputMode="decimal"
                value={ha}
                aria-invalid={haError ? true : undefined}
                aria-describedby={haError ? "os-ha-error os-decimal-help" : "os-decimal-help"}
                onChange={(e) => {
                  setHa(e.target.value);
                  setHaError(null);
                  remember({ ha: e.target.value });
                }}
                placeholder="ex.: 30"
              />
              {haError ? (
                <span id="os-ha-error" role="alert" className="mt-1 block font-semibold text-danger">
                  {haError}
                </span>
              ) : null}
            </label>
            <label className="text-[12px] font-semibold text-muted">
              Horas do turno
              <Input
                className="mt-1"
                inputMode="decimal"
                value={hours}
                aria-invalid={hoursError ? true : undefined}
                aria-describedby={hoursError ? "os-hours-error os-decimal-help" : "os-decimal-help"}
                onChange={(e) => {
                  setHours(e.target.value);
                  setHoursError(null);
                  remember({ hours: e.target.value });
                }}
              />
              {hoursError ? (
                <span id="os-hours-error" role="alert" className="mt-1 block font-semibold text-danger">
                  {hoursError}
                </span>
              ) : null}
            </label>
            <p id="os-decimal-help" className="col-span-2 text-[12px] font-semibold text-muted">
              {DECIMAL_HELP}
            </p>
          </div>
        )}

        <Block title="Atividade">
          <Row k="Operação" v={os.operation} />
          <Row k="Gatilho" v={os.trigger} />
          <Row k="Conjunto" v={os.machineIds.map((id) => MACHINES.find((m) => m.id === id)?.name).join(" · ")} />
          <Row k="Pessoas" v={os.peopleIds.map((id) => PEOPLE.find((p) => p.id === id)?.name).join(" · ")} />
          <Row k="Horas previstas" v={`${os.hoursPlanned.toString().replace(".", ",")} h`} />
          <Row k="Janela" v={os.window} />
        </Block>

        {os.inputs.length > 0 && (
          <Block title="Insumos e doses">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="text-left text-[11px] font-bold uppercase tracking-[0.06em] text-muted">
                  <th className="py-1">Produto</th>
                  <th className="py-1 text-right">Dose</th>
                  <th className="py-1 text-right">Ordem</th>
                  <th className="py-1 text-right">Usado</th>
                  <th className="py-1">Situação</th>
                </tr>
              </thead>
              <tbody>
                {os.inputs.map((i) => {
                  const p = PRODUCTS.find((x) => x.id === i.productId);
                  const sit =
                    i.qtyCustody > 0
                      ? `Em custódia · ${formatQty(i.qtyCustody, i.unit)}`
                      : i.qtyDelivered > 0
                        ? "Entregue"
                        : i.qtyReserved > 0
                          ? "Reservado"
                          : "Sem reserva";
                  return (
                    <tr key={i.productId} className="border-t border-line">
                      <td className="py-1.5 font-semibold">{p?.name}</td>
                      <td className="py-1.5 text-right tabular">{formatQty(i.dosePerHa, `${i.unit}/ha`)}</td>
                      <td className="py-1.5 text-right tabular">{formatQty(i.qtyOrder, i.unit)}</td>
                      <td className="py-1.5 text-right tabular">{formatQty(i.qtyUsed, i.unit)}</td>
                      <td className="py-1.5">{sit}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {os.loads && (
              <p className="mt-2 text-[12px] font-semibold text-muted">
                Cargas {os.loads.map((l) => `${l.ha} ha · ${l.productL} L`).join(" → ")} · tanque {os.tankL} L · {os.flowLha} L/ha
              </p>
            )}
          </Block>
        )}

        {os.irrigation && (
          <Block title="Irrigação">
            <Row k="Modalidade" v={os.irrigation.waterOnly ? "Água sem produto" : "Fertirrigação"} />
            <Row k="Lâmina" v={`${os.irrigation.laminaMm.toString().replace(".", ",")} mm`} />
            <Row k="Passadas" v={`${os.irrigation.passadas} × ${os.irrigation.mmPerPass.toString().replace(".", ",")} mm`} />
            {os.irrigation.estimated ? <Row k="Fonte" v="Estimativa por ET · sem sonda" /> : <Row k="Fonte" v="Balanço hídrico do setor" />}
          </Block>
        )}

        <Block title="Apontamentos">
          {aps.length === 0 && fila.pendentes.length === 0 && fila.retidos.length === 0 ? (
            <p className="text-[13px] text-muted">Nenhum apontamento neste aparelho.</p>
          ) : (
            <ul className="space-y-1.5">
              {aps.map((a) => (
                <li key={a.id} data-sync={a.sync} className="flex items-center justify-between text-[13px]">
                  <span>
                    {a.date.slice(8, 10)}/{a.date.slice(5, 7)} · {formatArea(a.ha)} · {a.hours.toString().replace(".", ",")} h · {a.author}
                  </span>
                  <Chip tone={a.sync === "sincronizado" ? "sucesso" : "atencao"}>
                    {a.sync === "sincronizado" ? "Sincronizado" : "Aguardando envio"}
                  </Chip>
                </li>
              ))}
              {fila.pendentes.map((item) => {
                const quando = dataDoItem(item);
                return (
                <li key={item.id} data-sync="aguardando-envio" className="flex items-center justify-between text-[13px]">
                  <span>
                    {quando.slice(8, 10)}/{quando.slice(5, 7)} · {formatArea(Number(item.payload.ha))} · {String(item.payload.hours).replace(".", ",")} h
                  </span>
                  <Chip tone="atencao">Aguardando envio</Chip>
                </li>
                );
              })}
              {fila.retidos.map(({ item, motivo }) => {
                const quando = dataDoItem(item);
                return (
                <li key={item.id} data-sync="retido" className="flex items-center justify-between gap-2 text-[13px]">
                  <span>
                    {quando.slice(8, 10)}/{quando.slice(5, 7)} · {formatArea(Number(item.payload.ha))} · {String(item.payload.hours).replace(".", ",")} h
                  </span>
                  <Chip tone="atencao">Retido · {motivo}</Chip>
                </li>
                );
              })}
            </ul>
          )}
          <p className="mt-2 text-[13px] font-bold tabular">
            Realizado {formatArea(os.doneHa)} · aguardando envio {formatArea(pendenteHa)} · saldo {formatArea(saldo <= 1e-6 ? 0 : saldo)}
          </p>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-subtle">
            <div
              className="h-full bg-primary"
              style={{ width: `${Math.min(100, (os.doneHa / Math.max(os.areaHa, 0.01)) * 100)}%` }}
            />
          </div>
        </Block>

        <Block title="Situação e origem">
          <Row k="Origem" v={`${os.origin} · ${os.originId}`} />
          <Row k="Talhões" v={os.plotIds.map((id) => `${id} · ${PLOTS.find((p) => p.id === id)?.culture}`).join(", ")} />
          <Row k="Safra" v={os.seasonId === "2627" ? "2026/27" : "2025/26"} />
          {os.machineIds.map((id) => {
            const m = MACHINES.find((x) => x.id === id);
            if (!m) return null;
            const conflict =
              (os.id === "OS-0424" || os.id === "OS-0421") && id === "pj"
                ? "Conflito 24/09 06:00–11:00 com a outra pulverização"
                : m.condition === "bloqueado"
                  ? `Bloqueado · ${m.omId}`
                  : "Sem conflito";
            return <Row key={id} k={m.name} v={`${m.condition} · ${conflict}`} />;
          })}
        </Block>

        <div className="mt-3 flex flex-wrap gap-2">
          <Tag>Fazenda Santa Rita</Tag>
          <Tag>{os.operation}</Tag>
          {os.paused ? <Tag>Pausa não vence a reserva</Tag> : null}
        </div>
      </div>
    </aside>
  );
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-4 rounded-2xl border border-line p-3">
      <h3 className="mb-2 text-[15px] font-bold">{title}</h3>
      {children}
    </section>
  );
}
function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-3 py-0.5 text-[13px]">
      <span className="text-muted">{k}</span>
      <span className="max-w-[60%] text-right font-semibold">{v}</span>
    </div>
  );
}
