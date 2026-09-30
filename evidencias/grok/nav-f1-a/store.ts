import { create } from "zustand";
import {
  FARMS,
  LOTS,
  MACHINES,
  ORDERS,
  PEOPLE,
  PRODUCTS,
  PURCHASES,
  PLOTS,
  SEASONS,
  YIELDS,
} from "./seed";
import { AUDIT_SEED, DOCS, HARVEST_SEED, currentStep } from "./ledger";
import { formatNumber } from "./format";
import type {
  Apontamento,
  AuditEntry,
  CountAdjust,
  FeedbackDraft,
  HarvestStock,
  Lot,
  Machine,
  OfflineItem,
  OpDoc,
  OsPhase,
  Person,
  Plot,
  Purchase,
  Role,
  ToastMsg,
  WorkOrder,
  YieldRow,
} from "./types";

const KEY = "safrion-demo-v2";
type HydrationPhase = AppState["hydration"];
const PERSISTED_KEYS = [
  "role",
  "farmId",
  "seasonId",
  "offline",
  "orders",
  "lots",
  "machines",
  "people",
  "purchases",
  "yields",
  "apontamentos",
  "parcels",
  "queue",
  "counts",
  "receiptsConfirmed",
  "feedback",
  "selectedOsId",
  "docs",
  "audit",
  "harvest",
] as const;
let hydrationPhase: HydrationPhase = "initial";
let hydrationRead = false;
let persistLock = false;
let lastSaved: AppState | null = null;
let lastPayload: string | null = null;

function isPlain(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringArray(value: unknown) {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function objectArray(value: unknown) {
  return Array.isArray(value) && value.every(isPlain);
}

function finiteNumber(value: unknown) {
  return typeof value === "number" && Number.isFinite(value);
}

function orderRenderable(value: unknown) {
  if (!isPlain(value)) return false;
  return (
    typeof value.id === "string" &&
    typeof value.farmId === "string" &&
    typeof value.seasonId === "string" &&
    typeof value.phase === "string" &&
    typeof value.operation === "string" &&
    typeof value.window === "string" &&
    typeof value.origin === "string" &&
    typeof value.version === "number" &&
    finiteNumber(value.areaHa) &&
    finiteNumber(value.doneHa) &&
    finiteNumber(value.hoursPlanned) &&
    stringArray(value.plotIds) &&
    stringArray(value.machineIds) &&
    stringArray(value.peopleIds) &&
    objectArray(value.inputs)
  );
}

function savedIsUsable(value: unknown): value is Partial<AppState> {
  if (!isPlain(value)) return false;
  if (!Object.keys(value).every((key) => PERSISTED_KEYS.includes(key as (typeof PERSISTED_KEYS)[number]))) return false;
  if ("role" in value && typeof value.role !== "string") return false;
  if ("farmId" in value && typeof value.farmId !== "string") return false;
  if ("seasonId" in value && typeof value.seasonId !== "string") return false;
  if ("offline" in value && typeof value.offline !== "boolean") return false;
  if ("selectedOsId" in value && typeof value.selectedOsId !== "string") return false;
  if ("orders" in value && !(Array.isArray(value.orders) && value.orders.every(orderRenderable))) return false;
  if ("receiptsConfirmed" in value && !stringArray(value.receiptsConfirmed)) return false;
  for (const key of ["lots", "machines", "people", "purchases", "yields", "apontamentos", "parcels", "queue", "counts", "docs", "audit"] as const) {
    if (key in value && !objectArray(value[key])) return false;
  }
  if ("feedback" in value && !isPlain(value.feedback)) return false;
  if ("harvest" in value && !isPlain(value.harvest)) return false;
  return true;
}

function pickSaved(value: Partial<AppState>): Partial<AppState> {
  const picked: Partial<AppState> = {};
  for (const key of PERSISTED_KEYS) {
    if (key in value) (picked as Record<string, unknown>)[key] = value[key];
  }
  return picked;
}

export function persistedPayload(state: AppState) {
  const bag: Record<string, unknown> = {};
  for (const key of PERSISTED_KEYS) bag[key] = state[key];
  return JSON.stringify(bag);
}

function persistable(state: AppState): AppState {
  return { ...JSON.parse(persistedPayload(state)), toasts: [], helpOpen: false, journeysOpen: false, hydration: "ready", hydrationNotice: null };
}

function rememberSaved(state: AppState) {
  lastPayload = persistedPayload(state);
  lastSaved = persistable(state);
}

function persist(partial: AppState) {
  if (typeof window === "undefined") return;
  if (hydrationPhase !== "ready" || persistLock) return;
  const text = persistedPayload(partial);
  if (text === lastPayload) return;
  persistLock = true;
  try {
    localStorage.setItem(KEY, text);
    lastPayload = text;
    lastSaved = persistable(partial);
  } catch {
    hydrationPhase = "error";
    const notice = "Não gravado neste aparelho. A alteração não foi salva.";
    const back = lastSaved ?? persistable(partial);
    useApp.setState({
      ...back,
      hydration: "error",
      hydrationNotice: notice,
      toasts: [{ id: `t-${toastSeq++}`, tone: "alert", text: notice }],
    });
  } finally {
    persistLock = false;
  }
}

export interface ParcelDraft {
  id: string;
  plotId: string;
  name: string;
  areaHa: number;
}

export interface AppState {
  role: Role;
  farmId: string;
  seasonId: string;
  offline: boolean;
  orders: WorkOrder[];
  lots: Lot[];
  machines: Machine[];
  people: Person[];
  purchases: Purchase[];
  yields: YieldRow[];
  apontamentos: Apontamento[];
  parcels: ParcelDraft[];
  toasts: ToastMsg[];
  queue: OfflineItem[];
  counts: CountAdjust[];
  receiptsConfirmed: string[];
  helpOpen: boolean;
  journeysOpen: boolean;
  hydration: "initial" | "ready" | "error";
  hydrationNotice: string | null;
  feedback: FeedbackDraft;
  selectedOsId?: string;
  docs: OpDoc[];
  audit: AuditEntry[];
  harvest: HarvestStock;
}

function clone<T>(v: T): T {
  return structuredClone(v);
}

export function seedState(): AppState {
  return {
    role: "gerente",
    farmId: "sr",
    seasonId: "2627",
    offline: false,
    orders: clone(ORDERS),
    lots: clone(LOTS),
    machines: clone(MACHINES),
    people: clone(PEOPLE),
    purchases: clone(PURCHASES),
    yields: clone(YIELDS),
    apontamentos: [
      {
        id: "AP-0420-1",
        osId: "OS-0420",
        date: "2026-09-22",
        ha: 30,
        hours: 2.4,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: "ap-0420-d1",
        conference: "conferido",
      },
    ],
    parcels: [],
    toasts: [],
    queue: [],
    counts: [],
    receiptsConfirmed: [],
    helpOpen: false,
    journeysOpen: false,
    hydration: "initial",
    hydrationNotice: null,
    feedback: { comment: "" },
    selectedOsId: undefined,
    docs: clone(DOCS),
    audit: clone(AUDIT_SEED),
    harvest: clone(HARVEST_SEED),
  };
}

export function loadPersisted(): Partial<AppState> | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    return JSON.parse(raw) as Partial<AppState>;
  } catch {
    return null;
  }
}

