"""SwiftRoute demo app.  Run:  streamlit run app.py"""
import json
import os
from urllib.parse import quote

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components


def embed(html, height):
    """Embed an HTML page (newer Streamlit: st.iframe; older: components.html)."""
    return st.iframe(html, height=height) if hasattr(st, "iframe") else components.html(html, height=height)

import replay
import sample
import scenarios
from geo import geocode, reverse, route_detail
from i18n import DAYS as DAY_NAMES, ICON, LANGS, SPEECH_CODE, T, step_text
from plan import run, SHIFT_HOURS
from traffic import load_profile

st.set_page_config(page_title="SwiftRoute", page_icon="🚚", layout="wide", initial_sidebar_state="expanded")

PALETTE = [[34, 211, 238], [168, 85, 247], [74, 222, 128], [251, 146, 60], [244, 114, 182],
           [250, 204, 21], [96, 165, 250], [248, 113, 113], [45, 212, 191], [203, 213, 225]]
OKABE_ITO = [[86, 180, 233], [230, 159, 0], [0, 158, 115], [240, 228, 66], [0, 114, 178],
             [213, 94, 0], [204, 121, 167], [255, 255, 255], [153, 153, 153], [117, 112, 179]]
hexc = lambda c: "#%02x%02x%02x" % tuple(c)


def fit_view(lonlats, width=800, height=600, pad=0.85):
    """Map view (centre + zoom) that shows every point, like a 'home' / zoom-to-fit button."""
    import math
    lons, lats = [p[0] for p in lonlats], [p[1] for p in lonlats]
    lon0, lon1, lat0, lat1 = min(lons), max(lons), min(lats), max(lats)
    y = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))      # Web Mercator
    zx = math.log2(width * pad / 512 * 360 / max(lon1 - lon0, 1e-4))
    zy = math.log2(height * pad / 512 * 2 * math.pi / max(y(lat1) - y(lat0), 1e-6))
    return pdk.ViewState(longitude=(lon0 + lon1) / 2, latitude=(lat0 + lat1) / 2, zoom=min(zx, zy, 16), pitch=0, bearing=0)
def html_table(df, num=()):
    """A table that follows the light/dark theme (Streamlit's data grid can't be re-themed at runtime)."""
    import html as h
    head = "".join(f"<th>{h.escape(str(c))}</th>" for c in df.columns)
    rows = "".join("<tr>" + "".join(f'<td class="{"num" if c in num else ""}">{h.escape(str(v))}</td>'
                                    for c, v in zip(df.columns, r)) + "</tr>" for r in df.itertuples(index=False))
    return f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'


clock = lambda start, m: f"{start + int(m) // 60:02d}:{int(m) % 60:02d}"

# ----------------------------------------------------- sidebar (settings first: they drive the styling)
with st.sidebar:
    lang = LANGS[st.selectbox("🌐 Language / Idioma / Langue", list(LANGS), key="lang")]
    t = T(lang)
    light = st.segmented_control(t("theme"), ["dark", "light"], default="dark", key="theme_mode",
                                 format_func=lambda m: f"🌙 {t('dark')}" if m == "dark" else f"☀️ {t('light')}") == "light"
    st.markdown(f'<div class="side-h">{t("shift")}</div>', unsafe_allow_html=True)
    day_idx = st.selectbox(t("day"), range(7), index=2, format_func=lambda i: DAY_NAMES[lang][i])
    day = day_idx + 1                       # Chicago data: 1 = Sunday ... 7 = Saturday
    start_hour = st.slider(t("start_hour"), 5, 14, 9, format="%d:00")
    st.caption(t("drivers_work", a=start_hour, b=start_hour + SHIFT_HOURS))
    st.markdown(f'<div class="side-h">{t("fleet")}</div>', unsafe_allow_html=True)
    n_trucks = st.slider(t("trucks"), 1, 10, 4)
    capacity = st.slider(t("capacity"), 5, 40, 15)
    van_cost = st.slider(t("van_cost"), 0, 200, scenarios.VAN_COST, step=10, format="$%d", help=t("van_cost_help"))
    st.markdown(f'<div class="side-h">{t("chaos")}</div>', unsafe_allow_html=True)
    jam = st.slider(t("jam"), 0, 60, 0, format="%d%%")
    broken = st.toggle(t("breakdown"))
    urgent = st.toggle(t("urgent"))
    st.markdown(f'<div class="side-h">{t("map")}</div>', unsafe_allow_html=True)
    show_naive = st.toggle(t("show_naive"), False)
    st.markdown(f'<div class="side-h">♿ {t("access")}</div>', unsafe_allow_html=True)
    big = st.toggle(t("big_text"))
    contrast = st.toggle(t("contrast"))
    cb = st.toggle(t("cb_colors"))
    calm = st.toggle(t("calm"))

COLORS = OKABE_ITO if cb else PALETTE

# ------------------------------------------------------------------ style
DARK = dict(BG="#070B17", SIDE="#0A1020", CARD="#0F1629", CARD_GRAD="linear-gradient(180deg,#0F1629,#0B1122)",
            LINE="#1E293B", TXT="#F8FAFC", MUTED="#94A3B8", ACC="#22D3EE", UP="#4ADE80", DOWN="#F87171",
            ALERT="#FCA5A5", MAPBG="#0B1122", BTN="#334155", GRID="#1E293B", TICK="#94A3B8",
            GLOW1="rgba(34,211,238,.10)", GLOW2="rgba(168,85,247,.10)",
            HERO="linear-gradient(135deg,rgba(34,211,238,.16),rgba(168,85,247,.16))", BIGGRAD="#22D3EE,#C084FC")
