import json
ras = json.load(open("data/processed/ras.geojson"))
pts = json.load(open("data/processed/ouvidorias.geojson"))
ITENS = ["Rampa de acesso","Corrimão na rampa de acesso","Corrimão nas escadas","Piso tátil","Piso antiderrapante",
         "Banheiro adaptado","Estacionamento com vaga reservada para PCD",
         "Sala da ouvidoria em conformidade com os padrões e normas de acessibilidade"]
REC = ITENS + ["Atendimento presencial em Libras","Equipe capacitada em acessibilidade"]
SHORT = {"Estacionamento com vaga reservada para PCD":"Vaga PCD",
         "Sala da ouvidoria em conformidade com os padrões e normas de acessibilidade":"Sala conforme NBR 9050",
         "Atendimento presencial em Libras":"Libras presencial","Equipe capacitada em acessibilidade":"Equipe capacitada",
         "Corrimão na rampa de acesso":"Corrimão na rampa"}
# jitter para pontos coincidentes (mesmo prédio)
import math, collections
grp=collections.defaultdict(list)
for f in pts["features"]: grp[tuple(round(c,5) for c in f["geometry"]["coordinates"])].append(f)
for k,fs in grp.items():
    if len(fs)>1:
        for i,f in enumerate(fs):
            a=2*math.pi*i/len(fs); f["geometry"]["coordinates"]=[k[0]+0.00035*math.cos(a), k[1]+0.00035*math.sin(a)]
