"""Family page (/family/) for the public meal-plan site. Called from build.py main().

Kid-friendly and phone-first: this week's teas, a bin-day helper, the next family event countdown and a joke.
PUBLIC + ANONYMOUS: no names, addresses, schools, health or money. build.py's privacy scan runs over this page too.
Bin rota (computed in the browser, Europe/London date):
  food bin            every Tuesday MORNING (never out overnight: foxes)
  wheelie bins        out Monday evening for Tuesday. Weeks counted from Tue 3 Nov 2026:
                      even weeks = black (rubbish) + blue lid (cardboard); odd weeks = pink lid (plastic bottles and tins)
  garden waste        every Wednesday
"""
import html, json, datetime
from glass_extras import SCENE_HTML, SWITCHER_HTML, SWITCHER_JS

def e(s): return html.escape(str(s), quote=True)

EVENTS = [  # (iso date, emoji, title) -- public-safe wording only
    ("2026-11-07", "🎆", "Fireworks party at home"),
]

JOKES = [
    ["What do you call a sleeping dinosaur?", "A dino-snore!"],
    ["Why did the cookie go to the doctor?", "Because it felt crummy!"],
    ["What do you call a bear with no teeth?", "A gummy bear!"],
    ["Why are ghosts bad at telling lies?", "Because you can see right through them!"],
    ["What does a cloud wear under its coat?", "Thunderwear!"],
    ["Why did the banana go to the doctor?", "It wasn't peeling well!"],
    ["What do you call a fish with no eyes?", "A fsh!"],
    ["What's orange and sounds like a parrot?", "A carrot!"],
    ["Why can't you give Elsa a balloon?", "Because she'll let it go!"],
    ["What do you call a pig that does karate?", "A pork chop!"],
    ["How do you make a tissue dance?", "Put a little boogie in it!"],
    ["What did the big flower say to the little flower?", "Hi, bud!"],
    ["Why do bees have sticky hair?", "Because they use honeycombs!"],
    ["What kind of tree fits in your hand?", "A palm tree!"],
]

WOULD = [
    "Would you rather have pancakes or pizza for breakfast?",
    "Would you rather be able to fly or be invisible?",
    "Would you rather have a pet dragon or a pet unicorn?",
    "Would you rather live in a treehouse or a castle?",
    "Would you rather swim with dolphins or ride a giant tortoise?",
    "Would you rather eat only peas or only carrots for a week?",
    "Would you rather be a superhero or a wizard?",
]

FAMILY_CSS = r'''
.fam-nav{margin:0 0 14px;font-size:1rem}
.fam-grid{display:grid;gap:16px;grid-template-columns:1fr}
@media(min-width:760px){.fam-grid{grid-template-columns:1fr 1fr}}
.fcard{background:#FFFBF3;background:var(--card);border:3px solid #D9A85F;border:3px solid var(--line);border-radius:22px;padding:16px 18px}
.fcard h2{font-size:1.35rem;margin-bottom:8px}
.big{font-size:1.5rem;font-weight:700;margin:4px 0 8px}
.bins{list-style:none;margin:0;padding:0}
.bins li{display:flex;align-items:center;gap:12px;padding:8px 0;border-top:2px dashed #D9A85F;border-top:2px dashed var(--line)}
.bins li:first-child{border-top:0}
.dot{flex:0 0 38px;height:38px;border-radius:10px;border:3px solid rgba(0,0,0,.35)}
.d-black{background:#222}.d-blue{background:#1E6FD9}.d-pink{background:#F06BAA}.d-food{background:#7A4A1E}.d-garden{background:#3C9A3C}
.when{display:block;font-size:.95rem;opacity:.85}
.nudge{background:#FBE2B0;background:var(--tint);border-radius:14px;padding:10px 12px;font-weight:600;margin:8px 0}
.fox{font-size:.95rem}
.rota{width:100%;border-collapse:collapse;font-size:1rem;margin-top:8px}
.rota td{padding:5px 4px;border-top:1px solid #D9A85F;border-top:1px solid var(--line)}
.meals{list-style:none;margin:0;padding:0}
.meals li{padding:8px 10px;border-radius:12px;margin:2px 0}
.meals li.today{background:#FFE08A;background:var(--today);font-weight:700}
.meals li.past{opacity:.55}
.meals .md{display:block;font-size:.9rem;opacity:.85}
.count{font-size:2.6rem;font-weight:800;line-height:1.1;margin:6px 0}
.btn{display:inline-block;padding:10px 16px;border-radius:999px;background:#A33A0C;background:var(--accent);color:#fff;text-decoration:none;border:0;font:inherit;font-size:1rem;cursor:pointer;margin:4px 6px 4px 0}
.ans{font-size:1.25rem;font-weight:700;margin:8px 0}
'''