LIGHT = dict(BG="#F4F6FB", SIDE="#FFFFFF", CARD="#FFFFFF", CARD_GRAD="linear-gradient(180deg,#FFFFFF,#F8FAFC)",
             LINE="#E2E8F0", TXT="#0F172A", MUTED="#526077", ACC="#0E7490", UP="#15803D", DOWN="#B91C1C",
             ALERT="#991B1B", MAPBG="#E8EDF5", BTN="#CBD5E1", GRID="#E2E8F0", TICK="#526077",
             GLOW1="rgba(14,116,144,.08)", GLOW2="rgba(124,58,237,.07)",
             HERO="linear-gradient(135deg,rgba(14,116,144,.10),rgba(124,58,237,.10))", BIGGRAD="#0E7490,#7C3AED")
TH = dict(LIGHT if light else DARK)
if contrast:   # high contrast: pure black/white, one strong accent
    TH.update(BG="#FFFFFF" if light else "#000000", SIDE="#FFFFFF" if light else "#000000",
              CARD="#FFFFFF" if light else "#000000", LINE="#000000" if light else "#FFFFFF",
              TXT="#000000" if light else "#FFFFFF", MUTED="#000000" if light else "#FFFFFF",
              ACC="#0033CC" if light else "#FFE600", GLOW1="transparent", GLOW2="transparent")
    TH.update(CARD_GRAD=TH["CARD"], HERO=TH["CARD"], MAPBG=TH["CARD"])
BG, CARD, LINE, TXT, MUTED, ACC = TH["BG"], TH["CARD"], TH["LINE"], TH["TXT"], TH["MUTED"], TH["ACC"]
MAP_STYLE = None if os.environ.get("SWIFTROUTE_NO_TILES") else ("light" if light else "dark")
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
html {{font-size: {'118%' if big else '100%'};}}
html, body, [class*="css"], .stMarkdown, button, input, textarea, select, label {{font-family: 'Inter', sans-serif !important;}}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{display: none !important;}}
header[data-testid="stHeader"] {{background: transparent; height: 0;}}
.block-container {{padding: 1.4rem 2rem 3rem; max-width: 1500px;}}
[data-testid="stAppViewContainer"], .stApp {{background: radial-gradient(1200px 500px at 85% -10%, {TH["GLOW1"]}, transparent 60%),
   radial-gradient(900px 500px at -10% 10%, {TH["GLOW2"]}, transparent 60%), {BG};}}
[data-testid="stSidebar"] {{background: {TH["SIDE"]}; border-right: 1px solid {LINE};}}
/* Streamlit's own widgets follow our theme too */
.stApp, [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h4, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] p, [data-testid="stExpander"] summary,
[data-testid="stRadio"] label p, [data-testid="stSidebar"] label p {{color: {TXT} !important;}}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{color: {MUTED} !important;}}
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="base-input"], [data-baseweb="textarea"],
textarea, input {{background: {CARD} !important; color: {TXT} !important; border-color: {LINE} !important;}}
[data-baseweb="select"] * {{color: {TXT} !important;}}
.stSelectbox .react-aria-ComboBox > div, .stSelectbox input, .stSelectbox button {{background: {CARD} !important;
  color: {TXT} !important; border-color: {LINE} !important;}}
[role="listbox"], [role="listbox"] [role="option"] {{background: {CARD} !important; color: {TXT} !important;}}
[role="listbox"] [role="option"][data-focused="true"], [role="listbox"] [role="option"]:hover {{background: {LINE} !important;}}
[data-testid="stRadioOption"]:not([data-selected="true"]) > div:first-of-type > div:first-child {{background: {CARD} !important;
  border: 2px solid {MUTED} !important; box-sizing: border-box;}}
