"""
The American Frontier ETF — Public Dashboard
Read-only view. PIN protected. Hosted on Render.
Data feed: https://jarvis.ankurjoshi-demo.com/etf-data
"""
from flask import Flask, request, redirect, session, render_template_string
import requests, json, os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gfc-etf-2026-frontier')
PIN = os.environ.get('ETF_PIN', '2026')
DATA_URL = 'https://jarvis.ankurjoshi-demo.com/etf-data'

def get_etf_data():
    try:
        r = requests.get(DATA_URL, timeout=8)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

LOGIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>American Frontier ETF</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F8F9FC;font-family:'Inter',system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#fff;border-radius:16px;padding:48px 40px;border:1px solid #E2E8F0;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center;width:360px}
.logo{font-size:13px;font-weight:800;color:#1E293B;letter-spacing:.05em;margin-bottom:4px}
.logo span{color:#7C3AED}
.sub{color:#94A3B8;font-size:12px;margin-bottom:36px}
h2{font-size:20px;font-weight:700;color:#1E293B;margin-bottom:8px}
p{color:#64748B;font-size:13px;margin-bottom:28px}
input{width:100%;padding:14px;border:2px solid #E2E8F0;border-radius:10px;font-size:22px;text-align:center;letter-spacing:8px;color:#1E293B;font-weight:700;outline:none;transition:border .15s}
input:focus{border-color:#7C3AED}
button{width:100%;padding:14px;background:#7C3AED;color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;margin-top:16px;transition:background .15s}
button:hover{background:#6D28D9}
.err{color:#DC2626;font-size:13px;margin-top:12px}
.badge{display:inline-flex;align-items:center;gap:6px;background:#F0FDF4;color:#16A34A;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid #BBF7D0;margin-bottom:32px}
</style></head><body>
<div class="box">
  <div class="logo">AMERICAN <span>FRONTIER</span> ETF</div>
  <div class="sub">Agent-Managed · GFC · Inception May 26 2026</div>
  <span class="badge">&#x1F512; Investor Access</span>
  <h2>Enter PIN</h2>
  <p>This dashboard is protected.<br>Enter your investor PIN to continue.</p>
  <form method="POST">
    <input type="password" name="pin" maxlength="6" placeholder="••••" autofocus>
    {% if error %}<div class="err">Incorrect PIN. Try again.</div>{% endif %}
    <button type="submit">Access Dashboard &rarr;</button>
  </form>
</div>
</body></html>"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        if request.form.get('pin', '') == PIN:
            session['auth'] = True
            return redirect('/')
        error = True
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def index():
    if not session.get('auth'):
        return redirect('/login')
    s = get_etf_data()
    if not s:
        return '<h2 style="font-family:sans-serif;padding:40px">Data feed unavailable — try again shortly.</h2>', 503
    from datetime import datetime
    return render_template_string(DASHBOARD_HTML, s=s, now=datetime.now().strftime('%Y-%m-%d %H:%M'))

# ── Dashboard template (same white theme, read-only) ──────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>American Frontier ETF</title>
<meta http-equiv="refresh" content="120">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F8F9FC;color:#1E293B;font-family:'Inter',system-ui,sans-serif;font-size:14px}
.topbar{background:#fff;border-bottom:1px solid #E2E8F0;padding:16px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.logo{font-size:15px;font-weight:800;color:#1E293B;letter-spacing:.03em}
.logo span{color:#7C3AED}
.tagline{color:#94A3B8;font-size:11px;margin-top:2px}
.badge-live{font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0}
.logout{font-size:11px;color:#94A3B8;text-decoration:none;margin-left:16px}
.logout:hover{color:#DC2626}
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
.p1{background:#EFF6FF;color:#2563EB}.p2{background:#F0FDF4;color:#16A34A}.p3{background:#F5F3FF;color:#7C3AED}
.long{background:#F0FDF4;color:#16A34A}.spread{background:#EFF6FF;color:#2563EB}
.filled{background:#F0FDF4;color:#16A34A}
.section-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
footer{text-align:center;color:#94A3B8;font-size:11px;padding:24px;border-top:1px solid #E2E8F0;margin-top:20px;background:#fff}
</style></head><body>
<div class="topbar">
  <div>
    <div class="logo">AMERICAN <span>FRONTIER</span> ETF</div>
    <div class="tagline">Agent-Managed · GFC · Inception {{ s.get('inception_date','May 26 2026') }} · Read-only view</div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <span class="muted">{{ now }} ET</span>
    <span class="badge-live">{{ s.get('status','LIVE') }}</span>
    <a href="/logout" class="logout">Sign out</a>
  </div>
</div>

<div class="page">
{% set perf = s.get('performance', {}) %}
{% set positions = s.get('positions', []) %}
{% set alpha_pos = s.get('alpha_layer', {}).get('positions', []) %}
{% set txns = s.get('transactions', []) %}

<div class="grid4">
  <div class="card card-accent" style="margin:0"><div class="sl">Total NAV</div>
    <div class="sv">${{ '%.2f'|format(s.get('nav', 0)) }}</div>
    <div class="ss">Inception ${{ '%.2f'|format(perf.get('inception_nav', 2000)) }}</div></div>
  <div class="card" style="margin:0"><div class="sl">Total Return</div>
    <div class="sv {{ 'pos' if perf.get('total_return_pct', 0) >= 0 else 'neg' }}">{{ '%+.2f'|format(perf.get('total_return_pct', 0)) }}%</div>
    <div class="ss">vs $2,000 inception · 30-day review Jun 25</div></div>
  <div class="card" style="margin:0"><div class="sl">Unrealized P&L</div>
    <div class="sv {{ 'pos' if perf.get('unrealized_pnl', 0) >= 0 else 'neg' }}">${{ '%+.2f'|format(perf.get('unrealized_pnl', 0)) }}</div>
    <div class="ss">Realized: ${{ '%+.2f'|format(perf.get('realized_pnl', 0)) }}</div></div>
  <div class="card" style="margin:0"><div class="sl">Cash</div>
    <div class="sv">${{ '%.2f'|format(s.get('cash', 0)) }}</div>
    <div class="ss">Alpha budget: ${{ '%.0f'|format(s.get('initial_capital', 2000) * 0.20) }}</div></div>
</div>

{% set hist = s.get('performance_history', []) %}
<div class="card">
  <div class="section-hdr"><h2>Performance vs Benchmarks</h2>
    <span class="muted">Base ETF (Rupesh) · Agent ETF (+ Alpha) · QQQ</span></div>
  {% if hist|length < 2 %}
  <div style="text-align:center;padding:32px;color:#94A3B8;font-size:13px">Chart builds from Day 2 ({{ hist|length }} data point recorded)</div>
  {% endif %}
  <canvas id="perfChart" height="75"></canvas>
</div>
<script>
(function(){
  var hist={{ hist|tojson }};if(!hist||hist.length===0)return;
  new Chart(document.getElementById('perfChart'),{type:'line',
    data:{labels:hist.map(h=>h.date),datasets:[
      {label:'Agent ETF (+ Alpha)',data:hist.map(h=>h.agent_return_pct||0),borderColor:'#7C3AED',borderWidth:2.5,pointRadius:3,tension:0.3,fill:false},
      {label:'Base ETF / Rupesh',data:hist.map(h=>h.base_return_pct||0),borderColor:'#2563EB',borderWidth:2,pointRadius:3,tension:0.3,fill:false,borderDash:[5,3]},
      {label:'QQQ',data:hist.map(h=>h.qqq_return_pct||0),borderColor:'#94A3B8',borderWidth:1.5,pointRadius:2,tension:0.3,fill:false,borderDash:[3,3]},
    ]},
    options:{responsive:true,interaction:{mode:'index',intersect:false},
      plugins:{legend:{position:'top',labels:{font:{size:11},usePointStyle:true}},
        tooltip:{callbacks:{label:c=>' '+c.dataset.label+': '+(c.parsed.y>=0?'+':'')+c.parsed.y.toFixed(2)+'%'}}},
      scales:{x:{grid:{color:'#F1F5F9'},ticks:{font:{size:11},color:'#94A3B8'}},
        y:{grid:{color:'#F1F5F9'},ticks:{font:{size:11},color:'#94A3B8',callback:v=>(v>=0?'+':'')+v.toFixed(1)+'%'}}}}});
})();
</script>

<div class="card">
  <div class="section-hdr"><h2>Base ETF — Live Positions</h2>
    <span class="muted">Amatya Research AR-ETF-2026-0525 · Risk-Tier Weighted · No stop loss (2-5yr thesis)</span></div>
  {% if positions %}
  {% set ns = namespace(tc=0,tv=0,tp=0) %}
  <table><thead><tr><th>Ticker</th><th>Qty</th><th>Avg Cost</th><th>Current</th><th>Mkt Value</th><th>P&L</th><th>P&L %</th></tr></thead><tbody>
  {% for p in positions %}
  {% set cost = p.avg_cost * p.quantity %}{% set mval = p.get('market_value', p.current_price * p.quantity) %}
  {% set ns.tc = ns.tc + cost %}{% set ns.tv = ns.tv + mval %}{% set ns.tp = ns.tp + p.get('unrealized_pnl',0) %}
  <tr><td><strong>{{ p.ticker }}</strong></td><td>{{ p.quantity }}</td>
  <td>${{ '%.2f'|format(p.avg_cost) }}</td><td>${{ '%.2f'|format(p.current_price) }}</td>
  <td>${{ '%.2f'|format(mval) }}</td>
  <td class="{{ 'pos' if p.get('unrealized_pnl',0)>=0 else 'neg' }}">${{ '%+.2f'|format(p.get('unrealized_pnl',0)) }}</td>
  <td class="{{ 'pos' if p.get('pnl_pct',0)>=0 else 'neg' }}">{{ '%+.1f'|format(p.get('pnl_pct',0)) }}%</td></tr>
  {% endfor %}
  <tr class="totals-row"><td>TOTAL</td><td>—</td><td>${{ '%.2f'|format(ns.tc) }}</td><td>—</td>
  <td>${{ '%.2f'|format(ns.tv) }}</td>
  <td class="{{ 'pos' if ns.tp>=0 else 'neg' }}">${{ '%+.2f'|format(ns.tp) }}</td>
  <td class="{{ 'pos' if ns.tp>=0 else 'neg' }}">{{ '%+.2f'|format((ns.tp/ns.tc*100) if ns.tc else 0) }}%</td></tr>
  </tbody></table>
  {% else %}<span class="muted">No positions yet.</span>{% endif %}
</div>

{% if alpha_pos %}
<div class="card">
  <div class="section-hdr"><h2>Alpha Layer — Agent Active (~20%)</h2>
    <span class="muted">Long · Short · Spreads · Hedges · Vol Arb</span></div>
  <table><thead><tr><th>Ticker</th><th>Structure</th><th>Cost</th><th>MTM</th><th>P&L</th><th>P&L %</th><th>Max Profit</th><th>Exit Rule</th><th>Status</th></tr></thead><tbody>
  {% for p in alpha_pos %}
  {% set mtm = p.get('mtm', p.get('cost', 0)) %}{% set pnl = p.get('pnl', 0) %}{% set pct = p.get('pnl_pct', 0) %}
  <tr><td><strong>{{ p.ticker }}</strong></td>
  <td><span class="chip spread">{{ p.get('asset_type','SPREAD') }}</span></td>
  <td>${{ '%.2f'|format(p.get('cost',0)) }}</td>
  <td>${{ '%.2f'|format(mtm) }}</td>
  <td class="{{ 'pos' if pnl>=0 else 'neg' }}">${{ '%+.2f'|format(pnl) }}</td>
  <td class="{{ 'pos' if pct>=0 else 'neg' }}">{{ '%+.1f'|format(pct) }}%</td>
  <td>${{ '%.2f'|format(p.get('max_profit',0)) if p.get('max_profit') else 'Uncapped' }}</td>
  <td class="muted">{{ p.get('stop_type','THESIS_BREAK_ONLY') }}</td>
  <td><span class="chip filled">FILLED</span></td></tr>
  {% endfor %}
  </tbody></table>
</div>{% endif %}

{% if txns %}
<div class="card">
  <h2>Transaction Log — Confirmed Fills</h2>
  <table><thead><tr><th>Date</th><th>Ticker</th><th>Action</th><th>Qty</th><th>Fill Price</th><th>Total</th><th>Status</th></tr></thead><tbody>
  {% set ns2 = namespace(total=0) %}
  {% for t in txns|reverse %}{% set ns2.total = ns2.total + t.get('total',0) %}
  <tr><td class="muted">{{ t.get('date','') }}</td><td><strong>{{ t.get('ticker','') }}</strong></td>
  <td><span class="chip long">{{ t.get('action','BUY') }}</span></td>
  <td>{{ t.get('quantity','') }}</td><td>${{ '%.4f'|format(t.get('price',0)) }}</td>
  <td>${{ '%.2f'|format(t.get('total',0)) }}</td>
  <td><span class="chip filled">FILLED</span></td></tr>
  {% endfor %}
  <tr class="totals-row"><td colspan="5" style="text-align:right;padding-right:14px">TOTAL DEPLOYED</td>
  <td>${{ '%.2f'|format(ns2.total) }}</td><td>—</td></tr>
  </tbody></table>
</div>{% endif %}

</div>
<footer>American Frontier ETF · GFC · Agent-Managed · Read-only investor view · Auto-refresh 2 min · {{ now }}</footer>
</body></html>"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