export function custodyLeft(os: WorkOrder) {
  return os.inputs.reduce((sum, i) => sum + i.qtyCustody, 0);
}

export function readiness(os: WorkOrder, s: AppState): { ok: boolean; reason?: string } {
  if (!os.approved && !os.irrigation?.waterOnly) {
    return { ok: false, reason: "Aguardando agrônomo · aprovação da versão" };
  }
  if (os.irrigation?.waterOnly && os.window.toLowerCase().includes("definir")) {
    return { ok: false, reason: "Janela a definir" };
  }
  for (const mid of os.machineIds) {
    const m = s.machines.find((x) => x.id === mid);
    if (m?.condition === "bloqueado") {
      return { ok: false, reason: `Falta máquina · ${m.name} bloqueado` };
    }
  }
  for (const iid of os.peopleIds) {
    const p = s.people.find((x) => x.id === iid);
    if (p && !p.allocatable) {
      return { ok: false, reason: `${p.name} não alocável em O.S.` };
    }
  }
  for (const inp of os.inputs) {
    const available = s.lots
      .filter((l) => l.productId === inp.productId && l.status === "apto" && l.farmId === os.farmId)
      .reduce((sum, l) => sum + l.qty, 0);
    if (available + inp.qtyReserved < inp.qtyOrder - 0.001) {
      return { ok: false, reason: `Falta material · ${inp.productId}` };
    }
  }
  return { ok: true };
}

function peopleName(role: Role) {
  const map: Record<Role, string> = {
    gerente: "Carlos Ribeiro",
    agronomo: "Helena Costa",
    pcp: "Ricardo Alves",
    operador: "Marcos Pereira",
    almoxarife: "João Mendes",
    mecanico: "Ana Souza",
    irrigante: "Pedro Lima",
    comprador: "Lívia Prado",
    colheita: "Rafael Nunes",
    comercial: "Clara Vasconcelos",
    financeiro: "Otávio Pires",
    admin: "Admin da fazenda",
    parceiro: "Marta · AgroBrasil",
  };
  return map[role];
}

