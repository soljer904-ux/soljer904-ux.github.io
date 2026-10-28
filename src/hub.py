"""Hub page (/hub/) for the public meal-plan site. Called from build.py main().

Phone-first static copy of the Family Hub: public links only (meal plan, family page,
training, Spotify). No private cursor.com Pages, no money/pay/salary, no card or Clubcard
numbers. build.py runs a privacy scan over this page.
"""
import html, json, datetime
from glass_extras import SCENE_HTML, SWITCHER_HTML, SWITCHER_JS

def e(s): return html.escape(str(s), quote=True)

HUB_CSS = r'''
.fam-nav{margin:0 0 14px;font-size:1rem}
.fam-nav a{margin-right:14px;display:inline-block}
.fcard{background:#FFFBF3;background:var(--card);border:3px solid #D9A85F;border:3px solid var(--line);border-radius:22px;padding:16px 18px;margin:0 0 16px}
.fcard h2{font-size:1.35rem;margin:0 0 8px}
.fcard h3{font-size:1.15rem;margin:14px 0 6px}
.links-grid{display:grid;gap:10px;grid-template-columns:1fr}
@media(min-width:640px){.links-grid{grid-template-columns:1fr 1fr}}
.lcard{display:block;text-decoration:none;color:inherit;background:#FFF3DC;background:var(--bg);border:2px solid #D9A85F;border:2px solid var(--line);border-radius:16px;padding:14px 16px;min-height:72px}
.lcard strong{display:block;font-size:1.15rem;color:#A33A0C;color:var(--accent);margin-bottom:2px}
.lcard span{display:block;font-size:.95rem;opacity:.85}
.rowlist{list-style:none;margin:0;padding:0}
.rowlist li{padding:10px 0;border-top:2px dashed #D9A85F;border-top:2px dashed var(--line)}
.rowlist li:first-child{border-top:0}
.rowlist .t{font-weight:700}
.rowlist .d{display:block;font-size:.95rem;opacity:.85}
.rota{width:100%;border-collapse:collapse;font-size:1rem;margin-top:4px}
.rota th,.rota td{padding:8px 6px;border-top:1px solid #D9A85F;border-top:1px solid var(--line);text-align:left;vertical-align:top}
.rota th{font-size:.9rem;text-transform:uppercase;letter-spacing:.04em;opacity:.8}
.note{background:#FBE2B0;background:var(--tint);border-radius:14px;padding:10px 12px;font-weight:600;margin:8px 0}
'''