PAGE = r'''<!doctype html>
<html lang="en-GB" data-theme="%%THEME%%"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="1800">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">
<title>Our Family Page</title>
<style>
%%CSS%%
%%FCSS%%
</style></head>
<body>
%%SCENE%%
%%SWITCHER%%
<header class="hdr"><div class="hdr-in">
<p class="deco" id="deco" aria-hidden="true">%%DECO%%</p>
<div class="hdr-row">
<div class="hdr-left"><h1>Our Family Page</h1><p class="theme-tag">Bins, teas, countdowns and giggles</p></div>
<div class="clock-box"><div class="clock" id="clock"></div><div class="datefull" id="datefull">%%DATEFULL%%</div></div>
</div></div></header>
<main>
<p class="fam-nav">
<a href="../">🍽️ Meal plan</a>
<a href="../hub/">🏠 Hub</a>
<a href="../training/">🏋️ Training</a>
</p>
<div class="fam-grid">

<section class="fcard" id="bins"><h2>🗑️ Bin day helper</h2>
<p class="nudge" id="bin-nudge" hidden></p>
<p class="big" id="bin-week">Wheelie bins this week</p>
<ul class="bins" id="bin-list">
<li><span class="dot d-food"></span><span><strong>Food bin</strong> every Tuesday<span class="when">Put it out on Tuesday morning, never the night before 🦊</span></span></li>
<li><span class="dot d-garden"></span><span><strong>Garden waste</strong> every Wednesday</span></li>
</ul>
<p class="fox">🦊 Foxes love the food bin, so it only goes out in the morning!</p>
<table class="rota" id="rota" aria-label="Wheelie bin rota"><tbody></tbody></table>
<noscript><p>Wheelie bins alternate each Tuesday: black and blue-lid on 3 Nov, 17 Nov and 1 Dec; pink-lid on 10 Nov, 24 Nov and 8 Dec.</p></noscript>
</section>

<section class="fcard" id="meals"><h2>🍽️ This week's teas</h2>
<p class="sub">Week of %%WEEKOF%%</p>
<ol class="meals">%%MEALS%%</ol>
<p><a href="/">Recipes and details</a></p>
</section>

<section class="fcard" id="events"><h2>🎉 Coming up</h2>
%%EVENTS%%
</section>

<section class="fcard" id="fun"><h2>😄 Joke of the day</h2>
<p class="big" id="joke-q">%%JOKEQ%%</p>
<button class="btn" id="joke-btn" type="button">Tell me!</button>
<p class="ans" id="joke-a" hidden>%%JOKEA%%</p>
<h2 style="margin-top:16px">🤔 Would you rather…</h2>
<p class="big" id="wyr">%%WYR%%</p>
<button class="btn" id="wyr-btn" type="button">Another one!</button>
</section>

</div>
<footer>Updated %%UPDATED%%.</footer>
</main>
<script>
%%JSPURE%%
</script>
<script>
// ES5 only. No network, cookies or storage.
(function () {
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var THEMES = %%THEMES_JSON%%;
  var JOKES = %%JOKES_JSON%%, WOULD = %%WOULD_JSON%%;
  var ANCHOR = WFT.parse("2026-11-03");   // a black + blue week
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
    } catch (e) {}
    return { iso: iso, hh: hh, mm: mm };
  }
  var dp = qs("date"), override = WFT.parse(dp) ? dp : "";
  var hp = parseInt(qs("hour"), 10);
  var L0 = london(), iso = override || L0.iso;
  var hour = (override && hp >= 0 && hp < 24) ? hp : L0.hh;
  var P = WFT.parse(iso), dow = new Date(P.t).getUTCDay();
  function addDays(p, n) { var d = new Date(p.t + n * 86400000); return WFT.parse(d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate())); }
  function short(p) { var d = new Date(p.t); return DAYS[d.getUTCDay()].slice(0, 3) + " " + p.d + " " + MON[p.m - 1]; }
  // Wheelie bins for the collection Tuesday p: even weeks from the anchor = black + blue, odd = pink.
  function wheelie(p) {
    var w = Math.round((p.t - ANCHOR.t) / (7 * 86400000));
    return (w % 2 === 0) ? { html: '<span class="dot d-black"></span><span class="dot d-blue"></span>', txt: "Black (rubbish) and blue-lid (cardboard)", cls: "bb" }
                         : { html: '<span class="dot d-pink"></span>', txt: "Pink-lid (plastic bottles and tins)", cls: "pk" };
  }
  // Collection Tuesday for this Mon-Sun week (after Tuesday, show next week's too).
  var tue = addDays(P, 1 - ((dow + 6) % 7));            // Tuesday of this Mon-Sun week
  var nextTue = addDays(tue, 7);
  var shown = (((dow + 6) % 7) > 1) ? nextTue : tue;     // Wed-Sun: look ahead to next Tuesday
  var wb = wheelie(shown);
  var list = byId("bin-list");
  var li = document.createElement("li");
  li.innerHTML = wb.html + '<span><strong>' + wb.txt + '</strong><span class="when">Collected ' + short(shown) + '. Put out on Monday evening.</span></span>';
  list.insertBefore(li, list.firstChild);
  byId("bin-week").textContent = (shown === tue ? "This week's bins" : "Next week's bins") + " (Tuesday " + shown.d + " " + MONTHS[shown.m - 1] + ")";
  var n = "";
  if (dow === 1 && hour >= 15) n = "Tonight: put out the " + wb.txt.toLowerCase() + " bins. Not the food bin yet!";
  else if (dow === 1) n = "Tonight is wheelie bin night: " + wb.txt.toLowerCase() + ".";
  else if (dow === 2 && hour < 12) n = "This morning: food bin out now, plus the " + wb.txt.toLowerCase() + " bins if they're not out.";
  else if (dow === 3 && hour < 12) n = "Today: garden waste bin day.";
  else if (dow === 2) n = "Tomorrow is garden waste day.";
  if (n) { var ne = byId("bin-nudge"); ne.textContent = n; ne.hidden = false; }
  var rows = "";
  for (var k = 0; k < 4; k++) { var t = addDays(shown, 7 * k), w = wheelie(t); rows += "<tr><td>" + short(t) + "</td><td>" + w.html + "</td><td>" + w.txt + " + food</td></tr>"; }
  byId("rota").tBodies[0].innerHTML = rows;

  // Meals: mark today
  var ms = document.querySelectorAll(".meals li");
  for (var i = 0; i < ms.length; i++) { var d = ms[i].getAttribute("data-date"); ms[i].className = d < iso ? "past" : (d === iso ? "today" : ""); }
  // Event countdowns
  var ev = document.querySelectorAll(".event");
  for (var j = 0; j < ev.length; j++) {
    var ed = WFT.parse(ev[j].getAttribute("data-date")); var c = Math.round((ed.t - P.t) / 86400000);
    var ce = ev[j].querySelector(".count");
    if (c < 0) ev[j].hidden = true;
    else ce.textContent = c === 0 ? "It's today! 🎉" : (c + (c === 1 ? " sleep to go!" : " sleeps to go!"));
  }
  if (ev.length && !document.querySelector(".event:not([hidden])")) { var np = document.createElement("p"); np.textContent = "Nothing on the list just now."; byId("events").appendChild(np); }
  // Theme (prototype switcher can override via ?theme=)
  var themeParam = qs("theme");
  if (!WFT.NAMES[themeParam]) themeParam = "";
  function applyPageTheme() {
    var th = themeParam || WFT.themeFor(iso);
    document.documentElement.setAttribute("data-theme", th);
    var em = (THEMES[th] || THEMES.autumn).emoji;
    byId("deco").textContent = em.join(" ") + "   " + em.slice().reverse().join(" ") + "   " + em.join(" ");
  }
  applyPageTheme();
  window.__glassSetTheme = function (name) {
    themeParam = (name && WFT.NAMES[name]) ? name : "";
    applyPageTheme();
  };
  byId("datefull").textContent = DAYS[dow] + " " + P.d + " " + MONTHS[P.m - 1];
  function tick() { var L = london(); byId("clock").textContent = pad(L.hh) + ":" + pad(L.mm); }
  tick(); setInterval(tick, 20000);
  // Fun
  var dayN = Math.round(P.t / 86400000), jk = JOKES[dayN % JOKES.length];
  byId("joke-q").textContent = jk[0]; byId("joke-a").textContent = jk[1];
  byId("joke-btn").onclick = function () { byId("joke-a").hidden = false; };
  var wi = dayN % WOULD.length; byId("wyr").textContent = WOULD[wi];
  byId("wyr-btn").onclick = function () { wi = (wi + 1) % WOULD.length; byId("wyr").textContent = WOULD[wi]; };
})();
</script>
<script>
%%SWITCHER_JS%%
</script>
</body></html>
'''