n=len(pts["features"]); n_lib=sum(f["properties"]["libras"]=="Sim" for f in pts["features"]); n_cap=sum(f["properties"]["capacitado"]=="Sim" for f in pts["features"])
n_aprox=sum(f["properties"]["fonte"]=="aprox" for f in pts["features"])

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ouvidorias Acessíveis do DF</title>
<style>__LCSS__</style>
<style>
:root{--azul:#1e3a8a;--azul2:#2563eb;--verde:#15803d;--bg:#f6f7f9;--txt:#1f2937;--muted:#6b7280;--card:#fff;--b:#e5e7eb}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;color:var(--txt);background:var(--bg)}
header{background:var(--azul);color:#fff;padding:14px 20px;display:flex;align-items:center;gap:14px}
header h1{font-size:1.15rem;margin:0;font-weight:600}
header .tag{margin-left:auto;font-size:.75rem;background:#fbbf24;color:#111;padding:3px 8px;border-radius:999px;font-weight:600}
.layout{display:grid;grid-template-columns:360px 1fr;height:calc(100vh - 54px)}
aside{background:var(--card);border-right:1px solid var(--b);overflow:auto;padding:16px}
aside h2{font-size:.85rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin:14px 0 8px}
input[type=search],select{width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:8px;font-size:.95rem}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid #cbd5e1;border-radius:999px;padding:5px 10px;font-size:.8rem;cursor:pointer;background:#fff}
.chip[aria-pressed=true]{background:var(--azul2);color:#fff;border-color:var(--azul2)}
.chip:focus-visible,.card:focus-visible,button:focus-visible{outline:3px solid #f59e0b;outline-offset:2px}
.card{border:1px solid var(--b);border-radius:10px;padding:10px 12px;margin-bottom:8px;cursor:pointer;background:#fff}
.card:hover,.card.active{border-color:var(--azul2);box-shadow:0 0 0 2px #bfdbfe}
.card b{display:block;font-size:.95rem}
.card small{color:var(--muted)}
.ic{display:inline-flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.ic span{font-size:.7rem;background:#dcfce7;color:var(--verde);padding:2px 6px;border-radius:6px}
#map{height:100%}
.count{font-size:.8rem;color:var(--muted)}
.popup b{color:var(--azul)}
.popup ul{margin:6px 0 0 16px;padding:0;font-size:.85rem}
.legend{background:#fff;padding:8px 10px;border-radius:8px;font-size:.8rem;line-height:1.6;box-shadow:0 1px 4px rgba(0,0,0,.2)}
.legend i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;vertical-align:middle}
@media(max-width:800px){.layout{grid-template-columns:1fr;grid-template-rows:auto 1fr}aside{max-height:45vh}}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.kpis div{background:#eff6ff;border-radius:8px;padding:8px;text-align:center}.kpis b{display:block;font-size:1.3rem;color:var(--azul)}.kpis span{font-size:.7rem;color:var(--muted)}
.badge{font-size:.7rem;padding:2px 6px;border-radius:6px;margin-right:4px}.b-lib{background:#dcfce7;color:#15803d}.b-nolib{background:#f3f4f6;color:#6b7280}.b-aprox{background:#fef3c7;color:#92400e}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9999}
</style>
</head>
<body>
<a class="skip" href="#lista">Ir para a lista de ouvidorias</a>
<header>
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="9" r="3"/><path d="M12 2a7 7 0 0 1 7 7c0 5-7 13-7 13S5 14 5 9a7 7 0 0 1 7-7z"/></svg>
  <h1>Ouvidorias Acessíveis do Distrito Federal</h1>
  <span class="tag">Selo Acessibilidade 2024 · __N__ ouvidorias</span>
</header>
<div class="layout">
<aside aria-label="Filtros e lista">
  <div class="kpis"><div><b>__N__</b><span>ouvidorias com selo</span></div><div><b>__NLIB__</b><span>com Libras presencial</span></div><div><b>__NCAP__</b><span>com equipe capacitada</span></div></div>
  <label for="q"><h2>Buscar</h2></label>
  <input id="q" type="search" placeholder="Nome, órgão ou região…" aria-label="Buscar ouvidoria">
  <label for="ra"><h2>Região Administrativa</h2></label>
  <select id="ra"><option value="">Todas as RAs</option></select>
  <h2>Recursos de acessibilidade</h2>
  <div class="chips" id="chips" role="group" aria-label="Filtrar por recurso"></div>
  <h2 id="lista">Ouvidorias <span class="count" id="count"></span></h2>
  <div id="cards"></div>
</aside>
<main><div id="map" role="application" aria-label="Mapa das ouvidorias do DF"></div></main>
</div>
<script>__LJS__</script>
<script>
const RAS = __RAS__;
const PTS = __PTS__;
const REC = __REC__;const SHORT=__SHORT__;const sh=a=>SHORT[a]||a;
const map = L.map('map',{zoomControl:true}).setView([-15.78,-47.85],10);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors',maxZoom:19}).addTo(map);
const RA_COLS=["#60a5fa","#34d399","#fbbf24","#f472b6","#a78bfa","#fb923c","#2dd4bf","#f87171","#a3e635","#38bdf8","#facc15","#4ade80","#c084fc","#fda4af","#93c5fd","#86efac","#fdba74","#fcd34d","#67e8f9","#d8b4fe","#bef264","#f9a8d4","#7dd3fc","#6ee7b7","#fecaca","#c4b5fd","#a5f3fc","#fde68a","#bbf7d0","#fed7aa","#e9d5ff","#bae6fd","#fecdd3"];
const raLayer = L.geoJSON(RAS,{style:(f)=>{const i=RAS.features.indexOf(f);return {color:'#1f2937',weight:1.2,fillColor:RA_COLS[i%RA_COLS.length],fillOpacity:.22};},
  onEachFeature:(f,l)=>{l.bindTooltip(f.properties.RA,{sticky:true,opacity:.95});
    l.on('mouseover',()=>l.setStyle({fillOpacity:.45,weight:1.8}));l.on('mouseout',()=>l.setStyle({fillOpacity:.22,weight:1.2}));
    l.on('click',()=>{sel.value=f.properties.RA;render()})}}).addTo(map);
const legend=L.control({position:'bottomleft'});legend.onAdd=()=>{const d=L.DomUtil.create('div','legend');
 d.innerHTML='<b>Marcadores</b><br><i style="background:#16a34a"></i>Libras presencial<br><i style="background:#3b82f6"></i>Sem Libras presencial<br><small>Ponto maior = mais itens de acessibilidade</small><hr style="margin:7px 0;border:none;border-top:1px solid #e5e7eb"><b>Regiões Administrativas</b><br><span style="display:inline-block;width:12px;height:12px;border:1.5px solid #1f2937;background:#93c5fd;vertical-align:middle;margin-right:6px"></span>33 RAs (base oficial)<br><small>Clique numa RA para filtrar a lista</small>';return d};legend.addTo(map);
const sel=document.getElementById('ra');
[...new Set(RAS.features.map(f=>f.properties.RA))].sort((a,b)=>a.localeCompare(b,'pt')).forEach(r=>sel.add(new Option(r,r)));
const chips=document.getElementById('chips');const active=new Set();
REC.forEach(r=>{const b=document.createElement('button');b.className='chip';b.textContent=sh(r);b.setAttribute('aria-pressed','false');
 b.onclick=()=>{active.has(r)?active.delete(r):active.add(r);b.setAttribute('aria-pressed',active.has(r));render()};chips.appendChild(b)});
const col=p=>p.libras==='Sim'?'#16a34a':'#3b82f6';
const markers=L.layerGroup().addTo(map);let cur=null;
function popup(p,y,x){return `<div class="popup"><b>${p.nome}</b><br><small>${p.orgao}</small><br><small>${p.endereco} · RA ${p.RA}</small><br>
 <span class="badge ${p.libras==='Sim'?'b-lib':'b-nolib'}">${p.libras==='Sim'?'Libras presencial':'Sem Libras presencial'}</span>${p.fonte==='aprox'?'<span class="badge b-aprox">localização aproximada</span>':''}
 <ul>${p.itens.map(a=>'<li>'+a+'</li>').join('')}${p.capacitado==='Sim'?'<li>Equipe com capacitação em acessibilidade (2020–2024)</li>':''}</ul>
 <a href="https://www.google.com/maps/dir/?api=1&destination=${y},${x}" target="_blank" rel="noopener">Como chegar ↗</a> · <small>Autodeclaração em ${p.data}</small></div>`}
function render(){
 const q=document.getElementById('q').value.toLowerCase(),ra=sel.value;
 const list=PTS.features.filter(f=>{const p=f.properties;
  return (!q||(p.nome+p.orgao+p.RA+p.sigla).toLowerCase().includes(q))&&(!ra||p.RA===ra)&&[...active].every(a=>p.acess.includes(a))});
 markers.clearLayers();const cards=document.getElementById('cards');cards.innerHTML='';
 list.forEach((f,i)=>{const p=f.properties,[x,y]=f.geometry.coordinates;
  const m=L.circleMarker([y,x],{radius:7+p.n_itens*0.8,color:'#fff',weight:2.5,fillColor:col(p),fillOpacity:1}).bindPopup(popup(p,y,x)).addTo(markers);
  const c=document.createElement('div');c.className='card';c.tabIndex=0;c.setAttribute('role','button');
  c.innerHTML=`<b>${p.nome}</b><small>${p.orgao}</small><br><small>RA ${p.RA}${p.fonte==='aprox'?' · <span class="badge b-aprox">local aprox.</span>':''}</small><div class="ic">${p.acess.map(a=>'<span>'+sh(a)+'</span>').join('')}</div>`;
  const go=()=>{map.flyTo([y,x],14);m.openPopup();document.querySelectorAll('.card').forEach(e=>e.classList.remove('active'));c.classList.add('active')};
  c.onclick=go;c.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}};cards.appendChild(c)});
 document.getElementById('count').textContent=`(${list.length})`;
 if(ra){const l=raLayer.getLayers().find(l=>l.feature.properties.RA===ra);if(l)map.fitBounds(l.getBounds())}
}
document.getElementById('q').oninput=render;sel.onchange=render;render();
// Clicar fora das regiões/marcadores (área vazia do mapa) volta à visão inicial.
map.on('click',()=>{map.setView([-15.78,-47.85],10,{animate:true});if(sel.value){sel.value='';render();}});
</script>
</body></html>"""
out = (HTML.replace("__RAS__", json.dumps(ras, ensure_ascii=False))
           .replace("__PTS__", json.dumps(pts, ensure_ascii=False))
           .replace("__REC__", json.dumps(REC, ensure_ascii=False)).replace("__SHORT__", json.dumps(SHORT, ensure_ascii=False)).replace("__N__", str(n)).replace("__NLIB__", str(n_lib)).replace("__NCAP__", str(n_cap))
           .replace("__LCSS__", open("src/leaflet.css").read())
           .replace("__LJS__", open("src/leaflet.js").read()))
open("docs/index.html", "w", encoding="utf-8").write(out)
print("ok", len(out)//1024, "KB")
