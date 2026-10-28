"""Liquid-glass overlay for the meal-plan prototype (site-glass only). Not used by the live site."""

# Extra CSS variables per theme (glass fills + animated scene colours).
GLASS_VARS = {
  "autumn": {
    "glass": "rgba(255,251,243,.55)", "glass2": "rgba(255,243,220,.42)", "gline": "rgba(255,255,255,.45)",
    "gshadow": "0 8px 32px rgba(53,25,10,.18)", "ink": "#2a1408",
    "s1": "#7B1E2B", "s2": "#A8420F", "s3": "#E8A317", "s4": "#FFF3DC",
  },
  "halloween": {
    "glass": "rgba(37,26,58,.55)", "glass2": "rgba(21,15,32,.45)", "gline": "rgba(255,162,58,.28)",
    "gshadow": "0 10px 36px rgba(0,0,0,.45)", "ink": "#F7F0FF",
    "s1": "#07040C", "s2": "#4C1D7D", "s3": "#FF7A00", "s4": "#150F20",
  },
  "christmas": {
    "glass": "rgba(255,253,246,.58)", "glass2": "rgba(247,241,224,.45)", "gline": "rgba(255,255,255,.55)",
    "gshadow": "0 8px 32px rgba(27,42,30,.16)", "ink": "#142218",
    "s1": "#A4161A", "s2": "#0F5132", "s3": "#D4A017", "s4": "#F7F1E0",
  },
  "winter": {
    "glass": "rgba(255,255,255,.55)", "glass2": "rgba(234,243,251,.48)", "gline": "rgba(255,255,255,.6)",
    "gshadow": "0 8px 32px rgba(16,36,62,.16)", "ink": "#0c1c30",
    "s1": "#1F4E79", "s2": "#6FB1E6", "s3": "#EAF3FB", "s4": "#BFE0FF",
  },
  "spring": {
    "glass": "rgba(255,255,255,.55)", "glass2": "rgba(243,250,236,.48)", "gline": "rgba(255,255,255,.55)",
    "gshadow": "0 8px 32px rgba(28,51,24,.14)", "ink": "#142814",
    "s1": "#2E7D32", "s2": "#E0699B", "s3": "#DFF1D2", "s4": "#F3FAEC",
  },
  "summer": {
    "glass": "rgba(255,255,255,.55)", "glass2": "rgba(255,250,224,.48)", "gline": "rgba(255,255,255,.55)",
    "gshadow": "0 8px 32px rgba(46,36,0,.14)", "ink": "#241c00",
    "s1": "#00689B", "s2": "#B8400C", "s3": "#FFB300", "s4": "#FFFAE0",
  },
}

SCENE_HTML = '''<div class="scene" aria-hidden="true">
<div class="scene-base"></div>
<div class="scene-blob b1"></div>
<div class="scene-blob b2"></div>
<div class="scene-blob b3"></div>
<div class="scene-motif"></div>
<div class="scene-vignette"></div>
</div>
'''

SWITCHER_HTML = '''<p class="proto-banner">Liquid glass prototype · not the live site</p>
'''

# Shared switcher JS (ES5). Works with meal-plan applyAll or simple data-theme pages.
SWITCHER_JS = r'''/* theme dock removed; ?theme= still works via page JS */'''

