"""'Replay the day': an animated deck.gl map where every truck drives its real street route,
timed by the hour-by-hour traffic replay. Stops turn green the moment they are delivered.

deck.gl + MapLibre are bundled in ./static (served by Streamlit), so the demo needs no CDN."""
import json
import math

from solver import SERVICE_MIN


def _km(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def trips(routes, points, details):
    """routes: simulated [(node, minute)], details: route_detail() per truck (or None -> straight lines).
    Returns [{"path": [[lon, lat]], "ts": [minute], "truck": i}] with a timestamp for every point."""
    out = []
    for i, (route, det) in enumerate(zip(routes, details)):
        path, ts = [], []
        for k, ((a, ta), (b, tb)) in enumerate(zip(route, route[1:])):
            depart = ta + (SERVICE_MIN if a != 0 else 0)
            arrive = max(tb, depart + 0.1)
            if det:
                line = det["legs"][k]["coords"]
            else:
                line = [[points[a][1], points[a][0]], [points[b][1], points[b][0]]]
            cum = [0.0]
            for p, q in zip(line, line[1:]):
                cum.append(cum[-1] + _km(p, q))
            total = cum[-1] or 1.0
            for j, (p, c) in enumerate(zip(line, cum)):
                if path and j == 0:
                    path.append(p); ts.append(depart)   # truck waits at the stop while unloading
                    continue
                path.append(p); ts.append(depart + (arrive - depart) * c / total)
        out.append({"path": path, "ts": ts, "truck": i})
    return out


def html(trip_data, stops, depot, colors, start_hour, labels, autoplay=True, height=620):
    """stops: [{"lon", "lat", "t" (minute delivered), "truck", "name"}]"""
    end = max((max(t["ts"]) for t in trip_data if t["ts"]), default=480)
    payload = json.dumps({"trips": trip_data, "stops": stops, "depot": depot, "colors": colors,
                          "start": start_hour, "end": end, "labels": labels, "autoplay": autoplay}).replace("</", "<\\/")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="app/static/maplibre-gl.css" rel="stylesheet">
<script src="app/static/maplibre-gl.js"></script>
<script src="app/static/deck.min.js"></script>
<style>
 html,body{{margin:0;height:100%;background:#070B17;font-family:Inter,system-ui,sans-serif;color:#E2E8F0;overflow:hidden}}
 #map{{position:absolute;inset:0;border-radius:16px;overflow:hidden}}
 .hud{{position:absolute;left:16px;top:16px;background:rgba(10,16,32,.82);backdrop-filter:blur(8px);
      border:1px solid #1E293B;border-radius:14px;padding:14px 18px;min-width:210px;z-index:2}}
 .clock{{font:700 38px 'JetBrains Mono',ui-monospace,monospace;letter-spacing:-.02em;
        background:linear-gradient(90deg,#22D3EE,#C084FC);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
 .sub{{color:#94A3B8;font-size:13px;margin-top:2px}} .sub b{{color:#4ADE80;font-size:15px}}
 .ctrl{{position:absolute;left:16px;right:16px;bottom:16px;display:flex;gap:12px;align-items:center;z-index:2;
       background:rgba(10,16,32,.82);backdrop-filter:blur(8px);border:1px solid #1E293B;border-radius:14px;padding:10px 14px}}
 button,select{{background:linear-gradient(135deg,#06B6D4,#8B5CF6);color:#fff;border:0;border-radius:10px;
       padding:8px 16px;font-weight:700;cursor:pointer;font-size:14px}}
 select{{background:#0F1629;border:1px solid #334155}}
 button:focus-visible,select:focus-visible,input:focus-visible{{outline:3px solid #FACC15;outline-offset:2px}}
 input[type=range]{{flex:1;accent-color:#22D3EE}}
 .bar{{height:6px;background:#1E293B;border-radius:9px;margin-top:10px;overflow:hidden}} .bar i{{display:block;height:100%;
       background:linear-gradient(90deg,#22D3EE,#4ADE80);width:0}}
</style></head><body>
<div id="map" role="img" aria-label="{labels['aria']}"></div>
<div class="hud" aria-live="polite"><div class="clock" id="clock">09:00</div>
 <div class="sub"><b id="done">0</b> / <span id="total">0</span> {labels['delivered']}</div><div class="bar"><i id="prog"></i></div></div>
<div class="ctrl"><button id="play" aria-label="{labels['play']}">▶ {labels['play']}</button>
 <input id="time" type="range" min="0" max="1000" value="0" aria-label="time">
 <label style="font-size:13px;color:#94A3B8">{labels['speed']}
  <select id="spd"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option></select></label></div>
<script>
const D = {payload};
const C = D.colors, END = D.end, START = D.start;
let T = 0, playing = D.autoplay, last = null;
const total = D.stops.length; document.getElementById('total').textContent = total;
function heads(t) {{
  return D.trips.map(tr => {{
    const ts = tr.ts, p = tr.path; if (!ts.length) return null;
    if (t <= ts[0]) return {{pos: p[0], truck: tr.truck}};
    if (t >= ts[ts.length-1]) return {{pos: p[p.length-1], truck: tr.truck}};
    let lo = 0, hi = ts.length - 1; while (hi - lo > 1) {{ const m = (lo+hi)>>1; if (ts[m] <= t) lo = m; else hi = m; }}
    const f = (t - ts[lo]) / Math.max(ts[hi] - ts[lo], 1e-6);
    return {{pos: [p[lo][0] + (p[hi][0]-p[lo][0])*f, p[lo][1] + (p[hi][1]-p[lo][1])*f], truck: tr.truck}};
  }}).filter(Boolean);
}}
function layers() {{
  return [
    new deck.PathLayer({{id:'ghost', data:D.trips, getPath:d=>d.path, getColor:d=>[...C[d.truck%C.length],40],
      widthMinPixels:2, capRounded:true, jointRounded:true}}),
    new deck.TripsLayer({{id:'trips', data:D.trips, getPath:d=>d.path, getTimestamps:d=>d.ts,
      getColor:d=>C[d.truck%C.length], widthMinPixels:5, trailLength:60, currentTime:T, fadeTrail:true,
      capRounded:true, jointRounded:true}}),
    new deck.ScatterplotLayer({{id:'stops', data:D.stops, getPosition:d=>[d.lon,d.lat], radiusMinPixels:5, getRadius:60,
      getFillColor:d=> d.t===null ? [248,113,113] : (T>=d.t ? [74,222,128] : [71,85,105]),
      stroked:true, getLineColor:[7,11,23], lineWidthMinPixels:2, pickable:true, updateTriggers:{{getFillColor:T}}}}),
    new deck.ScatterplotLayer({{id:'glow', data:heads(T), getPosition:d=>d.pos, getRadius:260, radiusMinPixels:12,
      getFillColor:d=>[...C[d.truck%C.length],70]}}),
    new deck.ScatterplotLayer({{id:'heads', data:heads(T), getPosition:d=>d.pos, getRadius:90, radiusMinPixels:6,
      getFillColor:[255,255,255], stroked:true, getLineColor:d=>C[d.truck%C.length], lineWidthMinPixels:3}}),
    new deck.ScatterplotLayer({{id:'depot', data:[D.depot], getPosition:d=>[d.lon,d.lat], getRadius:160, radiusMinPixels:9,
      getFillColor:[255,255,255], stroked:true, getLineColor:[34,211,238], lineWidthMinPixels:4}}),
  ];
}}
const opts = {{container:'map', controller:true,
  initialViewState:{{longitude:D.depot.lon, latitude:D.depot.lat-0.02, zoom:10.8, pitch:45, bearing:-12}},
  getTooltip:({{object}}) => object && object.name ? object.name : null, layers:layers()}};
try {{ if (window.maplibregl) {{ opts.map = maplibregl; opts.mapStyle = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'; }} }} catch(e) {{}}
const view = new deck.DeckGL(opts);
const pad = n => String(Math.floor(n)).padStart(2,'0');
function draw() {{
  const m = START*60 + T; document.getElementById('clock').textContent = pad(m/60%24)+':'+pad(m%60);
  const done = D.stops.filter(s => s.t!==null && T>=s.t).length;
  document.getElementById('done').textContent = done;
  document.getElementById('prog').style.width = (100*done/Math.max(total,1))+'%';
  document.getElementById('time').value = 1000*T/END;
  view.setProps({{layers:layers()}});
}}
function tick(now) {{
  if (playing) {{ if (last!==null) T += (now-last)/1000 * END/30 * parseFloat(document.getElementById('spd').value);
    if (T >= END) {{ T = END; playing = false; setBtn(); }} draw(); }}
  last = now; requestAnimationFrame(tick);
}}
const btn = document.getElementById('play');
function setBtn() {{ btn.textContent = playing ? '⏸ {labels['pause']}' : '▶ {labels['play']}'; }}
btn.onclick = () => {{ if (T>=END) T = 0; playing = !playing; setBtn(); }};
document.getElementById('time').oninput = e => {{ T = END*e.target.value/1000; playing = false; setBtn(); draw(); }};
if (!D.autoplay) T = END;
setBtn(); draw(); requestAnimationFrame(tick);
</script></body></html>"""