PAGE = r'''<!doctype html>
<html lang="en-GB" data-theme="%%THEME%%"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="1800">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">
<title>Family Hub</title>
<style>
%%CSS%%
%%HCSS%%
</style></head>
<body>
%%SCENE%%
%%SWITCHER%%
<header class="hdr"><div class="hdr-in">
<p class="deco" id="deco" aria-hidden="true">%%DECO%%</p>
<div class="hdr-row">
<div class="hdr-left"><h1>Family Hub</h1><p class="theme-tag">Quick links for phone and tablet</p></div>
<div class="clock-box"><div class="clock" id="clock"></div><div class="datefull" id="datefull">%%DATEFULL%%</div></div>
</div></div></header>
<main>
<p class="fam-nav">
<a href="../">🍽️ Meal plan</a>
<a href="../family/">👨‍👩‍👧‍👦 Family page</a>
<a href="../training/">🏋️ Training</a>
</p>

<section class="fcard" id="quick">
<h2>Quick links</h2>
<div class="links-grid">
<a class="lcard" href="../"><strong>What's for Tea?</strong><span>This week's meal plan and recipes</span></a>
<a class="lcard" href="../family/"><strong>Family page</strong><span>Bins, teas, countdowns and a joke</span></a>
<a class="lcard" href="../training/"><strong>Training portal</strong><span>Weekly plan and interval timer</span></a>
<a class="lcard" href="./"><strong>This hub</strong><span>Bookmark for quick access</span></a>
</div>
</section>

<section class="fcard" id="listening">
<h2>Listening</h2>
<h3>Audiobooks on Spotify</h3>
<div class="links-grid">
<a class="lcard" href="https://open.spotify.com/show/26fYzlJR7hh5rZZHYW9BpN" target="_blank" rel="noopener"><strong>Liar's Poker</strong><span>Michael Lewis · read by the author</span></a>
<a class="lcard" href="https://open.spotify.com/show/6fmnkPJRJlvviWakl57HnN" target="_blank" rel="noopener"><strong>The Wolf of Wall Street</strong><span>Jordan Belfort</span></a>
<a class="lcard" href="https://open.spotify.com/show/3AF0085IetY8d0d6iFMvVe" target="_blank" rel="noopener"><strong>Empire of Pain</strong><span>Patrick Radden Keefe · read by the author</span></a>
</div>
<ul class="rowlist">
<li><span class="t">Good Cop, Bad War</span><span class="d">Neil Woods · search Spotify</span></li>
<li><span class="t">Say Nothing</span><span class="d">Patrick Radden Keefe · search Spotify</span></li>
<li><span class="t">The Big Short</span><span class="d">Michael Lewis · search Spotify</span></li>
<li><span class="t">Billion Dollar Whale</span><span class="d">Tom Wright and Bradley Hope · search Spotify</span></li>
<li><span class="t">Bad Blood</span><span class="d">John Carreyrou · search Spotify</span></li>
</ul>
<h3>Morning podcasts</h3>
<div class="links-grid">
<a class="lcard" href="https://open.spotify.com/show/1Ysx8g1Iw42gESAtegrFaH" target="_blank" rel="noopener"><strong>The Rest Is Politics</strong><span>Wed and Thu at midnight</span></a>
<a class="lcard" href="https://open.spotify.com/show/0Z0KhuivFm1Ry4WIpWspPv" target="_blank" rel="noopener"><strong>Leading</strong><span>Interview spin-off · Mondays</span></a>
<a class="lcard" href="https://open.spotify.com/show/2qZ0xpaBBwf3bTYhA10KZY" target="_blank" rel="noopener"><strong>Times Radio News Briefing</strong><span>About 3 minutes · by 3:30am</span></a>
<a class="lcard" href="https://open.spotify.com/show/1410RabA4XOqO6IV8p0gYF" target="_blank" rel="noopener"><strong>FT News Briefing</strong><span>About 12 minutes · at 5am</span></a>
</div>
</section>

<section class="fcard" id="routines">
<h2>Routines</h2>
<p class="note">UK time. Ask Eve if something looks off.</p>
<table class="rota" aria-label="Routines">
<thead><tr><th>Routine</th><th>When</th><th>What it does</th></tr></thead>
<tbody>
<tr><td>Morning commute check</td><td>Mon, Tue, Thu ~5:40am</td><td>Traffic and weather for the drive</td></tr>
<tr><td>Evening commute check</td><td>Mon, Tue, Thu ~4:40pm</td><td>Traffic for the drive home</td></tr>
<tr><td>Weekly family meal plan</td><td>Saturdays ~9am</td><td>Plans the week and updates What's for Tea?</td></tr>
<tr><td>Lakeland basket ready</td><td>Fri 30 Oct, 9am (one-off)</td><td>Rebuilds the freezer box basket · no checkout</td></tr>
<tr><td>Lidl steak and mince</td><td>Sat 31 Oct, 10am (one-off)</td><td>Reminder for steaks and mince at Lidl</td></tr>
</tbody>
</table>
</section>

<section class="fcard" id="team">
<h2>Your team</h2>
<ul class="rowlist">
<li><span class="t">Eve</span><span class="d">Chief of staff: coordinates the bots, meal plans and this hub</span></li>
<li><span class="t">Ember</span><span class="d">Executive assistant: email, calendar and follow-ups</span></li>
<li><span class="t">Shopping</span><span class="d">Weekly Tesco shop and other buying</span></li>
<li><span class="t">Family Finances</span><span class="d">Budget, spending, debts and savings</span></li>
<li><span class="t">Dashboard Builder</span><span class="d">Builds dashboards from the other bots' data</span></li>
<li><span class="t">Hearthwright</span><span class="d">House upkeep, repairs and home projects</span></li>
<li><span class="t">Atlas</span><span class="d">Fitness coach: training, stretching and food</span></li>
<li><span class="t">Life Coach</span><span class="d">Goals and habits across work, family, health and money</span></li>
<li><span class="t">Compass</span><span class="d">Holidays, days out and work travel</span></li>
<li><span class="t">Day Trading</span><span class="d">Research and risk for the trading side hustle</span></li>
</ul>
</section>

<footer>Updated %%UPDATED%%. Ask Eve for files that live on her computer (shopping lists, history, home plans).</footer>
</main>
<script>
%%JSPURE%%
</script>
<script>
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
  var dp = qs("date"), override = WFT.parse(dp) ? dp : "";
  var L0 = london(), iso = override || L0.iso;
  var P = WFT.parse(iso), dow = new Date(P.t).getUTCDay();
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
})();
</script>
<script>
%%SWITCHER_JS%%
</script>
</body></html>
'''

def build_hub(*, today, css, js_pure, themes, theme0):
    th = themes[theme0]
    deco = " ".join(th["emoji"]) + "   " + " ".join(reversed(th["emoji"])) + "   " + " ".join(th["emoji"])
    themes_json = json.dumps({key: {"emoji": v["emoji"]} for key, v in themes.items()})
    rep = {
        "%%THEME%%": theme0,
        "%%CSS%%": css,
        "%%HCSS%%": HUB_CSS,
        "%%SCENE%%": SCENE_HTML,
        "%%SWITCHER%%": SWITCHER_HTML,
        "%%SWITCHER_JS%%": SWITCHER_JS,
        "%%DECO%%": e(deco),
        "%%DATEFULL%%": e(f"{today:%A} {today.day} {today:%B}"),
        "%%UPDATED%%": f"{today:%d %b %Y}",
        "%%JSPURE%%": js_pure,
        "%%THEMES_JSON%%": themes_json,
    }
    page = PAGE
    for a, b in rep.items():
        page = page.replace(a, b)
    return page
