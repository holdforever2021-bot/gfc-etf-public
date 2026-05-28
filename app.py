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
AGENT_API_KEY = os.environ.get('AGENT_API_KEY', '')  # for agent-to-agent calls
_jobs = {}  # in-memory job store for async PDF analysis
_latest_brief = {'analysis': None, 'timestamp': None, 'date': None}  # latest agent thinking

def _agent_auth():
    """Accept either PIN session or X-API-Key header (for Amatya agent calls)."""
    if session.get('auth'):
        return True
    key = request.headers.get('X-API-Key', '')
    return bool(AGENT_API_KEY and key == AGENT_API_KEY)

BACKTEST = {"dates": ["2024-01-02", "2024-01-11", "2024-01-23", "2024-02-01", "2024-02-12", "2024-02-22", "2024-03-04", "2024-03-13", "2024-03-22", "2024-04-03", "2024-04-12", "2024-04-23", "2024-05-02", "2024-05-13", "2024-05-22", "2024-06-03", "2024-06-12", "2024-06-24", "2024-07-03", "2024-07-15", "2024-07-24", "2024-08-02", "2024-08-13", "2024-08-22", "2024-09-03", "2024-09-12", "2024-09-23", "2024-10-02", "2024-10-11", "2024-10-22", "2024-10-31", "2024-11-11", "2024-11-20", "2024-12-02", "2024-12-11", "2024-12-20", "2025-01-02", "2025-01-14", "2025-01-24", "2025-02-04", "2025-02-13", "2025-02-25", "2025-03-06", "2025-03-17", "2025-03-26", "2025-04-04", "2025-04-15", "2025-04-25", "2025-05-06", "2025-05-15", "2025-05-27", "2025-06-05", "2025-06-16", "2025-06-26", "2025-07-08", "2025-07-17", "2025-07-28", "2025-08-06", "2025-08-15", "2025-08-26", "2025-09-05", "2025-09-16", "2025-09-25", "2025-10-06", "2025-10-15", "2025-10-24", "2025-11-04", "2025-11-13", "2025-11-24", "2025-12-04", "2025-12-15", "2025-12-24", "2026-01-06", "2026-01-15", "2026-01-27", "2026-02-05", "2026-02-17", "2026-02-26", "2026-03-09", "2026-03-18", "2026-03-27", "2026-04-08", "2026-04-17", "2026-04-28", "2026-05-07", "2026-05-18", "2026-05-26"], "etf": [10010.0, 10320.38, 10551.0, 11518.36, 12992.04, 15319.86, 13394.17, 13585.85, 13645.61, 13665.77, 12811.57, 13018.67, 13813.68, 14959.04, 14645.52, 14898.03, 14571.85, 14059.9, 14896.65, 16461.5, 15786.53, 16136.94, 16718.22, 20113.86, 19069.58, 18808.16, 20795.79, 19797.61, 20257.02, 21655.82, 19475.74, 23314.28, 23119.72, 27142.22, 29857.11, 33206.87, 49312.93, 34544.89, 43356.6, 43392.79, 41199.14, 33979.62, 30801.45, 30959.9, 28786.14, 23272.96, 27042.4, 29310.21, 30292.13, 35322.95, 39015.53, 36153.18, 40382.22, 41404.78, 41742.28, 50027.26, 47865.38, 46108.45, 45182.63, 43666.35, 41463.07, 47204.99, 62402.17, 79216.27, 100773.44, 76955.26, 68646.85, 54114.47, 54148.31, 63386.3, 54395.92, 60663.12, 67027.7, 67880.13, 68583.16, 51742.73, 51795.03, 57024.2, 56922.73, 52929.21, 46799.04, 56022.45, 63440.55, 55898.89, 57413.98, 64593.31, 82937.23], "qqq": [10000.0, 10167.91, 10518.89, 10479.15, 10813.48, 10881.29, 11029.09, 10935.45, 11102.37, 10995.92, 10900.66, 10572.35, 10617.86, 11020.29, 11334.43, 11270.26, 11793.07, 11807.08, 12232.57, 12359.86, 11543.51, 11179.06, 11523.58, 11829.25, 11504.4, 11788.64, 12050.18, 12022.99, 12307.63, 12372.49, 12070.39, 12818.54, 12552.36, 12854.71, 13219.68, 12938.78, 12749.01, 12620.32, 13233.75, 13104.82, 13390.41, 12826.21, 12198.55, 12062.87, 12121.15, 10576.91, 11460.76, 11825.36, 12046.82, 12993.73, 13043.03, 13132.37, 13370.09, 13683.98, 13837.3, 14074.29, 14233.13, 14212.59, 14463.61, 14345.11, 14431.54, 14810.33, 14886.44, 15242.09, 15104.39, 15477.6, 15531.53, 15259.4, 15178.13, 15624.08, 15313.07, 15669.07, 15656.26, 15615.07, 15849.89, 14993.52, 15100.75, 15300.15, 15262.98, 14940.02, 14146.17, 15240.24, 16315.44, 16534.21, 17474.38, 17749.47, 18363.01], "etf_return": 729.4, "qqq_return": 83.6, "etf_final": 82937.23, "qqq_final": 18363.01, "start_date": "Jan 2024"}

def get_etf_data():
    try:
        r = req_lib.get(DATA_URL, timeout=8)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

