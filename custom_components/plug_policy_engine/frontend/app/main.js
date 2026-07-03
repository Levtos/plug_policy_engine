const WS_GET_STATUS = "plug_policy_engine/get_status";
const DOMAIN = "plug_policy_engine";

const CSS = `
:host{display:block;min-height:100vh;background:#0b1020;color:#e7eaf6;font:14px/1.45 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}
button,select{font:inherit}
.app{min-height:100vh;padding:14px;background:radial-gradient(circle at 20% 0,#22264a 0,#111827 36%,#090d18 100%)}
.top{height:58px;display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:8px}
.brand{display:flex;align-items:center;gap:14px;min-width:0}
.logo{width:44px;height:44px;border-radius:9px;display:grid;place-items:center;background:linear-gradient(145deg,#7b5cff,#9f78ff);box-shadow:0 12px 28px rgba(124,92,255,.34);font-size:26px}
.brand h1{margin:0;font-size:28px;font-weight:650;letter-spacing:0}
.brand small{display:block;color:#aab2cb;font-size:15px;margin-top:-3px}
.top-actions{display:flex;gap:8px}
.iconbtn,.btn,.select{height:40px;border:1px solid #2b344a;background:#151b2b;color:#e9edf8;border-radius:8px;padding:0 14px;display:inline-flex;align-items:center;gap:8px}
.iconbtn{width:42px;justify-content:center;padding:0;font-size:18px}
.btn:hover,.iconbtn:hover,.select:hover{border-color:#735cff}
.hero{display:grid;grid-template-columns:340px 1fr 300px;gap:24px;align-items:center;border:1px solid #263146;border-radius:9px;background:linear-gradient(180deg,rgba(24,31,48,.92),rgba(16,22,36,.92));padding:18px 22px;margin-bottom:10px;box-shadow:inset 0 1px 0 rgba(255,255,255,.04)}
.hero-title{display:flex;align-items:center;gap:18px}
.lock{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;background:#282444;color:#a887ff;font-size:30px}
.hero h2{margin:0;color:#a985ff;font-size:24px}
.hero code{display:block;margin-top:4px;color:#c8cee3;font-size:16px}
.gate{display:grid;grid-template-columns:1fr 1fr;border:1px solid #2b344a;border-radius:10px;overflow:hidden}
.gate button{height:58px;border:0;background:#121929;color:#ccd4e8;font-size:22px;font-weight:650;cursor:pointer}
.gate button span{display:block;font-size:13px;font-weight:650;margin-top:4px;color:#aeb6cc}
.gate button.active.shadow{background:linear-gradient(90deg,rgba(255,210,20,.28),rgba(255,210,20,.08));outline:1px solid #f5d30a;color:#ffe100}
.gate button.active.live{background:linear-gradient(90deg,rgba(89,226,100,.18),rgba(89,226,100,.07));outline:1px solid #59e264;color:#6dff78}
.notice{border-left:1px dashed #3d465c;padding-left:24px;color:#b7bfd4}
.notice b{display:block;color:#ffe100;margin-bottom:4px;font-size:15px}
.context{display:flex;align-items:center;gap:12px;border:1px solid #263146;border-radius:8px;background:#151c2c;padding:6px 14px;margin-bottom:10px;overflow:auto}
.context .why{white-space:nowrap;color:#c4cadb;font-size:13px}
.chip{display:inline-flex;align-items:center;gap:7px;min-height:29px;padding:4px 12px;border:1px solid #303a52;border-radius:999px;background:#111827;color:#d4daeb;white-space:nowrap}
.chip.green{border-color:#32623d;color:#77f382;background:rgba(41,130,58,.11)}
.chip.blue{border-color:#2c83a6;color:#54d8ff;background:rgba(32,126,166,.11)}
.chip.orange{border-color:#9a5b22;color:#ffb451;background:rgba(166,91,32,.11)}
.chip.pink{border-color:#8d4773;color:#ff91cb;background:rgba(161,67,124,.11)}
.chip.red{border-color:#8e3344;color:#ff6b7b;background:rgba(157,54,70,.11)}
.work{display:grid;grid-template-columns:minmax(0,1fr) 430px;gap:8px}
.left,.detail,.trace{border:1px solid #263146;border-radius:9px;background:rgba(16,22,36,.86)}
.left{padding:8px}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px}
.tools,.filters{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.filters .chip{cursor:pointer}
.filters .chip.active{box-shadow:0 0 0 1px currentColor inset}
.grid{display:grid;grid-template-columns:repeat(3,minmax(250px,1fr));gap:10px}
.card{border:1px solid #2b344a;border-radius:8px;background:linear-gradient(180deg,rgba(27,35,54,.95),rgba(18,24,38,.95));min-height:190px;overflow:hidden;cursor:pointer}
.card.selected{border-color:#8d67ff;box-shadow:0 0 0 1px rgba(141,103,255,.65),0 0 28px rgba(141,103,255,.16)}
.cardhead{height:48px;display:flex;align-items:center;gap:11px;padding:0 14px;border-bottom:1px solid #263146}
.kind{font-size:24px;color:#aa8cff;width:28px;text-align:center}
.name{font-size:17px;font-weight:600;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.policy{font-size:13px;color:#c8b5ff;border:1px solid #7552b8;background:rgba(112,70,190,.25);border-radius:5px;padding:2px 8px;margin-left:auto}
.dots{color:#8791aa;font-size:22px}
.row{display:grid;grid-template-columns:44px 1fr;gap:10px;align-items:start;padding:5px 14px;color:#c9d0e2}
.row .label{color:#aeb6cc}
.state-line{display:flex;align-items:center;gap:12px;min-width:0}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;background:#8791aa;box-shadow:0 0 10px currentColor}
.on{color:#65f176}.off{color:#ff5d6b}.standby{color:#ffd51e}.keep{color:#b9c0d2}.would-on{color:#50cbff}.would-cut{color:#ff596c}
.reason{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.blockers{display:flex;gap:5px;flex-wrap:wrap}
.mini{font-size:12px;border:1px solid #3b465d;border-radius:5px;padding:1px 6px;color:#cfc7ff}
.suspend{height:36px;border-top:1px solid #263146;margin-top:6px;padding:6px 14px;display:flex;align-items:center;justify-content:flex-end;gap:12px;color:#b8c0d4;font-size:12px}
.toggle{width:39px;height:20px;border-radius:99px;border:1px solid #334058;background:#0e1422;position:relative}
.toggle:before{content:"";position:absolute;top:2px;left:2px;width:14px;height:14px;border-radius:50%;background:#aab2c6}
.toggle.on:before{left:21px;background:#9f78ff}
.widget{margin:4px 14px 0 auto;border:1px solid #303a52;border-radius:6px;width:126px;min-height:40px;padding:5px 8px;color:#d6def1;font-size:12px;text-align:center}
.detail{padding:12px}
.detail-head{height:38px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #263146;margin:-2px -2px 10px;padding:0 6px 10px}
.detail h2{margin:0;color:#b896ff;font-size:16px}
.x{border:0;background:transparent;color:#c5ccdd;font-size:25px;cursor:pointer}
.selected-title{height:40px;display:flex;align-items:center;gap:10px;border:1px solid #2b344a;border-radius:8px;padding:0 12px;margin-bottom:10px}
.section{border-bottom:1px solid #263146;padding:10px 4px}
.section:last-child{border-bottom:0}
.section h3{margin:0 0 6px;color:#b896ff;font-size:14px}
.kv{display:grid;grid-template-columns:120px 1fr;gap:4px;color:#c8cfdf}
.debug{width:100%;justify-content:center;margin-top:10px;border-color:#7d55d7;color:#c6aaff}
.trace{margin-top:8px;padding:14px}
.trace h2{margin:0 0 12px;color:#b896ff;font-size:16px}
.chain{display:grid;grid-template-columns:repeat(5,minmax(140px,1fr));gap:22px}
.node{position:relative;border:1px solid #354158;border-radius:8px;background:#151c2c;padding:12px;min-height:84px}
.node:after{content:"";position:absolute;right:-17px;top:38px;width:12px;height:12px;border-top:2px solid #9aa5bf;border-right:2px solid #9aa5bf;transform:rotate(45deg)}
.node:last-child:after{display:none}
.node.active{border-color:#8d67ff;box-shadow:0 0 0 1px rgba(141,103,255,.6)}
.node b{display:block;margin-bottom:5px}
.node small{color:#b8c0d4}
.okmark{float:right;color:#68ee75}
.foot{display:flex;justify-content:flex-end;color:#9fa8bf;font-size:12px;margin-top:4px}
@media(max-width:1260px){.hero{grid-template-columns:1fr}.notice{border-left:0;border-top:1px dashed #3d465c;padding:14px 0 0}.work{grid-template-columns:1fr}.detail{order:3}.grid{grid-template-columns:repeat(2,minmax(240px,1fr))}}
@media(max-width:760px){.app{padding:8px}.top{height:auto;align-items:flex-start}.brand h1{font-size:22px}.top-actions{display:none}.grid,.chain{grid-template-columns:1fr}.hero{padding:14px}.gate{grid-template-columns:1fr}.context{align-items:flex-start}.toolbar{align-items:flex-start;flex-direction:column}.work{display:block}.detail{margin-top:8px}}
`;

