#!/usr/bin/env python3
"""Build the public weekly meal-plan page.

Reads ../current-week.json (incl. optional "extras"), ../rotation_data.json, ../ratings.json, recipe_links.json.
Writes site/index.html (and a copy in site/public/ for deploying, so nothing else is uploaded),
plus site/public/family/index.html (family.py), /hub/ (hub.py) and /training/ (training.py).
Schema of current-week.json: see ../current-week.schema.md (days may cover any of Mon-Sun; a day's
"dish" is a rotation id or an inline dish object; optional "cook": "mel").

Testing without touching the real files:
  WEEK_JSON=/tmp/sample.json BUILD_OUT=/tmp/out python3 build.py   (or: python3 build.py /tmp/sample.json)
BUILD_OUT writes index.html into that directory only (no site/ or site/public/ copy).
BUILD_TODAY=YYYY-MM-DD fakes the build date (the no-JS fallback theme, Tonight and festive panel).

THEMES (picked in the browser from the Europe/London date, so no rebuild is needed; precedence top to bottom).
The build date only sets the fallback used when JS is off.  Preview: ?date=YYYY-MM-DD and/or ?theme=NAME.
  christmas  1 Dec - 31 Dec inclusive    red / green / gold      (festive panel: 1-17 Dec set A, 18-31 Dec set B)
  halloween  25 Oct - 31 Oct inclusive   black / purple / orange (festive panel: Halloween set)
  autumn     Sep-Nov (default look)      harvest orange / burgundy / mustard / brown / cream
  winter     Jan-Feb                     spring Mar-May   summer Jun-Aug
FESTIVE ideas live in the FESTIVE dict below (static, rendered into the HTML so the privacy scan covers them;
JS only shows/hides a window and picks one idea per day: (days since window start) % number of ideas).
No dish may appear in two windows (standing rule: never repeat a meal the following week).
"Tonight" is filled client-side from the day whose data-date is today (London); the build-time Tonight stays as no-JS fallback.
"""
import json, re, sys, html, datetime, shutil, urllib.parse
from pathlib import Path
from glass_extras import append_glass_css, SCENE_HTML, SWITCHER_HTML, SWITCHER_JS

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
sys.path.insert(0, str(ROOT))
from ratings import status  # same scoring rules as ratings.md

# Public page: none of these may appear anywhere in the output.
BLOCKED = ["Durant", "Parrish", "Jason", "Sarah", "Isla", "Amber", "Joseph", "Melanie", "Mel",
           "medication", "GLP", "Ozempic", "Mounjaro", "Wegovy", "semaglutide", "tirzepatide",
           "allerg", "diet", "weight", "appetite", "street", "road"]
NAMES = {"Durant", "Parrish", "Jason", "Sarah", "Isla", "Amber", "Joseph", "Melanie", "Mel"}
BLOCK_RE = re.compile("|".join((r"\b%s\b" if b in NAMES else "%s") % re.escape(b) for b in BLOCKED), re.I)
RATE_TO = "ember-sol+tea@mail.grokbot.com"
SPLIT_TWEAK = "Kids' version: keep it plainer and milder, sauce on the side, or serve the parts separately."

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def e(s): return html.escape(str(s), quote=True)
def safe(s): return s if s and not BLOCK_RE.search(s) else ""   # drop any line that would leak private info

COOK_TAGS = {"mel": "Mel's night"}   # first name only; the privacy scan skips exactly this tag markup
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def slug(s): return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")

def cook_tag(day):
    t = COOK_TAGS.get(str(day.get("cook") or "").strip().lower())
    return f'<span class="cook">{e(t)}</span>' if t else ""

def subtitle(days):
    """'Tuesday to Thursday' only for exactly Tue-Thu; otherwise the actual first-to-last day range."""
    wds = sorted({datetime.date.fromisoformat(d["date"]).weekday() for d in days})
    if not wds: return ""
    if wds == [1, 2, 3]: return "Tuesday to Thursday"
    if wds[0] == wds[-1]: return DAY_NAMES[wds[0]]
    return f"{DAY_NAMES[wds[0]]} to {DAY_NAMES[wds[-1]]}"

def fmt_day(iso):
    d = datetime.date.fromisoformat(iso); return f"{d:%A} {d.day} {d:%B}"

def today_london():
    """Today's date in Europe/London. BUILD_TODAY=YYYY-MM-DD overrides it for testing."""
    import os
    from zoneinfo import ZoneInfo
    o = os.environ.get("BUILD_TODAY")
    return datetime.date.fromisoformat(o) if o else datetime.datetime.now(ZoneInfo("Europe/London")).date()

def pick_tonight(week, today):
    """Tonight = the explicit 'tonight' entry if its date is today, else the planned day dated today."""
    t = week.get("tonight")
    if t and datetime.date.fromisoformat(t["date"]) == today:
        return {**t, **({"name": t["label"]} if t.get("label") else {})}
    for d in week["days"]:
        if datetime.date.fromisoformat(d["date"]) == today: return d
    return None

def inline_dish(obj, recipes):
    """An inline (non-rotation) dish: {name, time, type, recipe_url, note, [id], [ingredients], [steps], [tip]}.
    Returns a recipe-like dict with an id slug (from "id" or the name)."""
    if not obj.get("name"): sys.exit(f"inline dish needs a name: {obj}")
    did = slug(obj.get("id") or obj["name"])
    if not did: sys.exit(f"inline dish id is empty: {obj}")
    if did in recipes: sys.exit(f"inline dish id '{did}' clashes with a rotation dish; use \"dish\": \"{did}\" or give it another id")
    return {"id": did, "name": obj["name"], "time": obj.get("time", ""), "type": obj.get("type", ""),
            "recipe_url": obj.get("recipe_url", ""), "note": obj.get("note", ""),
            "ingredients": obj.get("ingredients", []), "steps": obj.get("steps", []),
            "tip": obj.get("tip", ""), "inline": True,
            **{k: obj[k] for k in EST_KEYS if k in obj}}

# Optional estimates (see ../current-week.schema.md): looked up on the day entry first, then the dish.
EST_KEYS = ("macros", "est_cost_gbp", "est_cost_portions")
def est_of(day, r):
    return {k: day[k] if k in day else r.get(k) for k in EST_KEYS}

def est_html(day, r):
    """'≈ 520 kcal · 38g protein ...' and '≈ £9.50 for the family (~£1.90 a head)'. Empty if nothing is set."""
    x = est_of(day, r); out = ""
    m = x["macros"]
    if isinstance(m, dict) and all(isinstance(m.get(k), (int, float)) for k in ("kcal", "protein_g", "carbs_g", "fat_g")):
        out += (f'<p class="est">≈ {m["kcal"]:.0f} kcal · {m["protein_g"]:.0f}g protein · {m["carbs_g"]:.0f}g carbs · '
                f'{m["fat_g"]:.0f}g fat <span class="est-q">(adult portion, estimate)</span></p>')
    c = x["est_cost_gbp"]
    if isinstance(c, (int, float)) and c > 0:
        n = x["est_cost_portions"] if isinstance(x["est_cost_portions"], int) and x["est_cost_portions"] > 0 else 5
        each = c / n
        what = "for the family" if n == 5 else f"for the whole batch, {n} portions"
        unit = "a head" if n == 5 else "a portion"
        out += f'<p class="est">≈ £{c:.2f} {what} <span class="est-q">(~£{each:.2f} {unit}, estimate)</span></p>'
    return out

