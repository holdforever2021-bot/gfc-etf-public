#!/usr/bin/env python3
"""
DECOMMISSIONED 29 September 2026.

Ankur, 29 Sep 2026:
  "remove any public references to american frontier etf - ai managed thematic
   fund.. that idea is scratched and decommissioned as of today.. rationale -
   strategy resulted in 50% loss of capital, fund idea scratched."

WHAT WAS HERE, AND WHY IT IS GONE
  A public page titled "American Frontier ETF - AI-Managed Thematic Fund",
  presented as an "Investor Product" for GFC LLC, headlining a "+729% Backtest
  Return (Jan 2024 - May 2026)" against QQQ's +83.6%, and describing an "AI-
  Managed Alpha Layer" actively trading 20% of capital.

  Two independent reasons it had to come down:

  1. THE STRATEGY LOST ~50% OF CAPITAL. Whatever the backtest showed, the live
     result did not follow it. A page marketing the backtest while the live
     book was down half is not a page that should be reachable.

  2. THE 729% WAS NOT REPRODUCIBLE. The figure was hardcoded into this file;
     the generator script was never in the repo and no source data was kept.
     The QQQ leg was independently recomputed and is real (+83.6% exactly), so
     the number was produced from real prices - but the ETF leg cannot be
     rebuilt by anyone, including its author, and the page's own disclosure
     conceded one holding's weight was synthetically backfilled pre-IPO.

  The old page is preserved in git history. It is not restored, and the
  "American Frontier" name and the "AI-Managed" framing are retired with it.

SUCCESSOR
  A single consolidated vehicle exists going forward. It is private, it is
  managed by Ankur, and no agent holds execution authority over it. It has no
  public page and does not need one.
"""

import os
from flask import Flask

app = Flask(__name__)

NOTICE = """<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Decommissioned</title>
<style>
 html,body{height:100%;margin:0;background:#0b0e14;color:#e8ecf4;
   font:16px/1.6 -apple-system,BlinkMacSystemFont,system-ui,sans-serif}
 .w{max-width:560px;margin:0 auto;padding:16vh 24px 40px}
 h1{font-size:22px;font-weight:600;margin:0 0 14px;letter-spacing:-.01em}
 p{color:#9aa5bb;margin:0 0 13px}
 .d{color:#5f6b82;font-size:13px;margin-top:26px;border-top:1px solid #232a38;padding-top:14px}
</style>
<div class=w>
<h1>This project has been decommissioned.</h1>
<p>The page previously published here is no longer available, and the strategy
it described is not being pursued.</p>
<p>Nothing here was, or is, an offer, a solicitation, or investment advice.</p>
<div class=d>Retired 29 September 2026.</div>
</div>"""


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def gone(path):
    # Everything returns the same notice. No PIN page, no data endpoints, no
    # charts. 410 Gone is the honest status: this existed and was withdrawn.
    return NOTICE, 410


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