GLASS_CSS = r'''
/* ===== Liquid glass prototype overlay ===== */
html{background:transparent !important}
body{background:transparent !important;color:var(--ink, var(--fg));position:relative;min-height:100vh;overflow-x:hidden}
body > *:not(.scene):not(.proto-banner){position:relative;z-index:1}
.proto-banner{position:fixed}

/* Fixed full-bleed animated scene (Roadster-style blend) */
.scene{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.scene-base{position:absolute;inset:0;background:
  radial-gradient(120% 80% at 10% -10%, var(--s3) 0%, transparent 55%),
  radial-gradient(100% 70% at 90% 10%, var(--s2) 0%, transparent 50%),
  linear-gradient(165deg, var(--s1) 0%, var(--s2) 42%, var(--s4) 78%, var(--s4) 100%);
  background-size:120% 120%;animation:sceneDrift 28s ease-in-out infinite alternate}
.scene-blob{position:absolute;border-radius:50%;filter:blur(40px);opacity:.55;mix-blend-mode:screen}
.scene-blob.b1{width:55vw;height:55vw;max-width:520px;max-height:520px;left:-8%;top:8%;background:var(--s3);animation:blobFloat 18s ease-in-out infinite}
.scene-blob.b2{width:45vw;height:45vw;max-width:420px;max-height:420px;right:-6%;top:35%;background:var(--s2);animation:blobFloat 22s ease-in-out infinite reverse}
.scene-blob.b3{width:40vw;height:40vw;max-width:380px;max-height:380px;left:30%;bottom:-10%;background:var(--s1);opacity:.4;animation:blobFloat 26s ease-in-out infinite}
.scene-vignette{position:absolute;inset:0;background:linear-gradient(180deg, transparent 0%, transparent 55%, color-mix(in srgb, var(--s4) 70%, transparent) 100%);opacity:.85}
.scene-motif{position:absolute;inset:0;opacity:.18;background-repeat:repeat;background-size:140px 140px;animation:motifDrift 60s linear infinite}

html[data-theme="halloween"] .scene-blob{mix-blend-mode:lighten;opacity:.45}
html[data-theme="halloween"] .scene-motif{opacity:.22;background-image:radial-gradient(circle at 20% 30%, rgba(255,162,58,.5) 0 2px, transparent 3px),radial-gradient(circle at 70% 60%, rgba(255,122,0,.35) 0 1.5px, transparent 3px);background-size:90px 90px, 140px 140px}
html[data-theme="christmas"] .scene-motif{opacity:.28;background-image:radial-gradient(circle, #fff 0 1.5px, transparent 2.5px),radial-gradient(circle, rgba(255,255,255,.7) 0 1px, transparent 2px);background-size:110px 110px, 70px 70px;animation:snowDrift 36s linear infinite}
html[data-theme="winter"] .scene-motif{opacity:.22;background-image:radial-gradient(circle, #fff 0 1.5px, transparent 2.5px);background-size:100px 100px;animation:snowDrift 40s linear infinite}
html[data-theme="autumn"] .scene-motif{opacity:.15;background-image:radial-gradient(ellipse at 30% 40%, rgba(232,163,23,.4) 0 8px, transparent 9px);background-size:160px 160px}
html[data-theme="spring"] .scene-motif{opacity:.16;background-image:radial-gradient(circle at 40% 50%, rgba(224,105,155,.35) 0 6px, transparent 7px);background-size:150px 150px}
html[data-theme="summer"] .scene-motif{opacity:.14;background-image:radial-gradient(circle at 50% 50%, rgba(255,179,0,.45) 0 10px, transparent 12px);background-size:180px 180px}

@keyframes sceneDrift{from{background-position:0% 0%}to{background-position:100% 40%}}
@keyframes blobFloat{0%{transform:translate(0,0) scale(1)}50%{transform:translate(4%,6%) scale(1.08)}100%{transform:translate(-3%,-4%) scale(.96)}}
@keyframes motifDrift{from{transform:translateY(0)}to{transform:translateY(-140px)}}
@keyframes snowDrift{from{transform:translate3d(0,0,0)}to{transform:translate3d(-40px,140px,0)}}
@keyframes liftIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

@media (prefers-reduced-motion:reduce){
  .scene-base,.scene-blob,.scene-motif{animation:none !important}
  .tile a:hover,.lcard:hover,.fcard:hover,.day:hover,.idea-in:hover,.tonight:hover{transform:none !important}
}

/* Glass chrome: header fades into content */
.hdr{
  background:linear-gradient(180deg, color-mix(in srgb, var(--hdrbg) 72%, transparent) 0%, color-mix(in srgb, var(--hdrbg) 28%, transparent) 70%, transparent 100%) !important;
  -webkit-backdrop-filter:blur(22px) saturate(1.5);
  backdrop-filter:blur(22px) saturate(1.5);
  border-bottom:1px solid var(--gline) !important;
  box-shadow:none !important;
  padding-bottom:28px !important;
}
.hdr h1,.theme-tag,.clock,.datefull{text-shadow:0 1px 2px rgba(0,0,0,.25)}
html[data-theme="autumn"] .hdr h1,html[data-theme="christmas"] .hdr h1,html[data-theme="winter"] .hdr h1,html[data-theme="spring"] .hdr h1,html[data-theme="summer"] .hdr h1{text-shadow:0 1px 2px rgba(0,0,0,.35)}

main{padding-top:8px}
.sub,.fam-nav,.fam-link{color:var(--ink) !important}
.sub a,.fam-nav a,.fam-link a{
  color:var(--ink) !important;font-weight:700;text-decoration:none;
  background:var(--glass);border:1px solid var(--gline);border-radius:999px;
  padding:.35em .85em;display:inline-block;margin:.15em .25em .15em 0;
  -webkit-backdrop-filter:blur(12px) saturate(1.3);backdrop-filter:blur(12px) saturate(1.3);
  box-shadow:var(--gshadow);
}
.sec-h{color:var(--ink) !important;text-shadow:0 1px 0 rgba(255,255,255,.2)}

/* Shared glass surface */
.tonight,.day,.card,.tile a,.festive,.idea-in,.fcard,.lcard,.note,.tweak,.nudge,
.btns button,.tab,.timer select,.timer input[type=number]{
  background:var(--glass) !important;
  -webkit-backdrop-filter:blur(20px) saturate(1.45);
  backdrop-filter:blur(20px) saturate(1.45);
  border:1px solid var(--gline) !important;
  box-shadow:var(--gshadow), inset 0 1px 0 rgba(255,255,255,.35) !important;
  border-radius:22px !important;
  transition:transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.tonight{
  background:linear-gradient(145deg, color-mix(in srgb, var(--herobg) 55%, transparent), var(--glass2)) !important;
  border:1px solid var(--gline) !important;
  border-radius:28px !important;
  box-shadow:var(--gshadow), inset 0 1px 0 rgba(255,255,255,.4) !important;
  margin-top:4px;
}
.festive{
  background:var(--glass2) !important;
  border-style:solid !important;
  border-width:1px !important;
}
.tile a,.lcard,.fcard,.day,.idea-in{border-radius:20px !important}
.tile.today a,.dw.today .day,.idea.pick .idea-in{
  border:2px solid var(--accent2) !important;
  background:color-mix(in srgb, var(--today) 55%, var(--glass)) !important;
  box-shadow:0 10px 36px color-mix(in srgb, var(--accent2) 35%, transparent), inset 0 1px 0 rgba(255,255,255,.4) !important;
}
.tile a:hover,.lcard:hover,.fcard:hover,.day:hover,.idea-in:hover,.tonight:hover{
  transform:translateY(-3px);
  box-shadow:0 14px 40px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.45) !important;
}
.btn{
  background:var(--glass) !important;
  -webkit-backdrop-filter:blur(12px) saturate(1.3);
  backdrop-filter:blur(12px) saturate(1.3);
  border:1px solid var(--gline) !important;
  border-radius:14px !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.35);
  color:var(--accent) !important;
}
.tonight .btn{background:rgba(255,255,255,.9) !important;color:var(--herobg) !important}
.cook{background:var(--glass2) !important;border:1px solid var(--gline) !important}
.note,.tweak,.nudge{border-radius:16px !important}

/* Text contrast on glass */
.t-day,.t-dish,.dish,.fest-h,.fcard h2,.lcard strong,.idea h3,.card h3,.extras-h{color:var(--ink) !important}
.t-date,.t-meta,.meta,.est,.c,.hint,footer,.when,.rowlist .d,.rowlist .m,.props .k{color:color-mix(in srgb, var(--ink) 78%, transparent) !important}
html[data-theme="halloween"] .t-day,html[data-theme="halloween"] .lcard strong,html[data-theme="halloween"] .props .k{color:var(--accent) !important}
.tonight .kicker,.tonight h2,.tonight .dish,.tonight .meta,.tonight .est,.tonight .none,.tonight .next{color:#fff !important;text-shadow:0 1px 2px rgba(0,0,0,.35)}
.tonight .note,.tonight .tweak{background:rgba(255,255,255,.16) !important;color:#fff !important}

/* Scroll reveal */
.tile,.dw,.fcard,.festive,.tonight,.card,.lcard{animation:liftIn .55s ease both}
.tile:nth-child(1),.dw:nth-child(1){animation-delay:.02s}
.tile:nth-child(2),.dw:nth-child(2){animation-delay:.06s}
.tile:nth-child(3),.dw:nth-child(3){animation-delay:.1s}
.tile:nth-child(4),.dw:nth-child(4){animation-delay:.14s}
.tile:nth-child(5),.dw:nth-child(5){animation-delay:.18s}
.tile:nth-child(6),.dw:nth-child(6){animation-delay:.22s}
.tile:nth-child(7),.dw:nth-child(7){animation-delay:.26s}

/* Prototype banner (no theme dock) */
.proto-banner{
  position:fixed !important;top:0;left:0;right:0;z-index:40;text-align:center;
  font-size:.8rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
  padding:6px 10px;margin:0;color:#fff;
  background:rgba(20,20,30,.55);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
  border-bottom:1px solid rgba(255,255,255,.2);
}
body{padding-top:28px;padding-bottom:24px}

/* Training timer glass polish */
.tab.on{background:var(--accent) !important;color:#fff !important;border-color:var(--accent) !important}
.btns button.pri{background:#14B8A6 !important;border-color:#0F766E !important;color:#042f2e !important}
.bar{background:rgba(0,0,0,.12) !important}
.timebig{color:var(--ink)}


/* Cook / mode chips readable on glass hero */
.tonight .cook,.tonight .mode,.tonight .badge{
  background:rgba(255,255,255,.92) !important;color:#1a1020 !important;
  border:1px solid rgba(255,255,255,.6) !important;font-weight:800;
}
html[data-theme="halloween"] .tonight .cook,
html[data-theme="halloween"] .tonight .mode{background:rgba(255,162,58,.95) !important;color:#1a0a00 !important}
.tile.today .t-now,.pick-tag{background:var(--accent2) !important;color:#1a1000 !important}


  .ts-btn{min-width:36px;min-height:36px;padding:4px 6px}
}


/* Thumb rating buttons */
.thumbs{display:flex;flex-wrap:wrap;gap:10px;border:0;padding:.2em 0;margin:0 0 .5em}
.thumbs legend{padding:0;margin:0 0 .4em;color:var(--ink);font-size:1rem;font-weight:700}
.thumb{
  position:relative;display:inline-flex;align-items:center;justify-content:center;
  min-width:48px;min-height:48px;padding:8px 14px;margin:0;cursor:pointer;
  border-radius:16px;border:1px solid var(--gline);
  background:var(--glass);
  -webkit-backdrop-filter:blur(12px) saturate(1.3);backdrop-filter:blur(12px) saturate(1.3);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.35);
  -webkit-tap-highlight-color:transparent;font-size:1.55rem;line-height:1;
  transition:transform .2s ease, background .2s ease, box-shadow .2s ease;
}
.thumb input{position:absolute;opacity:0;width:1px;height:1px;margin:0;pointer-events:none}
.thumb:hover{transform:translateY(-2px)}
.thumb:focus-within{outline:2px solid var(--accent);outline-offset:2px}
.thumb.is-on,.thumb:has(input:checked){
  background:color-mix(in srgb, var(--accent2) 55%, var(--glass));
  border-color:var(--accent2);
  box-shadow:0 6px 18px color-mix(in srgb, var(--accent2) 35%, transparent), inset 0 1px 0 rgba(255,255,255,.45);
}
.tonight .thumb{background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.35);color:#fff}
.tonight .thumb.is-on,.tonight .thumb:has(input:checked){background:rgba(255,255,255,.9);color:#1a1020}

/* Fallback when backdrop-filter unsupported */
@supports not ((-webkit-backdrop-filter:blur(1px)) or (backdrop-filter:blur(1px))){
  .tonight,.day,.card,.tile a,.festive,.idea-in,.fcard,.lcard,.note,.tweak,.nudge,.sub a,.fam-nav a,.btn,.tab,.btns button{
    background:var(--card) !important;
  }
  .hdr{background:var(--hdrbg) !important}
  .tonight{background:var(--herobg) !important}
  body{background:var(--bg) !important}
  .scene{display:none}
}

/* color-mix fallback: older Safari still gets blur; keep readable card fills via theme glass vars already set */
'''


def glass_var_blocks(themes_keys=None):
    blocks = []
    for name, v in GLASS_VARS.items():
        decls = "".join("--%s:%s;" % (k, val) for k, val in v.items())
        blocks.append('html[data-theme="%s"]{%s}' % (name, decls))
    # default root from autumn
    a = GLASS_VARS["autumn"]
    root = ":root{%s}\n" % "".join("--%s:%s;" % (k, val) for k, val in a.items())
    return root + "\n".join(blocks) + "\n"


def append_glass_css(base_css: str) -> str:
    return base_css + "\n" + glass_var_blocks() + GLASS_CSS