# ── LANDING PAGE ───────────────────────────────────────────────────────────────
LANDING = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>American Frontier ETF — AI-Managed Thematic Fund</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--p:#6D28D9;--pl:#8B5CF6;--dk:#0F0720;--cd:#1A0F35;--cd2:#150C2E;--br:#2D1B69;--tx:#F9FAFB;--mt:#A78BFA;--gr:#10B981}
html{scroll-behavior:smooth}
body{background:var(--dk);color:var(--tx);font-family:'Inter',system-ui,sans-serif;font-size:15px;line-height:1.6;overflow-x:hidden}
nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(15,7,32,.97);backdrop-filter:blur(16px);border-bottom:1px solid var(--br);padding:0 5%;height:60px;display:flex;align-items:center;justify-content:space-between}
.nav-logo{font-size:13px;font-weight:800;letter-spacing:.08em}
.nav-logo span{color:var(--p)}
.nav-links{display:flex;gap:24px;align-items:center}
.nav-links a{color:var(--mt);font-size:13px;font-weight:500;text-decoration:none;transition:color .15s}
.nav-links a:hover{color:#fff}
.nav-cta{background:var(--p);color:#fff!important;padding:8px 20px;border-radius:8px;font-weight:700!important}
.nav-cta:hover{background:var(--pl)!important}

.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 5% 60px;background:radial-gradient(ellipse 120% 80% at 50% -5%,rgba(109,40,217,.55) 0%,rgba(124,58,237,.2) 40%,transparent 70%)}
.hero-tag{display:inline-block;background:rgba(124,58,237,.12);color:var(--pl);font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;padding:5px 16px;border-radius:20px;border:1px solid rgba(124,58,237,.25);margin-bottom:24px}
.hero h1{font-size:clamp(36px,6vw,76px);font-weight:900;line-height:1.06;letter-spacing:-.03em;margin-bottom:18px}
.hero h1 em{font-style:normal;background:linear-gradient(135deg,#c4b5fd,#7C3AED);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-size:clamp(15px,2vw,18px);color:var(--mt);max-width:560px;margin:0 auto 20px;line-height:1.75}
.hero-scroll{margin-top:48px;color:var(--mt);font-size:12px;letter-spacing:.08em;text-transform:uppercase}
.hero-scroll a{color:var(--mt);text-decoration:none}

.stats-band{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--br);border-bottom:1px solid var(--br);background:linear-gradient(135deg,#1A0F35,#0F0720)}
.stat{background:var(--cd);padding:28px 20px;text-align:center;border-right:1px solid var(--br)}
.stat:last-child{border-right:none}
.sv{font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:-.02em;line-height:1}
.sv.g{color:var(--gr)}.sv.p{color:#a78bfa}
.sl{font-size:11px;color:var(--mt);text-transform:uppercase;letter-spacing:.08em;margin-top:6px;font-weight:600}
.ss{font-size:11px;color:#4B5563;margin-top:3px}

.section{padding:80px 5%;max-width:1280px;margin:0 auto}
.stag{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--pl);margin-bottom:10px}
.stitle{font-size:clamp(26px,3.5vw,42px);font-weight:800;letter-spacing:-.02em;line-height:1.15;margin-bottom:14px}
.ssub{font-size:15px;color:var(--mt);max-width:580px;line-height:1.75}

/* CHART */
.chart-wrap{background:var(--cd);border:1px solid var(--br);border-radius:16px;padding:32px;margin-top:40px;position:relative}
.chart-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#8B5CF6,#C4B5FD,#8B5CF6,transparent);border-radius:16px 16px 0 0}
.chart-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px;gap:16px;flex-wrap:wrap}
.chart-title-main{font-size:18px;font-weight:700}
.chart-sub-text{font-size:12px;color:var(--mt);margin-top:3px}
.legend{display:flex;gap:20px;flex-wrap:wrap}
.leg{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600}
.leg-line{width:20px;height:3px;border-radius:2px}

/* SIDE-BY-SIDE CHARTS */
.two-charts{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:40px}
.mini-chart-card{background:var(--cd);border:1px solid var(--br);border-radius:14px;padding:24px}
.mini-chart-title{font-size:13px;font-weight:700;margin-bottom:4px}
.mini-chart-sub{font-size:11px;color:var(--mt);margin-bottom:16px}

/* PILLARS */
.pillars{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:44px}
.pillar{background:var(--cd);border:1px solid var(--br);border-radius:14px;padding:28px;position:relative;overflow:hidden;transition:transform .2s,border-color .2s}
.pillar:hover{transform:translateY(-3px);border-color:rgba(124,58,237,.4)}
.pillar-accent{position:absolute;bottom:0;left:0;right:0;height:2px}
.pa1{background:linear-gradient(90deg,#2563EB,#60A5FA)}
.pa2{background:linear-gradient(90deg,#059669,#34D399)}
.pa3{background:linear-gradient(90deg,var(--p),#a78bfa)}
.pn{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px}
.pn1{color:#60A5FA}.pn2{color:#34D399}.pn3{color:#a78bfa}
.pillar h3{font-size:16px;font-weight:700;margin-bottom:8px}
.pillar p{font-size:13px;color:var(--mt);line-height:1.65}
.tickers{display:flex;gap:6px;flex-wrap:wrap;margin-top:14px}
.tk{font-size:10px;font-weight:700;padding:3px 8px;border-radius:6px}
.tk1{background:rgba(37,99,235,.15);color:#60A5FA}
.tk2{background:rgba(5,150,105,.15);color:#34D399}
.tk3{background:rgba(124,58,237,.15);color:#a78bfa}

/* TABLE */
.htable{background:var(--cd);border:1px solid var(--br);border-radius:14px;overflow:hidden;margin-top:36px}
.htable table{width:100%;border-collapse:collapse}
.htable th{background:#0d0d1a;padding:11px 18px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--mt);text-align:left;border-bottom:1px solid var(--br)}
.htable td{padding:12px 18px;font-size:13px;border-bottom:1px solid rgba(31,41,55,.5)}
.htable tr:last-child td{border-bottom:none}
.htable tr:hover td{background:rgba(124,58,237,.04)}
.tier{display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;border-radius:12px}
.t-a{background:rgba(124,58,237,.15);color:#a78bfa}
.t-g{background:rgba(16,185,129,.15);color:#34D399}
.t-s{background:rgba(245,158,11,.15);color:#FCD34D}

/* WHY */
.why-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-top:40px}
.why{background:var(--cd);border:1px solid var(--br);border-radius:14px;padding:28px;transition:border-color .2s}
.why:hover{border-color:rgba(124,58,237,.35)}
.why-icon{font-size:26px;margin-bottom:14px}
.why h3{font-size:15px;font-weight:700;margin-bottom:8px}
.why p{font-size:13px;color:var(--mt);line-height:1.7}

/* ALPHA BOX */
.alpha-box{background:linear-gradient(135deg,rgba(124,58,237,.1),rgba(79,70,229,.07));border:1px solid rgba(124,58,237,.25);border-radius:16px;padding:44px;margin-top:40px;text-align:center}
.alpha-box h3{font-size:22px;font-weight:800;margin-bottom:10px}
.alpha-box p{color:var(--mt);max-width:580px;margin:0 auto 24px;font-size:14px;line-height:1.75}
.af-tags{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.aft{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);padding:7px 16px;border-radius:20px;font-size:12px;font-weight:600}

/* DISCLAIMER */
.disc{margin-top:40px;padding:0 4px}
.disc p{font-size:13px;color:#6B7280;line-height:1.9}

footer{border-top:1px solid var(--br);padding:36px 5%;text-align:center;color:var(--mt);font-size:12px}
footer strong{color:#fff}
footer a{color:#a78bfa;text-decoration:none}

/* MOBILE */
.desktop-only{display:inline}
@media(max-width:768px){
  .desktop-only{display:none!important}
  nav{padding:0 20px}
  .nav-links a:not(.nav-cta){display:none}
  .hero{padding:80px 20px 40px}
  .stats-band{grid-template-columns:repeat(2,1fr)}
  .stat{padding:20px 14px}
  .sv{font-size:28px}
  .section{padding:56px 20px}
  .pillars{grid-template-columns:1fr}
  .two-charts{grid-template-columns:1fr}
  .why-grid{grid-template-columns:1fr}
  .chart-wrap{padding:20px}
  .chart-head{flex-direction:column}
  .legend{gap:12px}
  .htable th,.htable td{padding:10px 12px;font-size:12px}
  .alpha-box{padding:28px 20px}
}
@media(max-width:640px){
  .htable th:nth-child(1),.htable td:nth-child(1),
  .htable th:nth-child(3),.htable td:nth-child(3){display:none}
  .htable th,.htable td{padding:10px 10px;font-size:12px}
  .pillars{grid-template-columns:1fr}
  .two-charts{grid-template-columns:1fr}
}
@media(max-width:480px){
  .stats-band{grid-template-columns:1fr 1fr}
  .hero h1{font-size:36px}
}
</style></head><body>

<nav>
  <div class="nav-logo">AMERICAN <span>FRONTIER</span> ETF</div>
  <div class="nav-links">
    <a href="#performance">Performance</a>
    <a href="#strategy">Strategy</a>
    <a href="#portfolio">Portfolio</a>
    <a href="/dashboard" class="nav-cta">Investor Portal →</a>
  </div>
</nav>

<div class="hero">
  <div>
    <div class="hero-tag">AI-Managed · Launched May 26, 2026 · GFC LLC</div>
    <h1>The Next American<br><em>Frontier ETF</em></h1>
    <p class="hero-sub">A concentrated 10-stock thematic portfolio across three structural megatrends. AI-managed alpha layer. Transparent. Built for the long term.</p>
    <div class="hero-scroll"><a href="#performance">↓ Explore the strategy</a></div>
  </div>
</div>

<div class="stats-band">
  <div class="stat"><div class="sv g">+729%</div><div class="sl">Backtest Return</div><div class="ss">Jan 2024 – May 2026</div></div>
  <div class="stat"><div class="sv g">+645%</div><div class="sl">Alpha vs Nasdaq</div><div class="ss">vs QQQ +84% same period</div></div>
  <div class="stat"><div class="sv p">3</div><div class="sl">Structural Pillars</div><div class="ss">Sovereign · Space · Physical AI</div></div>
  <div class="stat"><div class="sv p">AI</div><div class="sl">Alpha Layer</div><div class="ss">Autonomous options management</div></div>
</div>

<!-- PERFORMANCE -->
<div class="section" id="performance">
  <div class="stag">Performance</div>
  <div class="stitle">$10,000 invested January 2024.<br>See where it is today.</div>
  <p class="ssub">Backtested performance of the American Frontier ETF portfolio at risk-tier weights vs. Nasdaq 100 (QQQ). Holdings adjusted for FLY IPO in Aug 2025.</p>

  <div class="chart-wrap">
    <div class="chart-head">
      <div>
        <div class="chart-title-main">Growth of $10,000 · Jan 2024 – May 2026</div>
        <div class="chart-sub-text">Hypothetical backtest · Risk-tier weighted · FLY weight redistributed pre-IPO</div>
      </div>
      <div class="legend">
        <div class="leg"><div class="leg-line" style="background:#7C3AED"></div>Frontier ETF: <strong style="color:#a78bfa;margin-left:4px">${{ "%.0f"|format(bt.etf_final) }} (+{{bt.etf_return}}%)</strong></div>
        <div class="leg"><div class="leg-line" style="background:#374151;border-top:2px dashed #374151;height:0"></div>QQQ: <strong style="color:#6B7280;margin-left:4px">${{ "%.0f"|format(bt.qqq_final) }} (+{{bt.qqq_return}}%)</strong></div>
      </div>
    </div>
    <div style="height:320px;position:relative"><canvas id="btChart"></canvas></div>
  </div>

  <div class="two-charts">
    <div class="mini-chart-card">
      <div class="mini-chart-title">Portfolio Allocation by Pillar</div>
      <div class="mini-chart-sub">Target weighting across 3 structural themes</div>
      <div style="height:220px;position:relative"><canvas id="pillarChart"></canvas></div>
    </div>
    <div class="mini-chart-card">
      <div class="mini-chart-title">Allocation by Risk Tier</div>
      <div class="mini-chart-sub">ANCHOR · GROWTH · SPECULATIVE</div>
      <div style="height:220px;position:relative"><canvas id="tierChart"></canvas></div>
    </div>
  </div>
</div>

<script>
window.addEventListener('DOMContentLoaded', function() {
  var bt = {{ bt_json | safe }};

  // Main backtest chart
  new Chart(document.getElementById('btChart'), {
    type: 'line',
    data: {
      labels: bt.dates,
      datasets: [
        {label:'American Frontier ETF',data:bt.etf,borderColor:'#7C3AED',backgroundColor:'rgba(124,58,237,.12)',borderWidth:2.5,pointRadius:0,tension:0.4,fill:true},
        {label:'QQQ (Nasdaq 100)',data:bt.qqq,borderColor:'#374151',backgroundColor:'transparent',borderWidth:1.5,pointRadius:0,tension:0.4,fill:false,borderDash:[6,3]},
      ]
    },
    options: {
      responsive:true,maintainAspectRatio:false,
      interaction:{mode:'index',intersect:false},
      plugins:{
        legend:{display:false},
        tooltip:{backgroundColor:'#1F2937',borderColor:'#374151',borderWidth:1,padding:12,
          callbacks:{label:c=>' '+c.dataset.label+': $'+c.parsed.y.toLocaleString('en',{maximumFractionDigits:0})}}
      },
      scales:{
        x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#4B5563',font:{size:11},maxTicksLimit:10}},
        y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#4B5563',font:{size:11},callback:v=>'$'+v.toLocaleString('en',{maximumFractionDigits:0})}}
      }
    }
  });

  // Pillar pie chart
  new Chart(document.getElementById('pillarChart'), {
    type: 'doughnut',
    data: {
      labels: ['Pillar 1 · Sovereign', 'Pillar 2 · Space', 'Pillar 3 · Physical AI'],
      datasets: [{data:[40,30,30],backgroundColor:['#2563EB','#059669','#7C3AED'],borderColor:'#111827',borderWidth:3,hoverOffset:8}]
    },
    options: {
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'bottom',labels:{color:'#9CA3AF',font:{size:11},padding:16,usePointStyle:true}}}
    }
  });

  // Tier bar chart
  new Chart(document.getElementById('tierChart'), {
    type: 'bar',
    data: {
      labels: ['ANCHOR','GROWTH','SPECULATIVE'],
      datasets: [{
        data:[50,40,10],
        backgroundColor:['rgba(124,58,237,.7)','rgba(16,185,129,.7)','rgba(245,158,11,.7)'],
        borderColor:['#7C3AED','#10B981','#F59E0B'],
        borderWidth:2, borderRadius:6
      }]
    },
    options: {
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},
        tooltip:{callbacks:{label:c=>c.parsed.y+'% of portfolio'}}},
      scales:{
        x:{grid:{display:false},ticks:{color:'#9CA3AF',font:{size:11}}},
        y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#4B5563',font:{size:11},callback:v=>v+'%'},max:60}
      }
    }
  });
});
</script>

<!-- STRATEGY / PILLARS -->
<div class="section" id="strategy">
  <div class="stag">Investment Thesis</div>
  <div class="stitle">Three forces shaping the next decade.</div>
  <p class="ssub">The American Frontier ETF is built on three structural megatrends that most retail investors are dramatically underexposed to.</p>
  <div class="pillars">
    <div class="pillar">
      <div class="pn pn1">Pillar 1 · 40% Allocation</div>
      <h3>Sovereign Infrastructure</h3>
      <p>5G/6G networks, direct-to-cell satellites, titanium manufacturing, and rare earth supply chains rebuilt outside China's control. The backbone nations need to build for the next era of competition.</p>
      <div class="tickers">{% for t in ['NOK','ASTS','IPX','USAR'] %}<span class="tk tk1">{{t}}</span>{% endfor %}</div>
      <div class="pillar-accent pa1"></div>
    </div>
    <div class="pillar">
      <div class="pn pn2">Pillar 2 · 30% Allocation</div>
      <h3>The New High Ground</h3>
      <p>Space launches, lunar infrastructure, quantum computing. The commercial and military contest is moving above the atmosphere. Early movers will compound for decades.</p>
      <div class="tickers">{% for t in ['FLY','LUNR','RGTI'] %}<span class="tk tk2">{{t}}</span>{% endfor %}</div>
      <div class="pillar-accent pa2"></div>
    </div>
    <div class="pillar">
      <div class="pn pn3">Pillar 3 · 30% Allocation</div>
      <h3>Intelligent Physical World</h3>
      <p>Enterprise AI, organ transport logistics, LiDAR and physical AI systems. Intelligence is leaving the screen and embedding itself into hospitals, factories, and infrastructure.</p>
      <div class="tickers">{% for t in ['NOW','TMDX','OUST'] %}<span class="tk tk3">{{t}}</span>{% endfor %}</div>
      <div class="pillar-accent pa3"></div>
    </div>
  </div>
</div>

<!-- PORTFOLIO TABLE -->
<div class="section" id="portfolio" style="padding-top:0">
  <div class="stag">Holdings</div>
  <div class="stitle">10 high-conviction positions.</div>
  <p class="ssub">Risk-tier weighted: ANCHOR names carry more weight. GROWTH offers asymmetric upside. SPECULATIVE is sized for max return with limited capital at risk.</p>
  <div class="htable" style="overflow-x:auto;-webkit-overflow-scrolling:touch">
    <table>
      <thead><tr><th>#</th><th>Ticker</th><th>Company</th><th>Pillar</th><th>Tier</th><th>Weight</th></tr></thead>
      <tbody>
        {% for h in holdings %}
        <tr>
          <td style="color:#374151">{{loop.index}}</td>
          <td><strong>{{h.ticker}}</strong></td>
          <td style="color:#6B7280">{{h.name}}</td>
          <td><span class="tk tk{{h.p}}">P{{h.p}}</span></td>
          <td><span class="tier t-{{h.tier_class}}">{{h.tier}}</span></td>
          <td>{{h.weight}}%</td>
        </tr>{% endfor %}
      </tbody>
    </table>
  </div>

  <div class="why-grid" style="margin-top:60px">
    <div class="why"><div class="why-icon">🤖</div><h3>AI-Managed Alpha Layer</h3><p>20% of capital is actively managed by an AI agent — no emotions, no hesitation. The agent analyzes options chains, identifies catalysts, and executes spread strategies to beat the base portfolio.</p></div>
    <div class="why"><div class="why-icon">🎯</div><h3>Thesis-Driven, Not Stop-Loss Driven</h3><p>No stop losses on base positions. Each holding is a 2-5 year structural thesis. The ETF holds through volatility because the underlying trends are decade-long structural forces, not momentum plays.</p></div>
    <div class="why"><div class="why-icon">📊</div><h3>Monthly Research Updates</h3><p>The portfolio rebalances monthly based on updated Amatya Research conviction reports. If a name's thesis weakens, the agent recommends substitution to the portfolio manager for approval.</p></div>
    <div class="why"><div class="why-icon">🔒</div><h3>Transparent & Secure</h3><p>All positions, transactions, and agent decisions are logged and visible in real time. The AI agent can trade freely but cannot transfer funds — enforced at the API layer.</p></div>
  </div>

  <div class="alpha-box">
    <h3>The Alpha Layer</h3>
    <p>Most ETFs are passive. American Frontier has an active AI agent managing a 20% risk layer — deploying options spreads, hedges, and tactical bets tied to near-term catalysts while the base portfolio compounds over years.</p>
    <div class="af-tags">
      <span class="aft">Bull call spreads</span>
      <span class="aft">Catalyst-driven entries</span>
      <span class="aft">Vol arbitrage</span>
      <span class="aft">Downside hedging</span>
      <span class="aft">Agent discretion</span>
    </div>
  </div>

  <div class="disc">
    <p><strong style="color:#6B7280">Important Disclosure:</strong> The American Frontier ETF is a personal investment vehicle managed by GFC LLC. Backtest performance (Jan 2024–May 2026) is hypothetical, based on actual historical prices at risk-tier weights, with FLY weight redistributed to other holdings prior to its August 2025 IPO. Past hypothetical performance does not guarantee future results. This is not an SEC-registered fund. All investing involves risk including possible loss of principal. This material is for informational purposes only and does not constitute investment advice.</p>
  </div>
</div>

<footer>
  <strong>The American Frontier ETF</strong> · GFC LLC · AI-Managed · Launched May 26, 2026<br>
  <span style="margin-top:8px;display:block;color:#4B5563">Investor access: <a href="/dashboard">Investor Portal →</a></span>
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
<title>Investor Portal — American Frontier ETF</title>
<meta http-equiv="refresh" content="120">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--p:#7C3AED;--pl:#8B5CF6;--dk:#0A0A14;--cd:#111827;--cd2:#0d1117;--br:#1F2937;--tx:#F9FAFB;--mt:#9CA3AF;--gr:#10B981;--rd:#EF4444}
body{background:var(--dk);color:var(--tx);font-family:'Inter',system-ui,sans-serif;font-size:14px;line-height:1.6;min-height:100vh}
nav{background:rgba(15,7,32,.97);backdrop-filter:blur(16px);border-bottom:1px solid var(--br);padding:0 5%;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.nav-logo{font-size:13px;font-weight:800;letter-spacing:.08em;color:#fff}
.nav-logo span{color:var(--p)}
.nav-right{display:flex;gap:16px;align-items:center}
.nav-right a{color:var(--mt);font-size:12px;text-decoration:none;transition:color .15s}
.nav-right a:hover{color:#fff}
.badge{font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;background:rgba(16,185,129,.12);color:var(--gr);border:1px solid rgba(16,185,129,.25)}

.page{padding:28px 5%}

/* STAT CARDS */
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.grid5{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px}
.scard{background:var(--cd);border:1px solid var(--br);border-radius:12px;padding:20px 22px;transition:border-color .2s}
.scard:first-child{border-left:3px solid var(--p)}
.scard:hover{border-color:rgba(124,58,237,.35)}
.sl{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--mt);font-weight:700;margin-bottom:6px}
.sv{font-size:26px;font-weight:800;letter-spacing:-.02em;line-height:1}
.ss{font-size:11px;color:#4B5563;margin-top:4px}
.pos{color:var(--gr)}.neg{color:var(--rd)}

/* SECTION CARDS */
.card{background:var(--cd);border:1px solid var(--br);border-radius:14px;padding:24px;margin-bottom:16px;position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,.4),transparent)}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px}
.card-title{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--mt);font-weight:700}
.card-sub{font-size:11px;color:#374151}

/* CHART */
.chart-container{height:280px;position:relative;margin-top:8px}

/* TABLES */
table{width:100%;border-collapse:collapse}
th{background:var(--cd2);padding:10px 16px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#4B5563;text-align:left;border-bottom:1px solid var(--br)}
td{padding:11px 16px;font-size:13px;border-bottom:1px solid rgba(31,41,55,.6);color:var(--tx)}
tr:hover td{background:rgba(124,58,237,.05)}
tr.totals td{background:#0d1117;font-weight:700;border-top:2px solid var(--br);border-bottom:none;color:var(--tx)}

/* CHIPS */
.chip{display:inline-block;font-size:10px;font-weight:700;padding:2px 9px;border-radius:20px}
.chip-green{background:rgba(16,185,129,.12);color:var(--gr);border:1px solid rgba(16,185,129,.2)}
.chip-blue{background:rgba(37,99,235,.12);color:#60A5FA;border:1px solid rgba(37,99,235,.2)}
.chip-purple{background:rgba(124,58,237,.12);color:#a78bfa;border:1px solid rgba(124,58,237,.2)}
.chip-amber{background:rgba(245,158,11,.12);color:#FCD34D;border:1px solid rgba(245,158,11,.2)}

/* NOTICE */
.notice{background:rgba(124,58,237,.08);border:1px solid rgba(124,58,237,.2);border-radius:8px;padding:10px 16px;margin-bottom:20px;font-size:12px;color:#a78bfa;text-align:center;font-weight:600;letter-spacing:.04em}

/* MINI STATS ROW */
.mini-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.mstat{background:var(--cd2);border:1px solid var(--br);border-radius:10px;padding:14px 16px;text-align:center}
.mstat-val{font-size:20px;font-weight:800;letter-spacing:-.01em}
.mstat-label{font-size:10px;color:var(--mt);text-transform:uppercase;letter-spacing:.06em;margin-top:3px;font-weight:600}

footer{border-top:1px solid var(--br);padding:20px 5%;text-align:center;color:#374151;font-size:11px;background:var(--cd2);margin-top:20px}
footer a{color:#a78bfa;text-decoration:none}
/* Brief toggle JS */
.brief-card{background:rgba(13,7,27,.8);border:1px solid rgba(124,58,237,.25);border-radius:14px;padding:18px 20px;margin-bottom:20px}
.brief-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px}
.brief-title{font-size:13px;font-weight:700;color:#E2E8F0}
.brief-ts{font-size:10px;color:#4B5563;margin-top:2px}
.brief-upload-btn{font-size:11px;font-weight:600;color:#a78bfa;text-decoration:none;background:rgba(124,58,237,.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(124,58,237,.2);white-space:nowrap}
.brief-upload-btn:hover{background:rgba(124,58,237,.2)}
.brief-sentiment{font-size:10px;font-weight:800;padding:3px 10px;border-radius:20px;letter-spacing:.08em;text-transform:uppercase}
.sent-bull{background:rgba(16,185,129,.12);color:#34D399;border:1px solid rgba(16,185,129,.2)}
.sent-caut{background:rgba(245,158,11,.12);color:#FCD34D;border:1px solid rgba(245,158,11,.2)}
.sent-neut{background:rgba(148,163,184,.1);color:#94A3B8;border:1px solid rgba(148,163,184,.15)}
.brief-thesis{font-size:12px;color:#94A3B8;margin-bottom:14px;line-height:1.5;padding:10px 12px;background:rgba(255,255,255,.03);border-radius:8px;border-left:2px solid rgba(124,58,237,.4)}
.brief-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.brief-section{background:rgba(255,255,255,.03);border-radius:10px;padding:12px 14px}
.brief-section-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#4B5563;margin-bottom:8px}
.brief-item{display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;font-size:12px;line-height:1.4}
.brief-item:last-child{margin-bottom:0}
.brief-ticker{font-weight:800;color:#E2E8F0;min-width:40px}
.brief-action{font-size:10px;font-weight:700;padding:1px 7px;border-radius:10px;white-space:nowrap;align-self:flex-start;margin-top:1px}
.act-buy{background:rgba(16,185,129,.12);color:#34D399}
.act-sell{background:rgba(239,68,68,.12);color:#F87171}
.act-hold{background:rgba(148,163,184,.1);color:#94A3B8}
.brief-note{color:#64748B;font-size:12px}
.brief-action-item{font-size:12px;color:#94A3B8;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);line-height:1.4}
.brief-action-item:last-child{border-bottom:none}
.brief-alpha{font-size:11px;color:#a78bfa;margin-top:10px;padding:8px 12px;background:rgba(124,58,237,.07);border-radius:8px}
.brief-empty{text-align:center;font-size:12px;color:#374151;padding:12px;margin-bottom:20px}
.brief-empty a{color:#a78bfa;text-decoration:none}
@media(max-width:640px){.brief-grid{grid-template-columns:1fr}}

/* MOBILE */
@media(max-width:640px){
  table{min-width:500px}
  .table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:0 0 14px 14px}
  th,td{padding:9px 10px;font-size:11px}
  .grid4{grid-template-columns:repeat(2,1fr)}
  /* Hide less essential columns on positions table */
  table.pos-table th:nth-child(3),table.pos-table td:nth-child(3),
  table.pos-table th:nth-child(5),table.pos-table td:nth-child(5){display:none}
  /* Hide on alpha table */
  table.alpha-table th:nth-child(7),table.alpha-table td:nth-child(7),
  table.alpha-table th:nth-child(8),table.alpha-table td:nth-child(8){display:none}
  /* Hide on txn table */
  table.txn-table th:nth-child(4),table.txn-table td:nth-child(4),
  table.txn-table th:nth-child(5),table.txn-table td:nth-child(5){display:none}
}
@media(max-width:768px){
  .grid4{grid-template-columns:repeat(2,1fr)}
  .mini-stats{grid-template-columns:repeat(2,1fr)}
  .page{padding:20px}
  nav{padding:0 20px}
  th,td{padding:9px 12px;font-size:12px}
}
@media(max-width:480px){
  .grid4{grid-template-columns:1fr 1fr}
  .sv{font-size:22px}
}
</style></head><body>

<nav>
  <div class="nav-logo">AMERICAN <span>FRONTIER</span> ETF</div>
  <div class="nav-right">
    <span class="badge">{{ s.get('status','LIVE') }}</span>
    <a href="/chat-page">💬 Chat</a>
    <a href="/upload">📄 Upload Report</a>
    <a href="/">Overview</a>
    <a href="/logout" style="color:var(--rd)!important">Sign out</a>
  </div>
</nav>

<div class="page">
{% set perf = s.get('performance', {}) %}
{% set positions = s.get('positions', []) %}
{% set alpha_pos = s.get('alpha_layer', {}).get('positions', []) %}
{% set txns = s.get('transactions', []) %}
{% set hist = s.get('performance_history', []) %}

{# ── DAILY BRIEF SECTION ── #}
{% if brief and brief.analysis %}
{%- set bd = brief.parsed %}
<div class="brief-card" id="briefCard">
  <div class="brief-header">
    <div style="display:flex;align-items:center;gap:12px">
      <div>
        <span class="brief-sentiment {{ 'sent-bull' if bd and bd.sentiment=='BULLISH' else 'sent-caut' if bd and bd.sentiment=='CAUTIOUS' else 'sent-neut' }}">
          {{ bd.sentiment if bd else '—' }}
        </span>
      </div>
      <div>
        <div class="brief-title">Agent Daily Brief</div>
        <div class="brief-ts">Amatya Research · {{ brief.date }} · {{ brief.timestamp }} ET</div>
      </div>
    </div>
    <a href="/upload" class="brief-upload-btn">+ New Brief</a>
  </div>
  {% if bd %}
  {% if bd.sentiment_reason %}
  <div class="brief-thesis">{{ bd.sentiment_reason }}</div>
  {% endif %}
  <div class="brief-grid">
    {% if bd.top_opportunities %}
    <div class="brief-section">
      <div class="brief-section-title">🎯 Top Opportunities</div>
      {% for opp in bd.top_opportunities %}
      <div class="brief-item">
        <span class="brief-ticker">{{ opp.ticker }}</span>
        <span class="brief-action act-buy">{{ opp.action }}</span>
        <span class="brief-note">{{ opp.reason }}{% if opp.level %} · <strong>{{ opp.level }}</strong>{% endif %}</span>
      </div>
      {% endfor %}
    </div>
    {% endif %}
    {% if bd.key_risks %}
    <div class="brief-section">
      <div class="brief-section-title">⚠️ Key Risks</div>
      {% for risk in bd.key_risks %}
      <div class="brief-item">
        <span class="brief-ticker">{{ risk.ticker }}</span>
        <span class="brief-note">{{ risk.risk }}</span>
      </div>
      {% endfor %}
    </div>
    {% endif %}
  </div>
  {% if bd.action_items %}
  <div class="brief-section" style="margin-top:12px">
    <div class="brief-section-title">⚡ Action Items</div>
    {% for item in bd.action_items %}
    <div class="brief-action-item">{{ loop.index }}. {{ item }}</div>
    {% endfor %}
  </div>
  {% endif %}
  {% if bd.alpha_watch %}
  <div class="brief-alpha">🔬 Alpha Watch: {{ bd.alpha_watch }}</div>
  {% endif %}
  {% else %}
  <div style="font-size:12px;color:#4B5563;margin-top:8px">{{ brief.analysis[:200] }}...</div>
  {% endif %}
</div>
{% else %}
<div class="brief-empty">
  No daily brief — <a href="/upload">upload the Amatya brief</a> to see the agent's thinking.
</div>
{% endif %}

{% set hist = s.get('performance_history', []) %}
{% set last = hist[-1] if hist else {} %}
<!-- NAV STATS -->
<div class="grid5">
  <div class="scard">
    <div class="sl">Total NAV</div>
    <div class="sv">${{ '%.2f'|format(last.get('agent_etf_nav', s.get('nav',0))) }}</div>
    <div class="ss">Inception ${{ '%.2f'|format(perf.get('inception_nav',2000)) }} · May 26 2026</div>
  </div>
  <div class="scard">
    <div class="sl">Total Return</div>
    {% set live_ret = ((last.get('agent_etf_nav',2000)-2000)/2000*100) if last.get('agent_etf_nav') else perf.get('total_return_pct',0) %}
    <div class="sv {{ 'pos' if live_ret>=0 else 'neg' }}">{{ '%+.2f'|format(live_ret) }}%</div>
    <div class="ss">30-day review Jun 25, 2026</div>
  </div>
  <div class="scard">
    <div class="sl">Unrealized P&L</div>
    <div class="sv {{ 'pos' if perf.get('unrealized_pnl',0)>=0 else 'neg' }}">${{ '%+.2f'|format(perf.get('unrealized_pnl',0)) }}</div>
    <div class="ss">Realized: ${{ '%+.2f'|format(perf.get('realized_pnl',0)) }}</div>
  </div>
  <div class="scard">
    <div class="sl">Cash</div>
    <div class="sv">${{ '%.2f'|format(s.get('cash',0)) }}</div>
    <div class="ss">Alpha budget: ${{ '%.0f'|format(s.get('initial_capital',2000)*0.20) }}</div>
  </div>
</div>

<!-- LIVE PERFORMANCE CHART — dollar value, same style as backtest -->
{% set last = hist[-1] if hist else {} %}
<div class="card" style="position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#8B5CF6,#C4B5FD,#8B5CF6,transparent)"></div>
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;flex-wrap:wrap;gap:12px">
    <div>
      <div style="font-size:16px;font-weight:700;color:#E2E8F0">Growth of $2,000 · May 26, 2026</div>
      <div style="font-size:11px;color:#4B5563;margin-top:3px">Live portfolio · Account 668 · Updated {{ now }} ET</div>
    </div>
    <div style="display:flex;gap:16px;flex-wrap:wrap">
      <div style="display:flex;align-items:center;gap:7px;font-size:12px;font-weight:600">
        <div style="width:22px;height:3px;background:#A78BFA;border-radius:2px"></div>
        Agent ETF: <strong style="color:#A78BFA">${{ '%.2f'|format(last.get('agent_etf_nav',2000)) }} ({{ '%+.2f'|format(last.get('agent_return_pct',0)) }}%)</strong>
      </div>
      <div style="display:flex;align-items:center;gap:7px;font-size:12px;font-weight:600">
        <div style="width:22px;border-top:2px dashed #38BDF8"></div>
        Base ETF: <strong style="color:#38BDF8">${{ '%.2f'|format(last.get('base_etf_nav',2000)) }} ({{ '%+.2f'|format(last.get('base_return_pct',0)) }}%)</strong>
      </div>
      <div style="display:flex;align-items:center;gap:7px;font-size:12px;font-weight:600">
        <div style="width:22px;border-top:2px dashed #6B7280"></div>
        QQQ: <strong style="color:#6B7280">${{ '%.2f'|format(last.get('qqq_nav',2000)) }} ({{ '%+.2f'|format(last.get('qqq_return_pct',0)) }}%)</strong>
      </div>
    </div>
  </div>
  {% if hist|length < 2 %}
  <div style="text-align:center;padding:40px;color:#374151;font-size:13px">Chart builds from Day 2</div>
  {% endif %}
  <canvas id="liveChart" style="width:100%;height:260px;display:block"></canvas>
</div>

<!-- ALLOCATION CHARTS -->
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px">
  <div class="card">
    <div style="font-size:12px;font-weight:700;color:#E2E8F0;margin-bottom:4px">Portfolio Allocation by Pillar</div>
    <div style="font-size:10px;color:#4B5563;margin-bottom:14px">Actual positions · Account 668</div>
    <canvas id="pillarLive" style="width:100%;height:180px;display:block"></canvas>
  </div>
  <div class="card">
    <div style="font-size:12px;font-weight:700;color:#E2E8F0;margin-bottom:4px">Allocation by Risk Tier</div>
    <div style="font-size:10px;color:#4B5563;margin-bottom:14px">ANCHOR · GROWTH · SPECULATIVE</div>
    <canvas id="tierLive" style="width:100%;height:180px;display:block"></canvas>
  </div>
</div>

<script>
window.addEventListener('DOMContentLoaded',function(){
  var hist = {{ hist | tojson | safe }};

  // Main NAV chart — dollar values, backtest style
  if(hist && hist.length > 0){
    new Chart(document.getElementById('liveChart'),{
      type:'line',
      data:{labels:hist.map(h=>h.date),datasets:[
        {label:'Agent ETF',data:hist.map(h=>h.agent_etf_nav||2000),
         borderColor:'#A78BFA',backgroundColor:'rgba(167,139,250,.12)',borderWidth:2.5,pointRadius:hist.length<5?4:2,tension:0.4,fill:true},
        {label:'Base ETF',data:hist.map(h=>h.base_etf_nav||2000),borderColor:'#38BDF8',backgroundColor:'transparent',borderWidth:1.8,pointRadius:hist.length<5?3:1,tension:0.4,fill:false,borderDash:[5,3]},
        {label:'QQQ ($2K)',data:hist.map(h=>h.qqq_nav||2000),
         borderColor:'#4B5563',backgroundColor:'transparent',borderWidth:1.5,pointRadius:hist.length<5?3:1,tension:0.4,fill:false,borderDash:[6,3]},
      ]},
      options:{
        responsive:false,
        interaction:{mode:'index',intersect:false},
        plugins:{legend:{display:false},
          tooltip:{backgroundColor:'#1F2937',borderColor:'#374151',borderWidth:1,padding:12,
            callbacks:{label:c=>' '+c.dataset.label+': $'+c.parsed.y.toLocaleString('en',{maximumFractionDigits:2})}}},
        scales:{
          x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#4B5563',font:{size:11}}},
          y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#4B5563',font:{size:11},
            callback:v=>'$'+v.toLocaleString('en',{maximumFractionDigits:0})}}
        }
      }
    });
  }

  // Pillar doughnut — actual position values
  var positions = {{ s.get('positions',[]) | tojson | safe }};
  var pillarMap = {NOK:1,ASTS:1,IPX:1,USAR:1,FLY:2,LUNR:2,RGTI:2,NOW:3,TMDX:3,OUST:3};
  var pillarVals = [0,0,0];
  positions.forEach(function(p){
    var pil = pillarMap[p.ticker];
    if(pil) pillarVals[pil-1] += p.market_value || (p.current_price * p.quantity) || 0;
  });
  new Chart(document.getElementById('pillarLive'),{
    type:'doughnut',
    data:{labels:['P1 · Sovereign','P2 · Space','P3 · Physical AI'],
      datasets:[{data:pillarVals.map(v=>Math.round(v)),
        backgroundColor:['#2563EB','#059669','#7C3AED'],borderColor:'#0F172A',borderWidth:3,hoverOffset:6}]},
    options:{responsive:false,plugins:{legend:{position:'bottom',labels:{color:'#9CA3AF',font:{size:11},padding:14,usePointStyle:true}}}}
  });

  // Tier bar — actual values
  var tierMap = {NOW:'anchor',TMDX:'anchor',LUNR:'anchor',FLY:'anchor',ASTS:'growth',USAR:'growth',IPX:'growth',NOK:'growth',OUST:'growth',RGTI:'speculative'};
  var tierVals = {anchor:0,growth:0,speculative:0};
  positions.forEach(function(p){ var t=tierMap[p.ticker]; if(t) tierVals[t]+=(p.market_value||(p.current_price*p.quantity)||0); });
  new Chart(document.getElementById('tierLive'),{
    type:'bar',
    data:{labels:['ANCHOR','GROWTH','SPECULATIVE'],
      datasets:[{data:[Math.round(tierVals.anchor),Math.round(tierVals.growth),Math.round(tierVals.speculative)],
        backgroundColor:['rgba(124,58,237,.7)','rgba(16,185,129,.7)','rgba(245,158,11,.7)'],
        borderColor:['#7C3AED','#10B981','#F59E0B'],borderWidth:2,borderRadius:6}]},
    options:{responsive:false,plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=>'$'+c.parsed.y.toLocaleString('en',{maximumFractionDigits:0})}}},
      scales:{x:{grid:{display:false},ticks:{color:'#9CA3AF',font:{size:11}}},
        y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#4B5563',font:{size:11},callback:v=>'$'+v.toLocaleString('en',{maximumFractionDigits:0})}}}}
  });
});
</script>

<!-- POSITIONS -->
{% if positions %}
<div class="card">
  <div class="card-header">
    <div class="card-title">Base ETF — Live Positions</div>
    <div class="card-sub">Amatya Research · Risk-Tier Weighted · No stop loss · 2-5yr thesis</div>
  </div>
  {% set ns=namespace(tc=0,tv=0,tp=0) %}
  <div class="table-scroll"><table class="pos-table">
    <thead><tr><th>Ticker</th><th>Qty</th><th>Avg Cost</th><th>Current</th><th>Mkt Value</th><th>P&L</th><th>P&L %</th></tr></thead>
    <tbody>
    {% for p in positions %}
    {% set cost=p.avg_cost*p.quantity %}
    {% set mval=p.get('market_value',p.current_price*p.quantity) %}
    {% set ns.tc=ns.tc+cost %}{% set ns.tv=ns.tv+mval %}{% set ns.tp=ns.tp+p.get('unrealized_pnl',0) %}
    <tr>
      <td><span style="display:inline-flex;align-items:center;gap:6px"><span style="width:6px;height:6px;border-radius:50%;background:{% if p.ticker in ('NOK','ASTS','IPX','USAR') %}#2563EB{% elif p.ticker in ('FLY','LUNR','RGTI') %}#059669{% else %}#7C3AED{% endif %};flex-shrink:0"></span><strong>{{p.ticker}}</strong></span></td>
      <td style="color:var(--mt)">{{p.quantity}}</td>
      <td style="color:var(--mt)">${{'%.2f'|format(p.avg_cost)}}</td>
      <td>${{'%.2f'|format(p.current_price)}}</td>
      <td>${{'%.2f'|format(mval)}}</td>
      <td class="{{'pos' if p.get('unrealized_pnl',0)>=0 else 'neg'}}">${{'%+.2f'|format(p.get('unrealized_pnl',0))}}</td>
      <td class="{{'pos' if p.get('pnl_pct',0)>=0 else 'neg'}}">{{'%+.1f'|format(p.get('pnl_pct',0))}}%</td>
    </tr>
    {% endfor %}
    <tr class="totals">
      <td>TOTAL</td><td>—</td><td style="color:var(--mt)">${{'%.2f'|format(ns.tc)}}</td><td>—</td>
      <td>${{'%.2f'|format(ns.tv)}}</td>
      <td class="{{'pos' if ns.tp>=0 else 'neg'}}">${{'%+.2f'|format(ns.tp)}}</td>
      <td class="{{'pos' if ns.tp>=0 else 'neg'}}">{{'%+.2f'|format((ns.tp/ns.tc*100) if ns.tc else 0)}}%</td>
    </tr>
    </tbody>
  </table></div>
</div>
{% endif %}

<!-- ALPHA -->
{% if alpha_pos %}
<div class="card">
  <div class="card-header">
    <div class="card-title">Alpha Layer — Agent Active</div>
    <div class="card-sub">Options · Spreads · Hedges · Full agent discretion</div>
  </div>
  <div class="table-scroll"><table class="alpha-table">
    <thead><tr><th>Ticker</th><th>Qty</th><th>Avg Cost</th><th>Current</th><th>Mkt Value</th><th>P&L</th><th>P&L %</th></tr></thead>
    <tbody>
    {%- set ns_a = namespace(tc=0,tv=0,tp=0) %}
    {% for p in alpha_pos %}
    {%- set mtm=p.get('mtm',p.get('cost',0)) %}{%- set pnl=p.get('pnl',0) %}{%- set pct=p.get('pnl_pct',0) %}
    {%- set ns_a.tc=ns_a.tc+p.get('cost',0) %}{%- set ns_a.tv=ns_a.tv+mtm %}{%- set ns_a.tp=ns_a.tp+pnl %}
    <tr>
      <td><span style="display:inline-flex;align-items:center;gap:6px"><span style="width:6px;height:6px;border-radius:50%;background:{% if p.ticker in ('NOK','ASTS','IPX','USAR') %}#2563EB{% elif p.ticker in ('FLY','LUNR','RGTI') %}#059669{% else %}#7C3AED{% endif %};flex-shrink:0"></span><strong>{{p.ticker}}</strong></span></td>
      <td style="color:var(--mt)">1</td>
      <td style="color:var(--mt)">${{'%.2f'|format(p.get('cost',0))}}</td>
      <td>${{'%.2f'|format(mtm)}}</td>
      <td>${{'%.2f'|format(mtm)}}</td>
      <td class="{{'pos' if pnl>=0 else 'neg'}}">${{'%+.2f'|format(pnl)}}</td>
      <td class="{{'pos' if pct>=0 else 'neg'}}">{{'%+.1f'|format(pct)}}%</td>
    </tr>
    {% endfor %}
    <tr class="totals">
      <td>TOTAL</td><td>—</td>
      <td style="color:var(--mt)">${{'%.2f'|format(ns_a.tc)}}</td><td>—</td>
      <td>${{'%.2f'|format(ns_a.tv)}}</td>
      <td class="{{'pos' if ns_a.tp>=0 else 'neg'}}">${{'%+.2f'|format(ns_a.tp)}}</td>
      <td class="{{'pos' if ns_a.tp>=0 else 'neg'}}">{{'%+.2f'|format((ns_a.tp/ns_a.tc*100) if ns_a.tc else 0)}}%</td>
    </tr>
    </tbody>
  </table></div>
</div>
{% endif %}

<!-- TRANSACTIONS -->
{% if txns %}
<div class="card">
  <div class="card-header">
    <div class="card-title">Transaction Log</div>
    <div class="card-sub">Confirmed Schwab fills · Account 668</div>
  </div>
  {% set ns2=namespace(total=0) %}
  <div class="table-scroll"><table class="txn-table">
    <thead><tr><th>Date</th><th>Ticker</th><th>Action</th><th>Qty</th><th>Fill Price</th><th>Total</th><th>Status</th></tr></thead>
    <tbody>
    {% for t in txns|reverse %}
    {% set ns2.total=ns2.total+t.get('total',0) %}
    <tr>
      <td style="color:var(--mt)">{{t.get('date','')}}</td>
      <td><strong>{{t.get('ticker','')}}</strong></td>
      <td><span class="chip chip-green">{{t.get('action','BUY')}}</span></td>
      <td style="color:var(--mt)">{{t.get('quantity','')}}</td>
      <td style="color:var(--mt)">${{'%.4f'|format(t.get('price',0))}}</td>
      <td>${{'%.2f'|format(t.get('total',0))}}</td>
      <td><span class="chip chip-green">FILLED</span></td>
    </tr>
    {% endfor %}
    <tr class="totals">
      <td colspan="5" style="text-align:right;padding-right:16px;color:var(--mt)">TOTAL DEPLOYED</td>
      <td>${{'%.2f'|format(ns2.total)}}</td><td>—</td>
    </tr>
    </tbody>
  </table>
</div>
{% endif %}

</div>
<footer>
  American Frontier ETF · GFC LLC · AI-Managed · Account 668 · Auto-refresh 2 min · {{now}}<br>
  <a href="/">← Back to overview</a>
</footer>
<script>
function toggleBrief() {
  var b = document.getElementById('briefBody');
  var e = b.nextElementSibling;
  if(b.classList.contains('expanded')) {
    b.classList.remove('expanded');
    e.textContent = 'Show more ↓';
  } else {
    b.classList.add('expanded');
    e.textContent = 'Show less ↑';
  }
}
</script>
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
    # Seed brief from DO state if Render memory lost it (deploy/restart)
    if not _latest_brief.get('analysis') and s.get('daily_brief',{}).get('analysis'):
        _latest_brief.update(s['daily_brief'])
    return render_template_string(DASHBOARD_HTML, s=s, brief=_latest_brief,
                                   now=datetime.now().strftime('%Y-%m-%d %H:%M'))

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# ── UPLOAD ROUTE — Amatya Research report upload → triggers rebalance analysis ──
UPLOAD_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Upload Report — American Frontier ETF</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0F0720;color:#F9FAFB;font-family:'Inter',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.box{background:#1A0F35;border:1px solid #2D1B69;border-radius:20px;padding:48px 40px;width:100%;max-width:520px;text-align:center}
.logo{font-size:12px;font-weight:800;letter-spacing:.08em;color:#fff;margin-bottom:4px}
.logo span{color:#8B5CF6}
.sub{color:#6B7280;font-size:11px;margin-bottom:36px}
h2{font-size:20px;font-weight:700;margin-bottom:8px}
p{color:#A78BFA;font-size:13px;margin-bottom:28px;line-height:1.6}
.drop{border:2px dashed #2D1B69;border-radius:12px;padding:36px 20px;margin-bottom:20px;cursor:pointer;transition:border-color .2s}
.drop:hover{border-color:#8B5CF6}
.drop-icon{font-size:36px;margin-bottom:12px}
.drop p{color:#6B7280;font-size:13px;margin:0}
input[type=file]{display:none}
button{width:100%;padding:14px;background:#6D28D9;color:#fff;border:none;border-radius:12px;font-size:14px;font-weight:700;cursor:pointer;transition:background .15s;font-family:'Inter',sans-serif}
button:hover{background:#8B5CF6}
.result{background:#0d0b1e;border:1px solid #2D1B69;border-radius:10px;padding:16px;margin-top:20px;font-size:13px;color:#A78BFA;text-align:left;white-space:pre-wrap;display:none;max-height:300px;overflow-y:auto}
.back{display:block;margin-top:20px;color:#4B5563;font-size:12px;text-decoration:none}
.back:hover{color:#A78BFA}
</style></head><body>
<div class="box">
  <div class="logo">AMERICAN <span>FRONTIER</span> ETF</div>
  <div class="sub">Amatya Research Brief</div>
  <h2>Upload Brief</h2>
  <p>Upload the Amatya Research daily brief. The agent will analyze all holdings, signals, and catalysts.</p>
  <form id="uploadForm">
    <div class="drop" onclick="document.getElementById('pdfInput').click()">
      <div class="drop-icon">📄</div>
      <p id="fileName">Click to select Amatya Research PDF</p>
    </div>
    <input type="file" id="pdfInput" accept=".pdf,.txt,.md" onchange="document.getElementById('fileName').textContent=this.files[0].name">
    <button type="submit">Analyze Brief</button>
  </form>
  <div class="result" id="result"></div>
  <a href="/dashboard" class="back">← Back to portfolio</a>
</div>
<script>
document.getElementById('uploadForm').onsubmit = async function(e) {
  e.preventDefault();
  const file = document.getElementById('pdfInput').files[0];
  if(!file){alert('Please select a file');return;}
  const btn = this.querySelector('button');
  btn.textContent = 'Analyzing...'; btn.disabled = true;
  const fd = new FormData(); fd.append('report', file);
  try {
    const r = await fetch('/upload-report', {method:'POST', body:fd});
    let d;
    try { d = await r.json(); } catch(e) { d = {error: 'Server error ('+r.status+'): '+e.message}; }
    const res = document.getElementById('result');
    res.style.display = 'block';
    if(d.status === 'processing' && d.job_id) {
      res.textContent = 'Analyzing brief... (may take 30-60 seconds)';
      const poll = setInterval(async () => {
        const p = await fetch('/brief-status/'+d.job_id);
        const pd = await p.json();
        if(pd.status === 'done') { clearInterval(poll); res.textContent = 'Analysis complete — returning to portfolio...'; setTimeout(()=>{ window.location='/dashboard'; }, 1500); }
        else if(pd.status === 'error') { clearInterval(poll); res.textContent = 'Error: '+pd.analysis; }
      }, 3000);
    } else {
      res.textContent = d.analysis || d.error || JSON.stringify(d,null,2);
    }
  } catch(err) {
    document.getElementById('result').style.display='block';
    document.getElementById('result').textContent='Error: '+err.message;
  }
  btn.textContent = 'Analyze Brief'; btn.disabled = false;
};
</script>
</body></html>"""

# ── CHAT ROUTE — Talk to the ETF agent ────────────────────────────────────────
CHAT_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Chat — American Frontier ETF</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0F0720;color:#F9FAFB;font-family:'Inter',sans-serif;height:100vh;display:flex;flex-direction:column}
.topbar{background:rgba(15,7,32,.97);border-bottom:1px solid #2D1B69;padding:0 20px;height:56px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.logo{font-size:13px;font-weight:800;letter-spacing:.06em}
.logo span{color:#8B5CF6}
.topbar a{color:#6B7280;font-size:12px;text-decoration:none}
.topbar a:hover{color:#A78BFA}
.messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:80%;padding:12px 16px;border-radius:14px;font-size:14px;line-height:1.6}
.msg.user{background:#6D28D9;color:#fff;align-self:flex-end;border-radius:14px 14px 4px 14px}
.msg.agent{background:#1A0F35;color:#E2E8F0;align-self:flex-start;border-radius:14px 14px 14px 4px;border:1px solid #2D1B69}
.msg.agent strong{color:#A78BFA}
.typing{color:#6B7280;font-size:12px;padding:4px 16px;align-self:flex-start}
.input-bar{padding:16px;background:rgba(15,7,32,.97);border-top:1px solid #2D1B69;display:flex;gap:10px;flex-shrink:0}
.input-bar input{flex:1;background:#1A0F35;border:1px solid #2D1B69;border-radius:12px;padding:12px 16px;color:#F9FAFB;font-size:14px;font-family:'Inter',sans-serif;outline:none}
.input-bar input:focus{border-color:#6D28D9}
.input-bar input::placeholder{color:#4B3A7A}
.input-bar button{background:#6D28D9;color:#fff;border:none;border-radius:12px;padding:12px 20px;font-size:14px;font-weight:700;cursor:pointer;font-family:'Inter',sans-serif;transition:background .15s}
.input-bar button:hover{background:#8B5CF6}
.suggestion{display:inline-block;background:rgba(109,40,217,.15);border:1px solid rgba(109,40,217,.3);color:#A78BFA;font-size:12px;padding:6px 12px;border-radius:20px;cursor:pointer;margin:4px;transition:background .15s}
.suggestion:hover{background:rgba(109,40,217,.3)}
</style></head><body>
<div class="topbar">
  <div class="logo">AMERICAN <span>FRONTIER</span> ETF &nbsp;·&nbsp; Agent Chat</div>
  <a href="/dashboard">← Portfolio</a>
</div>
<div class="messages" id="messages">
  <div class="msg agent"><strong>ETF Agent</strong><br>Hi Ankur. I'm monitoring the American Frontier ETF. Ask me anything — positions, alpha layer, ASTS spread, LUNR, rebalancing. What do you need?</div>
  <div style="text-align:center;padding:8px 0">
    <span class="suggestion" onclick="ask('What is the current ETF status?')">ETF status</span>
    <span class="suggestion" onclick="ask('How is the ASTS spread doing?')">ASTS spread</span>
    <span class="suggestion" onclick="ask('Should I be worried about LUNR?')">LUNR concern</span>
    <span class="suggestion" onclick="ask('What is the alpha layer conviction level?')">Alpha conviction</span>
  </div>
</div>
<div class="input-bar">
  <input type="text" id="msg" placeholder="Ask the agent..." onkeydown="if(event.key==='Enter')send()">
  <button onclick="send()">Send</button>
</div>
<script>
const etfData = {{ etf_json | safe }};
function ask(q){document.getElementById('msg').value=q;send();}
async function send(){
  const input=document.getElementById('msg');
  const q=input.value.trim();
  if(!q)return;
  input.value='';
  const msgs=document.getElementById('messages');
  msgs.innerHTML+=`<div class="msg user">${q}</div>`;
  msgs.innerHTML+='<div class="typing" id="typing">Agent is thinking...</div>';
  msgs.scrollTop=msgs.scrollHeight;
  try{
    const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q})});
    const d=await r.json();
    document.getElementById('typing')?.remove();
    msgs.innerHTML+=`<div class="msg agent"><strong>ETF Agent</strong><br>${(d.reply||d.error||'No response').replace(/\\n/g,'<br>')}</div>`;
  }catch(e){
    document.getElementById('typing')?.remove();
    msgs.innerHTML+=`<div class="msg agent">Error: ${e.message}</div>`;
  }
  msgs.scrollTop=msgs.scrollHeight;
}
</script>
</body></html>"""


@app.route('/upload', methods=['GET'])
def upload_page():
    if not session.get('auth'):
        return redirect('/login')
    return render_template_string(UPLOAD_HTML)


@app.route('/upload-report', methods=['POST'])
def upload_report():
    if not _agent_auth():
        return req_lib.jsonify({'error': 'unauthorized'}), 401
    if not ANTHROPIC_KEY:
        return req_lib.jsonify({'error': 'Claude API not configured'}), 500
    from flask import jsonify
    file = request.files.get('report')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    file_bytes = file.read()
    filename = file.filename or ''
    etf_data = get_etf_data()
    positions = etf_data.get('positions', [])
    pos_summary = ', '.join(f"{p['ticker']} ({p.get('pnl_pct',0):+.1f}%)" for p in positions)

    system_prompt = f"""You are the GFC American Frontier ETF analyst. Return ONLY valid JSON, no markdown, no prose.

CURRENT PORTFOLIO: {pos_summary}
NAV: ${etf_data.get('nav', 0):,.2f} | Return: {etf_data.get('performance',{}).get('total_return_pct',0):+.2f}%

Analyze the Amatya brief. Return this exact JSON structure:
{{
  "sentiment": "BULLISH|CAUTIOUS|NEUTRAL",
  "sentiment_reason": "one sentence",
  "top_opportunities": [
    {{"ticker": "NOW", "action": "BUY/ADD", "reason": "one sentence", "level": ""}}
  ],
  "key_risks": [
    {{"ticker": "FLY", "risk": "one sentence"}}
  ],
  "signals": {{
    "NOK": {{"call": "HOLD", "note": "brief"}},
    "ASTS": {{"call": "HOLD", "note": "brief"}}
  }},
  "action_items": ["specific action 1", "specific action 2"],
  "alpha_watch": "one sentence on best alpha setup today"
}}

Max 2-3 items in each array. One sentence per field. No markdown."""

    import base64, threading, uuid as _uuid
    from flask import jsonify as _jfy

    # Build messages
    if filename.lower().endswith('.pdf') or file_bytes[:4] == b'%PDF':
        pdf_b64 = base64.standard_b64encode(file_bytes).decode()
        messages = [{'role': 'user', 'content': [
            {'type': 'document', 'source': {'type': 'base64', 'media_type': 'application/pdf', 'data': pdf_b64}},
            {'type': 'text', 'text': 'Analyze this Amatya Research daily brief per the system instructions.'}
        ]}]
    else:
        messages = [{'role': 'user', 'content': file_bytes.decode('utf-8', errors='ignore')[:8000]}]

    # Async — return job_id immediately, process in background thread
    job_id = _uuid.uuid4().hex[:8]
    _jobs[job_id] = {'status': 'processing', 'analysis': None}

    def _run():
        try:
            r = req_lib.post('https://api.anthropic.com/v1/messages',
                headers={'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
                json={'model': 'claude-sonnet-4-6', 'max_tokens': 1500,
                      'system': system_prompt, 'messages': messages},
                timeout=90)
            analysis = r.json()['content'][0]['text'] if r.status_code == 200 else f'API error: {r.status_code}'
            _jobs[job_id] = {'status': 'done', 'analysis': analysis}
            from datetime import datetime as _dt2
            import re as _re, json as _json
            try:
                m = _re.search(r'\{.*\}', analysis, _re.DOTALL)
                parsed = _json.loads(m.group()) if m else None
            except Exception:
                parsed = None

            brief_obj = {
                'analysis': analysis, 'parsed': parsed,
                'timestamp': _dt2.now().strftime('%Y-%m-%d %H:%M'),
                'date': _dt2.now().strftime('%b %d, %Y')
            }
            _latest_brief.update(brief_obj)

            # Also seed _latest_brief from DO on startup if available
            # Persist: push brief back into DO state so it survives Render deploys
            try:
                do_state = req_lib.get('https://jarvis.ankurjoshi-demo.com/etf-data', timeout=8).json()
                do_state['daily_brief'] = brief_obj
                req_lib.post('https://jarvis.ankurjoshi-demo.com/etf-write',
                    headers={'X-Write-Token': os.environ.get('DO_WRITE_TOKEN','')},
                    json=do_state, timeout=10)
            except Exception:
                pass  # best-effort
        except Exception as e:
            _jobs[job_id] = {'status': 'error', 'analysis': str(e)[:300]}

    threading.Thread(target=_run, daemon=True).start()
    return _jfy({'status': 'processing', 'job_id': job_id})


@app.route('/brief-status/<job_id>')
def brief_status(job_id):
    from flask import jsonify
    job = _jobs.get(job_id, {'status': 'not_found'})
    return jsonify(job)


@app.route('/chat-page')
def chat_page():
    if not session.get('auth'):
        return redirect('/login')
    etf = get_etf_data()
    from flask import jsonify
    import json as _json
    return render_template_string(CHAT_HTML, etf_json=_json.dumps(etf))


@app.route('/chat', methods=['POST'])
def chat():
    if not session.get('auth'):
        from flask import jsonify
        return jsonify({'error': 'unauthorized'}), 401
    from flask import jsonify
    if not ANTHROPIC_KEY:
        return jsonify({'error': 'Claude API not configured'}), 500

    message = (request.json or {}).get('message', '')
    etf = get_etf_data()
    perf = etf.get('performance', {})
    positions = etf.get('positions', [])
    alpha = etf.get('alpha_layer', {}).get('positions', [])

    pos_lines = '\n'.join(f"  {p['ticker']}: {p.get('quantity',0)} shares @ ${p.get('avg_cost',0):.2f}, current ${p.get('current_price',0):.2f}, P&L {p.get('pnl_pct',0):+.1f}%" for p in positions)
    def _alpha_desc(p):
        atype = p.get('asset_type','')
        buy_sym = p.get('buy_symbol','').strip()
        sell_sym = p.get('sell_symbol','').strip()
        if atype == 'SPREAD' and buy_sym and sell_sym:
            return (f"  {p['ticker']} BULL CALL SPREAD — BUY {buy_sym} / SELL {sell_sym} | "
                    f"Structure: {p.get('strike_display','')} | "
                    f"Cost=${p.get('cost',0):.0f} | MaxProfit=${p.get('max_profit',0):.0f} | "
                    f"MTM=${p.get('mtm',0):.0f} | P&L={p.get('pnl_pct',0):+.1f}% | "
                    f"Exit: {p.get('stop_type','Thesis only')} — NOT a naked call")
        return f"  {p['ticker']} {atype} cost=${p.get('cost',0):.0f} MTM=${p.get('mtm',0):.0f} P&L={p.get('pnl_pct',0):+.1f}%"
    alpha_lines = '\n'.join(_alpha_desc(p) for p in alpha)

    system = f"""You are the GFC American Frontier ETF agent — READ ONLY discussion mode.

HARD RULES:
1. You DISCUSS positions. You do NOT recommend buying, selling, or exiting anything.
2. If asked "should I sell X" or "exit the spread" — respond with thesis analysis only. Never say "exit now" or "sell it". That is CEO's call.
3. You flag thesis BREAKS (real events: launch scrubbed, company bankrupt). You do NOT flag price moves as exit signals.
4. You were decommissioned as an execution agent on May 27 2026. You are now a portfolio analyst only.
5. If the CEO has decided something — you support it. You don't re-litigate.

ETF STATUS: NAV=${etf.get('nav',0):,.2f} | Return={perf.get('total_return_pct',0):+.2f}% | Inception May 26 2026 | 30-day review Jun 25

BASE ETF POSITIONS:
{pos_lines}

ALPHA LAYER:
{alpha_lines}

MANDATE: Amatya Research 3-pillar thematic ETF. Base = 2-5yr hold, no stop loss. Alpha = options/spreads, thesis-break exits only. Target 50% CAGR.

You speak directly to Ankur (CEO/CIO). Be sharp, direct, no fluff. Numbers-first. Flag risks. Surface what he didn't ask."""

    try:
        r = req_lib.post('https://api.anthropic.com/v1/messages',
            headers={'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
            json={'model': 'claude-haiku-4-5-20251001', 'max_tokens': 400,
                  'system': system, 'messages': [{'role': 'user', 'content': message}]},
            timeout=20)
        reply = r.json()['content'][0]['text'] if r.status_code == 200 else 'API unavailable'
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
