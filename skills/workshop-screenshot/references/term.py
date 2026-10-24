#!/usr/bin/env python3
"""Render a captured CLI output as a clean terminal-styled HTML page.
Usage: term.py <title> <output-file> <out-html> [width]
The output must be the REAL captured output of the command."""
import sys, html

title, infile, outfile = sys.argv[1], sys.argv[2], sys.argv[3]
width = sys.argv[4] if len(sys.argv) > 4 else "980"
body = open(infile, encoding='utf-8', errors='replace').read().rstrip('\n') or '(no output)'

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 24px; background: #f0f0f0; }}
  .term {{ width: {width}px; border-radius: 8px; overflow: hidden;
          box-shadow: 0 2px 14px rgba(0,0,0,.25); font-family: 'Red Hat Mono','JetBrains Mono',monospace; }}
  .bar {{ background: #2a2a35; padding: 9px 14px; display: flex; align-items: center; gap: 8px; }}
  .dot {{ width: 11px; height: 11px; border-radius: 50%; }}
  .r {{ background: #ff5f57; }} .y {{ background: #febc2e; }} .g {{ background: #28c840; }}
  .ttl {{ color: #b8b8c4; font-size: 13px; margin-left: 8px; white-space: nowrap; overflow: hidden; }}
  pre {{ margin: 0; padding: 14px 18px 16px; background: #16161f; color: #d6d6e0;
        font-size: 13.5px; line-height: 1.55; white-space: pre; overflow: hidden; }}
  .cmd {{ color: #7fd18c; font-weight: 600; }}
  .sep {{ color: #4a4a58; }}
</style></head>
<body>
<div class="term" id="term">
  <div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
    <span class="ttl">{title}</span></div>
<pre><span class="cmd">$ {cmd}</span>
<span class="sep"> </span>{body}</pre>
</div>
</body></html>"""

# command = the title (first part before any '&&' description); strip a leading path noise
cmd = title.split(' && ')[0].split(' (last')[0]
with open(outfile, 'w', encoding='utf-8') as f:
    f.write(TEMPLATE.format(title=html.escape(title), cmd=html.escape(cmd), body=html.escape(body), width=width))
print(f"rendered {outfile} (width {width})")
