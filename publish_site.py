#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds index.html from the canonical JSON source of truth.

Source of truth: mahmoud_apartments_canonical.json (next to this script).
Run:  python3 publish_site.py            # writes index.html next to the script
Canonical schema (v3):
  url, title, price, area, posted, platform,
  bedrooms, bathrooms_verified, sqm_verified,
  furnishing_status ('verified-unfurnished' | 'unfurnished (not re-verified)'),
  seller, seller_type, drive_am_min, drive_km
"""
import json
import html as H
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "mahmoud_apartments_canonical.json")
OUT = os.path.join(HERE, "index.html")

# ---------- HARD EXCLUSION (asserted, never advisory) ----------
EXCL = re.compile(r"زهراء|zahraa|zahrah|التبة|التبه|شبرا|shobra|shubra", re.I)

# ---------- HIDDEN from site but KEPT in JSON (user request) ----------
# Al Waha City compound + حي الواحة neighborhood MUST NOT appear in the HTML.
# Rows stay in the canonical JSON; they are simply not rendered.
HIDDEN_PAT = re.compile(
    r"al\s*-?\s*waha\b|waha\s*city\b|حي\s*الواح[ةه]|الواح[ةه]", re.I)

def assert_clean(rows):
    bad = []
    for r in rows:
        hay = " ".join(str(r.get(k, "")) for k in ("url", "title", "area"))
        if EXCL.search(hay):
            bad.append(r["url"])
    if bad:
        raise SystemExit("EXCLUSION VIOLATION: %d rows matched Zahraa/الزيبرا/التبة/شبرا: %s"
                         % (len(bad), [b["url"] for b in bad]))

def visible(rows):
    """Filter out hidden areas (Al Waha). Returned rows are what gets rendered."""
    return [r for r in rows if not HIDDEN_PAT.search(
        " ".join(str(r.get(k, "")) for k in ("url", "title", "area")))]

# ---------- formatting ----------
def fmt_price(p):
    return "{:,} EGP".format(p)

def sqm_txt(s):
    if s is None:
        return "—"
    s = float(s)
    return "{:g}m²".format(int(s) if s == int(s) else s)

def drive_txt(r):
    am, km = r.get("drive_am_min"), r.get("drive_km")
    if not am:
        return "—"
    line = "🚗 {:g} min · {} km".format(am, km) if km else "🚗 {:g} min".format(am)
    sub = "ذهاب 10ص؛ عودة ~{:g} min".format(2 * am + 6)
    return '<span class="b">%s</span><br><span class="s">%s</span>' % (H.escape(str(line)), H.escape(str(sub)))

FURN_LABEL = {
    "verified-unfurnished": "فاضية — تم التحقق ✅",
    "unfurnished (not re-verified)": "فاضية (غير مُتحقق منها)",
}

def seller_txt(r):
    name = (r.get("seller") or "").strip()
    styp = (r.get("seller_type") or "").strip()
    if not name:
        return "Verify on contact"
    return "%s<br><span class='s'>%s</span>" % (H.escape(name), H.escape(styp or "Verify on contact"))

def row_html(r):
    bath = r.get("bathrooms_verified")
    bath_s = "{:g}".format(bath) if bath else "—"
    sqm = sqm_txt(r.get("sqm_verified"))
    cell = "%s Bedrooms · %s · %s Bath" % (r["bedrooms"], sqm, bath_s)
    return """<tr class="row" data-am="%s" data-price="%s" data-sqm="%s" data-seller-type="%s" data-bed="%s" data-title="%s">
 <td><span class="area">%s</span><br><span class="s">%s</span></td>
 <td><a href="%s" target="_blank">%s</a></td>
 <td><b>%s</b></td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
