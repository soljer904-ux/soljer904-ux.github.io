(function () {
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var THEMES = %%THEMES_JSON%%;
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function byId(i) { return document.getElementById(i); }
  function qs(name) {
    var q = (location.search || "").replace(/^\?/, "").split("&");
    for (var i = 0; i < q.length; i++) { var kv = q[i].split("="); if (kv[0] === name) return decodeURIComponent(kv[1] || ""); }
    return "";
  }
  function london() {
    var now = new Date(), iso = now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate()), hh = now.getHours(), mm = now.getMinutes();
    try {
      var f = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false });
      var m = /(\d{1,2})\D+(\d{1,2})\D+(\d{4})\D+(\d{1,2})\D+(\d{2})/.exec(f.format(now));
      if (m) { iso = m[3] + "-" + pad(parseInt(m[2], 10)) + "-" + pad(parseInt(m[1], 10)); hh = parseInt(m[4], 10) % 24; mm = parseInt(m[5], 10); }
    } catch (err) {}
    return { iso: iso, hh: hh, mm: mm };
  }
  var dp = qs("date"), override = (typeof WFT !== "undefined" && WFT.parse(dp)) ? dp : "";
  var L0 = london(), iso = override || L0.iso;
  var P = (typeof WFT !== "undefined" && WFT.parse(iso)) ? WFT.parse(iso) : { d: +L0.iso.split("-")[2], m: +L0.iso.split("-")[1], t: Date.now() };
  var dow = new Date(P.t || Date.now()).getUTCDay();
  var themeParam = qs("theme");
  if (typeof WFT === "undefined" || !WFT.NAMES || !WFT.NAMES[themeParam]) themeParam = "";
  function applyPageTheme() {
    if (typeof WFT === "undefined") return;
    var th = themeParam || WFT.themeFor(iso);
    document.documentElement.setAttribute("data-theme", th);
    var em = (THEMES[th] || THEMES.autumn).emoji;
    byId("deco").textContent = em.join(" ") + "   " + em.slice().reverse().join(" ") + "   " + em.join(" ");
  }
  applyPageTheme();
  window.__glassSetTheme = function (name) {
    themeParam = (name && WFT && WFT.NAMES && WFT.NAMES[name]) ? name : "";
    applyPageTheme();
  };
  byId("datefull").textContent = DAYS[dow] + " " + P.d + " " + MONTHS[(P.m || 1) - 1];
  function tickClock() { var L = london(); byId("clock").textContent = pad(L.hh) + ":" + pad(L.mm); }
  tickClock(); setInterval(tickClock, 20000);

  var tabs = document.querySelectorAll(".tab");
  function showTab(name) {
    for (var i = 0; i < tabs.length; i++) tabs[i].className = tabs[i].getAttribute("data-tab") === name ? "tab on" : "tab";
    byId("panel-plan").hidden = name !== "plan";
    byId("panel-timer").hidden = name !== "timer";
  }
  for (var ti = 0; ti < tabs.length; ti++) (function (btn) {
    btn.onclick = function () { showTab(btn.getAttribute("data-tab")); };
  })(tabs[ti]);
  if (location.hash === "#timer") showTab("timer");

  function w(label, seconds, cue) { return { kind: "work", label: label, seconds: seconds, cue: cue || "" }; }
  function r(seconds, label) { return { kind: "rest", label: label || "Rest", seconds: seconds, cue: "" }; }
  function stretch() {
    return [
      { kind: "warmup", label: "Settle in", seconds: 20, cue: "Shoes off, phone ready" },
      w("Standing back extension", 45, "5 slow reps"), r(10, "Transition"),
      w("Hip flexor — left", 45, "Half-kneeling, gentle 6/10"), r(8, "Switch"),
      w("Hip flexor — right", 45, "Half-kneeling, gentle 6/10"), r(10, "Transition"),
      w("Figure-4 glute — left", 45, "Lying or door frame"), r(8, "Switch"),
      w("Figure-4 glute — right", 45), r(10, "Transition"),
      w("Cat-cow", 50, "8 slow reps"), r(10, "Transition"),
      w("Open-book — left", 40, "5 rotations"), r(8, "Switch"),
      w("Open-book — right", 40, "5 rotations"), r(10, "Transition"),
      w("Child's pose — centre", 30), w("Child's pose — left reach", 15), w("Child's pose — right reach", 15), r(8, "Transition"),
      w("Glute bridge", 60, "10 reps, 2s squeeze"),
      { kind: "cooldown", label: "Done — breathe", seconds: 20, cue: "Nose breathing" }
    ];
  }
  function mon() {
    var p = [{ kind: "warmup", label: "Door-to-Floor warm-up", seconds: 60, cue: "Or run Stretch preset first" }];
    for (var m = 1; m <= 10; m++) p.push(w("EMOM minute " + m, 60, "10x 12kg swings at start, then rest"));
    p.push({ kind: "cooldown", label: "Strength block next", seconds: 30, cue: "Goblet 3x12 then push-ups + rows 3x8-10" });
    return p;
  }
  function wed() {
    var p = [{ kind: "warmup", label: "Warm-up", seconds: 180, cue: "Hinges, bridges, air squats, cat-cow" }], s;
    for (s = 1; s <= 4; s++) {
      p.push(w("RFESS " + s + " L", 45, "8-10"), r(20));
      p.push(w("RFESS " + s + " R", 45, "8-10"), r(75));
    }
    for (s = 1; s <= 3; s++) {
      p.push(w("SL RDL " + s + " L", 40, "10"), r(15));
      p.push(w("SL RDL " + s + " R", 40, "10"), r(60));
    }
    for (s = 1; s <= 4; s++) p.push(w("1-arm press " + s, 50, "6-8/side"), r(75));
    for (s = 1; s <= 3; s++) p.push(w("Push-ups + flyes " + s, 70), r(75));
    p.push({ kind: "cooldown", label: "Cool-down", seconds: 120, cue: "5-8 min flexibility" });
    return p;
  }
  function fri() {
    var p = [{ kind: "warmup", label: "Warm-up", seconds: 180, cue: "Hinges, bridges, air squats, cat-cow" }], s;
    for (s = 1; s <= 5; s++) p.push(w("Clean-squat-press " + s, 70, "5/side, 12kg"), r(90));
    for (s = 1; s <= 3; s++) {
      p.push(w("TGU R " + s, 50), r(20));
      p.push(w("TGU L " + s, 50), r(60));
    }
    for (s = 1; s <= 3; s++) p.push(w("Rows + flyes " + s, 70), r(75));
    p.push({ kind: "cooldown", label: "Cool-down", seconds: 120, cue: "5-8 min flexibility" });
    return p;
  }
  function partner() {
    var p = [
      { kind: "warmup", label: "Warm-up together", seconds: 180, cue: "10 hinges, bridges, air squats, cat-cows" },
      w("Isla tip — slow hinge", 30, "Bottle at arm's length")
    ], m, s, rr;
    for (m = 1; m <= 10; m++) p.push(w("Swings min " + m, 60, "Alternate 5 each · Isla: no bell"));
    for (s = 1; s <= 3; s++) {
      p.push(w("Goblet " + s, 50, "12 reps"));
      p.push(w("Isla squats " + s, 50, "12 air/light"));
      p.push(r(45));
    }
    for (rr = 1; rr <= 3; rr++) {
      p.push(w("Push/row relay " + rr, 90, "Isla: knees or step"));
      p.push(r(45));
    }
    p.push({ kind: "cooldown", label: "High-five cool-down", seconds: 60 });
    return p;
  }
  function custom(work, rest, rounds) {
    var p = [{ kind: "warmup", label: "Warm-up", seconds: 60 }], r0;
    for (r0 = 1; r0 <= rounds; r0++) {
      p.push(w("Work " + r0, work));
      if (r0 < rounds) p.push(r(rest, "Rest " + r0));
    }
    p.push({ kind: "cooldown", label: "Cool-down", seconds: 60 });
    return p;
  }

  function buildPhases() {
    var id = byId("preset").value;
    if (id === "mon-emom") return mon();
    if (id === "stretch") return stretch();
    if (id === "wed") return wed();
    if (id === "fri") return fri();
    if (id === "partner") return partner();
    var work = Math.max(5, Math.min(600, parseInt(byId("cw").value, 10) || 40));
    var rest = Math.max(0, Math.min(600, parseInt(byId("cr").value, 10) || 20));
    var rounds = Math.max(1, Math.min(40, parseInt(byId("cn").value, 10) || 8));
    return custom(work, rest, rounds);
  }

  function fmt(total) {
    var s = Math.max(0, Math.ceil(total));
    return Math.floor(s / 60) + ":" + pad(s % 60);
  }

  var ctx = null;
  function ensureAudio() {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    if (!ctx) ctx = new AC();
    return ctx;
  }
  function unlockAudio() {
    var c = ensureAudio();
    if (!c) return;
    if (c.state === "suspended") c.resume();
    var o = c.createOscillator(), g = c.createGain();
    g.gain.value = 0.0001; o.connect(g); g.connect(c.destination);
    o.start(); o.stop(c.currentTime + 0.01);
  }
  function play(kind) {
    var c = ensureAudio();
    if (!c) return;
    if (c.state === "suspended") c.resume();
    function tone(freq, start, dur, vol) {
      vol = vol || 0.18;
      var o = c.createOscillator(), g = c.createGain();
      o.type = "sine"; o.frequency.value = freq;
      g.gain.setValueAtTime(0.0001, start);
      g.gain.exponentialRampToValueAtTime(vol, start + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
      o.connect(g); g.connect(c.destination);
      o.start(start); o.stop(start + dur + 0.02);
    }
    var t = c.currentTime;
    if (kind === "phase") tone(880, t, 0.4);
    else if (kind === "final") { tone(660, t, 0.22); tone(660, t + 0.32, 0.22); }
    else tone(990, t, 0.12, 0.14);
    try { if (navigator.vibrate) navigator.vibrate(kind === "final" ? [40, 40, 40] : 30); } catch (err) {}
  }

  var wake = null;
  function releaseWake() {
    if (wake) { try { wake.release(); } catch (err) {} wake = null; }
  }
  function requestWake() {
    try {
      if (navigator.wakeLock && navigator.wakeLock.request) {
        navigator.wakeLock.request("screen").then(function (lock) { wake = lock; }).catch(function () {});
      }
    } catch (err) {}
  }

  var phases = buildPhases();
  var running = false, paused = false, done = false, idx = 0, rem = 0;
  var timerId = null, lastSec = null, finalBeeped = false, cdBeeped = {};

  function totalSec(list) {
    var a = 0; for (var i = 0; i < list.length; i++) a += list[i].seconds; return a;
  }
  function elapsedSec() {
    var a = 0; for (var i = 0; i < idx; i++) a += phases[i].seconds;
    if (phases[idx]) a += phases[idx].seconds - rem;
    return a;
  }
  function workCount(list) {
    var n = 0; for (var i = 0; i < list.length; i++) if (list[i].kind === "work") n++; return n;
  }
  function workIndex(list, i) {
    var n = 0; for (var j = 0; j <= i && j < list.length; j++) if (list[j].kind === "work") n++; return n;
  }

  function render() {
    var phase = phases[idx];
    var kindEl = byId("kind");
    if (done) { kindEl.textContent = "Complete"; kindEl.className = "phase-kind cooldown"; }
    else if (paused) { kindEl.textContent = "Paused"; kindEl.className = "phase-kind ready"; }
    else if (running && phase) { kindEl.textContent = phase.kind; kindEl.className = "phase-kind " + phase.kind; }
    else { kindEl.textContent = "Ready"; kindEl.className = "phase-kind ready"; }
    byId("label").textContent = done ? "Session done" : (phase ? phase.label : "—");
    byId("cue").textContent = (!done && phase && phase.cue) ? phase.cue : "";
    byId("clock-t").textContent = done ? "0:00" : fmt(rem || (phase ? phase.seconds : 0));
    var tot = totalSec(phases), el = elapsedSec();
    var next = phases[idx + 1];
    var meta;
    if (running || done) {
      meta = "Phase " + Math.min(idx + 1, phases.length) + " / " + phases.length + " · " + fmt(Math.max(0, tot - el)) + " left";
      var wi = workIndex(phases, idx), wc = workCount(phases);
      if (phase && phase.kind === "work") meta += " · Work " + wi + "/" + wc;
      if (next && running && !done) meta += " · Next: " + next.label;
    } else {
      meta = phases.length + " phases · ~" + fmt(tot) + " total · " + workCount(phases) + " work rounds";
    }
    byId("tmeta").textContent = meta;
    byId("bar").style.width = (tot ? Math.min(100, (el / tot) * 100) : 0) + "%";
    byId("btn-start").hidden = !((!running && !done) || done);
    byId("btn-start").textContent = done ? "Start again" : "Start";
    byId("btn-pause").hidden = !running;
    byId("btn-pause").textContent = paused ? "Resume" : "Pause";
    byId("btn-skip").hidden = !running;
    byId("btn-reset").hidden = !(running || done || idx > 0);
    byId("preset").disabled = running;
    byId("custom-row").hidden = !(byId("preset").value === "custom" && !running);
  }

  function enter(i) {
    if (i >= phases.length) {
      running = false; paused = false; done = true; rem = 0; releaseWake();
      play("phase"); stopTick(); render(); return;
    }
    finalBeeped = false; cdBeeped = {}; lastSec = null;
    idx = i; rem = phases[i].seconds; play("phase");
    var moreWork = false;
    for (var j = i + 1; j < phases.length; j++) if (phases[j].kind === "work") { moreWork = true; break; }
    var lastWork = phases[i].kind === "work" && !moreWork;
    if (lastWork || /minute 10|min 10/i.test(phases[i].label)) { finalBeeped = true; play("final"); }
    render();
  }

  function stopTick() { if (timerId) { clearInterval(timerId); timerId = null; } }
  function startTick() {
    stopTick();
    timerId = setInterval(function () {
      if (!running || paused || done) return;
      var phase = phases[idx];
      if (!phase) return;
      if (rem <= 1) { enter(idx + 1); return; }
      var next = rem - 1;
      if (lastSec !== next) {
        lastSec = next;
        if (next === 60 && phase.seconds > 60 && !finalBeeped) { finalBeeped = true; play("final"); }
        if ((next === 3 || next === 2 || next === 1) && !cdBeeped[next]) { cdBeeped[next] = true; play("countdown"); }
      }
      rem = next; render();
    }, 1000);
  }

  function start() {
    unlockAudio(); requestWake();
    phases = buildPhases();
    done = false; paused = false; running = true;
    finalBeeped = false; cdBeeped = {}; lastSec = null;
    idx = 0; rem = phases[0] ? phases[0].seconds : 0;
    play("phase"); startTick(); render();
  }
  function reset() {
    stopTick(); running = false; paused = false; done = false;
    phases = buildPhases(); idx = 0; rem = phases[0] ? phases[0].seconds : 0;
    releaseWake(); render();
  }

  byId("btn-start").onclick = function () { start(); };
  byId("btn-pause").onclick = function () {
    if (!running) return;
    paused = !paused;
    if (paused) stopTick(); else startTick();
    render();
  };
  byId("btn-skip").onclick = function () { if (running) enter(idx + 1); };
  byId("btn-reset").onclick = function () { reset(); };
  byId("preset").onchange = function () { if (!running) reset(); };
  ["cw", "cr", "cn"].forEach(function (id) {
    byId(id).onchange = function () { if (!running) reset(); };
  });
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible" && running && !paused) requestWake();
  });
  reset();
})();
