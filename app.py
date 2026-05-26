"""
The American Frontier ETF — Investor Product
Landing page + PIN-protected live dashboard
"""
from flask import Flask, request, redirect, session, render_template_string
import requests as req_lib, json, os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gfc-etf-2026-frontier')
PIN = os.environ.get('ETF_PIN', '2026')
DATA_URL = 'https://jarvis.ankurjoshi-demo.com/etf-data'

BACKTEST = {"dates":["2026-01-02","2026-01-05","2026-01-06","2026-01-07","2026-01-08","2026-01-09","2026-01-12","2026-01-13","2026-01-14","2026-01-15","2026-01-16","2026-01-20","2026-01-21","2026-01-22","2026-01-23","2026-01-26","2026-01-27","2026-01-28","2026-01-29","2026-01-30","2026-02-02","2026-02-03","2026-02-04","2026-02-05","2026-02-06","2026-02-09","2026-02-10","2026-02-11","2026-02-12","2026-02-13","2026-02-17","2026-02-18","2026-02-19","2026-02-20","2026-02-23","2026-02-24","2026-02-25","2026-02-26","2026-02-27","2026-03-02","2026-03-03","2026-03-04","2026-03-05","2026-03-06","2026-03-09","2026-03-10","2026-03-11","2026-03-12","2026-03-13","2026-03-16","2026-03-17","2026-03-18","2026-03-19","2026-03-20","2026-03-23","2026-03-24","2026-03-25","2026-03-26","2026-03-27","2026-03-30","2026-03-31","2026-04-01","2026-04-02","2026-04-06","2026-04-07","2026-04-08","2026-04-09","2026-04-10","2026-04-13","2026-04-14","2026-04-15","2026-04-16","2026-04-17","2026-04-20","2026-04-21","2026-04-22","2026-04-23","2026-04-24","2026-04-27","2026-04-28","2026-04-29","2026-04-30","2026-05-01","2026-05-04","2026-05-05","2026-05-06","2026-05-07","2026-05-08","2026-05-11","2026-05-12","2026-05-13","2026-05-14","2026-05-15","2026-05-18","2026-05-19","2026-05-20","2026-05-21","2026-05-22"],"etf":[10000.0,10500.82,10849.13,10882.72,10982.37,11068.87,11204.9,10849.42,11309.4,11157.55,11647.4,11398.7,11100.64,11867.97,11809.47,11464.96,11809.66,11961.11,11192.38,10617.7,10310.59,10871.98,10179.0,9376.26,10069.52,10466.13,10148.05,9785.3,9072.89,9266.02,9386.3,9583.5,9669.98,9385.9,9505.8,9823.04,9637.86,9977.5,9699.36,10266.06,10230.46,10481.05,10105.46,9793.53,10056.82,10024.58,10235.92,9866.82,9745.84,9762.14,9938.35,9441.32,9458.28,9108.71,9479.24,9115.29,9553.52,9151.07,8563.26,8324.8,9078.15,9307.44,9986.11,10038.55,10002.25,10544.03,10299.11,10442.51,10889.67,10774.02,11050.45,11659.56,11771.75,11919.49,11768.31,12138.64,11370.18,11040.9,11199.44,10886.88,10836.9,11464.48,11481.17,11398.31,11381.87,11685.74,10990.94,11887.2,12311.84,12027.25,12701.81,12953.69,12516.37,12427.12,12077.49,12513.12,13093.01,14334.33],"qqq":[10000.0,10079.43,10167.99,10177.78,10119.88,10220.67,10229.16,10213.99,10104.87,10141.25,10132.76,9917.47,10051.54,10124.61,10156.58,10201.27,10293.74,10327.83,10266.02,10142.71,10212.36,10055.45,9879.8,9737.57,9943.4,10019.57,9973.09,9999.84,9796.45,9817.33,9807.21,9880.45,9842.61,9929.7,9809.01,9914.37,10058.06,9936.72,9904.91,9917.96,9811.78,9961.35,9931.33,9781.93,9912.58,9912.74,9911.44,9741.32,9683.58,9792.21,9840.0,9702.83,9672.17,9493.41,9602.38,9536.74,9599.45,9370.33,9187.26,9117.04,9425.69,9542.12,9553.07,9610.55,9612.02,9897.81,9964.76,9979.13,10082.34,10265.41,10409.12,10459.25,10596.1,10562.46,10522.29,10698.33,10638.07,10841.55,10847.26,10738.18,10803.83,10904.59,11009.26,10988.52,11131.09,11362.33,11348.78,11614.8,11648.44,11549.64,11671.63,11754.59,11577.24,11527.43,11456.4,11646.16,11668.37,11717.85],"etf_return":43.3,"qqq_return":17.2,"etf_final":14334.33,"qqq_final":11717.85}

def get_etf_data():
    try:
        r = req_lib.get(DATA_URL, timeout=8)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

