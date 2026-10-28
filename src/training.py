"""Training page (/training/) for the public meal-plan site. Called from build.py main().

Phone-first weekly plan plus an interval timer (presets, beeps, vibrate, wake lock).
Plain HTML/CSS/JS, no external dependencies. Built like family.py so it shares the site look.
Assets live in training_assets/. No financial data, card numbers or Clubcard numbers.
"""
import html, json
from pathlib import Path
from glass_extras import SCENE_HTML, SWITCHER_HTML, SWITCHER_JS

ASSETS = Path(__file__).resolve().parent / "training_assets"

def e(s): return html.escape(str(s), quote=True)

TRAIN_CSS = r"""
.fam-nav{margin:0 0 14px;font-size:1rem}
.fam-nav a{margin-right:14px;display:inline-block}
.fcard{background:#FFFBF3;background:var(--card);border:3px solid #D9A85F;border:3px solid var(--line);border-radius:22px;padding:16px 18px;margin:0 0 16px}
.fcard h2{font-size:1.35rem;margin:0 0 8px}
.fcard h3{font-size:1.15rem;margin:14px 0 6px}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 16px}
.tab{flex:1 1 90px;min-height:48px;border-radius:999px;border:3px solid #D9A85F;border-color:var(--line);background:#FFFBF3;background:var(--card);color:inherit;font:inherit;font-weight:700;font-size:1.05rem;cursor:pointer;padding:10px 14px}
.tab.on{background:#A33A0C;background:var(--accent);color:#fff;border-color:#A33A0C;border-color:var(--accent)}
.panel[hidden]{display:none !important}
.props{list-style:none;margin:0 0 12px;padding:0}
.props li{padding:6px 0;border-top:1px dashed #D9A85F;border-top:1px dashed var(--line);display:flex;flex-wrap:wrap;gap:6px 12px}
.props li:first-child{border-top:0}
.props .k{font-weight:700;min-width:5.5em;color:#A33A0C;color:var(--accent)}
.rowlist{list-style:none;margin:0;padding:0}
.rowlist li{padding:10px 0;border-top:2px dashed #D9A85F;border-top:2px dashed var(--line)}
.rowlist li:first-child{border-top:0}
.rowlist .t{font-weight:700}
.rowlist .d{display:block;font-size:.95rem;opacity:.85}
.rowlist .m{display:block;font-size:.9rem;opacity:.7}
.rota{width:100%;border-collapse:collapse;font-size:.98rem;margin:6px 0 4px}
.rota th,.rota td{padding:8px 6px;border-top:1px solid #D9A85F;border-top:1px solid var(--line);text-align:left;vertical-align:top}
.rota th{font-size:.85rem;text-transform:uppercase;letter-spacing:.04em;opacity:.8}
.note{background:#FBE2B0;background:var(--tint);border-radius:14px;padding:10px 12px;font-weight:600;margin:8px 0}
.steps{margin:0;padding-left:1.2em}
.steps li{margin:.4em 0}
.timer{display:flex;flex-direction:column;gap:12px}
.timer label{font-size:.95rem;opacity:.85;font-weight:600}
.timer select,.timer input[type=number]{min-height:48px;width:100%;font:inherit;font-size:1.05rem;border-radius:12px;border:2px solid #D9A85F;border-color:var(--line);background:#FFF3DC;background:var(--bg);color:inherit;padding:10px 12px}
.custom-row{display:flex;flex-wrap:wrap;gap:10px}
.custom-row label{flex:1 1 90px;display:flex;flex-direction:column;gap:4px}
.phase-kind{text-align:center;font-size:.95rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#0F766E}
.phase-kind.rest{color:#6B5A3E}
.phase-kind.warmup,.phase-kind.cooldown{color:#3C7A3C}
.phase-kind.ready{color:#6B5A3E}
.phase-label{text-align:center;font-size:1.35rem;font-weight:800;margin-top:4px}
.phase-cue{text-align:center;font-size:1rem;opacity:.85;margin-top:2px}
.timebig{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:4.6rem;line-height:1;font-weight:800;text-align:center;letter-spacing:-.04em;padding:8px 0}
.tmeta{text-align:center;font-size:.95rem;opacity:.8}
.bar{height:10px;border-radius:999px;background:#E8D4B0;overflow:hidden}
.bar>i{display:block;height:100%;width:0;background:#14B8A6;transition:width .35s linear}
.btns{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.btns button{flex:1 1 120px;min-height:56px;border-radius:14px;border:3px solid #D9A85F;border-color:var(--line);background:#FFFBF3;background:var(--card);color:inherit;font:inherit;font-size:1.15rem;font-weight:800;cursor:pointer;padding:12px 16px;-webkit-tap-highlight-color:transparent}
.btns button.pri{background:#14B8A6;border-color:#0F766E;color:#042f2e}
.thint{text-align:center;font-size:.85rem;opacity:.75;margin:0}
@media(max-width:640px){.timebig{font-size:3.8rem}}
"""

def build_training(*, today, css, js_pure, themes, theme0):
    th = themes[theme0]
    deco = " ".join(th["emoji"]) + "   " + " ".join(reversed(th["emoji"])) + "   " + " ".join(th["emoji"])
    themes_json = json.dumps({key: {"emoji": v["emoji"]} for key, v in themes.items()})
    page = (ASSETS / "page.html").read_text(encoding="utf-8")
    timer_js = (ASSETS / "timer.js").read_text(encoding="utf-8").replace("%%THEMES_JSON%%", themes_json)
    rep = {
        "%%THEME%%": theme0,
        "%%CSS%%": css,
        "%%TCSS%%": TRAIN_CSS,
        "%%SCENE%%": SCENE_HTML,
        "%%SWITCHER%%": SWITCHER_HTML,
        "%%SWITCHER_JS%%": SWITCHER_JS,
        "%%DECO%%": e(deco),
        "%%DATEFULL%%": e(f"{today:%A} {today.day} {today:%B}"),
        "%%UPDATED%%": f"{today:%d %b %Y}",
        "%%JSPURE%%": js_pure,
        "%%TIMER_JS%%": timer_js,
    }
    for a, b in rep.items():
        page = page.replace(a, b)
    return page