const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
const fmt = (v, fallback = "-") => v === null || v === undefined || v === "" ? fallback : String(v);
const seconds = (v) => {
  if (v === null || v === undefined) return "-";
  const n = Math.max(0, Number(v) || 0);
  const m = Math.floor(n / 60);
  const s = n % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
};
const kindIcon = (kind) => ({
  pc: "▱", tablet: "▯", diffuser: "♨", coffee_maker: "☕", denon: "▤",
  appliance: "▦", bias_light: "◐", h14_dock: "▣", generic: "♢",
}[kind] || "♢");
const desiredClass = (d) => d === "off" ? "would-cut" : d === "on" ? "would-on" : "keep";
const stateClass = (s) => s === "on" ? "on" : s === "off" ? "off" : "standby";

class PlugPolicyPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._status = null;
    this._selected = null;
    this._filters = { status: "all", policy: "all", kind: "all", sort: "name" };
    this._booted = false;
  }

  set hass(value) {
    this._hass = value;
    if (!this._booted) this._boot();
  }
  get hass() { return this._hass; }

  async _boot() {
    this._booted = true;
    this._render();
    await this.refresh();
  }

  async refresh() {
    if (!this._hass?.connection) return;
    try {
      this._status = await this._hass.connection.sendMessagePromise({ type: WS_GET_STATUS });
      if (!this._selected && this._status.devices?.length) this._selected = this._status.devices[0].device_id;
    } catch (err) {
      this._status = { _error: err?.message || "WebSocket error", global: {}, devices: [] };
    }
    this._render();
  }

  async _setEnable(enabled) {
    await this._hass.callService(DOMAIN, "set_enable_control", { enabled });
    await this.refresh();
  }

  async _setSuspend(deviceId, suspended) {
    await this._hass.callService(DOMAIN, suspended ? "suspend_device_policy" : "resume_device_policy", { device_id: deviceId });
    await this.refresh();
  }

  _devices() {
    let devices = [...(this._status?.devices || [])];
    const f = this._filters;
    if (f.status !== "all") {
      devices = devices.filter((d) => {
        if (f.status === "protected") return d.blockers?.length || d.active_state === "active";
        if (f.status === "on") return d.desired_switch_state === "on";
        if (f.status === "off") return d.desired_switch_state === "off";
        if (f.status === "would-cut") return d.desired_switch_state === "off" || d.stable_off_remaining_s;
        return true;
      });
    }
    if (f.policy !== "all") devices = devices.filter((d) => d.policy === f.policy);
    if (f.kind !== "all") devices = devices.filter((d) => d.kind === f.kind);
    devices.sort((a, b) => f.sort === "policy" ? a.policy.localeCompare(b.policy) || a.name.localeCompare(b.name) : a.name.localeCompare(b.name));
    return devices;
  }

  _render() {
    const s = this._status || { global: {}, devices: [] };
    const global = s.global || {};
    const ctx = global.context || {};
    const selected = (s.devices || []).find((d) => d.device_id === this._selected) || (s.devices || [])[0] || null;
    const enable = !!global.enable_control;
    this.shadowRoot.innerHTML = `
      <style>${CSS}</style>
      <div class="app">
        <div class="top">
          <div class="brand"><div class="logo">♜</div><div><h1>plug_policy</h1><small>Plug Hub Observability</small></div></div>
          <div class="top-actions"><button class="btn">⚙ Integration</button><button class="iconbtn" id="refreshTop">↻</button></div>
        </div>
        <section class="hero">
          <div class="hero-title"><div class="lock">▣</div><div><h2>Control Gate</h2><code>enable_control</code></div></div>
          <div class="gate">
            <button id="shadowGate" class="${!enable ? "active shadow" : "shadow"}">● Shadow<span>decides + shows, switches nothing</span></button>
            <button id="liveGate" class="${enable ? "active live" : "live"}">● Live<span>switches plugs automatically</span></button>
          </div>
          <div class="notice"><b>${enable ? "Live-Modus ist aktiv." : "Shadow-Modus ist aktiv."}</b>${enable ? "Schaltbefehle werden automatisch ausgefuehrt." : "Entscheidungen werden berechnet und angezeigt, aber keine Schaltbefehle ausgefuehrt."}</div>
        </section>
        <section class="context">
          <span class="why">Warum diese Entscheidungen?</span>
          ${this._contextChip("green", "⌂", "Presence", ctx.presence)}
          ${this._contextChip("green", "◌", "Bio", ctx.bio)}
          ${this._contextChip("orange", "☀", "Tagesphase", ctx.day_phase)}
          ${this._contextChip("blue", "⌁", "Media", ctx.media_context)}
          ${this._contextChip("blue", "◇", "Gaming", ctx.gaming_source)}
          ${this._contextChip("pink", "▣", "Entertainment", ctx.entertainment_active)}
        </section>
        <div class="work">
          <section class="left">
            ${this._toolbar()}
            <div class="grid">${this._devices().map((d) => this._card(d, selected?.device_id)).join("") || `<div class="card"><div class="row">Keine Devices</div></div>`}</div>
            ${this._trace(selected, enable)}
          </section>
          ${this._detail(selected)}
        </div>
        <div class="foot">Letztes Update: ${this._lastUpdate(global.last_update_ts)}</div>
      </div>`;
    this._wire();
  }

  _contextChip(color, icon, label, value) {
    return `<span class="chip ${color}">${icon} ${label}: ${esc(fmt(value))}</span>`;
  }

  _toolbar() {
    const policies = [...new Set((this._status?.devices || []).map((d) => d.policy))].sort();
    const kinds = [...new Set((this._status?.devices || []).map((d) => d.kind))].sort();
    return `<div class="toolbar">
      <div class="tools">
        <button class="iconbtn">▽</button>
        ${this._select("policy", [["all","Policy"], ...policies.map((p) => [p,p])])}
        ${this._select("kind", [["all","Kind"], ...kinds.map((k) => [k,k])])}
        ${this._select("sort", [["name","Sort: Name A-Z"],["policy","Sort: Policy"]])}
      </div>
      <div class="filters">
        ${this._filter("would-cut", "red", "wuerde-cutten")}
        ${this._filter("protected", "green", "geschuetzt")}
        ${this._filter("on", "blue", "on")}
        ${this._filter("off", "red", "off")}
        <button class="iconbtn" id="refresh">↻</button>
      </div>
    </div>`;
  }

  _select(key, options) {
    return `<select class="select" data-select="${key}">${options.map(([v,l]) => `<option value="${esc(v)}" ${this._filters[key] === v ? "selected" : ""}>${esc(l)}</option>`).join("")}</select>`;
  }

  _filter(id, color, label) {
    return `<span class="chip ${color} ${this._filters.status === id ? "active" : ""}" data-filter="${id}">${label}</span>`;
  }

  _card(d, selectedId) {
    const blockers = d.blockers?.length ? d.blockers.map((b) => `<span class="mini">${esc(b)}</span>`).join("") : "-";
    return `<article class="card ${d.device_id === selectedId ? "selected" : ""}" data-device="${esc(d.device_id)}">
      <div class="cardhead"><span class="kind">${kindIcon(d.kind)}</span><span class="name">${esc(d.name)}</span><span class="policy">${esc(d.policy)}</span><span class="dots">⋮</span></div>
      <div class="row"><span class="label">Ist:</span><span class="state-line"><span class="dot ${stateClass(d.switch_state)}"></span><b class="${stateClass(d.switch_state)}">${esc(fmt(d.switch_state).toUpperCase())}</b>${d.metered ? `<span>${esc(fmt(d.power_w, 0))} W</span><span>active_state</span><b class="${d.active_state === "active" ? "on" : "keep"}">${esc(d.active_state)}</b>` : ``}</span></div>
      <div class="row"><span class="label">Soll:</span><span class="state-line"><b class="${desiredClass(d.desired_switch_state)}">⊙ ${esc(d.desired_switch_state)}</b></span></div>
      <div class="row"><span class="label">Grund:</span><span class="reason">${esc(d.reason)}</span></div>
      <div class="row"><span class="label">Blocker:</span><span class="blockers">${blockers}</span></div>
      ${this._widget(d)}
      <div class="suspend"><span>Suspend Policy</span><span class="toggle ${d.suspended ? "on" : ""}" data-suspend="${esc(d.device_id)}"></span></div>
    </article>`;
  }

  _widget(d) {
    const w = d.kind_widget || {};
    if (w.type === "tablet") return `<div class="widget">Battery ${esc(fmt(w.battery_pct))}%<br><b class="blue">${esc(w.low)} / ${esc(w.high)}</b>${w.guard ? `<br><b class="red">&lt;20% guard</b>` : ""}</div>`;
    if (w.type === "diffuser") return `<div class="widget">Phase<br><b>${esc(w.phase)}</b><br>Countdown ${seconds(w.countdown_s)}</div>`;
    if (w.type === "pc" && w.cooldown_remaining_s) return `<div class="widget">Cooldown<br><b>${seconds(w.cooldown_remaining_s)}</b></div>`;
    return "";
  }

  _detail(d) {
    if (!d) return `<aside class="detail"><div class="detail-head"><h2>Detail / Trace</h2></div><p>Kein Device ausgewaehlt.</p></aside>`;
    const t = d.thresholds || {};
    const ctx = d.context_snapshot || {};
    return `<aside class="detail">
      <div class="detail-head"><h2>Detail / Trace</h2><button class="x">×</button></div>
      <div class="selected-title"><span class="kind">${kindIcon(d.kind)}</span><b>${esc(d.name)}</b><span class="policy">${esc(d.policy)}</span><b class="${stateClass(d.switch_state)}">${esc(fmt(d.switch_state).toUpperCase())}</b></div>
      <div class="section"><h3>Full reason</h3><div>${esc(d.reason)}</div></div>
      <div class="section"><h3>Blockers</h3><div class="blockers">${d.blockers?.length ? d.blockers.map((b) => `<span class="mini">${esc(b)}</span>`).join("") : "-"}</div></div>
      ${d.metered ? `<div class="section"><h3>Thresholds</h3><div class="kv"><span>active</span><b class="on">&gt; ${esc(fmt(t.active))} W</b><span>idle</span><b>&lt; ${esc(fmt(t.idle))} W</b><span>deadband</span><b class="standby">${esc(fmt(t.deadband_lower))}-${esc(fmt(t.deadband_upper))} W</b></div></div>` : ``}
      <div class="section"><h3>Stable-Off Countdown</h3><div>${seconds(d.stable_off_remaining_s)} verbleibend</div></div>
      <div class="section"><h3>Allowed Contexts</h3><div class="blockers">${(d.allowed_contexts || []).map((c) => `<span class="chip green">${esc(c)}</span>`).join("") || "-"}</div></div>
      <div class="section"><h3>Context Snapshot</h3><div class="kv">${Object.entries(ctx).map(([k,v]) => `<span>${esc(k)}</span><span>${esc(fmt(v))}</span>`).join("")}</div></div>
      <button class="btn debug" id="debugExport">⇩ Debug-Export</button>
    </aside>`;
  }

  _trace(d, enable) {
    if (!d) return "";
    const protectedReason = d.blockers?.length ? d.blockers.join(", ") : d.active_state === "active" ? "active_state: active" : "no blocker";
    const action = enable ? "Action (Live)" : "Action (Shadow)";
    return `<section class="trace"><h2>Diagnose / Trace</h2><div class="chain">
      <div class="node"><span class="okmark">●</span><b>Context OK</b><small>${esc(Object.values(d.context_snapshot || {}).filter((v) => v !== null && v !== undefined).join(", ") || "-")}</small></div>
      <div class="node"><span class="okmark">●</span><b>Device Active</b><small>${d.metered ? `${esc(fmt(d.power_w, 0))} W, active_state: ${esc(d.active_state)}` : `kein Strommesser`}</small></div>
      <div class="node"><span class="okmark">●</span><b>Protected</b><small>${esc(protectedReason)}</small></div>
      <div class="node active"><span class="okmark">●</span><b>Desired: ${esc(d.desired_switch_state)}</b><small>${esc(d.reason)}</small></div>
      <div class="node"><span class="${enable ? "okmark" : "standby"}">●</span><b>${action}</b><small>${enable ? "switch service allowed" : "Keine Schaltaktion, nur Anzeige"}</small></div>
    </div></section>`;
  }

  _lastUpdate(ts) {
    if (!ts) return "-";
    return new Date(Number(ts) * 1000).toLocaleTimeString();
  }

  _wire() {
    this.shadowRoot.getElementById("refresh")?.addEventListener("click", () => this.refresh());
    this.shadowRoot.getElementById("refreshTop")?.addEventListener("click", () => this.refresh());
    this.shadowRoot.getElementById("shadowGate")?.addEventListener("click", () => this._setEnable(false));
    this.shadowRoot.getElementById("liveGate")?.addEventListener("click", () => this._setEnable(true));
    this.shadowRoot.querySelectorAll("[data-device]").forEach((el) => el.addEventListener("click", () => {
      this._selected = el.dataset.device;
      this._render();
    }));
    this.shadowRoot.querySelectorAll("[data-filter]").forEach((el) => el.addEventListener("click", () => {
      this._filters.status = this._filters.status === el.dataset.filter ? "all" : el.dataset.filter;
      this._render();
    }));
    this.shadowRoot.querySelectorAll("[data-select]").forEach((el) => el.addEventListener("change", () => {
      this._filters[el.dataset.select] = el.value;
      this._render();
    }));
    this.shadowRoot.querySelectorAll("[data-suspend]").forEach((el) => el.addEventListener("click", (ev) => {
      ev.stopPropagation();
      const d = (this._status?.devices || []).find((x) => x.device_id === el.dataset.suspend);
      if (d) this._setSuspend(d.device_id, !d.suspended);
    }));
    this.shadowRoot.getElementById("debugExport")?.addEventListener("click", () => {
      const blob = new Blob([JSON.stringify(this._status?.debug_export || {}, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "plug_policy_debug_export.json";
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}

if (!customElements.get("plug-policy-panel")) {
  customElements.define("plug-policy-panel", PlugPolicyPanel);
}