# ── LANDING PAGE ───────────────────────────────────────────────────────────────
LANDING = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>American Frontier ETF — Next Generation AI-Managed Fund</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--purple:#7C3AED;--purple-light:#8B5CF6;--dark:#0A0A14;--card:#111827;--border:#1F2937;--text:#F9FAFB;--muted:#9CA3AF;--green:#10B981;--red:#EF4444}
body{background:var(--dark);color:var(--text);font-family:'Inter',system-ui,sans-serif;font-size:15px;line-height:1.6}

/* NAV */
nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(10,10,20,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 40px;height:64px;display:flex;align-items:center;justify-content:space-between}
.nav-logo{font-size:14px;font-weight:800;letter-spacing:.08em;color:#fff}
.nav-logo span{color:var(--purple)}
.nav-cta{background:var(--purple);color:#fff;padding:9px 22px;border-radius:8px;font-size:13px;font-weight:700;text-decoration:none;transition:background .15s}
.nav-cta:hover{background:var(--purple-light)}

/* HERO */
.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 24px 80px;background:radial-gradient(ellipse 80% 60% at 50% 0%, rgba(124,58,237,.2) 0%, transparent 70%)}
.hero-tag{display:inline-block;background:rgba(124,58,237,.15);color:var(--purple-light);font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:6px 16px;border-radius:20px;border:1px solid rgba(124,58,237,.3);margin-bottom:28px}
.hero h1{font-size:clamp(40px,7vw,80px);font-weight:900;line-height:1.05;letter-spacing:-.03em;margin-bottom:20px}
.hero h1 span{background:linear-gradient(135deg,#a78bfa,#7C3AED,#4f46e5);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-sub{font-size:18px;color:var(--muted);max-width:580px;margin:0 auto 48px;font-weight:400;line-height:1.7}
.hero-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.btn-primary{background:var(--purple);color:#fff;padding:14px 32px;border-radius:10px;font-size:15px;font-weight:700;text-decoration:none;transition:all .15s;box-shadow:0 0 40px rgba(124,58,237,.4)}
.btn-primary:hover{background:var(--purple-light);transform:translateY(-1px)}
.btn-secondary{background:rgba(255,255,255,.06);color:#fff;padding:14px 32px;border-radius:10px;font-size:15px;font-weight:600;text-decoration:none;border:1px solid rgba(255,255,255,.12);transition:all .15s}
.btn-secondary:hover{background:rgba(255,255,255,.1)}

/* STATS BAR */
.stats-bar{background:var(--card);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:32px 40px;display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border)}
.stat{background:var(--card);padding:28px 32px;text-align:center}
.stat-val{font-size:36px;font-weight:800;letter-spacing:-.02em;line-height:1}
.stat-val.green{color:var(--green)}
.stat-label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:6px;font-weight:600}
.stat-sub{font-size:12px;color:var(--muted);margin-top:4px}

/* SECTIONS */
section{padding:96px 40px;max-width:1200px;margin:0 auto}
.section-tag{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--purple-light);margin-bottom:12px}
.section-title{font-size:clamp(28px,4vw,44px);font-weight:800;letter-spacing:-.02em;line-height:1.15;margin-bottom:16px}
.section-sub{font-size:16px;color:var(--muted);max-width:600px;line-height:1.7}

/* CHART */
.chart-section{padding:0 40px 96px;max-width:1200px;margin:0 auto}
.chart-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:40px;position:relative;overflow:hidden}
.chart-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--purple),transparent)}
.chart-meta{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:32px;flex-wrap:wrap;gap:20px}
.chart-title{font-size:20px;font-weight:700}
.chart-title small{display:block;font-size:13px;color:var(--muted);font-weight:400;margin-top:4px}
.chart-legend{display:flex;gap:24px}
.leg{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600}
.leg-dot{width:12px;height:3px;border-radius:2px}