export function novaChaveApontamento(osId: string) {
  const cryptoObj = globalThis.crypto;
  let id: string;
  if (typeof cryptoObj?.randomUUID === "function") id = cryptoObj.randomUUID();
  else {
    const bytes = new Uint8Array(8);
    cryptoObj.getRandomValues(bytes);
    id = [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("");
  }
  return `ap-${osId}-k${id}`;
}

function queueOsId(item: OfflineItem) {
  return typeof item.payload.osId === "string" ? item.payload.osId : "";
}

function queueNumber(item: OfflineItem, key: "ha" | "hours") {
  const value = item.payload[key];
  return typeof value === "number" ? value : Number(value);
}

function mesmaMedida(a: number, b: number) {
  return Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= 1e-6;
}

export function saldoEfetivo(areaHa: number, doneHa: number, pendenteHa: number) {
  const raw = areaHa - doneHa - pendenteHa;
  return Math.abs(raw) <= 1e-6 ? 0 : raw;
}

export function classificarFila(estado: AppState, osId: string) {
  const os = estado.orders.find((order) => order.id === osId);
  let done = os?.doneHa ?? 0;
  const area = os?.areaHa ?? 0;
  const byId = new Set(estado.apontamentos.map((item) => item.id));
  const keyOwner = new Map(estado.apontamentos.map((item) => [item.intentionKey, item.id]));
  const pendentes: OfflineItem[] = [];
  const retidos: { item: OfflineItem; motivo: string }[] = [];
  const jaAplicados: OfflineItem[] = [];
  for (const item of estado.queue) {
    if (item.kind !== "apontamento" || queueOsId(item) !== osId) continue;
    if (byId.has(item.id)) {
      jaAplicados.push(item);
      continue;
    }
    const owner = keyOwner.get(item.intentionKey);
    if (owner && owner !== item.id) {
      retidos.push({ item, motivo: "chave já aplicada" });
      continue;
    }
    const ha = queueNumber(item, "ha");
    const hours = queueNumber(item, "hours");
    if (!os || !Number.isFinite(ha) || ha <= 0 || !Number.isFinite(hours) || hours < 0) {
      retidos.push({ item, motivo: !os ? "O.S. ausente" : "valor inválido" });
      continue;
    }
    if (ha > area - done + 1e-6) {
      retidos.push({ item, motivo: "saldo físico insuficiente" });
      continue;
    }
    pendentes.push(item);
    done += ha;
    byId.add(item.id);
    keyOwner.set(item.intentionKey, item.id);
  }
  return { pendentes, retidos, jaAplicados };
}

export type DecisaoChave =
  | { tipo: "nova" }
  | { tipo: "repetida"; via: "apontamento" | "pendente"; id: string }
  | { tipo: "retido"; motivo: string; id: string }
  | { tipo: "conflito" };

export function decidirChave(estado: AppState, osId: string, chave: string, ha: number, hours: number): DecisaoChave {
  const registros: { osId: string; ha: number; hours: number; origem: "apontamento" | "fila"; id: string }[] = [];
  for (const item of estado.apontamentos) {
    if (item.intentionKey !== chave) continue;
    registros.push({ osId: item.osId, ha: item.ha, hours: item.hours, origem: "apontamento", id: item.id });
  }
  for (const item of estado.queue) {
    if (item.kind !== "apontamento" || item.intentionKey !== chave) continue;
    registros.push({
      osId: queueOsId(item),
      ha: queueNumber(item, "ha"),
      hours: queueNumber(item, "hours"),
      origem: "fila",
      id: item.id,
    });
  }
  if (registros.length === 0) return { tipo: "nova" };
  const difere = (item: (typeof registros)[number]) => item.osId !== osId || !mesmaMedida(item.ha, ha) || !mesmaMedida(item.hours, hours);
  if (registros.some(difere)) return { tipo: "conflito" };
  const aplicado = registros.find((item) => item.origem === "apontamento");
  if (aplicado) return { tipo: "repetida", via: "apontamento", id: aplicado.id };
  const fila = classificarFila(estado, osId);
  const pendente = fila.pendentes.find((item) => item.intentionKey === chave);
  if (pendente) return { tipo: "repetida", via: "pendente", id: pendente.id };
  const retido = fila.retidos.find((item) => item.item.intentionKey === chave);
  if (retido) return { tipo: "retido", motivo: retido.motivo, id: retido.item.id };
  const ja = fila.jaAplicados.find((item) => item.intentionKey === chave);
  if (ja) return { tipo: "repetida", via: "apontamento", id: ja.id };
  return { tipo: "conflito" };
}

function avisoFila(estado: AppState, osId: string) {
  const fila = classificarFila(estado, osId);
  const parts: string[] = [];
  if (fila.pendentes.length > 0) parts.push(`${fila.pendentes.length} aguardando envio · sincronize quando houver sinal`);
  if (fila.retidos.length > 0) parts.push(`${fila.retidos.length} retidos · veja o motivo; a conferência fica presa até restaurar a demonstração`);
  return parts.join(" · ");
}

export function dataDoItem(item: OfflineItem) {
  if (item.date) return item.date;
  if (typeof item.payload.date === "string" && item.payload.date) return item.payload.date;
  if (item.createdAt) return item.createdAt.slice(0, 10);
  return "2026-09-24";
}

function autorDoItem(item: OfflineItem, role: Role) {
  if (item.author) return item.author;
  if (typeof item.payload.author === "string" && item.payload.author) return item.payload.author;
  return peopleName(role);
}

let toastSeq = 1;

export const useApp = create<AppState & Actions>()((set, get) => ({
  ...seedState(),

  hydrate: () => {
    if (typeof window === "undefined") return;
    if (hydrationPhase === "ready" || hydrationPhase === "error" || hydrationRead) return;
    hydrationRead = true;
    let raw: string | null;
    try {
      raw = localStorage.getItem(KEY);
    } catch {
      hydrationPhase = "error";
      set({
        hydration: "error",
        hydrationNotice: "Não foi possível ler os dados salvos. Nada foi substituído.",
      });
      return;
    }
    if (raw === null) {
      set({ hydration: "ready", hydrationNotice: null });
      rememberSaved(get());
      hydrationPhase = "ready";
      return;
    }
    try {
      const parsed: unknown = JSON.parse(raw);
      if (!savedIsUsable(parsed)) throw new Error("formato");
      const saved = pickSaved(parsed);
      const base = seedState();
      set({
        ...base,
        ...saved,
        docs: saved.docs?.length ? saved.docs : base.docs,
        audit: saved.audit?.length ? saved.audit : base.audit,
        harvest: saved.harvest ?? base.harvest,
        toasts: [],
        helpOpen: false,
        journeysOpen: false,
        hydration: "ready",
        hydrationNotice: null,
      });
      rememberSaved(get());
      hydrationPhase = "ready";
    } catch {
      hydrationPhase = "error";
      set({
        hydration: "error",
        hydrationNotice: "Leitura inválida. O texto salvo foi mantido.",
      });
    }
  },

  retryHydration: () => {
    if (typeof window === "undefined") return;
    if (hydrationPhase !== "error") return;
    hydrationPhase = "initial";
    hydrationRead = false;
    set({ hydration: "initial", hydrationNotice: null });
    get().hydrate();
  },

  setRole: (role) => set({ role }),
  setFarm: (farmId) => set({ farmId, selectedOsId: undefined }),
  setSeason: (seasonId) => set({ seasonId, selectedOsId: undefined }),
  setOffline: (offline) => set({ offline }),
  selectOs: (selectedOsId) => {
    if (get().selectedOsId === selectedOsId) return;
    set({ selectedOsId });
  },
  setHelpOpen: (helpOpen) => set({ helpOpen }),
  setJourneysOpen: (journeysOpen) => set({ journeysOpen }),
  setFeedback: (f) => set((s) => ({ feedback: { ...s.feedback, ...f } })),

  toast: (text, tone = "status") =>
    set((s) => ({ toasts: [...s.toasts, { id: `t-${toastSeq++}`, tone, text }] })),
  dismissToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),

  restore: () => {
    if (typeof window !== "undefined") localStorage.removeItem(KEY);
    hydrationPhase = "ready";
    hydrationRead = true;
    set({ ...seedState(), hydration: "ready", hydrationNotice: null });
    rememberSaved(get());
    get().toast("Demonstração restaurada · alterações simuladas apagadas");
  },

  approveVersion: (osId) => {
    const s = get();
    if (s.role !== "agronomo" && s.role !== "gerente") {
      get().toast("Aprovar versão · bloqueado · competência do agrônomo", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) =>
        o.id === osId
          ? { ...o, approved: true, awaitingAgronomist: false, returnedReason: undefined }
          : o,
      ),
    }));
    get().toast(`Versão aprovada · ${osId} · liberação continua com o PCP`);
  },

  returnVersion: (osId, reason) => {
    if (!reason.trim()) {
      get().toast("Devolver para ajuste · informe o motivo", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) =>
        o.id === osId
          ? { ...o, approved: false, awaitingAgronomist: false, returnedReason: reason, phase: "a-liberar" as OsPhase }
          : o,
      ),
    }));
    get().toast(`${osId} · Devolvida para ajuste`);
  },

  rejectVersion: (osId, reason) => {
    if (!reason.trim()) {
      get().toast("Rejeitar · informe o motivo", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) =>
        o.id === osId ? { ...o, approved: false, awaitingAgronomist: false, returnedReason: `Rejeitada · ${reason}` } : o,
      ),
    }));
    get().toast(`${osId} rejeitada · a ordem não foi cancelada`);
  },

  setIrrigationWindow: (osId, window) => {
    set((st) => ({
      orders: st.orders.map((o) =>
        o.id === osId
          ? {
              ...o,
              window,
              impediment: undefined,
              phase: o.irrigation?.waterOnly ? ("liberadas" as OsPhase) : o.phase,
            }
          : o,
      ),
    }));
    get().toast(`${osId} · janela ${window} · liberada pela prontidão`);
  },

  releaseOrder: (osId) => {
    const s = get();
    if (s.role !== "pcp" && s.role !== "gerente") {
      get().toast("Liberar · bloqueado · competência do PCP", "alert");
      return;
    }
    const os = s.orders.find((o) => o.id === osId);
    if (!os || os.phase !== "a-liberar") {
      get().toast("Liberar · a ordem não está A liberar", "alert");
      return;
    }
    const r = readiness(os, s);
    if (!r.ok) {
      get().toast(`Liberar · bloqueado · ${r.reason}`, "alert");
      return;
    }
    set((st) => {
      const lots = st.lots.map((l) => ({ ...l }));
      const orders = st.orders.map((o) => {
        if (o.id !== osId) return o;
        const inputs = o.inputs.map((inp) => {
          let need = inp.qtyOrder - inp.qtyReserved;
          let next = { ...inp };
          for (const lot of lots) {
            if (need <= 0) break;
            if (lot.productId !== inp.productId || lot.status !== "apto" || lot.farmId !== o.farmId) continue;
            const take = Math.min(lot.qty, need);
            lot.qty -= take;
            need -= take;
            next = { ...next, qtyReserved: next.qtyReserved + take, lotId: lot.id };
          }
          return next;
        });
        return { ...o, phase: "liberadas" as OsPhase, inputs, impediment: undefined };
      });
      return { lots, orders };
    });
    get().toast(`Liberar ${osId} · a requisição reserva os insumos da versão`);
  },

  reprogramOrder: (osId) => {
    const s = get();
    if (s.role !== "pcp" && s.role !== "gerente") {
      get().toast("Separar a janela · bloqueado · competência do PCP", "alert");
      return;
    }
    const os = s.orders.find((o) => o.id === osId);
    if (!os?.impediment?.cause.includes("Conflito")) {
      get().toast("Não há conflito de janela nesta ordem", "alert");
      return;
    }
    const afternoon = os.irrigation ? "24/09 18:00–22:00" : "24/09 13:00–18:00";
    set((st) => ({
      orders: st.orders.map((o) =>
        o.id === osId
          ? { ...o, window: afternoon, impediment: undefined, nextDue: afternoon.slice(0, 11), nextOwner: "Ricardo Alves" }
          : o,
      ),
    }));
    get().toast(`${osId} · janela ${afternoon} · o conflito saiu da agenda`);
  },

  startOrder: (osId) => {
    const s = get();
    const os = s.orders.find((o) => o.id === osId);
    if (!os || os.phase !== "liberadas") {
      get().toast("Iniciar · a ordem não está Liberada", "alert");
      return;
    }
    const r = readiness(os, s);
    if (!r.ok) {
      get().toast(`Iniciar · bloqueado · ${r.reason}`, "alert");
      return;
    }
    const needsDelivery = os.inputs.some((i) => i.qtyOrder > 0 && i.qtyDelivered <= 0);
    if (needsDelivery) {
      get().toast("Iniciar · bloqueado · falta entrega do almoxarifado", "alert");
      return;
    }
    const needsConfirm = os.inputs.some((i) => i.qtyDelivered > 0) && !s.receiptsConfirmed.includes(osId);
    if (needsConfirm) {
      get().toast("Iniciar · bloqueado · caldeiro ainda não confirmou a retirada", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) => (o.id === osId ? { ...o, phase: "em-execucao" as OsPhase, paused: false } : o)),
    }));
    get().toast(`${osId} · em execução`);
  },

  pauseOrder: (osId) => {
    set((st) => ({ orders: st.orders.map((o) => (o.id === osId ? { ...o, paused: true } : o)) }));
    get().toast(`${osId} pausada · a reserva permanece`);
  },

  recordProgress: (osId, ha, hours, chave) => {
    const s = get();
    if (s.hydration !== "ready") {
      get().toast("Não gravado neste aparelho · recupere a gravação antes de registrar", "alert");
      return;
    }
    const key = chave || novaChaveApontamento(osId);
    const decisao = decidirChave(s, osId, key, ha, hours);
    if (decisao.tipo === "conflito") {
      get().toast("Conflito · esta chave já tem outros valores · nada foi gravado", "alert");
      return;
    }
    if (decisao.tipo === "repetida") {
      get().toast(decisao.via === "apontamento" ? "Mesma intenção · já registrada" : "Mesma intenção · já aguardando envio");
      return;
    }
    if (decisao.tipo === "retido") {
      get().toast(`Já na fila, retido · ${decisao.motivo}`, "alert");
      return;
    }
    if (!Number.isFinite(ha) || ha <= 0 || !Number.isFinite(hours) || hours < 0) {
      get().toast("Informe a área feita, maior que zero", "alert");
      return;
    }
    const os = s.orders.find((order) => order.id === osId);
    if (!os) return;
    const pendenteHa = classificarFila(s, osId).pendentes.reduce((sum, item) => sum + queueNumber(item, "ha"), 0);
    const saldo = saldoEfetivo(os.areaHa, os.doneHa, pendenteHa);
    if (ha > saldo + 1e-6) {
      const saldoTxt = formatNumber(saldo);
      const extra = pendenteHa > 1e-6 ? ` · aguardando envio ${formatNumber(pendenteHa)} ha` : "";
      get().toast(`Registrar · recusado · saldo efetivo ${saldoTxt} ha${extra}`, "alert");
      return;
    }
    const author = peopleName(s.role);
    const date = "2026-09-24";
    const item: Apontamento = {
      id: `AP-${key}`,
      osId,
      date,
      ha,
      hours,
      author,
      sync: s.offline ? "aguardando-envio" : "sincronizado",
      intentionKey: key,
      conference: "pendente",
    };
    if (s.offline) {
      set((st) => ({
        queue: [
          ...st.queue,
          {
            id: item.id,
            kind: "apontamento",
            payload: { osId, ha, hours, key },
            intentionKey: key,
            createdAt: new Date().toISOString(),
            state: "aguardando-envio",
            author,
            date,
          },
        ],
      }));
      if (get().hydration !== "ready") return;
      get().toast("Salvo neste aparelho · aguardando envio");
      return;
    }
    applyProgress(osId, ha, item);
    if (get().hydration !== "ready") return;
    get().toast(`Apontamento ${ha.toFixed(2).replace(".", ",")} ha · sincronizado`);
  },

  sendToConference: (osId) => {
    const os = get().orders.find((o) => o.id === osId);
    if (!os) return;
    const fila = avisoFila(get(), osId);
    if (fila) {
      get().toast(fila, "alert");
      return;
    }
    if (os.doneHa + 1e-6 < os.areaHa) {
      get().toast("Concluir execução · ainda há saldo. Destine o saldo ou registre o restante.", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) => (o.id === osId ? { ...o, phase: "em-conferencia" as OsPhase, paused: false } : o)),
    }));
    get().toast(`${osId} · em conferência`);
  },

  closeOrder: (osId) => {
    const s = get();
    const os = s.orders.find((o) => o.id === osId);
    if (!os) return;
    const fila = avisoFila(s, osId);
    if (fila) {
      get().toast(fila, "alert");
      return;
    }
    const left = custodyLeft(os);
    if (left > 1e-6) {
      get().toast(`Encerrar · bloqueado · ainda em custódia · almoxarife recebe a devolução`, "alert");
      return;
    }
    if (s.apontamentos.some((a) => a.osId === osId && a.sync !== "sincronizado")) {
      get().toast("Encerrar · bloqueado · apontamento ainda no aparelho", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) => (o.id === osId ? { ...o, phase: "encerradas" as OsPhase, impediment: undefined } : o)),
    }));
    get().toast(`${osId} encerrada · integração ERP segue depois, sem mudar a etapa`);
  },

  deliverInputs: (osId) => {
    const s = get();
    if (s.role !== "almoxarife" && s.role !== "gerente") {
      get().toast("Entregar · bloqueado · competência do almoxarife", "alert");
      return;
    }
    set((st) => ({
      orders: st.orders.map((o) =>
        o.id === osId
          ? {
              ...o,
              inputs: o.inputs.map((i) => ({
                ...i,
                qtyDelivered: i.qtyReserved,
                qtyCustody: i.qtyReserved,
              })),
            }
          : o,
      ),
    }));
    get().toast(`${osId} · entregue ao campo · aguarda confirmação do caldeiro`);
  },

  confirmReceipt: (osId) => {
    if (get().receiptsConfirmed.includes(osId)) {
      get().toast("Recebimento já confirmado · mesmo recibo");
      return;
    }
    set((st) => ({ receiptsConfirmed: [...st.receiptsConfirmed, osId] }));
    get().toast(`${osId} · retirada confirmada · custódia inalterada`);
  },

  declareReturn: () => {
    get().toast("Devolução declarada · não aumenta o disponível até a conferência");
  },

  receiveReturn: (osId, productId, qty, apt) => {
    set((st) => {
      const orders = st.orders.map((o) => {
        if (o.id !== osId) return o;
        return {
          ...o,
          inputs: o.inputs.map((i) =>
            i.productId === productId ? { ...i, qtyCustody: Math.max(0, i.qtyCustody - qty) } : i,
          ),
        };
      });
      const lots = st.lots.map((l) => {
        if (!apt) return l;
        const os = orders.find((o) => o.id === osId);
        const inp = os?.inputs.find((i) => i.productId === productId);
        if (inp?.lotId === l.id) return { ...l, qty: l.qty + qty, status: "apto" as const };
        return l;
      });
      return { orders, lots };
    });
    get().toast(apt ? "Devolvido ao disponível" : "Recebido bloqueado · vai para inspeção");
  },

  receivePurchase: (purchaseId, apt, quarantine) => {
    set((st) => ({
      purchases: st.purchases.map((p) => {
        if (p.id !== purchaseId) return p;
        const pending = Math.max(0, p.pending - apt - quarantine);
        return {
          ...p,
          receivedApt: p.receivedApt + apt,
          receivedQuarantine: p.receivedQuarantine + quarantine,
          pending,
          status: pending === 0 ? ("entregue" as const) : ("parcial" as const),
        };
      }),
    }));
    get().toast("Recebimento conferido · apto e quarentena separados");
  },

  releaseQuarantine: (lotId) => {
    set((st) => ({
      lots: st.lots.map((l) => (l.id === lotId ? { ...l, status: "apto" as const } : l)),
    }));
    get().toast("Liberação de qualidade · soma ao apto uma vez");
  },

  blockMachine: (machineId, omId) => {
    set((st) => {
      const machines = st.machines.map((m) =>
        m.id === machineId ? { ...m, condition: "bloqueado" as const, omId } : m,
      );
      const orders = st.orders.map((o) => {
        if (o.phase === "liberadas" && o.machineIds.includes(machineId) && o.doneHa === 0) {
          return {
            ...o,
            phase: "a-liberar" as OsPhase,
            impediment: {
              cause: `Falta máquina · ativo bloqueado (${omId})`,
              owner: "PCM · Ana Souza",
              due: "25/09 12:00",
              href: "/cadastros/maquinas",
            },
          };
        }
        return o;
      });
      return { machines, orders };
    });
    get().toast("Ativo bloqueado · ordens não iniciadas voltam a A liberar · aprovação conservada");
  },

  releaseMachine: (machineId) => {
    set((st) => ({
      machines: st.machines.map((m) =>
        m.id === machineId ? { ...m, condition: "apto" as const, omId: undefined } : m,
      ),
    }));
    get().toast("Liberação técnica · não reassumiu agenda antiga");
  },

  updateYield: (id, patch) => {
    set((st) => ({ yields: st.yields.map((y) => (y.id === id ? { ...y, ...patch } : y)) }));
  },

  setParcels: (plotId, parcels) => {
    const plot = PLOTS.find((p) => p.id === plotId);
    if (!plot) return;
    const sum = parcels.reduce((n, p) => n + p.areaHa, 0);
    if (sum - plot.areaHa > 0.001) {
      get().toast(`Salvar · bloqueado · ${(sum - plot.areaHa).toFixed(2)} ha acima da área do talhão`, "alert");
      return;
    }
    set((st) => ({ parcels: [...st.parcels.filter((p) => p.plotId !== plotId), ...parcels] }));
    get().toast("Parcelas gravadas · soma dentro da área · plano da safra inalterado");
  },

  addPerson: (p) => set((st) => ({ people: [...st.people, p] })),
  addFarmPlot: () => {
    get().toast("Talhão cadastrado");
  },
  inactivatePerson: (id) =>
    set((st) => ({ people: st.people.map((p) => (p.id === id ? { ...p, allocatable: false } : p)) })),

  addCount: (c) => set((st) => ({ counts: [...st.counts, c] })),
  approveCount: (id) => {
    if (get().role !== "gerente") {
      get().toast("Ajuste de inventário · bloqueado · alçada do gestor", "alert");
      return;
    }
    set((st) => {
      const counts = st.counts.map((c) => (c.id === id ? { ...c, status: "aprovado" as const } : c));
      const row = counts.find((c) => c.id === id);
      if (!row) return { counts };
      return { counts, lots: st.lots.map((l) => (l.id === row.lotId ? { ...l, qty: row.counted } : l)) };
    });
    get().toast("Ajuste aprovado · saldo do lote atualizado uma vez");
  },

  commitDoc: (id) => {
    const st = get();
    const doc = st.docs.find((d) => d.id === id);
    if (!doc) return;
    const step = currentStep(doc);
    if (!step) {
      get().toast(`${doc.id} · já confirmado · a mesma intenção não repete o efeito`);
      return;
    }
    const actors = step.actors ?? doc.actors;
    if (st.role !== "gerente" && !actors.includes(st.role)) {
      get().toast(`${step.verb} · bloqueado · falta a competência deste papel`, "alert");
      return;
    }
    if (step.side?.type === "confirm-sale") {
      const free = st.harvest.mamaoCx - st.harvest.mamaoReserved;
      if (free < 200) {
        get().toast(`Confirmar pedido · bloqueado · só ${free} cx livres`, "alert");
        return;
      }
    }
    if (doc.id === "EX-77" && st.harvest.mamaoReserved < 200) {
      get().toast("Despachar · bloqueado · o pedido ainda não reservou as 200 cx", "alert");
      return;
    }
    if (step.side?.type === "adjust-lot" && st.role !== "gerente") {
      get().toast("Ajuste de inventário · bloqueado · alçada do gestor", "alert");
      return;
    }
    set((cur) => {
      let docs = cur.docs.map((d) =>
        d.id === id
          ? { ...d, status: step.status, tone: step.tone, missing: step.missing, next: step.next, cursor: d.cursor + 1 }
          : d,
      );
      let machines = cur.machines;
      let orders = cur.orders;
      let lots = cur.lots;
      let harvest = cur.harvest;
      const side = step.side;
      if (side?.type === "block") {
        machines = machines.map((m) =>
          m.id === side.machineId ? { ...m, condition: "bloqueado" as const, omId: side.omId } : m,
        );
        orders = orders.map((o) => {
          if (o.phase === "liberadas" && o.machineIds.includes(side.machineId) && o.doneHa === 0) {
            return {
              ...o,
              phase: "a-liberar" as OsPhase,
              impediment: {
                cause: `Falta máquina · ativo bloqueado (${side.omId})`,
                owner: "PCM · Ana Souza",
                due: "25/09 12:00",
                href: "/maquinas/ordens",
              },
            };
          }
          return o;
        });
      }
      if (side?.type === "release") {
        machines = machines.map((m) =>
          m.id === side.machineId ? { ...m, condition: "apto" as const, omId: undefined } : m,
        );
      }
      if (side?.type === "window") {
        orders = orders.map((o) =>
          o.id === side.osId
            ? {
                ...o,
                window: side.window,
                impediment: undefined,
                phase: o.irrigation?.waterOnly ? ("liberadas" as OsPhase) : o.phase,
              }
            : o,
        );
      }
      if (side?.type === "receive-boxes") harvest = { ...harvest, mamaoCx: harvest.mamaoCx + side.n };
      if (side?.type === "reserve-boxes") harvest = { ...harvest, mamaoReserved: harvest.mamaoReserved + side.n };
      if (side?.type === "adjust-lot") lots = lots.map((l) => (l.id === side.lotId ? { ...l, qty: side.qty } : l));
      if (side?.type === "patch") {
        docs = docs.map((d) =>
          d.id === side.id ? { ...d, status: side.status, tone: side.tone, missing: side.missing, next: side.next } : d,
        );
      }
      if (side?.type === "confirm-sale") {
        harvest = { ...harvest, mamaoReserved: harvest.mamaoReserved + 200 };
        docs = docs.map((d) => {
          if (d.id === "CR-150") {
            return { ...d, status: "Em aberto", tone: "atencao", missing: "Baixa do recebimento", next: "Baixar quando o crédito cair" };
          }
          if (d.id === "EX-77") {
            return { ...d, status: "Pronta para sair", tone: "prazo", missing: "Despacho", next: "Despachar a viagem VG-19" };
          }
          return d;
        });
      }
      if (doc.id === "EX-77") {
        harvest = {
          ...harvest,
          mamaoCx: Math.max(0, harvest.mamaoCx - 200),
          mamaoReserved: Math.max(0, harvest.mamaoReserved - 200),
        };
      }
      const entry = {
        id: `AU-${200 + cur.audit.length}`,
        at: "24/09 07:40",
        who: peopleName(cur.role),
        what: `${step.verb} · ${doc.id}`,
        result: step.toast,
      };
      return { docs, machines, orders, lots, harvest, audit: [entry, ...cur.audit] };
    });
    get().toast(step.toast);
  },

  flushQueue: () => {
    const s = get();
    if (s.hydration !== "ready") {
      get().toast("Não gravado neste aparelho · recupere a gravação antes de sincronizar", "alert");
      return;
    }
    if (s.offline) {
      get().toast("Sem sinal · a fila permanece neste aparelho", "alert");
      return;
    }
    const ids = s.queue.map((item) => item.id);
    let sairam = 0;
    const ficaram: string[] = [];
    let interrompida = false;
    for (const id of ids) {
      const live = get();
      if (live.hydration !== "ready") {
        interrompida = true;
        break;
      }
      const q = live.queue.find((item) => item.id === id);
      if (!q || q.kind !== "apontamento") continue;
      if (live.apontamentos.some((item) => item.id === q.id)) {
        set((st) => ({ queue: st.queue.filter((item) => item.id !== q.id) }));
        if (get().hydration !== "ready") {
          interrompida = true;
          break;
        }
        sairam += 1;
        continue;
      }
      const osId = queueOsId(q);
      const ha = queueNumber(q, "ha");
      const hours = queueNumber(q, "hours");
      const os = live.orders.find((order) => order.id === osId);
      const outro = live.apontamentos.find((item) => item.intentionKey === q.intentionKey && item.id !== q.id);
      if (outro) {
        ficaram.push(`${osId} · ${ha} ha · se foi outro turno, registre de novo; a conferência desta OS fica presa até restaurar a demonstração`);
        continue;
      }
      const fisico = os ? os.areaHa - os.doneHa : Number.NaN;
      if (!os || !Number.isFinite(ha) || ha <= 0 || !Number.isFinite(hours) || hours < 0 || ha > fisico + 1e-6) {
        const motivo = !os ? "O.S. ausente" : !Number.isFinite(ha) || ha <= 0 || !Number.isFinite(hours) || hours < 0 ? "valor inválido" : "saldo físico insuficiente";
        ficaram.push(`${osId || "?"} · ${Number.isFinite(ha) ? ha : "?"} ha · ${motivo}`);
        continue;
      }
      const item: Apontamento = {
        id: q.id,
        osId,
        date: dataDoItem(q),
        ha,
        hours,
        author: autorDoItem(q, live.role),
        sync: "sincronizado",
        intentionKey: q.intentionKey,
        conference: "pendente",
      };
      set((st) => ({
        apontamentos: [...st.apontamentos, item],
        queue: st.queue.filter((entry) => entry.id !== q.id),
        orders: st.orders.map((order) => {
          if (order.id !== osId) return order;
          return {
            ...order,
            doneHa: order.doneHa + ha,
            inputs: order.inputs.map((input) => {
              const used = input.dosePerHa * ha;
              return { ...input, qtyUsed: input.qtyUsed + used, qtyCustody: Math.max(0, input.qtyCustody - used) };
            }),
            paused: false,
          };
        }),
      }));
      if (get().hydration !== "ready") {
        interrompida = true;
        break;
      }
      sairam += 1;
    }
    if (interrompida) {
      const restantes = get().queue.length;
      get().toast(`Sincronização interrompida · ${restantes} itens continuam na fila`, "alert");
      return;
    }
    get().toast(`${sairam} saíram · ${ficaram.length} ficaram${ficaram.length ? ` (${ficaram.join("; ")})` : ""}`);
  },

  submitFeedback: () => {
    const { feedback } = get();
    if (!feedback.comment.trim()) {
      get().toast("Envio recusado · o comentário é obrigatório", "alert");
      return false;
    }
    if (!feedback.imageName) {
      get().toast("Envio recusado · anexe um print da tela", "alert");
      return false;
    }
    get().toast("Relato recebido · protocolo FB-2409-07");
    set({ feedback: { comment: "" }, helpOpen: false });
    return true;
  },
}));

