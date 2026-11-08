"""SwiftRoute demo app.  Run:  streamlit run app.py"""
import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

import sample
import scenarios
from geo import geocode, road_path
from plan import run, SHIFT_HOURS
from traffic import load_profile

st.set_page_config(page_title="SwiftRoute", page_icon="🚚", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ style
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, textarea, select, label {font-family: 'Inter', sans-serif !important;}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none !important;}
header[data-testid="stHeader"] {background: transparent; height: 0;}
.block-container {padding: 1.4rem 2rem 3rem; max-width: 1500px;}
[data-testid="stAppViewContainer"] {background:
   radial-gradient(1200px 500px at 85% -10%, rgba(34,211,238,.10), transparent 60%),
   radial-gradient(900px 500px at -10% 10%, rgba(168,85,247,.10), transparent 60%), #070B17;}
[data-testid="stSidebar"] {background: #0A1020; border-right: 1px solid #1E293B;}
[data-testid="stSidebar"] .block-container {padding-top: 1.2rem;}

/* top bar */
.topbar {display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;}
.brand {display: flex; align-items: center; gap: 14px;}
.logo {width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-size: 22px;
       background: linear-gradient(135deg, #22D3EE, #A855F7); box-shadow: 0 0 24px rgba(34,211,238,.35);}
.brand h1 {font-size: 1.55rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -.02em; color: #F8FAFC;}
.brand p {margin: 0; color: #94A3B8; font-size: .9rem;}
.pills {display: flex; gap: 8px; flex-wrap: wrap;}
.pill {font-size: .75rem; color: #CBD5E1; padding: 6px 12px; border-radius: 999px; background: #0F1629;
       border: 1px solid #1E293B; display: inline-flex; align-items: center; gap: 7px;}
.dot {width: 7px; height: 7px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 8px #22C55E;}
.dot.warn {background: #F59E0B; box-shadow: 0 0 8px #F59E0B;}

/* hero savings */
.hero {display: grid; grid-template-columns: 1.3fr 1fr 1fr 1fr; gap: 14px; margin-bottom: 14px;}
@media (max-width: 1100px) {.hero {grid-template-columns: 1fr 1fr;}}
.card {background: linear-gradient(180deg, #0F1629, #0B1122); border: 1px solid #1E293B; border-radius: 16px; padding: 18px 20px;}
.card .lbl {font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; color: #64748B; font-weight: 600;}
.card .big {font-family: 'JetBrains Mono', monospace; font-size: 2.1rem; font-weight: 700; color: #F8FAFC; line-height: 1.15; margin-top: 6px;}
.card .sub {font-size: .82rem; color: #94A3B8; margin-top: 4px;}
.card.accent {background: linear-gradient(135deg, rgba(34,211,238,.16), rgba(168,85,247,.16)); border-color: rgba(34,211,238,.35);}
.card.accent .big {font-size: 2.6rem; background: linear-gradient(90deg, #22D3EE, #C084FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.up {color: #4ADE80;} .down {color: #F87171;} .flat {color: #64748B;}
.bar {height: 6px; background: #1E293B; border-radius: 99px; margin-top: 10px; overflow: hidden; position: relative;}
.bar > i {position: absolute; inset: 0 auto 0 0; border-radius: 99px;}

/* side panel */
.panel-title {font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; color: #64748B; font-weight: 600; margin: 4px 0 10px;}
.mini {display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;}
.mini .card {padding: 12px 14px;} .mini .card .big {font-size: 1.35rem;}
.truck {display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 12px; background: #0F1629;
        border: 1px solid #1E293B; margin-bottom: 8px;}
.truck .sw {width: 10px; height: 34px; border-radius: 6px; flex: none;}
.truck .nm {font-weight: 700; color: #F1F5F9; font-size: .92rem;}
.truck .meta {color: #94A3B8; font-size: .78rem; font-family: 'JetBrains Mono', monospace;}
.truck .load {margin-left: auto; text-align: right; font-family: 'JetBrains Mono', monospace; font-size: .8rem; color: #CBD5E1;}
.alert {background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.35); color: #FCA5A5;
        border-radius: 12px; padding: 12px 14px; font-size: .88rem; margin-top: 6px;}
.alert b {color: #FECACA;}

/* map frame */
[data-testid="stDeckGlJsonChart"] {border-radius: 16px; overflow: hidden; border: 1px solid #1E293B; background: #0B1122;}

/* tabs */
.stTabs [data-baseweb="tab-list"] {gap: 6px; background: #0F1629; padding: 5px; border-radius: 12px; border: 1px solid #1E293B; width: fit-content;}
.stTabs [data-baseweb="tab"] {height: 36px; border-radius: 9px; padding: 0 16px; color: #94A3B8; background: transparent;}
.stTabs [aria-selected="true"] {background: linear-gradient(135deg, rgba(34,211,238,.18), rgba(168,85,247,.18)); color: #F8FAFC !important;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display: none;}

/* sidebar */
.side-h {font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; color: #22D3EE; font-weight: 700; margin: 10px 0 4px;}
.stButton > button, .stDownloadButton > button {border-radius: 10px; font-weight: 600; border: 1px solid #334155;}
.stButton > button[kind="primary"] {background: linear-gradient(135deg, #06B6D4, #8B5CF6); border: 0; color: white;}
[data-testid="stExpander"] {border: 1px solid #1E293B; border-radius: 12px; background: #0B1122;}
</style>
""", unsafe_allow_html=True)

profile, source, meta = st.cache_data(load_profile)()
real = "real" in source
DAYS = {"Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5, "Friday": 6, "Saturday": 7}
COLORS = [[34, 211, 238], [168, 85, 247], [74, 222, 128], [251, 146, 60], [244, 114, 182],
          [250, 204, 21], [96, 165, 250], [248, 113, 113], [45, 212, 191], [203, 213, 225]]
hexc = lambda c: "#%02x%02x%02x" % tuple(c)
clock = lambda start, m: f"{start + int(m) // 60:02d}:{int(m) % 60:02d}"
MAP_STYLE = None if __import__("os").environ.get("SWIFTROUTE_NO_TILES") else "dark"
road_path_cached = st.cache_data(road_path, show_spinner=False)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="side-h">Shift</div>', unsafe_allow_html=True)
    day = st.selectbox("Day", list(DAYS), index=2)
    start_hour = st.slider("Start hour", 5, 14, 9, format="%d:00")
    st.caption(f"Drivers work {start_hour}:00 – {start_hour + SHIFT_HOURS}:00")
    st.markdown('<div class="side-h">Fleet</div>', unsafe_allow_html=True)
    n_trucks = st.slider("Trucks", 1, 10, 4)
    capacity = st.slider("Packages per truck", 5, 40, 15)
    st.markdown('<div class="side-h">Chaos mode</div>', unsafe_allow_html=True)
    jam = st.slider("Traffic jam (% slower)", 0, 60, 0, format="%d%%")
    broken = st.toggle("A truck breaks down")
    urgent = st.toggle("Urgent order comes in (3 packages, deliver 12–14h)")
    st.markdown('<div class="side-h">Map</div>', unsafe_allow_html=True)
    show_naive = st.toggle("Show simple method's routes", False)

# ------------------------------------------------------------------ top bar
st.markdown(f"""
<div class="topbar">
  <div class="brand"><div class="logo">🚚</div>
    <div><h1>SwiftRoute</h1><p>Traffic-aware delivery planning · capacity + time slots</p></div></div>
  <div class="pills">
    <span class="pill"><span class="dot {'' if real else 'warn'}"></span>{'Chicago traffic history' if real else 'Placeholder traffic'}</span>
    <span class="pill"><span class="dot"></span>OpenStreetMap roads</span>
    <span class="pill"><span class="dot"></span>OR-Tools optimizer</span>
  </div>
</div>""", unsafe_allow_html=True)

plan_tab, whatif_tab, traffic_tab, about_tab = st.tabs(["Live plan", "What if?", "Traffic data", "How it works"])

# ------------------------------------------------------------------ live plan
with plan_tab:
    mode = st.radio("Deliveries", ["Sample day · Chicago · 40 stops", "My own addresses"],
                    horizontal=True, label_visibility="collapsed")
    if mode.startswith("Sample"):
        depot, stops = sample.DEPOT, sample.make(40)
    else:
        c1, c2 = st.columns([1, 2])
        depot_txt = c1.text_input("Depot address", "1200 W Fulton Market, Chicago, IL")
        txt = c2.text_area("Deliveries — one per line:  address | packages | time slot",
                           "233 S Wacker Dr, Chicago, IL | 2 | 9-12\n"
                           "1060 W Addison St, Chicago, IL | 1 | 10-17\n"
                           "5700 S Lake Shore Dr, Chicago, IL | 3 | 13-16", height=120)
        if c1.button("Find addresses", type="primary"):
            with st.spinner("Looking up addresses (1 per second)…"):
                d = geocode(depot_txt)
                found, missing = [], []
                for line in filter(None, map(str.strip, txt.splitlines())):
                    parts = [p.strip() for p in line.split("|")] + ["1", "9-17"]
                    try:
                        a, b = (int(x) for x in parts[2].split("-"))
                        loc = geocode(parts[0])
                    except Exception:
                        loc = None
                    if loc:
                        found.append({"name": parts[0], "lat": loc[0], "lon": loc[1],
                                      "demand": int(parts[1]), "slot": (a, b)})
                    else:
                        missing.append(parts[0])
            st.session_state["typed"] = ((depot_txt, *d) if d else None, found, missing)
        if "typed" not in st.session_state:
            st.info("Type your addresses and press **Find addresses**.")
            st.stop()
        depot, stops, missing = st.session_state["typed"]
        if depot is None:
            st.error("Couldn't find the depot address."); st.stop()
        for m in missing:
            st.warning(f"Skipped (not found or bad format): {m}")
        if not stops:
            st.stop()

    if urgent:
        stops = stops + [{"name": "⚡ URGENT order · 875 N Michigan Ave", "lat": 41.8988, "lon": -87.6229,
                          "demand": 3, "slot": (12, 14)}]
    trucks = max(1, n_trucks - (1 if broken else 0))
    with st.spinner("Optimizing routes…"):
        r = st.cache_data(run, show_spinner=False)(depot, stops, trucks, capacity, profile,
                                                    DAYS[day], start_hour, jam / 100)
    s, b = r["smart_kpi"], r["naive_kpi"]

    # ---- hero numbers
    saved = b["Cost ($)"] - s["Cost ($)"]
    pct = saved / b["Cost ($)"] * 100 if b["Cost ($)"] else 0
    def delta(v, base, lower_better=True, unit=""):
        d = v - base
        if abs(d) < 0.05:
            return '<span class="flat">same as simple method</span>'
        good = (d < 0) == lower_better
        return f'<span class="{"up" if good else "down"}">{"▼" if d < 0 else "▲"} {unit}{abs(d):,.1f}</span> vs simple ({unit}{base:,})'
    st.markdown(f"""
    <div class="hero">
      <div class="card accent"><div class="lbl">Saved today vs simple routing</div>
        <div class="big">${saved:,} · {pct:.0f}%</div>
        <div class="sub">${s['Cost ($)']:,} instead of ${b['Cost ($)']:,} — fuel + driver pay</div></div>
      <div class="card"><div class="lbl">On time</div><div class="big">{s['On time %']}%</div>
        <div class="sub">{delta(s['On time %'], b['On time %'], lower_better=False)}</div>
        <div class="bar"><i style="width:{s['On time %']}%;background:linear-gradient(90deg,#22D3EE,#4ADE80)"></i></div></div>
      <div class="card"><div class="lbl">Distance</div><div class="big">{s['Total km']} km</div>
        <div class="sub">{delta(s['Total km'], b['Total km'])}</div></div>
      <div class="card"><div class="lbl">Driver hours</div><div class="big">{s['Driver hours']} h</div>
        <div class="sub">{delta(s['Driver hours'], b['Driver hours'])}</div></div>
    </div>""", unsafe_allow_html=True)

    # ---- map + side panel
    routes = r["naive"] if show_naive else r["smart"]
    pts, st_list = r["points"], r["stops"]
    skipped_names = {x["name"] for x in r["skipped"]}

    paths, dots, labels = [], [], []
    for i, route in enumerate(routes):
        color = COLORS[i % 10]
        line = road_path_cached(tuple(pts[x] for x, _ in route)) or [[pts[x][1], pts[x][0]] for x, _ in route]
        paths.append({"path": line, "color": color, "label": f"Truck {i+1}"})
        for n, (x, t) in enumerate(route[1:-1], 1):
            stop = st_list[x - 1]
            dots.append({"lon": stop["lon"], "lat": stop["lat"], "color": color, "r": 70,
                         "label": f"Truck {i+1} · stop {n} · {stop['name']} · arrives {clock(start_hour, t)} "
                                  f"(slot {stop['slot'][0]}:00–{stop['slot'][1]}:00)"})
            labels.append({"lon": stop["lon"], "lat": stop["lat"], "text": str(n)})
    for x in (r["skipped"] + r["outside"]) if not show_naive else []:
        dots.append({"lon": x["lon"], "lat": x["lat"], "color": [248, 113, 113], "r": 90,
                     "label": f"❌ {x['name']} can't be delivered on time (slot {x['slot'][0]}:00–{x['slot'][1]}:00)"})
    depot_pt = [{"lon": depot[2], "lat": depot[1], "label": f"🏭 {depot[0]}"}]

    layers = [
        pdk.Layer("PathLayer", paths, get_path="path", get_color="color", width_min_pixels=10,
                  opacity=0.18, cap_rounded=True, joint_rounded=True),                       # glow
        pdk.Layer("PathLayer", paths, get_path="path", get_color="color", width_min_pixels=3,
                  cap_rounded=True, joint_rounded=True, pickable=True),                      # line
        pdk.Layer("ScatterplotLayer", dots, get_position=["lon", "lat"], get_fill_color="color",
                  get_radius="r", radius_min_pixels=5, stroked=True, get_line_color=[7, 11, 23],
                  line_width_min_pixels=2, pickable=True),
        pdk.Layer("ScatterplotLayer", depot_pt, get_position=["lon", "lat"], get_fill_color=[255, 255, 255],
                  get_radius=160, radius_min_pixels=9, stroked=True, get_line_color=[34, 211, 238],
                  line_width_min_pixels=4, pickable=True),
    ]

    map_col, side_col = st.columns([2.3, 1], gap="medium")
    with map_col:
        st.pydeck_chart(pdk.Deck(
            layers=layers, map_style=MAP_STYLE,
            initial_view_state=pdk.ViewState(latitude=depot[1] - 0.01, longitude=depot[2] + 0.005, zoom=11.1, pitch=35),
            tooltip={"text": "{label}", "style": {"background": "#0F1629", "color": "#E2E8F0",
                                                  "fontFamily": "Inter", "fontSize": "12px", "borderRadius": "8px"}}),
            height=600)
        st.caption(f"{'Simple “nearest stop next” routes' if show_naive else 'SwiftRoute plan'} · "
                   f"road speed this shift {r['factor']:.0%} of empty roads · {r['dist_source']}"
                   + (" · 🚚 one truck down" if broken else "") + (" · ⚡ urgent order added" if urgent else "") + (f" · 🔥 +{jam}% traffic" if jam else ""))

    with side_col:
        st.markdown(f"""
        <div class="mini">
          <div class="card"><div class="lbl">Delivered</div><div class="big">{s['Delivered']}</div></div>
          <div class="card"><div class="lbl">CO₂</div><div class="big">{s['CO2 (kg)']} kg</div></div>
        </div>
        <div class="panel-title">Fleet · {len(routes)} trucks{' (simple method)' if show_naive else ''}</div>""",
                    unsafe_allow_html=True)
        html = ""
        for i, route in enumerate(routes):
            load = sum(st_list[x - 1]["demand"] for x, _ in route[1:-1])
            html += (f'<div class="truck"><div class="sw" style="background:{hexc(COLORS[i % 10])};'
                     f'box-shadow:0 0 12px {hexc(COLORS[i % 10])}"></div>'
                     f'<div><div class="nm">Truck {i+1}</div><div class="meta">'
                     f'{clock(start_hour, route[0][1])} → {clock(start_hour, route[-1][1])}</div></div>'
                     f'<div class="load">{len(route) - 2} stops<br>{load}/{capacity} pkgs</div></div>')
        st.markdown(html, unsafe_allow_html=True)
        missed = r["skipped"] + r["outside"]
        if missed and not show_naive:
            st.markdown(f'<div class="alert"><b>{len(missed)} deliveries can\'t make their time slot</b> '
                        f'with {trucks} trucks (red dots). Add a truck in the sidebar to fix it.</div>',
                        unsafe_allow_html=True)

    # ---- schedule
    st.markdown('<div class="panel-title" style="margin-top:18px">Driver schedules</div>', unsafe_allow_html=True)
    all_rows = []
    for i, route in enumerate(routes):
        for n, (x, t) in enumerate(route):
            stop = None if x == 0 else st_list[x - 1]
            all_rows.append({"Truck": f"Truck {i+1}", "#": n,
                             "Stop": "🏭 Depot" if x == 0 else stop["name"],
                             "Arrives": clock(start_hour, t),
                             "Time slot": "" if x == 0 else f"{stop['slot'][0]}:00–{stop['slot'][1]}:00",
                             "Status": "" if x == 0 else ("On time" if start_hour + t / 60 <= stop["slot"][1] else "Late"),
                             "Packages": 0 if x == 0 else stop["demand"]})
    sched = pd.DataFrame(all_rows)
    pick = st.segmented_control("Truck", [f"Truck {i+1}" for i in range(len(routes))],
                                default="Truck 1", label_visibility="collapsed")
    st.dataframe(sched[sched.Truck == (pick or "Truck 1")].drop(columns="Truck"), hide_index=True, width="stretch",
                 column_config={"Packages": st.column_config.ProgressColumn("Packages", min_value=0, max_value=3, format="%d")})
    st.download_button("Download all schedules (CSV)", sched.to_csv(index=False), "swiftroute_plan.csv", "text/csv")

# ------------------------------------------------------------------ what if
with whatif_tab:
    st.markdown("#### What happens to cost and service when things change?")
    st.caption("Six scenarios on the sample Chicago day, each planned by SwiftRoute and by the simple method. ~1 minute.")
    if st.button("Run scenarios", type="primary"):
        bar = st.progress(0.0)
        df = scenarios.run_all(profile, DAYS[day], capacity,
                               progress=lambda i, n, name: bar.progress(i / n, text=name))
        bar.empty()
        st.session_state["scen"] = df
    if "scen" in st.session_state:
        df = st.session_state["scen"]
        long = pd.concat([
            df[["Scenario", "On time %", "Cost ($)"]].assign(Method="SwiftRoute"),
            df[["Scenario", "Simple method on time %", "Simple method cost ($)"]]
              .rename(columns={"Simple method on time %": "On time %", "Simple method cost ($)": "Cost ($)"})
              .assign(Method="Simple method")])
        scale = alt.Scale(domain=["SwiftRoute", "Simple method"], range=["#22D3EE", "#334155"])
        c1, c2 = st.columns(2, gap="large")
        for col, metric in ((c1, "On time %"), (c2, "Cost ($)")):
            col.markdown(f"**{metric}**")
            col.altair_chart(alt.Chart(long).mark_bar(cornerRadiusEnd=5, height=12).encode(
                y=alt.Y("Scenario:N", sort=list(df["Scenario"]), title=None, axis=alt.Axis(labelLimit=280)),
                x=alt.X(f"{metric}:Q", title=None), yOffset="Method:N",
                color=alt.Color("Method:N", scale=scale, legend=alt.Legend(orient="top", title=None)),
                tooltip=["Scenario", "Method", metric])
                .properties(height=380, background="transparent")
                .configure_view(strokeWidth=0).configure_axis(gridColor="#1E293B", domainColor="#334155",
                                                              labelColor="#94A3B8"), width="stretch")
        st.dataframe(df, hide_index=True, width="stretch")
        st.download_button("Download scenarios (CSV)", df.to_csv(index=False), "scenarios.csv", "text/csv")

# ------------------------------------------------------------------ traffic
with traffic_tab:
    st.markdown("#### When are Chicago's roads slow?")
    st.caption(f"Each road segment's speed as % of its own free-flow speed, averaged over all segments · {source}")
    if meta:
        m1, m2, m3 = st.columns(3)
        m1.metric("Speed readings", f"{meta['readings']:,}")
        m2.metric("Road segments", f"{meta['segments']:,}")
        m3.metric("Period", f"{pd.Timestamp(meta['from']):%b %d} – {pd.Timestamp(meta['to']):%b %d, %Y}")
    inv = {v: k[:3] for k, v in DAYS.items()}
    heat = profile.assign(Day=profile.day_of_week.map(inv), Speed=(profile.speed_factor * 100).round(1))
    st.altair_chart(alt.Chart(heat).mark_rect(cornerRadius=4).encode(
        x=alt.X("hour:O", title="Hour of day", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Day:N", sort=[k[:3] for k in DAYS], title=None),
        color=alt.Color("Speed:Q", scale=alt.Scale(scheme="turbo", reverse=True), title="Speed %"),
        tooltip=["Day", "hour", "Speed"])
        .properties(height=300, background="transparent")
        .configure_view(strokeWidth=0).configure_axis(domainColor="#334155", labelColor="#94A3B8", titleColor="#94A3B8")
        .configure_legend(labelColor="#94A3B8", titleColor="#94A3B8"), width="stretch")
    st.caption("Blue = free-flowing · red = rush hour. Every drive in a plan is slowed by the value for the hour it happens in.")

# ------------------------------------------------------------------ about
with about_tab:
    c1, c2 = st.columns(2, gap="large")
    c1.markdown("""
#### How it works
1. **Addresses → map points** with OpenStreetMap.
2. **Real roads:** distance and empty-road drive time between every pair of stops (OSRM on OpenStreetMap).
3. **Traffic:** 2.6M speed readings from 1,046 Chicago road segments (City of Chicago Traffic Tracker,
   April 2026) give how much slower roads are at each hour of the week. Each drive is slowed by the
   value for the hour it happens in.
4. **Optimizer:** Google OR-Tools solves the vehicle routing problem with truck capacity and customer
   time slots, minimizing real cost (fuel + driver pay).
5. **Check:** every route is replayed hour by hour with real traffic; all numbers come from that replay.
6. **Benchmark:** the same day planned with the simple "go to the nearest stop next" method.
""")
    c2.markdown("""
#### Assumptions
- Empty-road drive times from OpenStreetMap (40 km/h straight-line fallback if offline)
- **5 min** to hand over each delivery
- **$0.60 / km** fuel and wear · **$25 / hour** per driver
- **0.25 kg CO₂ / km** (delivery van)
- **8-hour** shift; trucks may leave later instead of waiting at a customer
""")