/* PILLARS */
.pillars{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:48px}
.pillar-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:32px;position:relative;overflow:hidden;transition:border-color .2s}
.pillar-card:hover{border-color:rgba(124,58,237,.5)}
.pillar-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px}
.p1::after{background:linear-gradient(90deg,#3B82F6,#60A5FA)}
.p2::after{background:linear-gradient(90deg,#10B981,#34D399)}
.p3::after{background:linear-gradient(90deg,#7C3AED,#A78BFA)}
.pillar-num{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}
.p1 .pillar-num{color:#60A5FA}.p2 .pillar-num{color:#34D399}.p3 .pillar-num{color:#A78BFA}
.pillar-card h3{font-size:18px;font-weight:700;margin-bottom:10px}
.pillar-card p{font-size:14px;color:var(--muted);line-height:1.7}
.pillar-tickers{display:flex;gap:6px;flex-wrap:wrap;margin-top:16px}
.tick{font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px}
.tick-1{background:rgba(59,130,246,.15);color:#60A5FA}
.tick-2{background:rgba(16,185,129,.15);color:#34D399}
.tick-3{background:rgba(124,58,237,.15);color:#A78BFA}

/* WHY */
.why-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:24px;margin-top:48px}
.why-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:32px}
.why-icon{font-size:28px;margin-bottom:16px}
.why-card h3{font-size:16px;font-weight:700;margin-bottom:8px}
.why-card p{font-size:14px;color:var(--muted);line-height:1.7}

/* HOLDINGS */
.holdings-table{margin-top:40px;background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.holdings-table table{width:100%;border-collapse:collapse}
.holdings-table th{background:#0d0d1a;padding:12px 20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);text-align:left;border-bottom:1px solid var(--border)}
.holdings-table td{padding:14px 20px;font-size:14px;border-bottom:1px solid rgba(31,41,55,.5)}
.holdings-table tr:last-child td{border-bottom:none}
.holdings-table tr:hover td{background:rgba(124,58,237,.05)}
.pct-bar{display:inline-block;height:4px;border-radius:2px;background:var(--purple);opacity:.7;vertical-align:middle;margin-left:8px}
.tier-badge{display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;border-radius:12px}
.t-anchor{background:rgba(124,58,237,.15);color:#A78BFA}
.t-growth{background:rgba(16,185,129,.15);color:#34D399}
.t-spec{background:rgba(245,158,11,.15);color:#FCD34D}

/* ALPHA */
.alpha-box{background:linear-gradient(135deg,rgba(124,58,237,.12),rgba(79,70,229,.08));border:1px solid rgba(124,58,237,.3);border-radius:16px;padding:48px;margin-top:48px;text-align:center}
.alpha-box h3{font-size:24px;font-weight:800;margin-bottom:12px}
.alpha-box p{color:var(--muted);max-width:600px;margin:0 auto 28px;font-size:15px;line-height:1.7}
.alpha-features{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.af{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);padding:8px 18px;border-radius:20px;font-size:13px;font-weight:600}

/* DISCLAIMER */
.disclaimer{background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:12px;padding:24px 32px;margin-top:48px}
.disclaimer p{font-size:12px;color:var(--muted);line-height:1.8}

/* FOOTER */
footer{border-top:1px solid var(--border);padding:40px;text-align:center;color:var(--muted);font-size:13px}
footer strong{color:#fff}

/* RESPONSIVE */
@media(max-width:768px){
  .stats-bar{grid-template-columns:repeat(2,1fr)}
  .pillars{grid-template-columns:1fr}
  .why-grid{grid-template-columns:1fr}
  nav{padding:0 20px}
  section{padding:60px 20px}
  .chart-section{padding:0 20px 60px}
}
</style></head><body>

<nav>
  <div class="nav-logo">AMERICAN <span>FRONTIER</span> ETF</div>
  <a href="/dashboard" class="nav-cta">Investor Portal →</a>
</nav>

<!-- HERO -->
<div class="hero">
  <div>
    <div class="hero-tag">AI-Managed · Launched May 26, 2026</div>
    <h1>The Next American<br><span>Frontier ETF</span></h1>
    <p class="hero-sub">A 10-stock thematic portfolio built around three structural megatrends — powered by an AI agent that actively manages risk and generates alpha.</p>
    <div class="hero-btns">
      <a href="#backtest" class="btn-primary">See the Performance</a>
      <a href="/dashboard" class="btn-secondary">Live Portfolio →</a>
    </div>
  </div>
</div>

<!-- STATS BAR -->
<div class="stats-bar">
  <div class="stat">
    <div class="stat-val green">+43.3%</div>
    <div class="stat-label">Backtest Return</div>
    <div class="stat-sub">Jan 1 – May 26, 2026</div>
  </div>
  <div class="stat">
    <div class="stat-val green">+26.1%</div>
    <div class="stat-label">Alpha vs Nasdaq</div>
    <div class="stat-sub">Outperformed QQQ by 26pts</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#A78BFA">10</div>
    <div class="stat-label">Conviction Holdings</div>
    <div class="stat-sub">3 structural pillars</div>
  </div>
  <div class="stat">
    <div class="stat-val" style="color:#60A5FA">AI</div>
    <div class="stat-label">Alpha Management</div>
    <div class="stat-sub">Autonomous agent layer</div>
  </div>
</div>

<!-- BACKTEST CHART -->
<div class="chart-section" id="backtest" style="padding-top:96px">
  <div style="max-width:1200px;margin:0 auto 32px">
    <div class="section-tag">Performance</div>
    <div class="section-title">$10,000 invested on January 1, 2026</div>
    <p class="section-sub">Backtested performance of the American Frontier ETF at risk-tier weights versus the Nasdaq 100 (QQQ). Past performance is hypothetical and does not guarantee future results.</p>
  </div>
  <div class="chart-card">
    <div class="chart-meta">
      <div>
        <div class="chart-title">Growth of $10,000
          <small>Jan 2026 – May 2026 · Hypothetical backtest · Risk-tier weighted</small>
        </div>
      </div>
      <div class="chart-legend">
        <div class="leg"><div class="leg-dot" style="background:#7C3AED;height:3px;width:24px"></div>American Frontier ETF: <strong style="color:#A78BFA;margin-left:4px">${{"{:,.0f}".format(bt.etf_final)}} (+{{bt.etf_return}}%)</strong></div>
        <div class="leg"><div class="leg-dot" style="background:#4B5563;height:2px;width:24px;border-top:2px dashed #4B5563"></div>QQQ (Nasdaq): <strong style="color:#9CA3AF;margin-left:4px">${{"{:,.0f}".format(bt.qqq_final)}} (+{{bt.qqq_return}}%)</strong></div>
      </div>
    </div>
    <canvas id="btChart" height="60"></canvas>
  </div>
</div>
<script>
var bt={{ bt_json }};
new Chart(document.getElementById('btChart'),{
  type:'line',
  data:{labels:bt.dates,datasets:[
    {label:'American Frontier ETF',data:bt.etf,borderColor:'#7C3AED',backgroundColor:'rgba(124,58,237,.1)',borderWidth:2.5,pointRadius:0,tension:0.4,fill:true},
    {label:'QQQ (Nasdaq 100)',data:bt.qqq,borderColor:'#4B5563',backgroundColor:'transparent',borderWidth:1.5,pointRadius:0,tension:0.4,fill:false,borderDash:[6,3]},
  ]},
  options:{responsive:true,interaction:{mode:'index',intersect:false},
    plugins:{legend:{display:false},tooltip:{
      backgroundColor:'#1F2937',borderColor:'#374151',borderWidth:1,
      callbacks:{label:c=>' '+c.dataset.label+': $'+c.parsed.y.toLocaleString('en',{maximumFractionDigits:0})}}},
    scales:{
      x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#6B7280',font:{size:11},maxTicksLimit:8}},
      y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#6B7280',font:{size:11},callback:v=>'$'+v.toLocaleString('en',{maximumFractionDigits:0})}}
    }}
});
</script>

<!-- PILLARS -->
<section>
  <div class="section-tag">Investment Thesis</div>
  <div class="section-title">Three structural megatrends.<br>One concentrated portfolio.</div>
  <p class="section-sub">The American Frontier ETF is built on the conviction that three structural forces will define the next decade of wealth creation — and most investors are underexposed to all three.</p>
  <div class="pillars">
    <div class="pillar-card p1">
      <div class="pillar-num">Pillar 1 · 40% Allocation</div>
      <h3>Sovereign Infrastructure</h3>
      <p>5G/6G networks, direct-to-cell satellites, titanium manufacturing, and rare earth supply chains being rebuilt outside China's control. The backbone nations need to survive the next era of competition.</p>
      <div class="pillar-tickers">
        {% for t in ['NOK','ASTS','IPX','USAR'] %}<span class="tick tick-1">{{t}}</span>{% endfor %}
      </div>
    </div>
    <div class="pillar-card p2">
      <div class="pillar-num">Pillar 2 · 30% Allocation</div>
      <h3>The New High Ground</h3>
      <p>Space launches, lunar infrastructure, quantum computing. The commercial and military contest is moving above the atmosphere. Early movers in this frontier will compound for decades.</p>
      <div class="pillar-tickers">
        {% for t in ['FLY','LUNR','RGTI'] %}<span class="tick tick-2">{{t}}</span>{% endfor %}
      </div>
    </div>
    <div class="pillar-card p3">
      <div class="pillar-num">Pillar 3 · 30% Allocation</div>
      <h3>Intelligent Physical World</h3>
      <p>Enterprise AI workflows, organ transport logistics, LiDAR and physical AI systems. Intelligence is leaving the screen and embedding itself in the real world — in hospitals, factories, and infrastructure.</p>
      <div class="pillar-tickers">
        {% for t in ['NOW','TMDX','OUST'] %}<span class="tick tick-3">{{t}}</span>{% endfor %}
      </div>
    </div>
  </div>
</section>

<!-- HOLDINGS -->
<section style="padding-top:0">
  <div class="section-tag">Portfolio</div>
  <div class="section-title">10 high-conviction holdings</div>
  <p class="section-sub">Risk-tier weighted allocation: ANCHOR names (revenue, momentum) carry more weight. GROWTH names offer asymmetric upside. SPECULATIVE names are sized for maximum return with limited capital at risk.</p>
  <div class="holdings-table">
    <table>
      <thead><tr><th>#</th><th>Ticker</th><th>Company</th><th>Pillar</th><th>Tier</th><th>Weight</th></tr></thead>
      <tbody>
        {% for h in holdings %}
        <tr>
          <td style="color:#6B7280">{{loop.index}}</td>
          <td><strong>{{h.ticker}}</strong></td>
          <td style="color:#9CA3AF">{{h.name}}</td>
          <td><span class="tick tick-{{h.p}}">P{{h.p}}</span></td>
          <td><span class="tier-badge t-{{h.tier_class}}">{{h.tier}}</span></td>
          <td>{{h.weight}}% <div class="pct-bar" style="width:{{h.weight*3}}px"></div></td>
        </tr>{% endfor %}
      </tbody>
    </table>
  </div>
</section>

<!-- WHY -->
<section style="padding-top:0">
  <div class="section-tag">Why This ETF</div>
  <div class="section-title">Built different from day one.</div>
  <div class="why-grid">
    <div class="why-card">
      <div class="why-icon">🤖</div>
      <h3>AI-Managed Alpha Layer</h3>
      <p>20% of capital is actively managed by an AI agent — no human emotions, no hesitation. The agent analyzes options chains, identifies catalysts, and executes spread strategies autonomously to beat the base portfolio.</p>
    </div>
    <div class="why-card">
      <div class="why-icon">🎯</div>
      <h3>Thesis-Driven, Not Momentum</h3>
      <p>No stop losses on base positions. Each holding is a 2-5 year structural thesis. The ETF holds through volatility because the underlying trends — sovereign infrastructure, space, physical AI — are decade-long forces.</p>
    </div>
    <div class="why-card">
      <div class="why-icon">📊</div>
      <h3>Monthly Research Updates</h3>
      <p>The portfolio rebalances monthly based on updated Amatya Research conviction reports. If a name's thesis weakens or a stronger opportunity emerges, the agent recommends substitution to the portfolio manager for approval.</p>
    </div>
    <div class="why-card">
      <div class="why-icon">🔒</div>
      <h3>Transparent & Secure</h3>
      <p>All positions, transactions, and agent decisions are logged and visible to investors in real time. The AI agent can trade freely but cannot move or transfer funds — security enforced at the API layer, not just policy.</p>
    </div>
  </div>

  <div class="alpha-box">
    <h3>The Alpha Layer — What Makes This Different</h3>
    <p>Most ETFs are passive index trackers. American Frontier is a thematic portfolio with an active AI agent that manages a 20% risk capital layer — deploying options spreads, hedges, and tactical bets tied to specific near-term catalysts while the base portfolio compounds over years.</p>
    <div class="alpha-features">
      <span class="af">Bull call spreads</span>
      <span class="af">Catalyst-driven entries</span>
      <span class="af">Vol arbitrage</span>
      <span class="af">Downside hedging</span>
      <span class="af">Dynamic reweighting</span>
    </div>
  </div>

  <div class="disclaimer">
    <p><strong style="color:#9CA3AF">Important Disclosure:</strong> The American Frontier ETF is a personal investment vehicle managed by GFC LLC. Backtest performance from January 1, 2026 to May 26, 2026 is hypothetical and based on actual historical prices of the underlying securities at risk-tier weights. Past hypothetical performance does not guarantee future results. This is not an SEC-registered fund or investment product. All investing involves risk including the possible loss of principal. The AI agent operates within defined parameters set by the portfolio manager. This material is for informational purposes only and does not constitute investment advice.</p>
  </div>
</section>

<footer>
  <strong>The American Frontier ETF</strong> · GFC LLC · Launched May 26, 2026 · AI-Managed · Account 668 · Schwab<br>
  <span style="margin-top:8px;display:block">Interested in investing? <a href="/dashboard" style="color:#A78BFA;text-decoration:none">Access the Investor Portal →</a></span>
</footer>
</body></html>"""

# ── LOGIN ─────────────────────────────────────────────────────────────────────
LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Investor Portal — American Frontier ETF</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0A0A14;font-family:'Inter',system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#111827;border:1px solid #1F2937;border-radius:20px;padding:52px 44px;text-align:center;width:400px;position:relative;overflow:hidden}
.box::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#7C3AED,transparent)}
.logo{font-size:13px;font-weight:800;letter-spacing:.08em;color:#fff;margin-bottom:4px}
.logo span{color:#7C3AED}
.sub{color:#6B7280;font-size:12px;margin-bottom:40px}
h2{font-size:22px;font-weight:700;color:#F9FAFB;margin-bottom:8px}
p{color:#6B7280;font-size:14px;margin-bottom:32px}
input{width:100%;padding:16px;background:#0d0d1a;border:2px solid #1F2937;border-radius:12px;font-size:28px;text-align:center;letter-spacing:10px;color:#F9FAFB;font-weight:700;outline:none;transition:border .15s;font-family:monospace}
input:focus{border-color:#7C3AED}
button{width:100%;padding:15px;background:#7C3AED;color:#fff;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;margin-top:16px;transition:background .15s;font-family:'Inter',sans-serif}
button:hover{background:#8B5CF6}
.err{color:#EF4444;font-size:13px;margin-top:14px;font-weight:500}
.back{display:block;margin-top:20px;color:#4B5563;font-size:13px;text-decoration:none}
.back:hover{color:#9CA3AF}
</style></head><body>
<div class="box">
  <div class="logo">AMERICAN <span>FRONTIER</span> ETF</div>
  <div class="sub">Investor Portal · GFC LLC</div>
  <h2>Enter Investor PIN</h2>
  <p>Access the live portfolio dashboard</p>
  <form method="POST">
    <input type="password" name="pin" maxlength="6" placeholder="••••" autofocus autocomplete="off">
    {% if error %}<div class="err">Incorrect PIN — please try again</div>{% endif %}
    <button type="submit">Access Portfolio →</button>
  </form>
  <a href="/" class="back">← Back to overview</a>
</div>
</body></html>"""

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Live Portfolio — American Frontier ETF</title>
<meta http-equiv="refresh" content="120">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F8F9FC;color:#1E293B;font-family:'Inter',system-ui,sans-serif;font-size:14px}
.topbar{background:#fff;border-bottom:1px solid #E2E8F0;padding:0 28px;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.logo{font-size:13px;font-weight:800;color:#1E293B;letter-spacing:.04em}
.logo span{color:#7C3AED}
.badge-live{font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0}
.links{display:flex;gap:16px;align-items:center}
.links a{font-size:13px;color:#94A3B8;text-decoration:none}
.links a:hover{color:#475569}
.page{padding:24px 28px}
h2{color:#94A3B8;font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;font-weight:700}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.card{background:#fff;border-radius:10px;padding:18px;border:1px solid #E2E8F0;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.card-accent{border-left:3px solid #7C3AED}
.sl{color:#94A3B8;font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;font-weight:700}
.sv{color:#1E293B;font-size:22px;font-weight:700}.ss{color:#94A3B8;font-size:11px;margin-top:3px}
.pos{color:#16A34A}.neg{color:#DC2626}.muted{color:#94A3B8;font-size:12px}
table{width:100%;border-collapse:collapse}
th{color:#94A3B8;font-size:10px;text-transform:uppercase;text-align:left;padding:9px 14px;border-bottom:2px solid #F1F5F9;letter-spacing:.06em;font-weight:700;background:#F8FAFC}
td{color:#1E293B;font-size:13px;padding:9px 14px;border-bottom:1px solid #F1F5F9}
tr:hover td{background:#F8FAFC}
tr.totals-row td{background:#F1F5F9;font-weight:700;border-top:2px solid #E2E8F0;border-bottom:none}
.chip{display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px}
.filled{background:#F0FDF4;color:#16A34A}.spread{background:#EFF6FF;color:#2563EB}.long{background:#F0FDF4;color:#16A34A}
.section-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
footer{text-align:center;color:#94A3B8;font-size:11px;padding:20px;border-top:1px solid #E2E8F0;background:#fff}
.notice{background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:14px 18px;margin-bottom:20px;font-size:13px;color:#92400E}
</style></head><body>
<div class="topbar">
  <div>
    <div class="logo">AMERICAN <span>FRONTIER</span> ETF &nbsp;·&nbsp; <span style="color:#94A3B8;font-weight:500">Live Portfolio</span></div>
  </div>
  <div class="links">
    <span class="muted">{{ now }} ET</span>
    <span class="badge-live">{{ s.get('status','LIVE') }}</span>
    <a href="/">← Overview</a>
    <a href="/logout">Sign out</a>
  </div>
</div>
<div class="page">
{% set perf = s.get('performance', {}) %}
{% set positions = s.get('positions', []) %}
{% set alpha_pos = s.get('alpha_layer', {}).get('positions', []) %}
{% set txns = s.get('transactions', []) %}

<div class="notice">
  ⚡ <strong>Launched May 26, 2026</strong> — This ETF launched today. Performance will materialize over the 2-5 year investment horizon. The backtest on the overview page shows the hypothetical return of these holdings from Jan 1 2026.
</div>

<div class="grid4">
  <div class="card card-accent" style="margin:0"><div class="sl">Total NAV</div>
    <div class="sv">${{ '%.2f'|format(s.get('nav',0)) }}</div>
    <div class="ss">Inception ${{ '%.2f'|format(perf.get('inception_nav',2000)) }}</div></div>
  <div class="card" style="margin:0"><div class="sl">Return vs Inception</div>
    <div class="sv {{ 'pos' if perf.get('total_return_pct',0)>=0 else 'neg' }}">{{ '%+.2f'|format(perf.get('total_return_pct',0)) }}%</div>
    <div class="ss">30-day review Jun 25, 2026</div></div>
  <div class="card" style="margin:0"><div class="sl">Unrealized P&L</div>
    <div class="sv {{ 'pos' if perf.get('unrealized_pnl',0)>=0 else 'neg' }}">${{ '%+.2f'|format(perf.get('unrealized_pnl',0)) }}</div>
    <div class="ss">Realized: ${{ '%+.2f'|format(perf.get('realized_pnl',0)) }}</div></div>
  <div class="card" style="margin:0"><div class="sl">Cash Available</div>
    <div class="sv">${{ '%.2f'|format(s.get('cash',0)) }}</div>
    <div class="ss">Alpha capital: ${{ '%.0f'|format(s.get('initial_capital',2000)*0.20) }}</div></div>
</div>

{% set hist = s.get('performance_history', []) %}
<div class="card">
  <div class="section-hdr"><h2>Live Performance vs Benchmarks</h2><span class="muted">Agent ETF · Base ETF · QQQ · Inception May 26</span></div>
  {% if hist|length < 2 %}<div style="text-align:center;padding:28px;color:#94A3B8;font-size:13px">Chart builds from Day 2 — first data point recorded</div>{% endif %}
  <canvas id="liveChart" height="75"></canvas>
</div>
<script>
var hist={{ hist|tojson }};if(hist&&hist.length>0){
  new Chart(document.getElementById('liveChart'),{type:'line',
    data:{labels:hist.map(h=>h.date),datasets:[
      {label:'Agent ETF',data:hist.map(h=>h.agent_return_pct||0),borderColor:'#7C3AED',borderWidth:2.5,pointRadius:3,tension:0.3,fill:false},
      {label:'Base ETF',data:hist.map(h=>h.base_return_pct||0),borderColor:'#2563EB',borderWidth:2,pointRadius:3,tension:0.3,fill:false,borderDash:[5,3]},
      {label:'QQQ',data:hist.map(h=>h.qqq_return_pct||0),borderColor:'#94A3B8',borderWidth:1.5,pointRadius:2,tension:0.3,fill:false,borderDash:[3,3]},
    ]},
    options:{responsive:true,interaction:{mode:'index',intersect:false},
      plugins:{legend:{position:'top',labels:{font:{size:11},usePointStyle:true}}},
      scales:{x:{grid:{color:'#F1F5F9'},ticks:{font:{size:11},color:'#94A3B8'}},
        y:{grid:{color:'#F1F5F9'},ticks:{font:{size:11},color:'#94A3B8',callback:v=>(v>=0?'+':'')+v.toFixed(1)+'%'}}}}});}
</script>

{% if positions %}
<div class="card">
  <div class="section-hdr"><h2>Base ETF — Live Positions</h2><span class="muted">Amatya Research AR-ETF-2026-0525 · No stop loss · 2-5yr thesis</span></div>
  {% set ns=namespace(tc=0,tv=0,tp=0) %}
  <table><thead><tr><th>Ticker</th><th>Qty</th><th>Avg Cost</th><th>Current</th><th>Mkt Value</th><th>P&L</th><th>P&L %</th></tr></thead><tbody>
  {% for p in positions %}
  {% set cost=p.avg_cost*p.quantity %}{% set mval=p.get('market_value',p.current_price*p.quantity) %}
  {% set ns.tc=ns.tc+cost %}{% set ns.tv=ns.tv+mval %}{% set ns.tp=ns.tp+p.get('unrealized_pnl',0) %}
  <tr><td><strong>{{p.ticker}}</strong></td><td>{{p.quantity}}</td>
  <td>${{'%.2f'|format(p.avg_cost)}}</td><td>${{'%.2f'|format(p.current_price)}}</td>
  <td>${{'%.2f'|format(mval)}}</td>
  <td class="{{'pos' if p.get('unrealized_pnl',0)>=0 else 'neg'}}">${{'%+.2f'|format(p.get('unrealized_pnl',0))}}</td>
  <td class="{{'pos' if p.get('pnl_pct',0)>=0 else 'neg'}}">{{'%+.1f'|format(p.get('pnl_pct',0))}}%</td></tr>
  {% endfor %}
  <tr class="totals-row"><td>TOTAL</td><td>—</td><td>${{'%.2f'|format(ns.tc)}}</td><td>—</td>
  <td>${{'%.2f'|format(ns.tv)}}</td>
  <td class="{{'pos' if ns.tp>=0 else 'neg'}}">${{'%+.2f'|format(ns.tp)}}</td>
  <td class="{{'pos' if ns.tp>=0 else 'neg'}}">{{'%+.2f'|format((ns.tp/ns.tc*100) if ns.tc else 0)}}%</td></tr>
  </tbody></table>
</div>{% endif %}

{% if alpha_pos %}
<div class="card">
  <div class="section-hdr"><h2>Alpha Layer — Agent Active</h2><span class="muted">Spreads · Options · Hedges · Agent discretion</span></div>
  <table><thead><tr><th>Ticker</th><th>Structure</th><th>Cost</th><th>MTM</th><th>P&L</th><th>P&L %</th><th>Max Profit</th><th>Exit Rule</th><th>Status</th></tr></thead><tbody>
  {% for p in alpha_pos %}
  {% set mtm=p.get('mtm',p.get('cost',0)) %}{% set pnl=p.get('pnl',0) %}{% set pct=p.get('pnl_pct',0) %}
  <tr><td><strong>{{p.ticker}}</strong></td>
  <td><span class="chip spread">{{p.get('asset_type','SPREAD')}}</span></td>
  <td>${{'%.2f'|format(p.get('cost',0))}}</td>
  <td>${{'%.2f'|format(mtm)}}</td>
  <td class="{{'pos' if pnl>=0 else 'neg'}}">${{'%+.2f'|format(pnl)}}</td>
  <td class="{{'pos' if pct>=0 else 'neg'}}">{{'%+.1f'|format(pct)}}%</td>
  <td>${{'%.2f'|format(p.get('max_profit',0)) if p.get('max_profit') else 'Uncapped'}}</td>
  <td class="muted">{{p.get('stop_type','Thesis only')}}</td>
  <td><span class="chip filled">FILLED</span></td></tr>
  {% endfor %}</tbody></table>
</div>{% endif %}

{% if txns %}
<div class="card">
  <h2>Transaction Log — Confirmed Fills</h2>
  {% set ns2=namespace(total=0) %}
  <table><thead><tr><th>Date</th><th>Ticker</th><th>Action</th><th>Qty</th><th>Fill Price</th><th>Total</th><th>Status</th></tr></thead><tbody>
  {% for t in txns|reverse %}{% set ns2.total=ns2.total+t.get('total',0) %}
  <tr><td class="muted">{{t.get('date','')}}</td><td><strong>{{t.get('ticker','')}}</strong></td>
  <td><span class="chip long">{{t.get('action','BUY')}}</span></td>
  <td>{{t.get('quantity','')}}</td><td>${{'%.4f'|format(t.get('price',0))}}</td>
  <td>${{'%.2f'|format(t.get('total',0))}}</td>
  <td><span class="chip filled">FILLED</span></td></tr>{% endfor %}
  <tr class="totals-row"><td colspan="5" style="text-align:right;padding-right:14px">TOTAL DEPLOYED</td>
  <td>${{'%.2f'|format(ns2.total)}}</td><td>—</td></tr></tbody></table>
</div>{% endif %}
</div>
<footer>American Frontier ETF · GFC LLC · Agent-Managed · Investor view · Auto-refresh 2 min · {{now}}</footer>
</body></html>"""

# ── ROUTES ────────────────────────────────────────────────────────────────────
HOLDINGS = [
    {'ticker':'NOK',  'name':'Nokia Corporation',     'p':1,'tier':'GROWTH',      'tier_class':'growth', 'weight':8},
    {'ticker':'ASTS', 'name':'AST SpaceMobile',       'p':1,'tier':'GROWTH',      'tier_class':'growth', 'weight':8},
    {'ticker':'IPX',  'name':'IperionX (Titanium)',   'p':1,'tier':'GROWTH',      'tier_class':'growth', 'weight':8},
    {'ticker':'USAR', 'name':'USA Rare Earth',        'p':1,'tier':'GROWTH',      'tier_class':'growth', 'weight':8},
    {'ticker':'FLY',  'name':'Firefly Aerospace',     'p':2,'tier':'ANCHOR',      'tier_class':'anchor', 'weight':12.5},
    {'ticker':'LUNR', 'name':'Intuitive Machines',    'p':2,'tier':'ANCHOR',      'tier_class':'anchor', 'weight':12.5},
    {'ticker':'RGTI', 'name':'Rigetti Computing',     'p':2,'tier':'SPECULATIVE', 'tier_class':'spec',   'weight':10},
    {'ticker':'NOW',  'name':'ServiceNow',            'p':3,'tier':'ANCHOR',      'tier_class':'anchor', 'weight':12.5},
    {'ticker':'TMDX', 'name':'TransMedics Group',     'p':3,'tier':'ANCHOR',      'tier_class':'anchor', 'weight':12.5},
    {'ticker':'OUST', 'name':'Ouster (LiDAR)',        'p':3,'tier':'GROWTH',      'tier_class':'growth', 'weight':8},
]

import json as _json

class _BT:
    def __init__(self, d):
        self.__dict__.update(d)

@app.route('/')
def landing():
    bt = _BT(BACKTEST)
    return render_template_string(LANDING, bt=bt, bt_json=_json.dumps(BACKTEST), holdings=HOLDINGS)

@app.route('/login', methods=['GET','POST'])
def login():
    error = False
    if request.method == 'POST':
        if request.form.get('pin','') == PIN:
            session['auth'] = True
            return redirect('/dashboard')
        error = True
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if not session.get('auth'):
        return redirect('/login')
    s = get_etf_data()
    if not s:
        return '<h2 style="font-family:sans-serif;padding:40px;color:#fff;background:#0a0a14;min-height:100vh">Data feed temporarily unavailable — try again shortly.</h2>', 503
    from datetime import datetime
    return render_template_string(DASHBOARD_HTML, s=s, now=datetime.now().strftime('%Y-%m-%d %H:%M'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