interface Actions {
  hydrate: () => void;
  retryHydration: () => void;
  setRole: (role: Role) => void;
  setFarm: (id: string) => void;
  setSeason: (id: string) => void;
  setOffline: (v: boolean) => void;
  selectOs: (id?: string) => void;
  setHelpOpen: (v: boolean) => void;
  setJourneysOpen: (v: boolean) => void;
  toast: (text: string, tone?: ToastMsg["tone"]) => void;
  dismissToast: (id: string) => void;
  restore: () => void;
  approveVersion: (osId: string) => void;
  returnVersion: (osId: string, reason: string) => void;
  rejectVersion: (osId: string, reason: string) => void;
  setIrrigationWindow: (osId: string, window: string) => void;
  releaseOrder: (osId: string) => void;
  reprogramOrder: (osId: string) => void;
  startOrder: (osId: string) => void;
  pauseOrder: (osId: string) => void;
  recordProgress: (osId: string, ha: number, hours: number, chave?: string) => void;
  sendToConference: (osId: string) => void;
  closeOrder: (osId: string) => void;
  deliverInputs: (osId: string) => void;
  confirmReceipt: (osId: string) => void;
  declareReturn: () => void;
  receiveReturn: (osId: string, productId: string, qty: number, apt: boolean) => void;
  receivePurchase: (purchaseId: string, apt: number, quarantine: number) => void;
  releaseQuarantine: (lotId: string) => void;
  blockMachine: (machineId: string, omId: string) => void;
  releaseMachine: (machineId: string) => void;
  updateYield: (id: string, patch: Partial<YieldRow>) => void;
  setParcels: (plotId: string, parcels: ParcelDraft[]) => void;
  addPerson: (p: Person) => void;
  addFarmPlot: (plot: Plot) => void;
  inactivatePerson: (id: string) => void;
  addCount: (c: CountAdjust) => void;
  approveCount: (id: string) => void;
  flushQueue: () => void;
  commitDoc: (id: string) => void;
  setFeedback: (f: Partial<FeedbackDraft>) => void;
  submitFeedback: () => boolean;
}

function applyProgress(osId: string, ha: number, item: Apontamento) {
  useApp.setState((st) => ({
    apontamentos: [...st.apontamentos, item],
    orders: st.orders.map((o) => {
      if (o.id !== osId) return o;
      return {
        ...o,
        doneHa: o.doneHa + ha,
        inputs: o.inputs.map((i) => {
          const used = i.dosePerHa * ha;
          return { ...i, qtyUsed: i.qtyUsed + used, qtyCustody: Math.max(0, i.qtyCustody - used) };
        }),
        paused: false,
      };
    }),
  }));
}

if (typeof window !== "undefined") {
  useApp.subscribe((s) => persist(s));
}

export { FARMS, PLOTS, PRODUCTS, SEASONS };
