import { chromium } from "playwright";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";

const out = "artifacts/nav-f1-offline-adendo";
mkdirSync(out, { recursive: true });
const KEY = "safrion-demo-v2";
const origin = "http://127.0.0.1:8080";
const K = "ap-OS-0420-klegacy";
const log = [];
const mark = (name, ok, detail) => {
  log.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"} ${name}`);
};

function sha(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

async function bind(page) {
  return page.evaluate(async () => {
    const aside = document.querySelector("aside[data-os-id]");
    const fiberKey = Object.keys(aside ?? {}).find((key) => key.startsWith("__reactFiber$"));
    let node = fiberKey ? aside[fiberKey] : null;
    let panel = null;
    while (node) {
      if (typeof node.type === "function" && node.type.name === "WorkPanel") panel = node.type;
      node = node.return;
    }
    const urls = performance.getEntriesByType("resource").map((entry) => entry.name);
    let panelUrl = null;
    for (const url of urls.filter((name) => name.includes("work-panel"))) {
      const mod = await import(url);
      if (mod.WorkPanel === panel) {
        panelUrl = url;
        break;
      }
    }
    let storeUrl = null;
    for (const url of urls.filter((name) => name.includes("store.ts"))) {
      try {
        const mod = await import(url);
        const state = mod.useApp?.getState?.();
        if (state?.hydration === "ready" && state.selectedOsId === aside?.getAttribute("data-os-id")) {
          storeUrl = url;
          break;
        }
      } catch {
        // próxima
      }
    }
    return { panelUrl, storeUrl };
  });
}

async function openCampo(browser, { offline = true, role = "operador" } = {}) {
  const context = await browser.newContext({ viewport: { width: 412, height: 915 } });
  const page = await context.newPage();
  await page.addInitScript(
    ({ key, offline, role }) => {
      localStorage.setItem(key, JSON.stringify({ role, selectedOsId: "OS-0420", offline, farmId: "sr", seasonId: "2627" }));
    },
    { key: KEY, offline, role },
  );
  await page.goto(`${origin}/campo`, { waitUntil: "networkidle" });
  await page.locator('aside[data-os-id="OS-0420"]').waitFor();
  const ids = await bind(page);
  if (!ids.panelUrl || !ids.storeUrl) throw new Error(`instância ${JSON.stringify(ids)}`);
  return { context, page, ids };
}

async function shot(page, ids) {
  return page.evaluate(async ({ storeUrl, panelUrl }) => {
    const store = await import(storeUrl);
    const panel = await import(panelUrl);
    const state = store.useApp.getState();
    const os = state.orders.find((order) => order.id === "OS-0420");
    const draftKey = panel.osDraftKey({
      farmId: state.farmId,
      seasonId: state.seasonId,
      osSeasonId: os.seasonId,
      osId: os.id,
      version: os.version,
      role: state.role,
    });
    const fila = store.classificarFila(state, "OS-0420");
    const pendenteHa = fila.pendentes.reduce((sum, item) => sum + Number(item.payload.ha), 0);
    return {
      draftKey,
      draft: panel.readOsDraft(draftKey) ?? null,
      toasts: state.toasts.map((item) => item.text),
      doneHa: os.doneHa,
      areaHa: os.areaHa,
      phase: os.phase,
      ap: state.apontamentos
        .filter((item) => item.osId === "OS-0420")
        .map((item) => ({ id: item.id, ha: item.ha, hours: item.hours, key: item.intentionKey })),
      queue: state.queue.map((item) => ({ id: item.id, key: item.intentionKey, ha: item.payload?.ha ?? null, hours: item.payload?.hours ?? null })),
      pendentes: fila.pendentes.map((item) => item.id),
      retidos: fila.retidos.map((item) => ({ id: item.item.id, motivo: item.motivo })),
      jaAplicados: fila.jaAplicados.map((item) => item.id),
      saldo: store.saldoEfetivo(os.areaHa, os.doneHa, pendenteHa),
      pendenteHa,
    };
  }, ids);
}

function item(id, key, ha, hours, extra = {}) {
  return {
    id,
    kind: "apontamento",
    payload: { osId: "OS-0420", ha, hours, key },
    intentionKey: key,
    createdAt: extra.createdAt,
    state: "aguardando-envio",
    author: extra.author,
    date: extra.date,
  };
}

async function plant(page, ids, patch) {
  await page.evaluate(
    async ({ storeUrl, patch }) => {
      const { useApp } = await import(storeUrl);
      const state = useApp.getState();
      useApp.setState({
        offline: patch.offline ?? state.offline,
        hydration: "ready",
        queue: patch.queue ?? state.queue,
        apontamentos: patch.apontamentos ?? state.apontamentos,
        orders: state.orders.map((order) => (order.id === "OS-0420" ? { ...order, ...patch.order } : order)),
      });
    },
    { storeUrl: ids.storeUrl, patch },
  );
}

async function showDraft(page, ids, draft) {
  await page.evaluate(
    async ({ storeUrl, panelUrl, draft }) => {
      const store = await import(storeUrl);
      const panel = await import(panelUrl);
      const state = store.useApp.getState();
      const os = state.orders.find((order) => order.id === "OS-0420");
      const key = panel.osDraftKey({
        farmId: state.farmId,
        seasonId: state.seasonId,
        osSeasonId: os.seasonId,
        osId: os.id,
        version: os.version,
        role: state.role,
      });
      panel.writeOsDraft(key, { reason: "", review: false, ...draft });
    },
    { ...ids, draft },
  );
  await page.getByRole("button", { name: "Fechar", exact: true }).click();
  await page.getByRole("button", { name: /OS-0420/ }).click();
  await page.locator("aside[data-os-id='OS-0420']").waitFor();
  await page.waitForFunction((value) => document.querySelector("aside[data-os-id='OS-0420'] input")?.value === value, draft.ha);
}

const browser = await chromium.launch({ headless: true });
try {
  const conflict = await openCampo(browser, { offline: true });
  await plant(conflict.page, conflict.ids, {
    order: { doneHa: 33.3 },
    apontamentos: [
      ...(await shot(conflict.page, conflict.ids)).ap.map((entry) => ({
        id: entry.id,
        osId: "OS-0420",
        date: "2026-09-22",
        ha: entry.ha,
        hours: entry.hours,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: entry.key,
        conference: "pendente",
      })),
      {
        id: "AP-A-legacy",
        osId: "OS-0420",
        date: "2026-09-23",
        ha: 3.3,
        hours: 3.3,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: K,
        conference: "pendente",
      },
    ],
    queue: [item("AP-B-retido", K, 4.4, 4.4, { createdAt: "2026-09-24T00:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" })],
  });
  const decisions = await conflict.page.evaluate(
    async ({ storeUrl, K }) => {
      const store = await import(storeUrl);
      const state = store.useApp.getState();
      return {
        quatro: store.decidirChave(state, "OS-0420", K, 4.4, 4.4),
        tres: store.decidirChave(state, "OS-0420", K, 3.3, 3.3),
      };
    },
    { storeUrl: conflict.ids.storeUrl, K },
  );
  await showDraft(conflict.page, conflict.ids, { ha: "4,4", hours: "4,4", chave: K });
  const beforeFour = await shot(conflict.page, conflict.ids);
  beforeFour.inputs = {
    ha: await conflict.page.getByRole("textbox", { name: /Área feita/ }).inputValue(),
    hours: await conflict.page.getByRole("textbox", { name: "Horas do turno", exact: true }).inputValue(),
  };
  await conflict.page.getByRole("button", { name: "Registrar apontamento", exact: true }).click();
  const afterFour = await shot(conflict.page, conflict.ids);
  afterFour.inputs = {
    ha: await conflict.page.getByRole("textbox", { name: /Área feita/ }).inputValue(),
    hours: await conflict.page.getByRole("textbox", { name: "Horas do turno", exact: true }).inputValue(),
  };
  const toastFour = afterFour.toasts.slice(beforeFour.toasts.length);
  mark(
    "A(i) K/4,4 conflita com o apontamento e preserva rascunho",
    decisions.quatro.tipo === "conflito" &&
      toastFour.length === 1 &&
      toastFour[0].includes("Conflito") &&
      !/registrad/i.test(toastFour[0]) &&
      afterFour.draft?.chave === K &&
      afterFour.draft.ha === "4,4" &&
      afterFour.inputs.ha === "4,4" &&
      JSON.stringify(beforeFour.queue) === JSON.stringify(afterFour.queue) &&
      JSON.stringify(beforeFour.ap) === JSON.stringify(afterFour.ap) &&
      beforeFour.doneHa === afterFour.doneHa,
    JSON.stringify({ decisions: decisions.quatro, toastFour, draft: afterFour.draft }),
  );
  await conflict.context.close();

  const conflictBack = await openCampo(browser, { offline: true });
  const baseAp = (await shot(conflictBack.page, conflictBack.ids)).ap;
  await plant(conflictBack.page, conflictBack.ids, {
    order: { doneHa: 33.3 },
    apontamentos: [
      ...baseAp.map((entry) => ({
        id: entry.id,
        osId: "OS-0420",
        date: "2026-09-22",
        ha: entry.ha,
        hours: entry.hours,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: entry.key,
        conference: "pendente",
      })),
      {
        id: "AP-A-legacy",
        osId: "OS-0420",
        date: "2026-09-23",
        ha: 3.3,
        hours: 3.3,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: K,
        conference: "pendente",
      },
    ],
    queue: [item("AP-B-retido", K, 4.4, 4.4, { createdAt: "2026-09-24T00:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" })],
  });
  await showDraft(conflictBack.page, conflictBack.ids, { ha: "3,3", hours: "3,3", chave: K });
  const beforeThree = await shot(conflictBack.page, conflictBack.ids);
  await conflictBack.page.getByRole("button", { name: "Registrar apontamento", exact: true }).click();
  const afterThree = await shot(conflictBack.page, conflictBack.ids);
  const toastThree = afterThree.toasts.slice(beforeThree.toasts.length);
  mark(
    "A(ii) K/3,3 também conflita por causa do retido",
    decisions.tres.tipo === "conflito" &&
      toastThree.length === 1 &&
      toastThree[0].includes("Conflito") &&
      !/registrad|aguardando envio/i.test(toastThree[0]) &&
      afterThree.draft?.chave === K &&
      afterThree.draft.ha === "3,3" &&
      afterThree.draft.hours === "3,3" &&
      JSON.stringify(beforeThree.queue) === JSON.stringify(afterThree.queue) &&
      JSON.stringify(beforeThree.ap) === JSON.stringify(afterThree.ap),
    JSON.stringify({ toastThree, draft: afterThree.draft }),
  );
  await conflictBack.context.close();

  const retained = await openCampo(browser, { offline: true });
  await plant(retained.page, retained.ids, {
    order: { areaHa: 31, doneHa: 30 },
    queue: [item("AP-so-retido", K, 4.4, 4.4, { createdAt: "2026-09-24T00:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" })],
  });
  const retidoDecisao = await retained.page.evaluate(
    async ({ storeUrl, K }) => (await import(storeUrl)).decidirChave((await import(storeUrl)).useApp.getState(), "OS-0420", K, 4.4, 4.4),
    { storeUrl: retained.ids.storeUrl, K },
  );
  await showDraft(retained.page, retained.ids, { ha: "4,4", hours: "4,4", chave: K });
  const beforeHeld = await shot(retained.page, retained.ids);
  await retained.page.getByRole("button", { name: "Registrar apontamento", exact: true }).click();
  const afterHeld = await shot(retained.page, retained.ids);
  const toastHeld = afterHeld.toasts.slice(beforeHeld.toasts.length);
  mark(
    "B retido sozinho não é recibo nem repetição",
    retidoDecisao.tipo === "retido" &&
      toastHeld.length === 1 &&
      toastHeld[0].includes("Já na fila, retido") &&
      toastHeld[0].includes("saldo físico insuficiente") &&
      !toastHeld[0].includes("já aguardando envio") &&
      afterHeld.draft?.chave === K &&
      afterHeld.draft.ha === "4,4" &&
      JSON.stringify(beforeHeld.queue) === JSON.stringify(afterHeld.queue) &&
      JSON.stringify(beforeHeld.ap) === JSON.stringify(afterHeld.ap),
    JSON.stringify({ retidoDecisao, toastHeld, draft: afterHeld.draft }),
  );
  await retained.context.close();

  const repeat = await openCampo(browser, { offline: true });
  await plant(repeat.page, repeat.ids, {
    queue: [item("AP-rep", K, 1, 1, { createdAt: "2026-09-24T00:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" })],
  });
  await showDraft(repeat.page, repeat.ids, { ha: "1", hours: "1", chave: K });
  const beforeRepeat = await shot(repeat.page, repeat.ids);
  beforeRepeat.inputs = {
    ha: await repeat.page.getByRole("textbox", { name: /Área feita/ }).inputValue(),
    hours: await repeat.page.getByRole("textbox", { name: "Horas do turno", exact: true }).inputValue(),
  };
  await repeat.page.getByRole("button", { name: "Registrar apontamento", exact: true }).click();
  const afterRepeat = await shot(repeat.page, repeat.ids);
  afterRepeat.inputs = {
    ha: await repeat.page.getByRole("textbox", { name: /Área feita/ }).inputValue(),
    hours: await repeat.page.getByRole("textbox", { name: "Horas do turno", exact: true }).inputValue(),
  };
  const toastRepeat = afterRepeat.toasts.slice(beforeRepeat.toasts.length);
  mark(
    "repetição de pendente consome rascunho sem duplicar",
    beforeRepeat.queue.length === 1 &&
      afterRepeat.queue.length === 1 &&
      beforeRepeat.queue[0].id === afterRepeat.queue[0].id &&
      beforeRepeat.ap.length === afterRepeat.ap.length &&
      beforeRepeat.doneHa === afterRepeat.doneHa &&
      beforeRepeat.draft?.chave === K &&
      afterRepeat.draft === null &&
      afterRepeat.inputs.ha === "" &&
      toastRepeat.length === 1 &&
      toastRepeat[0].includes("já aguardando envio") &&
      !toastRepeat[0].includes("Conflito"),
    JSON.stringify({ before: { queue: beforeRepeat.queue, draft: beforeRepeat.draft, doneHa: beforeRepeat.doneHa }, after: { queue: afterRepeat.queue, draft: afterRepeat.draft, doneHa: afterRepeat.doneHa, inputs: afterRepeat.inputs }, toastRepeat }),
  );
  await repeat.context.close();

  const repeatOnline = await openCampo(browser, { offline: false });
  const onlineBase = (await shot(repeatOnline.page, repeatOnline.ids)).ap;
  await plant(repeatOnline.page, repeatOnline.ids, {
    offline: false,
    order: { doneHa: 31 },
    queue: [],
    apontamentos: [
      ...onlineBase.map((entry) => ({
        id: entry.id,
        osId: "OS-0420",
        date: "2026-09-22",
        ha: entry.ha,
        hours: entry.hours,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: entry.key,
        conference: "pendente",
      })),
      {
        id: "AP-online-k",
        osId: "OS-0420",
        date: "2026-09-24",
        ha: 1,
        hours: 1,
        author: "Marcos Pereira",
        sync: "sincronizado",
        intentionKey: K,
        conference: "pendente",
      },
    ],
  });
  await showDraft(repeatOnline.page, repeatOnline.ids, { ha: "1", hours: "1", chave: K });
  const beforeOnline = await shot(repeatOnline.page, repeatOnline.ids);
  await repeatOnline.page.getByRole("button", { name: "Registrar apontamento", exact: true }).click();
  const afterOnline = await shot(repeatOnline.page, repeatOnline.ids);
  const toastOnline = afterOnline.toasts.slice(beforeOnline.toasts.length);
  mark(
    "repetição de apontamento consome rascunho sem duplicar",
    beforeOnline.ap.length === afterOnline.ap.length &&
      beforeOnline.doneHa === afterOnline.doneHa &&
      afterOnline.queue.length === 0 &&
      afterOnline.draft === null &&
      toastOnline.some((text) => text.includes("já registrada")) &&
      !toastOnline.some((text) => text.includes("Conflito")),
    JSON.stringify({ before: beforeOnline.ap.length, after: afterOnline.ap.length, doneHa: afterOnline.doneHa, toastOnline }),
  );
  await repeatOnline.context.close();

  const balance = await openCampo(browser, { offline: true });
  await plant(balance.page, balance.ids, {
    queue: [item("AP-max", "ap-OS-0420-kmax", 10, 1, { createdAt: "2026-09-24T00:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" })],
  });
  await balance.page.getByText(/máx\./).waitFor();
  const maxText = await balance.page.getByText(/Área feita/).innerText();
  const summaryMax = await balance.page.locator("p.tabular").innerText();
  const saldoMax = await balance.page.evaluate(async (storeUrl) => {
    const store = await import(storeUrl);
    const state = store.useApp.getState();
    const order = state.orders.find((item) => item.id === "OS-0420");
    const fila = store.classificarFila(state, "OS-0420");
    const pendente = fila.pendentes.reduce((sum, item) => sum + Number(item.payload.ha), 0);
    return { saldo: store.saldoEfetivo(order.areaHa, order.doneHa, pendente), pendente };
  }, balance.ids.storeUrl);
  await plant(balance.page, balance.ids, {
    order: { areaHa: 40, doneHa: 30 },
    queue: [
      item("AP-f1", "ap-OS-0420-kf1", 6.6, 1, { createdAt: "2026-09-24T00:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" }),
      item("AP-f2", "ap-OS-0420-kf2", 3.4, 1, { createdAt: "2026-09-24T01:00:00.000Z", author: "Marcos Pereira", date: "2026-09-24" }),
    ],
  });
  await balance.page.locator("p.tabular").waitFor();
  const summaryFloat = await balance.page.locator("p.tabular").innerText();
  const hidden = await balance.page.getByRole("button", { name: "Registrar apontamento", exact: true }).count();
  const floatInfo = await balance.page.evaluate(async (storeUrl) => {
    const store = await import(storeUrl);
    const state = store.useApp.getState();
    const order = state.orders.find((item) => item.id === "OS-0420");
    const fila = store.classificarFila(state, "OS-0420");
    const pendente = fila.pendentes.reduce((sum, item) => sum + Number(item.payload.ha), 0);
    return { saldo: store.saldoEfetivo(order.areaHa, order.doneHa, pendente), pendente, raw: order.areaHa - order.doneHa - pendente };
  }, balance.ids.storeUrl);
  const blockedOffline = await balance.page.getByText("Aguardando envio de").first().innerText();
  await balance.page.evaluate(async (storeUrl) => {
    (await import(storeUrl)).useApp.getState().setOffline(false);
  }, balance.ids.storeUrl);
  const blockedOnline = await balance.page.getByText(/Aguardando envio de .*sincronize$/).first().innerText();
  mark(
    "6 resumo e máximo batem com saldo efetivo, inclusive resíduo",
    saldoMax.saldo === 60 &&
      maxText.includes("60,00") &&
      summaryMax.includes("60,00") &&
      floatInfo.saldo === 0 &&
      summaryFloat.includes("0,00") &&
      hidden === 0 &&
      blockedOffline.includes("quando houver sinal") &&
      blockedOnline.includes("sincronize") &&
      !blockedOnline.includes("quando houver sinal"),
    JSON.stringify({ maxText, summaryMax, saldoMax, summaryFloat, floatInfo, blockedOffline, blockedOnline }),
  );
  await balance.context.close();

  const gate = await openCampo(browser, { offline: false, role: "gerente" });
  const mixed = await gate.page.evaluate(async (storeUrl) => {
    const { useApp } = await import(storeUrl);
    useApp.setState({
      offline: false,
      queue: [
        {
          id: "AP-mix-pend",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-kmix" },
          intentionKey: "ap-OS-0420-kmix",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-24",
        },
        {
          id: "AP-mix-ret",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-0420-d1" },
          intentionKey: "ap-0420-d1",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
        },
      ],
    });
    useApp.getState().sendToConference("OS-0420");
    const state = useApp.getState();
    return { toast: state.toasts.at(-1)?.text ?? "", phase: state.orders.find((order) => order.id === "OS-0420").phase };
  }, gate.ids.storeUrl);
  mark(
    "6a recusa única com pendente e retido",
    mixed.toast.includes("1 aguardando envio · sincronize quando houver sinal") &&
      mixed.toast.includes("1 retidos · veja o motivo") &&
      mixed.phase === "em-execucao",
    JSON.stringify(mixed),
  );

  const applied = await gate.page.evaluate(async (storeUrl) => {
    const { useApp, classificarFila } = await import(storeUrl);
    const state = useApp.getState();
    useApp.setState({
      offline: false,
      queue: [
        {
          id: "AP-0420-1",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 30, hours: 2.4, key: "ap-0420-d1" },
          intentionKey: "ap-0420-d1",
          createdAt: "2026-09-22T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-22",
        },
      ],
      orders: state.orders.map((order) =>
        order.id === "OS-0420"
          ? { ...order, doneHa: order.areaHa, inputs: order.inputs.map((input) => ({ ...input, qtyCustody: 0 })) }
          : order,
      ),
    });
    const fila = classificarFila(useApp.getState(), "OS-0420");
    useApp.getState().sendToConference("OS-0420");
    const mid = useApp.getState();
    useApp.getState().closeOrder("OS-0420");
    const end = useApp.getState();
    return {
      ja: fila.jaAplicados.map((item) => item.id),
      pendentes: fila.pendentes.length,
      retidos: fila.retidos.length,
      conferenceToast: mid.toasts.at(-1)?.text ?? "",
      closeToast: end.toasts.at(-1)?.text ?? "",
      phase: end.orders.find((order) => order.id === "OS-0420").phase,
      queue: end.queue.map((item) => item.id),
    };
  }, gate.ids.storeUrl);
  const waitingChips = await gate.page.locator('[data-sync="aguardando-envio"]').count();
  mark(
    "C item já aplicado não bloqueia conferência nem encerramento",
    applied.ja.includes("AP-0420-1") &&
      applied.pendentes === 0 &&
      applied.retidos === 0 &&
      applied.phase === "encerradas" &&
      !applied.conferenceToast.includes("aguardando envio") &&
      !applied.closeToast.includes("aguardando envio") &&
      waitingChips === 0,
    JSON.stringify({ applied, waitingChips }),
  );

  const dated = await gate.page.evaluate(async (storeUrl) => {
    const { useApp } = await import(storeUrl);
    const state = useApp.getState();
    useApp.setState({
      orders: state.orders.map((order) => (order.id === "OS-0420" ? { ...order, phase: "em-execucao", doneHa: 30, areaHa: 100 } : order)),
      queue: [
        {
          id: "AP-nodate",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-knodate" },
          intentionKey: "ap-OS-0420-knodate",
          state: "aguardando-envio",
        },
        {
          id: "AP-emptyday",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-kempty" },
          intentionKey: "ap-OS-0420-kempty",
          createdAt: "2026-09-21T08:00:00.000Z",
          date: "",
          state: "aguardando-envio",
        },
      ],
    });
  }, gate.ids.storeUrl);
  void dated;
  await gate.page.locator('[data-sync="aguardando-envio"]').first().waitFor();
  const chips = await gate.page.locator('[data-sync="aguardando-envio"]').allInnerTexts();
  mark(
    "E chip sem data usa o mesmo fallback do flush",
    chips.some((text) => text.includes("24/09")) && chips.some((text) => text.includes("21/09")) && !chips.some((text) => text.includes("d/in") || text.includes("/ ·")),
    JSON.stringify(chips),
  );
  await gate.context.close();

  const storePage = await openCampo(browser, { offline: false });
  const storeCases = await storePage.page.evaluate(async ({ storeUrl, KEY }) => {
    const store = await import(storeUrl);
    const { useApp, persistedPayload, saldoEfetivo, classificarFila } = store;
    const out = {};
    const base = useApp.getState();
    const seedAp = base.apontamentos;
    useApp.setState({
      offline: false,
      hydration: "ready",
      queue: [],
      apontamentos: seedAp,
      orders: base.orders.map((order) => (order.id === "OS-0420" ? { ...order, areaHa: 100, doneHa: 30, phase: "em-execucao" } : order)),
    });
    useApp.getState().recordProgress("OS-0420", 80, 1, "ap-OS-0420-kemptyqueue");
    const empty = useApp.getState();
    out.emptySaldo = {
      toast: empty.toasts.at(-1)?.text ?? "",
      doneHa: empty.orders.find((order) => order.id === "OS-0420").doneHa,
      queue: empty.queue.length,
    };
    useApp.setState({
      queue: [
        {
          id: "AP-p10",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 10, hours: 1, key: "ap-OS-0420-kp10" },
          intentionKey: "ap-OS-0420-kp10",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-24",
        },
      ],
    });
    useApp.getState().recordProgress("OS-0420", 80, 1, "ap-OS-0420-kover");
    out.withPending = { toast: useApp.getState().toasts.at(-1)?.text ?? "", queue: useApp.getState().queue.length };

    useApp.setState({
      orders: useApp.getState().orders.map((order) => (order.id === "OS-0420" ? { ...order, areaHa: 31, doneHa: 30 } : order)),
      queue: [
        {
          id: "AP-zero",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-kzero" },
          intentionKey: "ap-OS-0420-kzero",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-24",
        },
      ],
    });
    const beforeZero = useApp.getState();
    const orderZero = beforeZero.orders.find((order) => order.id === "OS-0420");
    const pendenteZero = classificarFila(beforeZero, "OS-0420").pendentes.reduce((sum, item) => sum + Number(item.payload.ha), 0);
    useApp.getState().recordProgress("OS-0420", 1, 1, "ap-OS-0420-kzero");
    const afterZero = useApp.getState();
    out.repeatAtZero = {
      saldo: saldoEfetivo(orderZero.areaHa, orderZero.doneHa, pendenteZero),
      before: { queue: beforeZero.queue.map((item) => item.id), doneHa: orderZero.doneHa },
      after: {
        queue: afterZero.queue.map((item) => item.id),
        doneHa: afterZero.orders.find((order) => order.id === "OS-0420").doneHa,
        toast: afterZero.toasts.at(-1)?.text ?? "",
      },
    };

    useApp.setState({
      offline: false,
      hydration: "error",
      queue: [
        {
          id: "AP-blocked",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-kblocked" },
          intentionKey: "ap-OS-0420-kblocked",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-24",
        },
      ],
    });
    const payloadBefore = persistedPayload(useApp.getState());
    const apBefore = useApp.getState().apontamentos.length;
    useApp.getState().flushQueue();
    const blocked = useApp.getState();
    out.blockedFlush = {
      toast: blocked.toasts.at(-1)?.text ?? "",
      queue: blocked.queue.map((item) => item.id),
      apSame: blocked.apontamentos.length === apBefore,
      payloadSame: persistedPayload(blocked) === payloadBefore,
    };

    useApp.getState().retryHydration();
    useApp.setState({
      offline: false,
      hydration: "ready",
      queue: [
        {
          id: "AP-stop-1",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-kstop1" },
          intentionKey: "ap-OS-0420-kstop1",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-24",
        },
        {
          id: "AP-stop-2",
          kind: "apontamento",
          payload: { osId: "OS-0420", ha: 1, hours: 1, key: "ap-OS-0420-kstop2" },
          intentionKey: "ap-OS-0420-kstop2",
          createdAt: "2026-09-24T00:00:00.000Z",
          state: "aguardando-envio",
          author: "Marcos Pereira",
          date: "2026-09-24",
        },
      ],
      orders: useApp.getState().orders.map((order) => (order.id === "OS-0420" ? { ...order, areaHa: 100, doneHa: 30 } : order)),
    });
    const doneBefore = useApp.getState().orders.find((order) => order.id === "OS-0420").doneHa;
    const original = localStorage.setItem.bind(localStorage);
    localStorage.setItem = (key, value) => {
      if (key !== KEY) return original(key, value);
      throw new Error("quota");
    };
    try {
      useApp.getState().flushQueue();
    } finally {
      localStorage.setItem = original;
    }
    const stopped = useApp.getState();
    out.interrupted = {
      toasts: stopped.toasts.map((item) => item.text),
      queue: stopped.queue.map((item) => item.id),
      doneHa: stopped.orders.find((order) => order.id === "OS-0420").doneHa,
      doneBefore,
      hydration: stopped.hydration,
    };
    return out;
  }, { storeUrl: storePage.ids.storeUrl, KEY });
  mark(
    "D saldo sem pendente não diz pendente",
    storeCases.emptySaldo.toast === "Registrar · recusado · saldo efetivo 70,00 ha" &&
      !storeCases.emptySaldo.toast.includes("pendente") &&
      !storeCases.emptySaldo.toast.includes("aguardando") &&
      storeCases.emptySaldo.queue === 0 &&
      storeCases.emptySaldo.doneHa === 30 &&
      storeCases.withPending.toast.includes("saldo efetivo 60,00 ha") &&
      storeCases.withPending.toast.includes("aguardando envio 10,00 ha") &&
      storeCases.withPending.queue === 1,
    JSON.stringify({ empty: storeCases.emptySaldo, withPending: storeCases.withPending }),
  );
  mark(
    "8 repetição com saldo efetivo zero não cria nem fala saldo",
    storeCases.repeatAtZero.saldo === 0 &&
      storeCases.repeatAtZero.after.toast.includes("já aguardando envio") &&
      !storeCases.repeatAtZero.after.toast.includes("saldo") &&
      JSON.stringify(storeCases.repeatAtZero.before.queue) === JSON.stringify(storeCases.repeatAtZero.after.queue) &&
      storeCases.repeatAtZero.before.doneHa === storeCases.repeatAtZero.after.doneHa,
    JSON.stringify(storeCases.repeatAtZero),
  );
  mark(
    "11 flush com fila não vazia em erro não aplica",
    storeCases.blockedFlush.queue.length === 1 &&
      storeCases.blockedFlush.apSame &&
      storeCases.blockedFlush.payloadSame &&
      storeCases.blockedFlush.toast.includes("Não gravado neste aparelho") &&
      !storeCases.blockedFlush.toast.includes("saíram"),
    JSON.stringify(storeCases.blockedFlush),
  );
  mark(
    "F interrupção não diz saíram e conta a fila restante",
    storeCases.interrupted.hydration === "error" &&
      storeCases.interrupted.queue.length === 2 &&
      storeCases.interrupted.doneHa === storeCases.interrupted.doneBefore &&
      storeCases.interrupted.toasts.some((text) => text.includes("Não gravado neste aparelho")) &&
      storeCases.interrupted.toasts.some((text) => text === "Sincronização interrompida · 2 itens continuam na fila") &&
      !storeCases.interrupted.toasts.some((text) => text.includes("saíram")),
    JSON.stringify(storeCases.interrupted),
  );
  await storePage.context.close();
} catch (error) {
  mark("harness", false, String(error));
} finally {
  await browser.close();
  const sources = {
    "src/lib/store.ts": sha("src/lib/store.ts"),
    "src/components/os/work-panel.tsx": sha("src/components/os/work-panel.tsx"),
    "src/lib/types.ts": sha("src/lib/types.ts"),
    "src/components/layout/shell.tsx": sha("src/components/layout/shell.tsx"),
    "src/components/layout/field-shell.tsx": sha("src/components/layout/field-shell.tsx"),
  };
  writeFileSync(`${out}/log.json`, JSON.stringify({ ok: log.every((item) => item.ok), sources, log }, null, 2) + "\n");
}
process.exitCode = log.every((item) => item.ok) ? 0 : 1;
console.log(JSON.stringify({ ok: process.exitCode === 0, marks: log.map((item) => [item.name, item.ok]) }));