</tr>
""" % (H.escape(str(r.get('drive_am_min') or ''), quote=True),
       H.escape(str(r['price']), quote=True),
       H.escape(str(r.get('sqm_verified') or 0), quote=True),
       H.escape(r.get('seller') and (r.get('seller_type') or '') or 'Verify on contact', quote=True),
       H.escape(str(r.get('bedrooms') or ''), quote=True),
       H.escape(r['title'], quote=True),
       H.escape(r['area']), H.escape(str(r['posted'])),
       H.escape(r['url'], quote=True), H.escape(r['title']),
       H.escape(fmt_price(r['price'])),
       H.escape(str(cell)),
       H.escape(r['platform']),
       seller_txt(r), drive_txt(r),
       H.escape(FURN_LABEL.get(r.get('furnishing_status'), r.get('furnishing_status') or '—')))

HEAD = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>شقق الإيجار القريبة من مكتب محمود — El Tayaran</title><style>
:root{--fg:#111;--muted:#6a6a6a;--border:#e5e5e5;--card:#fff;--bg:#fafafa}
body{font:15px/1.5 -apple-system,system-ui,Segoe UI,Tahoma,sans-serif;color:var(--fg);background:var(--bg);margin:0;padding:24px}
h1{font-size:20px;margin:0 0 6px} .sub{color:var(--muted);font-size:13px;margin-bottom:18px}
table{width:100%;border-collapse:separate;border-spacing:0 8px}
tr.row{background:var(--card);box-shadow:0 1px 2px rgba(0,0,0,.06)}
tr.row td{padding:12px 14px;vertical-align:top;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
tr.row td:first-child{border-inline-start:1px solid var(--border);border-start-start-radius:8px;border-end-start-radius:8px}
tr.row td:last-child{border-inline-end:1px solid var(--border);border-start-end-radius:8px;border-end-end-radius:8px}
a{color:#0a5bd6;text-decoration:none} a:hover{text-decoration:underline}
.area{background:#eef3ff;padding:2px 8px;border-radius:6px;font-size:13px}
.b{font-weight:600} .s{color:var(--muted);font-size:12px}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 12px;font-size:13px}
.toolbar select,.toolbar input{font:inherit;padding:6px 10px;border:1px solid var(--border);border-radius:8px;background:#fff}
.toolbar input{min-width:180px}
#count{color:var(--muted)}
th{padding:0 14px 4px;text-align:start;font-size:12px;color:var(--muted);font-weight:600}
</style></head><body>
<h1>🏘️ شقق الإيجار لـ محمود — قرب مكتبه، الطيران / مدينة نصر</h1>
<p class="sub">66 شقة فاضية (غير مفروشة)، 3+ غرف، 10-18 ألف، آخر 20 يوم — ⛔ مستبعد: زهراء مدينة نصر، التبة، شبرا (بالعنوان والوصف ورابط المرجع). مرتبة حسب أقرب وقت قيادة من المكتب. م² والحمامات معروضة فقط عند التحقق منها من المصدر.</p>
<div class="toolbar">
 <input id="q" type="search" placeholder="بحث (عربي/إنجليزي)…">
 <select id="f-seller"><option value="all">All / الكل</option><option value="Broker">Broker</option><option value="Owner">Owner</option><option value="Verify on contact">Verify on contact</option></select>
 <select id="f-sort"><option value="near">NearFirst</option><option value="price-asc">Price asc</option><option value="price-desc">Price desc</option><option value="size-desc">Size desc</option></select>
 <select id="f-bed"><option value="all">All beds</option><option value="3">3</option><option value="4+">4+</option></select>
 <span id="count"></span>
</div>
<table><thead><tr>
<th>Area · Posted<br>المنطقة · التاريخ</th>
<th>Title<br>العنوان</th>
<th>Price<br>السعر</th>
<th>Bedrooms·m²·Bath<br>الغرف · المساحة · الحمامات</th>
<th>Platform<br>المنصة</th>
<th>Seller<br>المعلن/المصدر</th>
<th>Drive time<br>وقت القيادة</th>
<th>Furnishing<br>الفرش</th>
</tr></thead><tbody>
<!--ROWS-->
</tbody></table>
<script>
(function(){
 var q=document.getElementById('q'),fs=document.getElementById('f-seller'),
     so=document.getElementById('f-sort'),fb=document.getElementById('f-bed'),
     cnt=document.getElementById('count');
 var rows=Array.prototype.slice.call(document.querySelectorAll('tr.row'));
 var tb=document.querySelector('tbody');
 function apply(){
  var term=q.value.trim().toLowerCase(), st=fs.value, b=fb.value;
  var shown=rows.filter(function(r){
   var ds=r.getAttribute('data-seller-type')||'';
   if(st!=='all'&&ds!==st)return false;
   if(b!=='all'){ if(b==='4+'&&!(parseInt(r.getAttribute('data-bed'),10)>=4))return false;
                  if(b==='3'&&r.getAttribute('data-bed')!=='3')return false;}
   if(term&&r.getAttribute('data-title').toLowerCase().indexOf(term)===-1)return false;
   return true;
  });
  var key;
  if(so.value==='near')key=function(a){return parseInt(a.getAttribute('data-am'),10)||9999;};
  else if(so.value==='price-asc')key=function(a){return parseInt(a.getAttribute('data-price'),10);};
  else if(so.value==='price-desc')key=function(a){return -parseInt(a.getAttribute('data-price'),10);};
  else key=function(a){return -parseFloat(a.getAttribute('data-sqm')||0);};
  shown.sort(function(a,b){return key(a)-key(b);});
  rows.forEach(function(r){r.style.display='none';});
  shown.forEach(function(r){tb.appendChild(r);r.style.display='';});
  cnt.textContent=shown.length+' / '+rows.length+' شقة';
 }
 [q,fs,so,fb].forEach(function(el){el.addEventListener('input',apply);el.addEventListener('change',apply);});
 apply();
})();
</script></body></html>
"""

def build():
    rows = json.load(open(SRC))
    assert_clean(rows)
    vis = visible(rows)
    body = "".join(row_html(r) for r in vis)
    out = HEAD.replace("<!--ROWS-->", body)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print("built %s: %d visible rows (hidden %d of %d in JSON)"
          % (OUT, len(vis), len(rows) - len(vis), len(rows)))

if __name__ == "__main__":
    build()
