#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds index.html from the canonical JSON source of truth.

Source of truth: mahmoud_apartments_canonical.json (next to this script).
Run:  python3 publish_site.py            # writes index.html next to the script
"""
import json
import html as H
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "mahmoud_apartments_canonical.json")
OUT = os.path.join(HERE, "index.html")

def fmt_price(p):
    return "{:,} EGP".format(p)

def plat_label(p):
    return {"dubizzle": "Dubizzle", "dubizzle-olx": "Dubizzle",
            "propertyfinder": "Propertyfinder", "facebook": "Facebook",
            "aqarmap": "Aqarmap"}.get(p, p or "—")

def sqm_txt(s):
    if s is None:
        return "—"
    s = float(s)
    return "{:g}m²".format(int(s) if s == int(s) else s)

def drive_txt(r):
    am, km = r.get("am"), r.get("km")
    if not am:
        return "—"
    line = "🚗 {:g} min · {} km".format(am, km) if km else "🚗 {:g} min".format(am)
    sub = "ذهاب 10ص؛ عودة ~{:g} min".format(2 * am + 6)
    return '<span class="b">%s</span><br><span class="s">%s</span>' % (H.escape(line), H.escape(sub))

def seller_txt(r):
    name = (r.get("seller") or "").strip()
    styp = (r.get("seller_type") or "").strip()
    if not name:
        return "Verify on contact"
    label = styp if styp else "Verify on contact"
    return "%s<br><span class='s'>%s</span>" % (H.escape(name), H.escape(label))

def furn_status(r):
    if r.get("verified_furn") is True:
        return "فاضية – تم التحقق ✅"
    if r.get("verified_furn") is False or r.get("verified_furn") is None:
        return "فاضية"
    return "فاضية"

def row_html(r):
    return """<tr class="row" data-am="%s" data-price="%s" data-sqm="%s" data-seller-type="%s" data-bed="%s" data-title="%s">
 <td><span class="area">%s</span><br><span class="s">%s</span></td>
 <td><a href="%s" target="_blank">%s</a></td>
 <td><b>%s</b></td>
 <td>%s Bedrooms · %s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
</tr>
""" % (H.escape(str(r['am'] or ''), quote=True), H.escape(str(r['price']), quote=True),
       H.escape(str(r['sqm'] or 0), quote=True),
       H.escape(r.get('seller_type') or '', quote=True),
       H.escape(str(r['br']), quote=True),
       H.escape(r['title'], quote=True),
       H.escape(r['area']), H.escape(r['posted']),
       H.escape(r['url'], quote=True), H.escape(r['title']),
       fmt_price(r['price']),
       r['br'], sqm_txt(r['sqm']),
       plat_label(r['plat']), seller_txt(r), drive_txt(r),
       furn_status(r))

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
<p class="sub">67 شقة فاضية (غير مفروشة)، 3+ غرف، 10-18 ألف، آخر 20 يوم — ⛔ مستبعد: زهراء مدينة نصر، التبة، شبرا (بالعنوان والوصف ورابط المرجع). مرتبة حسب أقرب وقت قيادة من المكتب.</p>
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
<th>Bedrooms·m²<br>الغرف · المساحة</th>
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
 var n=document.createElement('span'); // placeholder to avoid layout shift
 function val(el){return el.value;}
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
    body = "".join(row_html(r) for r in rows)
    out = HEAD.replace("<!--ROWS-->", body)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print("built %s: %d rows" % (OUT, len(rows)))

if __name__ == "__main__":
    build()