# ---------------------------------------------------------------- themes, festive ideas, CSS, JS (static)
THEMES = {
  "autumn":    {"emoji": ["🍂", "🍁", "🌰", "🍄", "🍎"], "tag": "Harvest-time dinners",
                "vars": {"bg": "#FFF3DC", "fg": "#35190A", "muted": "#5E3A1E", "card": "#FFFBF3", "line": "#D9A85F",
                         "accent": "#A33A0C", "accent2": "#E8A317", "tint": "#FBE2B0", "hdrbg": "#7B1E2B", "hdrfg": "#FFF3DC",
                         "herobg": "#A8420F", "herofg": "#FFF8EC", "today": "#FFE08A"}},
  "halloween": {"emoji": ["🎃", "👻", "🦇", "🕷️", "🕸️"], "tag": "Spooky season dinners",
                "vars": {"bg": "#150F20", "fg": "#F7F0FF", "muted": "#D3C6EA", "card": "#251A3A", "line": "#6A47A3",
                         "accent": "#FFA23A", "accent2": "#FF7A00", "tint": "#36264F", "hdrbg": "#07040C", "hdrfg": "#FFA23A",
                         "herobg": "#4C1D7D", "herofg": "#FFFFFF", "today": "#5A3200"}},
  "christmas": {"emoji": ["🎄", "❄️", "⭐", "🔔", "🎁"], "tag": "Festive season dinners",
                "vars": {"bg": "#F7F1E0", "fg": "#1B2A1E", "muted": "#41524A", "card": "#FFFDF6", "line": "#C9B27A",
                         "accent": "#0F6B3A", "accent2": "#D4A017", "tint": "#E3F0E2", "hdrbg": "#A4161A", "hdrfg": "#FFF8E1",
                         "herobg": "#0F5132", "herofg": "#FFFDF3", "today": "#FFE9A6"}},
  "winter":    {"emoji": ["❄️", "⛄", "🧣", "☕", "🧤"], "tag": "Cosy winter dinners",
                "vars": {"bg": "#EAF3FB", "fg": "#10243E", "muted": "#3B536E", "card": "#FFFFFF", "line": "#9BBFE0",
                         "accent": "#1B5AA6", "accent2": "#6FB1E6", "tint": "#D5E7F7", "hdrbg": "#1F4E79", "hdrfg": "#F2F8FF",
                         "herobg": "#17375E", "herofg": "#F2F8FF", "today": "#BFE0FF"}},
  "spring":    {"emoji": ["🌷", "🐣", "🌱", "🌼", "🦋"], "tag": "Fresh spring dinners",
                "vars": {"bg": "#F3FAEC", "fg": "#1C3318", "muted": "#43603C", "card": "#FFFFFF", "line": "#A9D18E",
                         "accent": "#2C7A30", "accent2": "#E0699B", "tint": "#DFF1D2", "hdrbg": "#2E7D32", "hdrfg": "#FFFFFF",
                         "herobg": "#276B2B", "herofg": "#FFFFFF", "today": "#FFD9E8"}},
  "summer":    {"emoji": ["☀️", "🍉", "🌻", "🍦", "🕶️"], "tag": "Sunny summer dinners",
                "vars": {"bg": "#FFFAE0", "fg": "#2E2400", "muted": "#5A4A10", "card": "#FFFFFF", "line": "#E8CB60",
                         "accent": "#005F8F", "accent2": "#FFB300", "tint": "#FFEDA8", "hdrbg": "#00689B", "hdrfg": "#FFFFFF",
                         "herobg": "#B8400C", "herofg": "#FFFFFF", "today": "#C9ECFF"}},
}
AUT = THEMES["autumn"]["vars"]

def theme_for(d):
    """Mirror of the JS picker: Christmas all December, Halloween 25-31 Oct, else meteorological season."""
    if d.month == 12: return "christmas"
    if d.month == 10 and 25 <= d.day <= 31: return "halloween"
    if d.month in (9, 10, 11): return "autumn"
    if d.month in (1, 2): return "winter"
    if d.month in (3, 4, 5): return "spring"
    return "summer"

# Festive dinner ideas. Windows: start is MM-DD, the idea shown on a day is (days since start) % len(ideas).
# Every URL was checked with curl (HTTP 200) when written. No dish may appear in two windows.
# Keep from-scratch, family-friendly, no names/health/address words (the privacy scan covers this text).
FESTIVE = {
  "halloween": {"start": "10-25", "end": "10-31", "emoji": "🎃", "title": "Festive idea: Halloween", "ideas": [
    {"name": "Witches' brew pea & bacon soup", "time": "32 min",
     "desc": "Bright green pea soup topped with crispy bacon. Serve with cheese on toast 'broomsticks'.",
     "url": "https://www.bbcgoodfood.com/recipes/witches-brew-pea-bacon-chowder"},
    {"name": "Mini monster burgers", "time": "30 min",
     "desc": "Little beef burgers with cheese 'teeth', cucumber tongues and olive eyes. Add oven wedges and salad sticks. Sit the olive eyes on top rather than using cocktail sticks for the little ones.",
     "url": "https://www.bbcgoodfood.com/recipes/mini-monster-burgers"},
    {"name": "Eyeball spaghetti & meatballs", "time": "1 hr",
     "desc": "Baked meatballs on spaghetti in a homemade tomato sauce. Top each with a mini mozzarella ball and a slice of olive for the eyeball. The recipe makes a big batch, so halve it or freeze half.",
     "url": "https://www.bbcgoodfood.com/recipes/spaghetti-meatballs"},
    {"name": "Spider pizzas", "time": "32 min",
     "desc": "Homemade pizza bases with passata, mozzarella and parmesan. Olives and salami become the spiders. Let the kids build their own.",
     "url": "https://www.bbcgoodfood.com/recipes/halloween-spider-pizzas"},
  ]},
  "xmas1": {"start": "12-01", "end": "12-17", "emoji": "🎄", "title": "Festive idea: Christmas", "ideas": [
    {"name": "Christmas tree pizza tart", "time": "30 min",
     "desc": "A tree cut from ready-rolled puff pastry, topped with passata and garlic, mozzarella and chopped ham or chipolatas. Twist the pastry offcuts into 'tinsel'.",
     "url": "https://www.bbcgoodfood.com/recipes/christmas-tree-pizza-tart"},
    {"name": "Quick roast Christmas chicken & sticky veg", "time": "1 hr 30",
     "desc": "A whole chicken roasted fast with orange butter, with honey-glazed carrots and parsnips and Brussels sprouts. Plenty left over for sandwiches.",
     "url": "https://www.bbcgoodfood.com/recipes/quick-roast-christmas-chicken-sticky-veg"},
    {"name": "Turkey twist pie", "time": "55 min",
     "desc": "Sliced turkey, ricotta and roasted veg wrapped in crisp filo and twisted into a wreath. Only four ingredients.",
     "url": "https://www.bbcgoodfood.com/recipes/turkey-twist-pie"},
    {"name": "Christmas dinner sausage rolls", "time": "50 min",
     "desc": "Turkey mince and chipolata sausage rolls with stuffing and cranberry, baked until golden. Serve with a pile of green veg.",
     "url": "https://www.bbcgoodfood.com/recipes/christmas-dinner-sausage-roll"},
  ]},
  # Order matters: 4 ideas over 18-25 Dec, so 21 Dec and 25 Dec land on the turkey crown (index 3).
  "xmas2": {"start": "12-18", "end": "12-31", "emoji": "🎄", "title": "Festive idea: Christmas", "ideas": [
    {"name": "Cheesy sprout pasta bake", "time": "50 min",
     "desc": "Penne in a homemade cheese sauce with roasted sprouts. Stir in shredded cooked ham or chicken for extra protein.",
     "url": "https://www.bbcgoodfood.com/recipes/cheesy-sprout-pasta-bake"},
    {"name": "Turkey minestrone", "time": "1 hr 5",
     "desc": "A warming veg, bean and orzo soup with shredded cooked turkey or chicken. Good with crusty bread.",
     "url": "https://www.bbcgoodfood.com/recipes/turkey-minestrone"},
    {"name": "Family fish cakes", "time": "45 min",
     "desc": "Soft fish and potato cakes with sweetcorn and cheddar, pan-fried until golden. Serve with peas.",
     "url": "https://www.bbcgoodfood.com/recipes/family-meals-easy-fish-cakes"},
    {"name": "Thyme & garlic turkey crown", "time": "2 hr",
     "desc": "A simple roast turkey crown rubbed with thyme, garlic, lemon and butter. Roast with potatoes and your favourite veg.",
     "url": "https://www.bbcgoodfood.com/recipes/thyme-garlic-turkey-crown"},
  ]},
}