def build_family(*, days, recipes, monday, today, css, js_pure, themes, theme0, safe):
    meals = []
    for d in days:
        r = recipes[d["dish"]]; name = safe(d.get("name", r["name"])) or "Something tasty"
        dd = datetime.date.fromisoformat(d["date"])
        meals.append(f'<li data-date="{e(d["date"])}"><span class="md">{dd:%A}</span>{e(name)}</li>')
    upcoming = [(iso, em, t) for iso, em, t in EVENTS if datetime.date.fromisoformat(iso) >= today]
    if upcoming:
        ev = "".join(f'<div class="event" data-date="{e(iso)}"><p class="big">{em} {e(t)}</p>'
                     f'<p>{datetime.date.fromisoformat(iso):%A} {datetime.date.fromisoformat(iso).day} {datetime.date.fromisoformat(iso):%B}</p>'
                     f'<p class="count">{(datetime.date.fromisoformat(iso) - today).days} sleeps to go!</p></div>' for iso, em, t in upcoming)
    else:
        ev = "<p>Nothing on the list just now.</p>"
    th = themes[theme0]
    deco = " ".join(th["emoji"]) + "   " + " ".join(reversed(th["emoji"])) + "   " + " ".join(th["emoji"])
    k = (today - datetime.date(1970, 1, 1)).days
    themes_json = json.dumps({key: {"emoji": v["emoji"]} for key, v in themes.items()})
    rep = {"%%THEME%%": theme0, "%%CSS%%": css, "%%FCSS%%": FAMILY_CSS, "%%SCENE%%": SCENE_HTML, "%%SWITCHER%%": SWITCHER_HTML, "%%SWITCHER_JS%%": SWITCHER_JS, "%%DECO%%": e(deco),
           "%%DATEFULL%%": e(f"{today:%A} {today.day} {today:%B}"), "%%WEEKOF%%": e(f"Monday {monday.day} {monday:%B %Y}"),
           "%%MEALS%%": "".join(meals), "%%EVENTS%%": ev, "%%JOKEQ%%": e(JOKES[k % len(JOKES)][0]),
           "%%JOKEA%%": e(JOKES[k % len(JOKES)][1]), "%%WYR%%": e(WOULD[k % len(WOULD)]), "%%UPDATED%%": f"{today:%d %b %Y}",
           "%%JSPURE%%": js_pure, "%%THEMES_JSON%%": themes_json, "%%JOKES_JSON%%": json.dumps(JOKES), "%%WOULD_JSON%%": json.dumps(WOULD)}
    page = PAGE
    for a, b in rep.items(): page = page.replace(a, b)
    return page