[data-testid="stCheckbox"] label:has(input:not(:checked)) > div:first-of-type {{background: {"#CBD5E1" if light else "rgba(226,232,240,.2)"} !important;}}
[data-testid="stCheckbox"] label > div:first-of-type > div {{box-shadow: 0 1px 3px rgba(0,0,0,.25);}}
[data-testid="stBaseButton-secondary"] {{background: {CARD} !important; color: {TXT} !important; border:1px solid {TH["BTN"]} !important;}}
[data-testid="stBaseButton-secondary"] p {{color: {TXT} !important;}}
[data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"] {{background: {CARD} !important; color: {TXT} !important;}}
[data-testid="stButtonGroup"] button {{background: {CARD}; color: {TXT}; border-color: {LINE};}}
[data-testid="stButtonGroup"] button[kind*="Active"], [data-testid="stButtonGroup"] button[aria-checked="true"] {{border-color: {ACC}; color: {ACC};}}
.stDownloadButton button {{background: {CARD}; color: {TXT};}}
.stTabs [data-baseweb="tab"] p {{color: {MUTED};}} .stTabs [aria-selected="true"] p {{color: {ACC};}}
[data-testid="stAlert"] {{color: {TXT};}}
.tbl {{width:100%;border-collapse:separate;border-spacing:0;font-size:.88rem;border:1px solid {LINE};border-radius:12px;overflow:hidden;}}
.tbl th {{text-align:left;background:{CARD};color:{MUTED};font-weight:600;font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;padding:10px 12px;border-bottom:1px solid {LINE};}}
.tbl td {{padding:9px 12px;color:{TXT};border-bottom:1px solid {LINE};background:{TH["SIDE"]};}}
.tbl tr:last-child td {{border-bottom:0;}} .tbl td.num {{text-align:right;font-family:'JetBrains Mono',monospace;}}
*:focus-visible {{outline: 3px solid #FACC15 !important; outline-offset: 2px;}}
.sr-only {{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0;}}
.topbar {{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;flex-wrap:wrap;gap:12px;}}
.brand {{display:flex;align-items:center;gap:14px;}}
.logo {{width:44px;height:44px;border-radius:12px;display:grid;place-items:center;font-size:22px;
        background:linear-gradient(135deg,#22D3EE,#A855F7);box-shadow:0 0 24px rgba(34,211,238,.35);}}
.brand h1 {{font-size:1.55rem;font-weight:800;margin:0;padding:0;letter-spacing:-.02em;color:{TXT};}}
.brand p {{margin:0;color:{MUTED};font-size:.9rem;}}
.pills {{display:flex;gap:8px;flex-wrap:wrap;}}
.pill {{font-size:.75rem;color:{TXT};padding:6px 12px;border-radius:999px;background:{CARD};border:1px solid {LINE};
        display:inline-flex;align-items:center;gap:7px;}}
.dot {{width:7px;height:7px;border-radius:50%;background:#22C55E;box-shadow:0 0 8px #22C55E;}}
.hero {{display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr;gap:14px;margin-bottom:14px;}}
@media (max-width:1100px) {{.hero {{grid-template-columns:1fr 1fr;}}}}
.card {{background:{TH["CARD_GRAD"]};border:1px solid {LINE};border-radius:16px;padding:18px 20px;}}
.card .lbl {{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:{MUTED};font-weight:600;}}
.card .big {{font-family:'JetBrains Mono',monospace;font-size:2.1rem;font-weight:700;color:{TXT};line-height:1.15;margin-top:6px;}}
.card .sub {{font-size:.82rem;color:{MUTED};margin-top:4px;}}
.card.accent {{background:{TH["HERO"]};border-color:{ACC};}}
.card.accent .big {{font-size:2.6rem;{f'color:{ACC};' if contrast else f'background:linear-gradient(90deg,{TH["BIGGRAD"]});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'}}}
.up {{color:{TH["UP"]};}} .down {{color:{TH["DOWN"]};}} .flat {{color:{MUTED};}}
.bar {{height:6px;background:{LINE};border-radius:99px;margin-top:10px;overflow:hidden;position:relative;}}
.bar > i {{position:absolute;inset:0 auto 0 0;border-radius:99px;}}
.panel-title {{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:{MUTED};font-weight:600;margin:4px 0 10px;}}
.mini {{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;}}
.mini .card {{padding:12px 14px;}} .mini .card .big {{font-size:1.35rem;}}
.truck {{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;background:{CARD};border:1px solid {LINE};margin-bottom:8px;}}
.truck .sw {{width:10px;height:34px;border-radius:6px;flex:none;}}
.truck .nm {{font-weight:700;color:{TXT};font-size:.92rem;}}
.truck .meta {{color:{MUTED};font-size:.78rem;font-family:'JetBrains Mono',monospace;}}
.truck .load {{margin-left:auto;text-align:right;font-family:'JetBrains Mono',monospace;font-size:.8rem;color:{TXT};}}
.alert {{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.5);color:{TXT if contrast else TH["ALERT"]};
         border-radius:12px;padding:12px 14px;font-size:.88rem;margin-top:6px;}}
.leg {{border-left:3px solid var(--c);padding:4px 0 4px 16px;margin:0 0 6px 8px;}}
.stopline {{display:flex;gap:10px;align-items:center;font-weight:700;color:{TXT};margin:10px 0 6px;}}
.badge {{background:var(--c);color:#070B17;border-radius:999px;min-width:26px;height:26px;display:grid;place-items:center;font-size:.8rem;font-weight:800;}}
.step {{color:{TXT};font-size:.88rem;padding:3px 0;display:flex;gap:10px;}}
.step .ic {{width:20px;text-align:center;color:var(--c);font-weight:800;}}
.step .km {{margin-left:auto;color:{MUTED};font-family:'JetBrains Mono',monospace;font-size:.78rem;}}
.gm {{display:inline-block;padding:8px 14px;border-radius:10px;background:{CARD};border:1px solid {ACC};color:{TXT} !important;
      text-decoration:none;margin:0 8px 8px 0;font-weight:600;}}
[data-testid="stDeckGlJsonChart"], iframe {{border-radius:16px;}}
[data-testid="stDeckGlJsonChart"] {{overflow:hidden;border:1px solid {LINE};background:{TH["MAPBG"]};}}
.side-h {{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:{ACC};font-weight:700;margin:10px 0 4px;}}
.stButton > button, .stDownloadButton > button {{border-radius:10px;font-weight:600;border:1px solid {TH["BTN"]};}}
.stButton > button[kind="primary"] {{background:{ACC if contrast else 'linear-gradient(135deg,#06B6D4,#8B5CF6)'};border:0;color:{'#000' if contrast else '#fff'};}}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ intro / loading screen (once per visit)
import time as _time
_t0 = st.session_state.setdefault("intro_t0", _time.time())
_el = _time.time() - _t0                       # seconds since this visit started
if _el < 3.6 and not calm:
    d = lambda s: f"{s - _el:.2f}s"            # negative delay = continue the animation where it was
    st.markdown(f"""
<style>
[data-testid="stElementContainer"]:has(.intro) {{opacity:1 !important; transition:none !important;}}
.intro {{position:fixed;inset:0;z-index:999999;display:grid;place-items:center;
  background:radial-gradient(900px 600px at 70% 20%, {TH["GLOW1"]}, transparent 60%),
             radial-gradient(800px 600px at 20% 80%, {TH["GLOW2"]}, transparent 60%), {BG};
  animation:introOut .9s cubic-bezier(.7,0,.3,1) {d(2.9)} forwards;}}
.intro-in {{text-align:center;display:flex;flex-direction:column;align-items:center;gap:14px;}}
.intro-logo {{width:96px;height:96px;border-radius:26px;display:grid;place-items:center;font-size:48px;
  background:linear-gradient(135deg,#22D3EE,#A855F7);box-shadow:0 0 60px rgba(34,211,238,.45);
  animation:pop .7s cubic-bezier(.2,1.4,.4,1) {d(0.1)} both;}}
.intro h1 {{font-size:4rem;font-weight:800;letter-spacing:-.04em;margin:8px 0 0;padding:0;color:{TXT};
  animation:rise .7s ease {d(0.35)} both;}}
.intro .tag {{font-size:1.25rem;margin:0;background:linear-gradient(90deg,{TH["BIGGRAD"]});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:600;animation:rise .7s ease {d(0.55)} both;}}
.road {{position:relative;width:min(420px,70vw);height:6px;border-radius:99px;background:{LINE};margin-top:34px;
  animation:rise .6s ease {d(0.75)} both;}}
.road i {{position:absolute;left:0;top:0;bottom:0;border-radius:99px;background:linear-gradient(90deg,#22D3EE,#A855F7);
  animation:fill 2s cubic-bezier(.4,0,.2,1) {d(0.85)} both;}}
.road b {{position:absolute;top:-30px;font-size:26px;transform:scaleX(-1);animation:drive 2s cubic-bezier(.4,0,.2,1) {d(0.85)} both;}}
.intro .load {{font-size:.85rem;color:{MUTED};margin-top:6px;animation:rise .6s ease {d(0.9)} both;}}
@keyframes pop {{from {{transform:scale(.3) rotate(-12deg);opacity:0}} to {{transform:none;opacity:1}}}}
@keyframes rise {{from {{transform:translateY(16px);opacity:0}} to {{transform:none;opacity:1}}}}
@keyframes fill {{from {{width:0}} to {{width:100%}}}}
@keyframes drive {{from {{left:-14px}} to {{left:calc(100% - 18px)}}}}
@keyframes introOut {{to {{opacity:0;visibility:hidden;transform:scale(1.06)}}}}
@keyframes appIn {{from {{opacity:0;transform:translateY(14px)}} to {{opacity:1;transform:none}}}}
@media (prefers-reduced-motion: reduce) {{.intro {{animation-delay:.6s}} .intro * {{animation-duration:.01s !important}}}}
</style>
<div class="intro" role="status" aria-label="SwiftRoute loading">
  <div class="intro-in">
    <div class="intro-logo" aria-hidden="true">🚚</div>
    <h1>SwiftRoute</h1>
    <p class="tag">{t("intro_tag")}</p>
    <div class="road" aria-hidden="true"><i></i><b>🚚</b></div>
    <p class="load">{t("intro_load")}</p>
  </div>
</div>""", unsafe_allow_html=True)

profile, source, meta = st.cache_data(load_profile)()
detail_cached = st.cache_data(route_detail, show_spinner=False)

# ------------------------------------------------------------------ top bar
st.markdown(f"""
<div class="topbar" role="banner">
  <div class="brand"><div class="logo" aria-hidden="true">🚚</div>
    <div><h1>SwiftRoute</h1><p>{t("tagline")}</p></div></div>
  <div class="pills">
    <span class="pill"><span class="dot"></span>{t("pill_traffic")}</span>
    <span class="pill"><span class="dot"></span>{t("pill_roads")}</span>
    <span class="pill"><span class="dot"></span>{t("pill_opt")}</span>
  </div>
</div>""", unsafe_allow_html=True)

tabs = st.tabs([t("tab_plan"), t("tab_replay"), t("tab_driver"), t("tab_whatif"), t("tab_traffic"), t("tab_about")])
plan_tab, replay_tab, driver_tab, whatif_tab, traffic_tab, about_tab = tabs

# ------------------------------------------------------------------ deliveries input
with plan_tab:
    mode = st.radio("input", [t("sample"), t("own")], horizontal=True, label_visibility="collapsed")
    if mode == t("sample"):
        depot, stops = sample.DEPOT, sample.make(40)
    else:
        st.session_state.setdefault("depot_text", "1200 W Fulton Market, Chicago, IL")
        st.session_state.setdefault("addr_text", "233 S Wacker Dr, Chicago, IL | 2 | 9-12\n"
                                                 "1060 W Addison St, Chicago, IL | 1 | 10-17\n"
                                                 "5700 S Lake Shore Dr, Chicago, IL | 3 | 13-16")
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            if st.button(t("use_location")):
                st.session_state["want_loc"] = True
            if st.session_state.get("want_loc"):
                from streamlit_js_eval import get_geolocation
                loc = get_geolocation()
                if loc and "coords" in loc:
                    lat, lon = loc["coords"]["latitude"], loc["coords"]["longitude"]
                    st.session_state["depot_text"] = reverse(lat, lon) or f"{lat:.5f}, {lon:.5f}"
                    st.session_state["depot_xy"] = (lat, lon, st.session_state["depot_text"])
                    st.session_state["want_loc"] = False
                    st.rerun()
            st.text_input(t("depot_addr"), key="depot_text")
            from streamlit_mic_recorder import speech_to_text
            heard = speech_to_text(start_prompt=t("voice"), stop_prompt=t("voice_stop"), language=SPEECH_CODE[lang],
                                   just_once=True, key="stt", use_container_width=True)
            if heard:
                st.session_state["addr_text"] = st.session_state["addr_text"].rstrip() + f"\n{heard} | 1 | 9-17"
                st.session_state["heard"] = heard
                st.rerun()
            if st.session_state.get("heard"):
                st.caption(t("heard", x=st.session_state["heard"]))
            go = st.button(t("find"), type="primary", use_container_width=True)
        c2.text_area(t("deliveries_help"), key="addr_text", height=190)
        if go:
            with st.spinner(t("looking_up")):
                dtxt = st.session_state["depot_text"]
                xy = st.session_state.get("depot_xy")
                d = (xy[0], xy[1]) if xy and xy[2] == dtxt else geocode(dtxt)
                found, missing = [], []
                for line in filter(None, map(str.strip, st.session_state["addr_text"].splitlines())):
                    parts = [p.strip() for p in line.split("|")] + ["1", "9-17"]
                    try:
                        a, b = (int(x) for x in parts[2].split("-"))
                        loc = geocode(parts[0])
                    except Exception:
                        loc = None
                    if loc:
                        found.append({"name": parts[0], "lat": loc[0], "lon": loc[1], "demand": int(parts[1]), "slot": (a, b)})
                    else:
                        missing.append(parts[0])
            st.session_state["typed"] = ((dtxt, *d) if d else None, found, missing)
        if "typed" not in st.session_state:
            st.info(t("type_hint"))
            st.stop()
        depot, stops, missing = st.session_state["typed"]
        if depot is None:
            st.error(t("no_depot")); st.stop()
        for m in missing:
            st.warning(t("skipped_addr", x=m))
        if not stops:
            st.stop()

    if urgent:
        stops = stops + [{"name": "⚡ URGENT · 875 N Michigan Ave", "lat": 41.8988, "lon": -87.6229, "demand": 3, "slot": (12, 14)}]
    trucks = max(1, n_trucks - (1 if broken else 0))
    with st.spinner(t("optimizing")):
        r = st.cache_data(run, show_spinner=False)(depot, stops, trucks, capacity, profile, day, start_hour, jam / 100, van_cost=van_cost)
    s, b = r["smart_kpi"], r["naive_kpi"]
    if not r["smart"]:
        st.error({"en": "No plan could be found for these settings. Try more trucks, bigger trucks or a different shift.",
                  "es": "No se encontró un plan con estos ajustes. Prueba más camiones, camiones más grandes u otro turno.",
                  "fr": "Aucun plan trouvé avec ces réglages. Essayez plus de camions, des camions plus grands ou un autre horaire."}[lang])
        st.stop()
    routes = r["naive"] if show_naive else r["smart"]
    pts, st_list = r["points"], r["stops"]
    details = [detail_cached(tuple(pts[x] for x, _ in route)) for route in routes]
    missed = r["skipped"] + r["outside"]

    # ---- hero numbers
    saved = b["Cost ($)"] - s["Cost ($)"]
    pct = saved / b["Cost ($)"] * 100 if b["Cost ($)"] else 0

    def delta(v, base, lower_better=True):
        dd = v - base
        if abs(dd) < 0.05:
            return f'<span class="flat">{t("same")}</span>'
        good = (dd < 0) == lower_better
        return f'<span class="{"up" if good else "down"}">{"▼" if dd < 0 else "▲"} {abs(dd):,.1f}</span> {t("vs_simple")} ({base:,})'
    st.markdown(f"""
    <div class="hero" role="region" aria-label="results">
      <div class="card accent"><div class="lbl">{t("saved")}</div><div class="big">${saved:,} · {pct:.0f}%</div>
        <div class="sub">{t("instead", a=f"{s['Cost ($)']:,}", b=f"{b['Cost ($)']:,}")}</div></div>
      <div class="card"><div class="lbl">{t("on_time")}</div><div class="big">{s['On time %']}%</div>
        <div class="sub">{delta(s['On time %'], b['On time %'], lower_better=False)}</div>
        <div class="bar"><i style="width:{s['On time %']}%;background:linear-gradient(90deg,#22D3EE,#4ADE80)"></i></div></div>
      <div class="card"><div class="lbl">{t("distance")}</div><div class="big">{s['Total km']} km</div>
        <div class="sub">{delta(s['Total km'], b['Total km'])}</div></div>
      <div class="card"><div class="lbl">{t("driver_hours")}</div><div class="big">{s['Driver hours']} h</div>
        <div class="sub">{delta(s['Driver hours'], b['Driver hours'])}</div></div>
    </div>""", unsafe_allow_html=True)

    # ---- map
    paths, dots = [], []
    for i, (route, det) in enumerate(zip(routes, details)):
        color = COLORS[i % 10]
        line = [c for leg in det["legs"] for c in leg["coords"]] if det else [[pts[x][1], pts[x][0]] for x, _ in route]
        paths.append({"path": line, "color": color, "label": f"{t('truck')} {i+1}"})
        for n, (x, tm) in enumerate(route[1:-1], 1):
            stop = st_list[x - 1]
            dots.append({"lon": stop["lon"], "lat": stop["lat"], "color": color, "r": 70,
                         "label": f"{t('truck')} {i+1} · #{n} · {stop['name']} · {clock(start_hour, tm)} "
                                  f"({stop['slot'][0]}:00–{stop['slot'][1]}:00)"})
    if not show_naive:
        for x in missed:
            dots.append({"lon": x["lon"], "lat": x["lat"], "color": [248, 113, 113], "r": 90, "label": f"❌ {x['name']}"})
    depot_pt = [{"lon": depot[2], "lat": depot[1], "label": f"🏭 {depot[0]}"}]
    layers = [
        pdk.Layer("PathLayer", paths, get_path="path", get_color="color", width_min_pixels=10, opacity=0.18,
                  cap_rounded=True, joint_rounded=True),
        pdk.Layer("PathLayer", paths, get_path="path", get_color="color", width_min_pixels=3,
                  cap_rounded=True, joint_rounded=True, pickable=True),
        pdk.Layer("ScatterplotLayer", dots, get_position=["lon", "lat"], get_fill_color="color", get_radius="r",
                  radius_min_pixels=5, stroked=True, get_line_color=[7, 11, 23], line_width_min_pixels=2, pickable=True),
        pdk.Layer("ScatterplotLayer", depot_pt, get_position=["lon", "lat"], get_fill_color=[255, 255, 255],
                  get_radius=160, radius_min_pixels=9, stroked=True, get_line_color=[34, 211, 238],
                  line_width_min_pixels=4, pickable=True),
    ]
    map_col, side_col = st.columns([2.3, 1], gap="medium")
    with map_col:
        st.markdown(f'<p class="sr-only">{t("map_alt", n=len(routes))}</p>', unsafe_allow_html=True)
        # "Home" button (like Desmos): fit the view to every route. Changing the initial view state by a
        # tiny amount makes the map jump back to it, even after the user has zoomed or dragged.
        if st.button(t("fit"), key="fit_btn", help=t("fit_help")):
            st.session_state["fit_n"] = st.session_state.get("fit_n", 0) + 1
        home = fit_view([c for p in paths for c in p["path"]] + [[d["lon"], d["lat"]] for d in dots + depot_pt])
        n = st.session_state.get("fit_n", 0)      # nudge EVERY field: Streamlit only re-applies fields that changed
        home.longitude += n * 1e-9; home.latitude += n * 1e-9; home.zoom += n * 1e-7
        home.pitch += n * 1e-7; home.bearing += n * 1e-7
        st.pydeck_chart(pdk.Deck(
            layers=layers, map_style=MAP_STYLE,
            initial_view_state=home,
            tooltip={"text": "{label}", "style": {"background": CARD, "color": TXT,
                                                  "fontFamily": "Inter", "fontSize": "12px", "borderRadius": "8px"}}),
            height=600)
        st.caption(f"{t('naive_caption') if show_naive else t('plan_caption')} · "
                   f"{t('speed_caption', p=format(r['factor'], '.0%'))} · {r['dist_source']}"
                   + (f" · 🚚 {t('breakdown')}" if broken else "") + (" · ⚡" if urgent else "") + (f" · 🔥 +{jam}%" if jam else ""))
    with side_col:
        st.markdown(f"""
        <div class="mini">
          <div class="card"><div class="lbl">{t("delivered")}</div><div class="big">{s['Delivered']}</div></div>
          <div class="card"><div class="lbl">CO₂</div><div class="big">{s['CO2 (kg)']} kg</div></div>
        </div><div class="panel-title">{t("fleet_panel", n=len(routes))}</div>""", unsafe_allow_html=True)
        html = ""
        for i, route in enumerate(routes):
            load = sum(st_list[x - 1]["demand"] for x, _ in route[1:-1])
            c = hexc(COLORS[i % 10])
            html += (f'<div class="truck"><div class="sw" style="background:{c};box-shadow:0 0 12px {c}"></div>'
                     f'<div><div class="nm">{t("truck")} {i+1}</div><div class="meta">'
                     f'{clock(start_hour, route[0][1])} → {clock(start_hour, route[-1][1])}</div></div>'
                     f'<div class="load">{len(route) - 2} {t("stops")}<br>{load}/{capacity} {t("pkgs")}</div></div>')
        st.markdown(html, unsafe_allow_html=True)
        if missed and not show_naive:
            st.markdown(f'<div class="alert" role="alert">{t("missed", n=len(missed), t=trucks)}</div>', unsafe_allow_html=True)
        # read aloud (browser speech synthesis, in the chosen language)
        say = t("summary", d=DAY_NAMES[lang][day_idx], t=s["Trucks used"], **{"del": s["Delivered"].split("/")[0]},
                o=s["On time %"], c=s["Cost ($)"], s=saved, p=f"{pct:.0f}")
        embed(f"""<button id="b" style="width:100%;padding:10px;border-radius:10px;border:1px solid {TH["BTN"]};
            background:{CARD};color:{TXT};font:600 14px Inter,sans-serif;cursor:pointer">{t("read_aloud")}</button>
            <script>document.getElementById('b').onclick=()=>{{speechSynthesis.cancel();
            const u=new SpeechSynthesisUtterance({json.dumps(say)});u.lang={json.dumps(SPEECH_CODE[lang])};
            speechSynthesis.speak(u);}};</script>""", 48)

    # ---- schedules
    st.markdown(f'<div class="panel-title" style="margin-top:18px">{t("schedules")}</div>', unsafe_allow_html=True)
    rows = []
    for i, route in enumerate(routes):
        for n, (x, tm) in enumerate(route):
            stop = None if x == 0 else st_list[x - 1]
            rows.append({"truck": f"{t('truck')} {i+1}", "#": n,
                         t("col_stop"): f"🏭 {t('depot')}" if x == 0 else stop["name"],
                         t("col_arrives"): clock(start_hour, tm),
                         t("col_slot"): "" if x == 0 else f"{stop['slot'][0]}:00–{stop['slot'][1]}:00",
                         t("col_status"): "" if x == 0 else (f"✅ {t('ontime_s')}" if start_hour + tm / 60 <= stop["slot"][1]
                                                              else f"⚠️ {t('late_s')}"),
                         t("col_pk"): 0 if x == 0 else stop["demand"]})
    sched = pd.DataFrame(rows)
    names = [f"{t('truck')} {i+1}" for i in range(len(routes))]
    pick = st.segmented_control("truck", names, default=names[0], label_visibility="collapsed", key="sched_pick")
    st.markdown(html_table(sched[sched.truck == (pick or names[0])].drop(columns="truck"), num={"#", t("col_pk")}),
                unsafe_allow_html=True)
    st.download_button(t("download_plan"), sched.to_csv(index=False), "swiftroute_plan.csv", "text/csv")

# ------------------------------------------------------------------ replay the day
with replay_tab:
    st.markdown(f"#### {t('replay_title')}")
    st.caption(t("replay_help"))
    when = {x: tm for route in routes for x, tm in route[1:-1]}
    truck_of = {x: i for i, route in enumerate(routes) for x, _ in route[1:-1]}
    rstops = [{"lon": st_list[k]["lon"], "lat": st_list[k]["lat"], "t": when.get(k + 1), "truck": truck_of.get(k + 1),
               "name": f"{st_list[k]['name']} · {clock(start_hour, when[k + 1]) if k + 1 in when else '—'}"}
              for k in range(len(st_list))]
    embed(replay.html(replay.trips(routes, pts, details), rstops,
                                {"lon": depot[2], "lat": depot[1], "name": depot[0]}, COLORS, start_hour,
                                {"delivered": t("delivered").lower(), "play": t("play"), "pause": t("pause"),
                                 "speed": t("speed"), "aria": t("map_alt", n=len(routes)), "fit": t("fit")},
                                autoplay=not calm, light=light), 640)

# ------------------------------------------------------------------ driver directions (Google-Maps style)
with driver_tab:
    names = [f"{t('truck')} {i+1}" for i in range(len(routes))]
    who = st.segmented_control(t("pick_truck"), names, default=names[0], key="drv_pick") or names[0]
    i = names.index(who)
    route, det, c = routes[i], details[i], hexc(COLORS[i % 10])
    left, right = st.columns([1.4, 1], gap="large")
    with right:
        # Google Maps directions links: max 9 waypoints each, so split long routes into parts
        ll = lambda x: f"{pts[x][0]:.6f},{pts[x][1]:.6f}"
        nodes = [x for x, _ in route]
        parts = [nodes[k:k + 11] for k in range(0, len(nodes) - 1, 10)]
        links = ""
        for p, part in enumerate(parts, 1):
            if len(part) < 2:
                continue
            url = (f"https://www.google.com/maps/dir/?api=1&travelmode=driving&origin={ll(part[0])}"
                   f"&destination={ll(part[-1])}" + (f"&waypoints={quote('|'.join(ll(x) for x in part[1:-1]))}" if len(part) > 2 else ""))
            links += f'<a class="gm" href="{url}" target="_blank" rel="noopener">🗺️ {t("open_gmaps")} · {t("part")} {p}</a>'
        st.markdown(links, unsafe_allow_html=True)
        st.caption(t("gmaps_note"))
        load = sum(st_list[x - 1]["demand"] for x, _ in route[1:-1])
        st.markdown(f"""<div class="mini"><div class="card"><div class="lbl">{t("stops")}</div><div class="big">{len(route) - 2}</div></div>
            <div class="card"><div class="lbl">{t("col_pk")}</div><div class="big">{load}/{capacity}</div></div></div>""",
                    unsafe_allow_html=True)
    with left:
        out = f'<div style="--c:{c}">'
        for k, ((a, ta), (bb, tb)) in enumerate(zip(route, route[1:])):
            title = f"🏭 {t('depot')}" if a == 0 else st_list[a - 1]["name"]
            badge = "🏭" if a == 0 else str(k)
            out += f'<div class="stopline"><span class="badge">{badge}</span>{title} · <span style="font-weight:500">{clock(start_hour, ta)}</span></div>'
            if det:
                out += '<div class="leg">' + "".join(
                    f'<div class="step"><span class="ic">{ICON.get(stp["modifier"], "↑") if stp["type"] not in ("depart", "arrive") else ("●" if stp["type"] == "depart" else "⚑")}</span>'
                    f'{step_text(stp, lang)}<span class="km">{(f"{stp['km']:.1f} km" if stp["km"] >= 1 else f"{round(stp['km'] * 1000, -1):.0f} m") if stp["type"] != "arrive" else ""}</span></div>'
                    for stp in det["legs"][k]["steps"] if stp["km"] > 0.02 or stp["type"] == "arrive") + "</div>"
        out += f'<div class="stopline"><span class="badge">🏁</span>{t("depot")} · {clock(start_hour, route[-1][1])}</div></div>'
        if not det:
            st.info(t("offline_dir"))
        st.markdown(out, unsafe_allow_html=True)

# ------------------------------------------------------------------ what if
with whatif_tab:
    st.markdown(f"#### {t('whatif_title')}")
    st.caption(t("whatif_help"))
    if st.button(t("run_scen"), type="primary"):
        bar = st.progress(0.0)
        df = scenarios.run_all(profile, day, capacity, van_cost=van_cost, progress=lambda i, n, name: bar.progress(i / n, text=t.scenario(name)))
        bar.empty()
        st.session_state["scen"] = df
    if "scen" in st.session_state:
        df = st.session_state["scen"].copy()
        df["Scenario"] = df["Scenario"].map(t.scenario)
        long = pd.concat([
            df[["Scenario", "On time %", "Cost ($)"]].assign(Method="SwiftRoute"),
            df[["Scenario", "Simple method on time %", "Simple method cost ($)"]]
              .rename(columns={"Simple method on time %": "On time %", "Simple method cost ($)": "Cost ($)"})
              .assign(Method="Simple")])
        scale = alt.Scale(domain=["SwiftRoute", "Simple"], range=[hexc(COLORS[0]), "#94A3B8" if light else "#475569"])
        c1, c2 = st.columns(2, gap="large")
        for col, metric in ((c1, "On time %"), (c2, "Cost ($)")):
            col.markdown(f"**{metric}**")
            col.altair_chart(alt.Chart(long).mark_bar(cornerRadiusEnd=5, height=12).encode(
                y=alt.Y("Scenario:N", sort=list(df["Scenario"]), title=None, axis=alt.Axis(labelLimit=280)),
                x=alt.X(f"{metric}:Q", title=None), yOffset="Method:N",
                color=alt.Color("Method:N", scale=scale, legend=alt.Legend(orient="top", title=None)),
                tooltip=["Scenario", "Method", metric])
                .properties(height=380, background="transparent")
                .configure_view(strokeWidth=0).configure_axis(gridColor=TH["GRID"], domainColor=TH["BTN"], labelColor=TH["TICK"])
                .configure_legend(labelColor=TXT), width="stretch")
        st.markdown(html_table(df, num=set(df.columns) - {"Scenario", "Delivered", "Simple method delivered"}),
                    unsafe_allow_html=True)
        st.download_button(t("download_scen"), df.to_csv(index=False), "scenarios.csv", "text/csv")

# ------------------------------------------------------------------ traffic
with traffic_tab:
    st.markdown(f"#### {t('traffic_title')}")
    st.caption(f"{t('traffic_cap')} · {source}")
    if meta:
        m1, m2, m3 = st.columns(3)
        m1.metric(t("readings"), f"{meta['readings']:,}")
        m2.metric(t("segments"), f"{meta['segments']:,}")
        m3.metric(t("period"), f"{pd.Timestamp(meta['from']):%b %d} – {pd.Timestamp(meta['to']):%b %d, %Y}")
    short = [d[:3] for d in DAY_NAMES[lang]]
    heat = profile.assign(Day=profile.day_of_week.map(lambda d: short[d - 1]), Speed=(profile.speed_factor * 100).round(1))
    st.altair_chart(alt.Chart(heat).mark_rect(cornerRadius=4).encode(
        x=alt.X("hour:O", title=t("hour_of_day"), axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Day:N", sort=short, title=None),
        color=alt.Color("Speed:Q", scale=alt.Scale(scheme="viridis" if cb else "turbo", reverse=not cb), title="%"),
        tooltip=["Day", "hour", "Speed"])
        .properties(height=300, background="transparent")
        .configure_view(strokeWidth=0).configure_axis(domainColor=TH["BTN"], labelColor=TH["TICK"], titleColor=TH["TICK"])
        .configure_legend(labelColor=TH["TICK"], titleColor=TH["TICK"]), width="stretch")
    st.caption(t("traffic_note"))

# ------------------------------------------------------------------ about
with about_tab:
    about = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", f"about_{lang}.md")
    st.markdown(open(about, encoding="utf-8").read() if os.path.exists(about) else "")