def festive_for(d, theme=None):
    """(window, idx) for a date, mirroring the JS. theme overrides (preview only)."""
    key = None
    if d.month == 10 and 25 <= d.day <= 31: key = "halloween"
    elif d.month == 12 and 1 <= d.day <= 17: key = "xmas1"
    elif d.month == 12 and 18 <= d.day <= 31: key = "xmas2"
    if not key: return None
    f = FESTIVE[key]; m, dd = map(int, f["start"].split("-"))
    return key, (d - datetime.date(d.year, m, dd)).days % len(f["ideas"])

PAGE = r'''<!doctype html>
<html lang="en-GB" data-theme="%%THEME%%"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="1800">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'">
<meta name="robots" content="noindex, nofollow, noarchive"><meta name="referrer" content="no-referrer">
<title>What's for Tea? Week of %%MONDAY%%</title>
<style>
%%CSS%%
</style></head>
<body>
%%SCENE%%
%%SWITCHER%%
<header class="hdr"><div class="hdr-in">
<p class="deco" id="deco" aria-hidden="true">%%DECO%%</p>
<div class="hdr-row">
<div class="hdr-left"><h1>What's for Tea?</h1><p class="theme-tag" id="theme-tag">%%TAG%%</p></div>
<div class="clock-box"><div class="clock" id="clock"></div><div class="datefull" id="datefull">%%DATEFULL%%</div></div>
</div></div></header>
<main id="top">
<p class="sub"><strong>%%SUBTITLE%%</strong> · Week of %%WEEKOF%%</p>
<p class="sub fam-link"><a href="family/">👨‍👩‍👧‍👦 Family page</a> · <a href="hub/">🏠 Hub</a> · <a href="training/">🏋️ Training</a></p>
%%HERO%%
%%FESTIVE%%
<h2 class="sec-h">The week at a glance</h2>
<ol class="tiles">%%TILES%%</ol>
<h2 class="sec-h">Dinner details</h2>
%%WEEKCOST%%<ol class="days">%%DAYS%%</ol>
%%EXTRAS%%
<h2 class="sec-h">Recipe cards</h2>
<div class="cards">%%CARDS%%</div>
<footer>Updated %%UPDATED%%. · Glass prototype preview</footer>
</main>
<script>
%%JSPURE%%
</script>
<script>
%%JSDOM%%
</script>
<script>
%%SWITCHER_JS%%
</script>
</body></html>
'''

JS_PURE = r'''// Pure date logic (no DOM). Keep in step with theme_for() / festive_for() in build.py.
var WFT = (function () {
  var WIN = { halloween: ["10", "25", 4], xmas1: ["12", "01", 4], xmas2: ["12", "18", 4] };
  var NAMES = { autumn: 1, halloween: 1, christmas: 1, winter: 1, spring: 1, summer: 1 };
  function parse(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
    if (!m) return null;
    var y = parseInt(m[1], 10), mo = parseInt(m[2], 10), d = parseInt(m[3], 10);
    var t = new Date(Date.UTC(y, mo - 1, d));
    if (t.getUTCFullYear() !== y || t.getUTCMonth() !== mo - 1 || t.getUTCDate() !== d) return null;
    return { y: y, m: mo, d: d, t: t.getTime() };
  }
  function days(a, b) { return Math.round((b.t - a.t) / 86400000); }
  function themeFor(iso) {
    var p = parse(iso); if (!p) return "autumn";
    if (p.m === 12) return "christmas";
    if (p.m === 10 && p.d >= 25 && p.d <= 31) return "halloween";
    if (p.m >= 9 && p.m <= 11) return "autumn";
    if (p.m <= 2) return "winter";
    if (p.m <= 5) return "spring";
    return "summer";
  }
  function festiveWindow(iso) {
    var p = parse(iso); if (!p) return "";
    if (p.m === 10 && p.d >= 25 && p.d <= 31) return "halloween";
    if (p.m === 12 && p.d >= 1 && p.d <= 17) return "xmas1";
    if (p.m === 12 && p.d >= 18 && p.d <= 31) return "xmas2";
    return "";
  }
  // Index of the idea to highlight on a date inside window win (n ideas).
  function ideaIndex(iso, win, n) {
    var p = parse(iso), w = WIN[win]; if (!p || !w || !n) return 0;
    var start = parse(p.y + "-" + w[0] + "-" + w[1]);
    var k = days(start, p) % n; return k < 0 ? k + n : k;
  }
  // Theme override from ?theme=: a festive theme maps to the festive window for the date.
  function windowForTheme(theme, iso) {
    var p = parse(iso);
    if (theme === "halloween") return "halloween";
    if (theme === "christmas") return (p && p.m === 12 && p.d >= 18) ? "xmas2" : "xmas1";
    return "";
  }
  function daysUntil(iso, mo, d) {
    var p = parse(iso); if (!p) return 0;
    return days(p, parse(p.y + "-" + (mo < 10 ? "0" : "") + mo + "-" + (d < 10 ? "0" : "") + d));
  }
  return { parse: parse, themeFor: themeFor, festiveWindow: festiveWindow, ideaIndex: ideaIndex,
           windowForTheme: windowForTheme, daysUntil: daysUntil, NAMES: NAMES };
})();
'''

