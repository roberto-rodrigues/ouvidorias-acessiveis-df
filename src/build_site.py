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
:root{--azul:#15324f;--azul2:#2563eb;--verde:#15803d;--bg:#dfeaf0;--txt:#1f2937;--muted:#64748b;--card:#fff;--b:#d7e1e8;--map-bg:#3e93ad;--map-bg2:#2f7893;--map-base:#789099;--map-line:#dce8ee;--map-focus:#17344f}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;color:var(--txt);background:var(--bg)}
header{background:linear-gradient(90deg,#17344f,#235f77);color:#fff;padding:14px 20px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 10px rgba(15,35,50,.25);position:relative;z-index:20}
header h1{font-size:1.15rem;margin:0;font-weight:650;letter-spacing:.01em}
header .tag{margin-left:auto;font-size:.75rem;background:#eef6f9;color:#17344f;padding:3px 8px;border-radius:999px;font-weight:700}
.layout{display:grid;grid-template-columns:360px 1fr;height:calc(100vh - 54px)}
aside{background:rgba(255,255,255,.96);border-right:1px solid var(--b);overflow:auto;padding:16px;box-shadow:4px 0 18px rgba(20,45,70,.08);z-index:15}
aside h2{font-size:.85rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin:14px 0 8px}
input[type=search],select{width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:8px;font-size:.95rem;background:#fff}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid #cbd5e1;border-radius:999px;padding:5px 10px;font-size:.8rem;cursor:pointer;background:#fff;color:#213547}
.chip[aria-pressed=true]{background:#17344f;color:#fff;border-color:#17344f}
.chip:focus-visible,.card:focus-visible,button:focus-visible{outline:3px solid #f59e0b;outline-offset:2px}
.card{border:1px solid var(--b);border-radius:10px;padding:10px 12px;margin-bottom:8px;cursor:pointer;background:#fff}
.card:hover,.card.active{border-color:#17344f;box-shadow:0 0 0 2px rgba(23,52,79,.18)}
.card b{display:block;font-size:.95rem}
.card small{color:var(--muted)}
.ic{display:inline-flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.ic span{font-size:.7rem;background:#e8f2f5;color:#17445d;padding:2px 6px;border-radius:6px}
#map{height:100%;background:radial-gradient(circle at 2px 2px,rgba(255,255,255,.86) 1.4px,transparent 1.6px) 0 58%/32px 32px no-repeat,radial-gradient(circle at 2px 2px,rgba(255,255,255,.78) 1.4px,transparent 1.6px) 100% 2%/32px 32px no-repeat,linear-gradient(180deg,var(--map-bg),var(--map-bg2));position:relative;overflow:hidden}
#map .leaflet-pane,#map .leaflet-control-container{z-index:2}.leaflet-container{background:transparent}.leaflet-interactive{filter:drop-shadow(0 1px 2px rgba(11,28,43,.18))}.leaflet-tooltip.ra-label{background:#fff;color:#17344f;border:0;border-radius:2px;box-shadow:0 2px 8px rgba(11,28,43,.22);font-weight:900;font-size:1.05rem;letter-spacing:.02em;padding:5px 9px;text-transform:uppercase}.leaflet-tooltip.ra-label:before{display:none}.leaflet-tooltip.ra-focus-label{background:rgba(255,255,255,.88);color:#17344f;border:1px solid rgba(220,232,238,.9);border-radius:999px;box-shadow:0 2px 8px rgba(11,28,43,.16);font-weight:700;font-size:.82rem;letter-spacing:.02em;padding:4px 9px}.leaflet-tooltip.ra-focus-label:before{display:none}
.count{font-size:.8rem;color:var(--muted)}
.popup b{color:var(--azul)}
.popup ul{margin:6px 0 0 16px;padding:0;font-size:.85rem}
.legend{background:rgba(255,255,255,.94);padding:8px 10px;border-radius:8px;font-size:.8rem;line-height:1.6;box-shadow:0 2px 10px rgba(11,28,43,.18);border:1px solid rgba(215,225,232,.9)}
.legend i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;vertical-align:middle}.reset-map{background:#fff;border:0;border-radius:8px;padding:8px 10px;font-weight:800;color:#17344f;box-shadow:0 2px 10px rgba(11,28,43,.22);cursor:pointer}.reset-map:hover{background:#eef6f9}
@media(max-width:800px){header{padding:10px 12px;gap:8px;flex-wrap:wrap}header h1{font-size:1rem}header .tag{margin-left:0;font-size:.68rem}.layout{grid-template-columns:1fr;grid-template-rows:auto minmax(56vh,1fr);height:auto;min-height:calc(100vh - 54px)}aside{max-height:42vh;border-right:0;border-bottom:1px solid var(--b);padding:12px}#map{height:58vh}.kpis{grid-template-columns:repeat(3,minmax(0,1fr))}.leaflet-tooltip.ra-label{font-size:.82rem;padding:4px 6px}}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.kpis div{background:#eef6f9;border-radius:8px;padding:8px;text-align:center}.kpis b{display:block;font-size:1.3rem;color:var(--azul)}.kpis span{font-size:.7rem;color:var(--muted)}
.badge{font-size:.7rem;padding:2px 6px;border-radius:6px;margin-right:4px}.b-lib{background:#dcfce7;color:#15803d}.b-nolib{background:#f3f4f6;color:#6b7280}.b-aprox{background:#fef3c7;color:#92400e}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9999}
@media(max-width:800px){html,body{max-width:100%;overflow-x:hidden}header{align-items:flex-start}header h1{white-space:normal;line-height:1.15;flex:1 1 100%;min-width:0;font-size:.95rem}header .tag{margin-left:0}.layout,aside,main,#map{min-width:0;width:100%;max-width:100vw}.leaflet-container{max-width:100vw}.kpis{grid-template-columns:repeat(3,minmax(0,1fr));width:100%;overflow:hidden}.kpis div{min-width:0;padding:7px 4px}.kpis b{font-size:1.15rem}.kpis span{font-size:.62rem}.chips{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}.chip{white-space:nowrap}.legend{max-width:82vw;font-size:.72rem}.reset-map{padding:7px 9px;font-size:.8rem}}
</style>
</head>
<body>
<a class="skip" href="#lista">Ir para a lista de ouvidorias</a>
<header>
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="9" r="3"/><path d="M12 2a7 7 0 0 1 7 7c0 5-7 13-7 13S5 14 5 9a7 7 0 0 1 7-7z"/></svg>
  <h1>Ouvidorias Acessíveis do Distrito Federal</h1>
  <span class="tag">Selo Acessibilidade 2024/2025 · __N__ ouvidorias</span>
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
const INITIAL_CENTER=[-15.78,-47.85],INITIAL_ZOOM=10;
const map = L.map('map',{zoomControl:true,attributionControl:false}).setView(INITIAL_CENTER,INITIAL_ZOOM);
let selectedRA='';
function estiloRA(f,hover=false){const selected=f.properties.RA===selectedRA;return {color:selected?'#ffffff':'#c7d8df',weight:selected?2.8:(hover?2.1:1.45),fillColor:selected?'#5f7882':'#789099',fillOpacity:selected?.96:(hover?.9:.82),opacity:.98};}
const raLayer = L.geoJSON(RAS,{style:(f)=>estiloRA(f),
  onEachFeature:(f,l)=>{l.bindTooltip(f.properties.RA,{sticky:true,opacity:.95});
    l.on('mouseover',()=>l.setStyle(estiloRA(f,true)));l.on('mouseout',()=>l.setStyle(estiloRA(f,false)));
    l.on('click',(e)=>{L.DomEvent.stopPropagation(e);sel.value=f.properties.RA;selectedRA=f.properties.RA;showRAName(selectedRA);render()})}}).addTo(map);
function fullPadding(){return map.getSize().x<600?[32,32]:[8,8]}
map.fitBounds(raLayer.getBounds(),{padding:fullPadding()});
const raNameLayer=L.layerGroup().addTo(map);
function getRALayer(ra){return raLayer.getLayers().find(l=>l.feature.properties.RA===ra)}
function updateRAStyles(){raLayer.eachLayer(l=>l.setStyle(estiloRA(l.feature)))}
function showRAName(ra){raNameLayer.clearLayers();if(!ra)return;const l=getRALayer(ra);if(!l)return;L.tooltip({permanent:true,direction:'center',className:'ra-focus-label',opacity:1,interactive:false}).setContent(ra).setLatLng(l.getBounds().getCenter()).addTo(raNameLayer)}
function focusRA(ra,animate=true){selectedRA=ra||'';updateRAStyles();showRAName(selectedRA);const l=getRALayer(selectedRA);if(l)map.fitBounds(l.getBounds(),{padding:[70,70],animate})}
function resetMapa(){selectedRA='';raNameLayer.clearLayers();sel.value='';document.getElementById('q').value='';active.clear();document.querySelectorAll('.chip').forEach(b=>b.setAttribute('aria-pressed','false'));render();updateRAStyles();map.fitBounds(raLayer.getBounds(),{padding:fullPadding(),animate:true});}
const resetControl=L.control({position:'topright'});resetControl.onAdd=()=>{const b=L.DomUtil.create('button','reset-map');b.type='button';b.title='Voltar ao mapa completo';b.textContent='Mapa completo';L.DomEvent.disableClickPropagation(b);b.onclick=resetMapa;return b};resetControl.addTo(map);
const legend=L.control({position:'bottomleft'});legend.onAdd=()=>{const d=L.DomUtil.create('div','legend');
 d.innerHTML='<b>Marcadores</b><br><i style="background:#16a34a"></i>Libras presencial<br><i style="background:#3b82f6"></i>Sem Libras presencial<br><small>Ponto maior = mais itens de acessibilidade</small><hr style="margin:7px 0;border:none;border-top:1px solid #d7e1e8"><b>Regiões Administrativas</b><br><span style="display:inline-block;width:12px;height:12px;border:1.5px solid #c7d8df;background:#789099;vertical-align:middle;margin-right:6px"></span>Mapa cinza-azulado<br><small>Clique numa RA para filtrar · botão “Mapa completo” reseta</small>';return d};legend.addTo(map);
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
  const m=L.circleMarker([y,x],{radius:7+p.n_itens*0.8,color:'#fff',weight:2.5,fillColor:col(p),fillOpacity:1}).bindPopup(popup(p,y,x)).addTo(markers);m.on('click',(e)=>{L.DomEvent.stopPropagation(e);focusRA(p.RA)});
  const c=document.createElement('div');c.className='card';c.tabIndex=0;c.setAttribute('role','button');
  c.innerHTML=`<b>${p.nome}</b><small>${p.orgao}</small><br><small>RA ${p.RA}${p.fonte==='aprox'?' · <span class="badge b-aprox">local aprox.</span>':''}</small><div class="ic">${p.acess.map(a=>'<span>'+sh(a)+'</span>').join('')}</div>`;
  const go=()=>{focusRA(p.RA);m.openPopup();document.querySelectorAll('.card').forEach(e=>e.classList.remove('active'));c.classList.add('active')};
  c.onclick=go;c.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}};cards.appendChild(c)});
 document.getElementById('count').textContent=`(${list.length})`;
 if(ra){focusRA(ra)}else if(selectedRA){updateRAStyles();showRAName(selectedRA)}
}
document.getElementById('q').oninput=render;sel.onchange=render;render();
function ajustarTamanhoMapa(){map.invalidateSize();if(!sel.value)map.fitBounds(raLayer.getBounds(),{padding:fullPadding()});}
setTimeout(ajustarTamanhoMapa,150);window.addEventListener('resize',()=>setTimeout(ajustarTamanhoMapa,150));
// Clicar fora das regiões/marcadores (área vazia do mapa) volta à visão inicial.
map.on('click',resetMapa);
</script>
</body></html>"""
out = (HTML.replace("__RAS__", json.dumps(ras, ensure_ascii=False))
           .replace("__PTS__", json.dumps(pts, ensure_ascii=False))
           .replace("__REC__", json.dumps(REC, ensure_ascii=False)).replace("__SHORT__", json.dumps(SHORT, ensure_ascii=False)).replace("__N__", str(n)).replace("__NLIB__", str(n_lib)).replace("__NCAP__", str(n_cap))
           .replace("__LCSS__", open("src/leaflet.css").read())
           .replace("__LJS__", open("src/leaflet.js").read()))
open("docs/index.html", "w", encoding="utf-8").write(out)
print("ok", len(out)//1024, "KB")