JS_DOM = r'''// Everything here is ES5 (plain var and function only). No network, cookies or storage.
(function () {
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var THEMES = %%THEMES_JSON%%;
  var root = document.documentElement;
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function byId(i) { return document.getElementById(i); }
  function setText(el, t) { if (el) el.textContent = t; }
  function qs(name) {
    try {
      var q = (location.search || "").replace(/^\?/, "").split("&");
      for (var i = 0; i < q.length; i++) {
        var kv = q[i].split("=");
        if (kv[0] === name) return decodeURIComponent(kv[1] || "");
      }
    } catch (e) {}
    return "";
  }
  // Europe/London date and time, falling back to the device clock if Intl/timeZone is unavailable.
  function london() {
    var now = new Date();
    var iso = now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate());
    var hh = now.getHours(), mm = now.getMinutes();
    try {
      var f = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false });
      var m = /(\d{1,2})\D+(\d{1,2})\D+(\d{4})\D+(\d{1,2})\D+(\d{2})/.exec(f.format(now));
      if (m) { iso = m[3] + "-" + pad(parseInt(m[2], 10)) + "-" + pad(parseInt(m[1], 10)); hh = parseInt(m[4], 10) % 24; mm = parseInt(m[5], 10); }
    } catch (e) {}
    return { iso: iso, hh: hh, mm: mm };
  }
  var dateParam = qs("date");
  var override = WFT.parse(dateParam) ? dateParam : "";            // preview only; ignored unless a valid date
  var themeParam = qs("theme");
  if (!WFT.NAMES[themeParam]) themeParam = "";                     // whitelist, never written to the page as-is
  window.__glassSetTheme = function (name) {
    themeParam = (name && WFT.NAMES[name]) ? name : "";
    applyAll();
    var btns = document.querySelectorAll(".ts-btn");
    for (var i = 0; i < btns.length; i++) {
      var v = btns[i].getAttribute("data-theme-set") || "";
      if ((themeParam && v === themeParam) || (!themeParam && v === "")) btns[i].classList.add("on");
      else btns[i].classList.remove("on");
    }
  };
  var loadedIso = london().iso;
  function today() { return override || loadedIso; }

  function longDate(iso) {
    var p = WFT.parse(iso); if (!p) return "";
    return DAYS[new Date(p.t).getUTCDay()] + " " + p.d + " " + MONTHS[p.m - 1];
  }
  function mark(sel, iso) {
    var els = document.querySelectorAll(sel);
    for (var i = 0; i < els.length; i++) {
      var d = els[i].getAttribute("data-date") || "";
      var cls = d < iso ? "past" : (d === iso ? "today" : "future");
      els[i].className = els[i].className.replace(/\s*\b(past|today|future)\b/g, "") + " " + cls;
    }
  }
  function applyTheme(iso) {
    var name = themeParam || WFT.themeFor(iso);
    var t = THEMES[name] || THEMES.autumn;
    root.setAttribute("data-theme", THEMES[name] ? name : "autumn");
    var deco = byId("deco");
    if (deco) deco.textContent = t.emoji.join(" ") + "   " + t.emoji.slice().reverse().join(" ") + "   " + t.emoji.join(" ");
    var tag = t.tag;
    if (name === "christmas") {
      var n = WFT.daysUntil(iso, 12, 25);
      tag = (n >= 1 && n <= 24) ? n + " sleep" + (n === 1 ? "" : "s") + " until Christmas" : (n === 0 ? "Merry Christmas!" : t.tag);
    } else if (name === "halloween") {
      var h = WFT.daysUntil(iso, 10, 31);
      tag = (h > 0 && h <= 7) ? h + " day" + (h === 1 ? "" : "s") + " until Halloween" : (h === 0 ? "Happy Halloween!" : t.tag);
    }
    setText(byId("theme-tag"), tag);
    return name;
  }
  function applyFestive(iso, name) {
    var win = themeParam ? WFT.windowForTheme(themeParam, iso) : WFT.festiveWindow(iso);
    var secs = document.querySelectorAll(".festive");
    for (var i = 0; i < secs.length; i++) {
      var sec = secs[i], on = sec.getAttribute("data-window") === win;
      sec.hidden = !on;
      if (!on) continue;
      var list = sec.querySelector(".ideas"), items = list.querySelectorAll(".idea");
      var pick = WFT.ideaIndex(iso, win, items.length), arr = [], j;
      for (j = 0; j < items.length; j++) {
        var isPick = j === pick;
        items[j].className = "idea" + (isPick ? " pick" : "");
        if (isPick) arr.unshift(items[j]); else arr.push(items[j]);
      }
      for (j = 0; j < arr.length; j++) list.appendChild(arr[j]);
    }
  }
  function applyTonight(iso) {
    var slots = document.querySelectorAll(".hero-slot"), found = false;
    for (var i = 0; i < slots.length; i++) {
      var on = slots[i].getAttribute("data-date") === iso;
      slots[i].hidden = !on; if (on) found = true;
    }
    var none = byId("hero-none"); if (none) none.hidden = found;
    var nextEl = byId("hero-next"), text = "";
    if (!found) {
      var tiles = document.querySelectorAll(".tile"), best = null;
      for (var k = 0; k < tiles.length; k++) {
        var d = tiles[k].getAttribute("data-date");
        if (d > iso && (!best || d < best.getAttribute("data-date"))) best = tiles[k];
      }
      if (best) text = "Next dinner: " + longDate(best.getAttribute("data-date")) + " \u00b7 " + best.getAttribute("data-dish");
    }
    if (nextEl) { setText(nextEl, text); nextEl.hidden = !text; }
  }
  function applyAll() {
    var iso = today();
    var name = applyTheme(iso);
    applyFestive(iso, name);
    applyTonight(iso);
    mark(".tile", iso); mark(".dw", iso);
    setText(byId("datefull"), longDate(iso));
  }
  function tick() {
    var L = london();
    setText(byId("clock"), pad(L.hh) + ":" + pad(L.mm));
    // Reload shortly after midnight (London) so the next day's dinner and theme appear. Not when previewing a fixed date.
    if (!override && L.iso !== loadedIso) { location.reload(); }
  }
  applyAll(); tick();
  setInterval(tick, 20000);
  // Selected state for thumb radios (also covered by :has() in modern browsers)
  document.addEventListener("change", function (ev) {
    var t = ev.target;
    if (!t || !t.matches || !t.matches("input[type=radio][name^=\"r-\"]")) return;
    var fs = t.closest(".thumbs"); if (!fs) return;
    var labs = fs.querySelectorAll(".thumb");
    for (var i = 0; i < labs.length; i++) {
      if (labs[i].querySelector("input").checked) labs[i].classList.add("is-on");
      else labs[i].classList.remove("is-on");
    }
  });
})();
// Builds the rating email on tap. Stores nothing, makes no network requests.
document.addEventListener("click", function (ev) {
  var a = ev.target.closest && ev.target.closest("a.send"); if (!a) return;
  var box = a.closest(".rate-body"); var pick = function (p) { var i = box.querySelector('input[name^="' + p + '"]:checked'); return i ? i.value : ""; };
  var id = box.dataset.dishId, r = pick("r-"), g = pick("g-") || "everyone";
  if (!r) { ev.preventDefault(); alert("Choose thumbs up or thumbs down first."); return; }
  var c = box.querySelector("textarea").value.replace(/\s+/g, " ").trim();
  var body = ["dish_id: " + id, "dish: " + box.dataset.dish, "rating: " + r, "group: " + g, "comment: " + c, "week: " + box.dataset.week].join("\n") + "\n";
  a.href = "mailto:%%RATE_TO%%?subject=" + encodeURIComponent("Rating: " + box.dataset.dish) + "&body=" + encodeURIComponent(body);
});
'''

CSS = r'''
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;background:#FFF3DC}
[hidden]{display:none !important}
body{margin:0;background:@bg;color:@fg;font:20px/1.5 "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-family:Roboto,"Segoe UI","Helvetica Neue",Arial,sans-serif}
a{color:@accent;}
main{max-width:1180px;margin:0 auto;padding:18px 16px 48px}
h1,h2,h3,h4,p{margin-top:0}
/* header with live clock */
.hdr{background:@hdrbg;color:@hdrfg;border-bottom:8px solid @accent2;padding:10px 16px 16px}
.hdr-in{max-width:1180px;margin:0 auto}
.deco{font-size:28px;line-height:1.4;letter-spacing:.5em;white-space:nowrap;overflow:hidden;text-align:center;margin:0 0 4px}
.hdr-row{display:-webkit-box;display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap;-webkit-box-pack:justify;-ms-flex-pack:justify;justify-content:space-between;-webkit-box-align:center;-ms-flex-align:center;align-items:center}
.hdr-left{padding-right:16px}
.hdr h1{font-size:2.6rem;line-height:1.1;margin:.1em 0 .1em;color:@hdrfg}
.theme-tag{font-size:1.15rem;margin:0;color:@hdrfg;font-weight:600}
.mode{display:inline-block;background:@accent2;color:#2A1600;border-radius:999px;padding:.15em .9em;font-weight:700;font-size:.95rem;margin:0 0 .3em}
.clock-box{text-align:right}
.clock{font-size:5.2rem;line-height:1;font-weight:800;letter-spacing:.02em;min-height:1em}
.datefull{font-size:1.6rem;font-weight:700;margin-top:.1em}
.sub{color:@muted;margin:.2em 0 .9em;font-size:1.05rem}
/* hero: tonight */
.tonight{background:@herobg;color:@herofg;border:6px solid @accent2;border-radius:24px;padding:20px 26px 24px;margin:0 0 22px}
.tonight .kicker{margin:0;font-weight:800;font-size:1.35rem;text-transform:uppercase;letter-spacing:.1em;color:@herofg}
.tonight h2{font-size:1.15rem;color:@herofg;margin:.1em 0 0;font-weight:600}
.tonight .dish{font-size:2.7rem;line-height:1.15;font-weight:800;margin:.15em 0}
.tonight .meta{color:@herofg;font-size:1.15rem}
.tonight .none{font-size:2.3rem;font-weight:800;margin:.3em 0 .1em}
.tonight .next{font-size:1.25rem;margin:0}
.tonight .note,.tonight .tweak{background:rgba(255,255,255,.18);color:@herofg}
.tonight .btn{background:@herofg;color:@herobg;border-color:@herofg}
.tonight .cook{background:@accent2;color:#2A1600}
.tonight .badge{color:@herofg}
.tonight legend,.tonight .hint,.tonight .c{color:@herofg}
.tonight fieldset{border-color:@herofg}
.tonight textarea{background:#fff;color:#222}
/* week at a glance */
.sec-h{font-size:1.5rem;margin:26px 0 8px;color:@fg}
.tiles{list-style:none;padding:0;margin:0 -6px;display:-webkit-box;display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap}
.tile{width:50%;padding:6px}
.tile a{display:block;height:100%;min-height:150px;text-decoration:none;color:@fg;background:@card;border:3px solid @line;border-radius:18px;padding:12px 14px;position:relative}
.t-day{display:block;font-size:1.2rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;color:@accent}
.t-date{display:block;font-size:1.05rem;color:@muted}
.t-dish{display:block;font-size:1.3rem;font-weight:700;line-height:1.25;margin-top:.3em}
.t-meta{display:block;font-size:1.05rem;color:@muted;margin-top:.2em}
.t-now{display:none;position:absolute;top:10px;right:10px;background:@accent2;color:#2A1600;font-weight:800;font-size:1rem;border-radius:999px;padding:.05em .7em;text-transform:uppercase}
.tile.today a{background:@today;border-color:@accent2;border-width:5px}
.tile.today .t-now{display:block}
.tile.past,.dw.past{opacity:.55}
/* day details */
.days{list-style:none;padding:0;margin:0 -8px;display:-webkit-box;display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap}
.dw{width:100%;padding:8px}
.day,.card{background:@card;border:2px solid @line;border-radius:18px;padding:16px 18px;height:100%}
.dw.today .day{border-color:@accent2;border-width:5px;background:@today}
.day h2{font-size:1.05rem;text-transform:uppercase;letter-spacing:.05em;color:@muted;margin:0}
.dish{font-size:1.5rem;font-weight:700;line-height:1.25;margin:.25em 0}
.meta{color:@muted;margin:0 0 .5em;font-size:1.05rem}
.est{color:@muted;margin:0 0 .3em;font-size:1.05rem;font-weight:600}.est-q{font-weight:400}
.tonight .est{color:@herofg}
.note,.tweak{background:@tint;border-radius:12px;padding:.5em .75em;margin:.5em 0}
.links{display:-webkit-box;display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap;margin:.5em -4px 0}
.links>*{margin:4px}
.btn{display:inline-block;padding:.6em 1em;border:2px solid @line;border-radius:12px;color:@accent;background:@card;text-decoration:none;font-weight:700;font-size:1.05rem;min-height:48px;line-height:1.3}
.cook{display:inline-block;margin:.35em .4em 0 0;background:@tint;color:@accent;border:1px solid @accent2;border-radius:999px;padding:.1em .75em;font-weight:700;font-size:1rem}
.badge{display:inline-block;margin:.4em 0 0;font-weight:700;font-size:1.05rem}
.rate{margin-top:.6em}.rate summary{list-style:none;cursor:pointer;display:inline-block}.rate summary::-webkit-details-marker{display:none}
.rate-body{margin-top:.6em}
.rate-body>*{margin-bottom:.5em}
fieldset{border:2px solid @line;border-radius:12px;margin:0 0 .5em;padding:.4em .8em;display:-webkit-box;display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap}
legend{color:@muted;font-size:1rem}
fieldset label{min-height:48px;display:-webkit-box;display:-ms-flexbox;display:flex;-webkit-box-align:center;-ms-flex-align:center;align-items:center;margin-right:1.2em;font-size:1.05rem}
input[type=radio]{width:26px;height:26px;margin:0 .45em 0 0}
.c{display:block;color:@muted;font-size:1.05rem}
textarea{display:block;font:inherit;color:@fg;background:@bg;border:2px solid @line;border-radius:12px;padding:.5em;width:100%;margin-top:.3em}
.hint{color:@muted;font-size:1rem;margin:0}
.send{margin-top:.3em}
/* festive panel */
.festive{background:@tint;border:4px dashed @accent2;border-radius:22px;padding:16px 18px 12px;margin:0 0 22px}
.fest-h{font-size:1.6rem;margin:0 0 .1em;color:@fg}
.ideas{list-style:none;padding:0;margin:0 -6px;display:-webkit-box;display:-ms-flexbox;display:flex;-ms-flex-wrap:wrap;flex-wrap:wrap}
.idea{width:100%;padding:6px}
.idea-in{background:@card;border:2px solid @line;border-radius:16px;padding:12px 16px;height:100%}
.idea.pick{width:100%}
.idea.pick .idea-in{border:5px solid @accent2;background:@today}
.idea h3{font-size:1.3rem;margin:0 0 .2em}
.idea.pick h3{font-size:1.7rem}
.idea p{margin:0 0 .4em}
.pick-tag{display:none;background:@accent2;color:#2A1600;font-weight:800;border-radius:999px;padding:.05em .8em;font-size:1rem;margin-bottom:.4em;text-transform:uppercase}
.idea.pick .pick-tag{display:inline-block}
/* extras, cards */
.extras{margin-top:30px}.extras-h{font-size:1.5rem;margin:0 0 .2em}
.cards{margin-top:12px}
.card{margin-bottom:14px;height:auto}
.card h3{font-size:1.4rem;margin:0 0 .4em}.card h4{margin:1em 0 .3em}
dl{margin:0}dt{color:@muted;float:left;clear:left;margin-right:.8em}dd{margin:0 0 .3em}dd:after{content:"";display:block;clear:both}
ol li,ul li{margin:.25em 0}
footer{color:@muted;font-size:1rem;margin-top:28px}
@media (min-width:560px){.tile{width:33.333%}}
@media (min-width:700px){.dw{width:50%}.idea{width:50%}}
@media (min-width:900px){.tile{width:25%}.idea{width:33.333%}.idea.pick{width:100%}}
@media (min-width:1100px){.dw{width:33.333%}}
@media (max-width:640px){.hdr h1{font-size:2rem}.clock{font-size:3.6rem}.datefull{font-size:1.3rem}.clock-box{text-align:left;margin-top:.4em}.tonight .dish{font-size:2.1rem}.deco{font-size:22px}}
@media print{.deco{display:none}}
'''
CSS_THEME_BLOCKS = "".join(
    'html[data-theme="%s"]{%s}\n' % (n, "".join("--%s:%s;" % (k, v) for k, v in t["vars"].items())) for n, t in THEMES.items())
CSS_ROOT = ":root{%s}\n" % "".join("--%s:%s;" % (k, v) for k, v in AUT.items())

def build_css():
    """Autumn literal fallback first, then the var() version, for every declaration that uses a @token."""
    def sub(m):
        prop, val = m.group(1), m.group(2)
        lit = re.sub(r"@(\w+)", lambda k: AUT[k.group(1)], val)
        var = re.sub(r"@(\w+)", lambda k: "var(--%s)" % k.group(1), val)
        return "%s:%s;%s:%s;" % (prop, lit, prop, var)
    base = CSS_ROOT + CSS_THEME_BLOCKS + re.sub(r"([a-z-]+):([^;{}]*@\w[^;{}]*);", sub, CSS)
    return append_glass_css(base)

def main():
    import os
    week_path = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WEEK_JSON") or ROOT / "current-week.json")
    out_dir = os.environ.get("BUILD_OUT")
    week = load(week_path)
    data = load(ROOT / "rotation_data.json"); recipes = {r["id"]: r for r in data["recipes"]}
    # Resolve inline dish objects into recipe-like entries keyed by their slug id; days then carry the id.
    def resolve(day):
        if isinstance(day.get("dish"), dict):
            r = inline_dish(day["dish"], recipes)
            prev = recipes.get(r["id"])
            if prev and prev.get("inline") and prev != r: sys.exit(f"two different inline dishes share id '{r['id']}'")
            recipes[r["id"]] = r
            return {**day, "dish": r["id"]}
        return day
    week["days"] = sorted((resolve(d) for d in week.get("days", [])), key=lambda d: d["date"])
    if week.get("tonight"): week["tonight"] = resolve(week["tonight"])
    if week.get("extras"): week["extras"] = {**week["extras"], "dishes": [resolve(d) for d in week["extras"].get("dishes", [])]}
    ratings = load(ROOT / "ratings.json")["dishes"]
    links = load(SITE / "recipe_links.json")
    monday = datetime.date.fromisoformat(week["week_of"])
    if monday.weekday() != 0: sys.exit(f"week_of {monday} is not a Monday")
    seen = set()
    for d in week["days"]:
        dd = datetime.date.fromisoformat(d["date"])
        if not monday <= dd <= monday + datetime.timedelta(days=6): sys.exit(f"day {dd} is outside the week of {monday} (Mon-Sun)")
        if dd in seen: sys.exit(f"two dinners on {dd}")
        seen.add(dd)

    today = today_london()
    tonight = pick_tonight(week, today)

    def render(day, idx, heading=None):
        dish_id = day["dish"]
        d0 = datetime.date.fromisoformat(day["date"]) if day.get("date") else monday
        wk = (d0 - datetime.timedelta(days=d0.weekday())).isoformat()
        if dish_id not in recipes: sys.exit(f"unknown dish {dish_id}")
        r = recipes[dish_id]; name = day.get("name", r["name"])
        rd = ratings.get(dish_id, {})
        fav = bool(rd.get("kids_favourite"))
        st, detail = status(rd.get("entries", []), fav)
        if fav and rd.get("entries"):
            base = status(rd["entries"])
            if base[0] == "split": st, detail = base    # still show the kids' tweak if split
        tweak = day.get("kids_tweak") or (f"Split rating ({detail.split('.')[0]}). {SPLIT_TWEAK}" if st == "split" else "")
        dish_links = day.get("links") or links.get(dish_id) or ([{"label": "Recipe", "url": r["recipe_url"]}] if r.get("recipe_url") else [])
        link_items = "".join(f'<a class="btn" href="{e(l["url"])}" rel="noopener noreferrer nofollow">{e(l["label"])}</a>' for l in dish_links)
        link_items += f'<a class="btn" href="#card-{e(dish_id)}">Recipe card</a>'
        extra = ""
        if safe(day.get("note", "")): extra += f'<p class="note">{e(day["note"])}</p>'
        if r.get("inline") and safe(r.get("note", "")) and r["note"] != day.get("note"): extra += f'<p class="note">{e(r["note"])}</p>'
        if safe(tweak): extra += f'<p class="tweak"><strong>Kids:</strong> {e(tweak)}</p>'
        badge = '<p class="badge">⭐ Kids\' favourite</p>' if fav else ""
        q = lambda subj, body: "mailto:" + RATE_TO + "?" + urllib.parse.urlencode({"subject": subj, "body": body}, quote_via=urllib.parse.quote)
        fallback_body = f"dish_id: {dish_id}\ndish: {name}\nrating: up|down\ngroup: kids|adults|everyone\ncomment: \nweek: {wk}\n"
        rate = f'''<details class="rate"><summary class="btn">Rate this</summary>
<div class="rate-body" data-dish-id="{e(dish_id)}" data-dish="{e(name)}" data-week="{e(wk)}">
<fieldset class="thumbs"><legend>Rating</legend><label class="thumb thumb-up"><input type="radio" name="r-{idx}" value="up" aria-label="Thumbs up"><span aria-hidden="true">👍</span></label><label class="thumb thumb-down"><input type="radio" name="r-{idx}" value="down" aria-label="Thumbs down"><span aria-hidden="true">👎</span></label></fieldset>
<fieldset><legend>From</legend><label><input type="radio" name="g-{idx}" value="kids"> Kids</label><label><input type="radio" name="g-{idx}" value="adults"> Adults</label><label><input type="radio" name="g-{idx}" value="everyone" checked> Everyone</label></fieldset>
<label class="c">Comment (optional)<textarea rows="2" maxlength="300" placeholder="e.g. too spicy, kids wouldn't eat it"></textarea></label>
<a class="btn send" href="{e(q("Rating: " + name, fallback_body))}">Open email to send</a>
<p class="hint">Nothing is saved on this page. This opens your email app with the rating filled in.</p></div></details>'''
        meta = " · ".join(e(x) for x in (r.get("time"), r.get("type")) if x)
        return f'''<h2>{e(heading or fmt_day(day["date"]))}</h2>{cook_tag(day)}{badge}
<p class="dish">{e(name)}</p><p class="meta">{meta}</p>{est_html(day, r)}{extra}
<div class="links">{link_items}</div>{rate}'''

    def card(dish_id):
        r = recipes[dish_id]
        ings = "".join(f"<li>{e(i)}</li>" for i in r["ingredients"] if safe(i))
        steps = "".join(f"<li>{e(s)}</li>" for s in r["steps"] if safe(s))
        rows = [("Serves", "5 (2 adults, 3 children)"), ("Time", r["time"]),
                ("Lighter adult plate", safe(r.get("healthy", ""))), ("Adult add-on", safe(r.get("adult", ""))),
                ("Tip", safe(r.get("tip", "")))]
        if r.get("inline"): rows.insert(2, ("Type", r.get("type", "")))
        dl = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in rows if v)
        body = (f"<h4>Ingredients</h4><ul>{ings}</ul>" if ings or not r.get("inline") else "") + \
               (f"<h4>Method</h4><ol>{steps}</ol>" if steps or not r.get("inline") else "")
        if r.get("inline"):
            if safe(r.get("note", "")): body += f'<p class="note">{e(r["note"])}</p>'
            if r.get("recipe_url"): body += f'<p><a class="btn" href="{e(r["recipe_url"])}" rel="noopener noreferrer nofollow">Full recipe</a></p>'
        return f'''<section class="card" id="card-{e(dish_id)}"><h3>{e(r["name"])}</h3><dl>{dl}</dl>
{body}<p><a href="#top">Back to the week</a></p></section>'''

    # --- day tiles (week at a glance) + full day cards + hero slots (Tonight is picked client-side by date)
    def tile(d):
        r = recipes[d["dish"]]; name = d.get("name", r["name"]); dd = datetime.date.fromisoformat(d["date"])
        st = "past" if dd < today else ("today" if dd == today else "future")
        return (f'<li class="tile {st}" data-date="{e(d["date"])}" data-dish="{e(name)}"><a href="#day-{e(d["date"])}">'
                f'<span class="t-now">Today</span><span class="t-day">{dd:%A}</span><span class="t-date">{dd.day} {dd:%B}</span>'
                f'<span class="t-dish">{e(name)}</span><span class="t-meta">{e(r.get("time", ""))}</span>{cook_tag(d)}</a></li>')
    def dwrap(d, i):
        dd = datetime.date.fromisoformat(d["date"])
        st = "past" if dd < today else ("today" if dd == today else "future")
        return f'<li class="dw {st}" id="day-{e(d["date"])}" data-date="{e(d["date"])}"><div class="day">{render(d, i)}</div></li>'
    tiles_html = [tile(d) for d in week["days"]]
    days_html = [dwrap(d, i) for i, d in enumerate(week["days"])]
    slots = {d["date"]: (d, f"h{i}") for i, d in enumerate(week["days"])}
    if week.get("tonight"): slots[week["tonight"]["date"]] = (week["tonight"], "ht")   # an explicit 'tonight' entry wins its date
    hero_slots = "".join(
        f'<div class="hero-slot" data-date="{e(dt)}"{"" if dt == today.isoformat() else " hidden"}>{render(d, k)}</div>'
        for dt, (d, k) in sorted(slots.items()))
    nxt = next((d for d in week["days"] if d["date"] > today.isoformat()), None)
    next_txt = f'Next dinner: {fmt_day(nxt["date"])} · {nxt.get("name", recipes[nxt["dish"]]["name"])}' if nxt else ""
    no_dinner = today.isoformat() not in slots
    hero_html = (f'<section class="tonight" id="tonight"><p class="kicker">🍽️ Tonight</p>{hero_slots}'
                 f'<div id="hero-none"{"" if no_dinner else " hidden"}><p class="none">No dinner planned today</p></div>'
                 f'<p class="next" id="hero-next"{"" if (no_dinner and next_txt) else " hidden"}>{e(next_txt if no_dinner else "")}</p></section>')
    # Optional "extras": ideas for the week that don't replace any night. The Saturday routine clears them.
    ex = week.get("extras") or {}
    ex_days = ex.get("dishes", [])
    extras_html = ""
    if ex_days:
        ex_title = safe(ex.get("title", "")) or "Extra ideas this week"
        ex_note = safe(ex.get("note", ""))
        items = "".join(f'<li class="dw"><div class="day">{render(d, f"x{i}", "Extra idea")}</div></li>' for i, d in enumerate(ex_days))
        extras_html = (f'<section class="extras" id="extras"><h2 class="extras-h">{e(ex_title)}</h2>'
                       + (f'<p class="sub">{e(ex_note)}</p>' if ex_note else "") + f'<ol class="days">{items}</ol></section>')
    # Weekly estimated cost: the planned days only (not 'tonight' from last week, not extras).
    costs = [est_of(d, recipes[d["dish"]])["est_cost_gbp"] for d in week["days"]]
    costs = [c for c in costs if isinstance(c, (int, float)) and c > 0]
    weekcost_html = ""
    if costs:
        of = "" if len(costs) == len(week["days"]) else f" ({len(costs)} of {len(week['days'])} dinners costed)"
        weekcost_html = (f'<p class="sub est-total"><strong>Estimated food cost for this week\'s dinners: ≈ £{sum(costs):.2f}</strong>{e(of)}. '
                         'Rough estimates from typical Tesco and Lidl prices, cooked from scratch; store-cupboard basics not included. '
                         'Nutrition figures are per adult portion and are estimates too.</p>')
    order = [d["dish"] for d in ([tonight] if tonight else []) + week["days"] + ex_days]
    cards_html = [card(d) for d in dict.fromkeys(order)]

    # --- festive panels: all windows are in the HTML; JS shows the one matching the London date (build date = no-JS fallback)
    fw = festive_for(today)
    def festive_section(key):
        f = FESTIVE[key]; on = fw and fw[0] == key; pick = fw[1] if on else 0
        idx = list(range(len(f["ideas"]))); idx.remove(pick); idx.insert(0, pick)
        lis = "".join(
            f'<li class="idea{" pick" if i == pick and on else ""}" data-i="{i}"><div class="idea-in"><span class="pick-tag">Today\'s pick</span>'
            f'<h3>{e(f["ideas"][i]["name"])}</h3><p>{e(f["ideas"][i]["desc"])}</p><p class="meta">⏱ {e(f["ideas"][i]["time"])} · serves 5</p>'
            f'<a class="btn" href="{e(f["ideas"][i]["url"])}" rel="noopener noreferrer nofollow">Recipe</a></div></li>' for i in idx)
        return (f'<section class="festive" data-window="{key}"{"" if on else " hidden"}>'
                f'<h2 class="fest-h">{f["emoji"]} {e(f["title"])}</h2>'
                f'<p class="sub">Fancy something festive? Today\'s pick is highlighted, and the others are there if you want a change or another night.</p>'
                f'<ol class="ideas">{lis}</ol></section>')
    festive_html = "".join(festive_section(k) for k in FESTIVE)

    theme0 = theme_for(today); th = THEMES[theme0]
    deco0 = " ".join(th["emoji"]) + "   " + " ".join(reversed(th["emoji"])) + "   " + " ".join(th["emoji"])
    if theme0 == "christmas":
        n = (datetime.date(today.year, 12, 25) - today).days
        tag0 = f"{n} sleep{'' if n == 1 else 's'} until Christmas" if 1 <= n <= 24 else ("Merry Christmas!" if n == 0 else th["tag"])
    elif theme0 == "halloween":
        n = (datetime.date(today.year, 10, 31) - today).days
        tag0 = f"{n} day{'' if n == 1 else 's'} until Halloween" if 0 < n <= 7 else ("Happy Halloween!" if n == 0 else th["tag"])
    else: tag0 = th["tag"]
    themes_json = json.dumps({k: {"emoji": v["emoji"], "tag": v["tag"]} for k, v in THEMES.items()})

    # The week's "mode" (current-week.json) is deliberately NOT shown on the public page any more.
    css = build_css()
    page = PAGE.replace("%%THEME%%", theme0).replace("%%MONDAY%%", e(f"{monday.day} {monday:%b %Y}")).replace("%%CSS%%", css) \
        .replace("%%DECO%%", e(deco0)).replace("%%TAG%%", e(tag0)).replace("%%DATEFULL%%", e(f"{today:%A} {today.day} {today:%B}")) \
        .replace("%%SUBTITLE%%", e(subtitle(week["days"]))).replace("%%WEEKOF%%", e(f"Monday {monday.day} {monday:%B %Y}")) \
        .replace("%%HERO%%", hero_html).replace("%%FESTIVE%%", festive_html).replace("%%TILES%%", "".join(tiles_html)) \
        .replace("%%WEEKCOST%%", weekcost_html).replace("%%DAYS%%", "".join(days_html)).replace("%%EXTRAS%%", extras_html).replace("%%CARDS%%", "".join(cards_html)) \
        .replace("%%UPDATED%%", f"{today:%d %b %Y}") \
        .replace("%%JSPURE%%", JS_PURE).replace("%%JSDOM%%", JS_DOM.replace("%%THEMES_JSON%%", themes_json).replace("%%RATE_TO%%", RATE_TO)).replace("%%SCENE%%", SCENE_HTML).replace("%%SWITCHER%%", SWITCHER_HTML).replace("%%SWITCHER_JS%%", SWITCHER_JS)
    # Privacy scan: HTML body (incl. festive ideas) minus the exact allowed tag, plus the JS text.
    scan = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", page, flags=re.S)
    for t in COOK_TAGS.values(): scan = scan.replace(f'<span class="cook">{e(t)}</span>', "")   # the only allowed name
    code = " ".join(re.findall(r"<script>(.*?)</script>", page, flags=re.S))   # JS text too (CSS is skipped: "font-weight")
    hit = BLOCK_RE.search(scan) or BLOCK_RE.search(code)
    if hit: sys.exit(f"privacy check failed: '{hit.group(0)}' would be published")
    # Family page (/family/): same privacy scan, no exceptions at all.
    from family import build_family
    fam = build_family(days=week["days"], recipes=recipes, monday=monday, today=today, css=css, js_pure=JS_PURE,
                       themes=THEMES, theme0=theme0, safe=safe)
    fscan = re.sub(r"<style>.*?</style>", "", fam, flags=re.S)
    hit = BLOCK_RE.search(fscan) or re.search(r"pages\.grok\.bot|cursor\.com|canvas|@|\+44|\b0\d{9,10}\b|money|financ|fitness|health|school|£|kcal|protein|carbs|calorie|macro", fscan, re.I)
    if hit: sys.exit(f"privacy check failed on family page: '{hit.group(0)}' would be published")
    # Hub (/hub/) and Training (/training/): phone-friendly public copies. No private Pages, no pay/salary/cards.
    from hub import build_hub
    from training import build_training
    hub = build_hub(today=today, css=css, js_pure=JS_PURE, themes=THEMES, theme0=theme0)
    train = build_training(today=today, css=css, js_pure=JS_PURE, themes=THEMES, theme0=theme0)
    hub_scan = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", hub, flags=re.S)
    train_scan = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", train, flags=re.S)
    PRIV_EXTRA = re.compile(
        r"pages\.grok\.bot|cursor\.com/canvas|clubcard|salary|£\d|card\s*number|cvv|sort\s*code|"
        r"Durant|Parrish|medication|Ozempic|Mounjaro|Wegovy|semaglutide|tirzepatide",
        re.I,
    )
    hit = PRIV_EXTRA.search(hub_scan) or PRIV_EXTRA.search(train_scan)
    if hit: sys.exit(f"privacy check failed on hub/training: '{hit.group(0)}' would be published")
    def write_tree(root):
        root.mkdir(parents=True, exist_ok=True)
        (root / "index.html").write_text(page, encoding="utf-8")
        for name, html in (("family", fam), ("hub", hub), ("training", train)):
            d = root / name; d.mkdir(exist_ok=True)
            (d / "index.html").write_text(html, encoding="utf-8")

    if out_dir:   # test build: write only there, leave site/ and site/public/ alone
        out = Path(out_dir)
        write_tree(out)
        print(f"wrote {out/'index.html'} ({len(page)} bytes) [test build, not deployable copy]"); return
    (SITE / "index.html").write_text(page, encoding="utf-8")
    pub = SITE / "public"; pub.mkdir(exist_ok=True)
    write_tree(pub)
    print(f"wrote {SITE/'index.html'} ({len(page)} bytes); hub+training+family in public/")

if __name__ == "__main__": main()
