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
n_valid=sum(f["properties"].get("fonte")=="validado" for f in pts["features"])

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ouvidorias Acessíveis do DF</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
<style>__LCSS__</style>
<style>__MCCSS__</style>
<style>
:root{
/* Direcao: sinalizacao de acessibilidade. A tipografia e a Atkinson Hyperlegible,
   desenhada pelo Braille Institute para leitura de baixa visao — a escolha vem do
   assunto, nao de um par default. Paleta reduzida a 3 papeis: tinta para estrutura,
   verde para "tem acessibilidade", ambar SO para "dado aproximado". */
--tinta:#10263a;--tinta-2:#3d5a73;--tinta-3:#7b93a7;
--papel:#f4f6f7;--papel-2:#e8edf0;--card:#ffffff;
--b:#cfdae1;--b-forte:#a9bcc8;
--verde:#0f7a3d;--verde-claro:#e6f4ec;
--ambar:#8a5300;--ambar-claro:#fdf0da;
--azul-dado:#1b5e8c;--azul-dado-claro:#e4eff7;
--map-base:#8b9aa3;--map-bg:#eef2f4;
--raio:4px;
--fonte:"Atkinson Hyperlegible",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;font-family:var(--fonte);color:var(--tinta);background:var(--papel);font-size:16px;line-height:1.5}
header{background:var(--tinta);color:#fff;padding:14px 20px;display:flex;align-items:center;gap:14px;position:relative;z-index:20;border-bottom:4px solid var(--verde)}
header h1{font-size:1.12rem;margin:0;font-weight:700;letter-spacing:-.01em}
header .tag{margin-left:auto;font-size:.78rem;background:var(--verde);color:#fff;padding:3px 9px;border-radius:var(--raio);font-weight:700}
.layout{display:grid;grid-template-columns:360px 1fr;height:calc(100vh - 54px)}
aside{background:var(--card);border-right:1px solid var(--b);overflow:auto;padding:16px;z-index:15}
/* titulo de secao: caixa baixa, peso alto, sem caixa alta espacada */
aside h2{font-size:.95rem;font-weight:700;color:var(--tinta);margin:16px 0 8px;letter-spacing:0}
aside h2:first-child{margin-top:0}
input[type=search],select{width:100%;padding:10px;border:1px solid var(--b-forte);border-radius:var(--raio);font-size:.95rem;background:#fff;font-family:inherit}
input[type=search]:focus,select:focus{outline:2px solid var(--azul-dado);outline-offset:1px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--b-forte);border-radius:var(--raio);padding:6px 10px;font-size:.82rem;cursor:pointer;background:#fff;color:var(--tinta);font-family:inherit}
.chip:hover{border-color:var(--tinta-2)}
.chip[aria-pressed=true]{background:var(--tinta);color:#fff;border-color:var(--tinta)}
.chip:focus-visible,.card:focus-visible,button:focus-visible{outline:3px solid var(--ambar);outline-offset:2px}
/* cartao: fio de hierarquia a esquerda em vez de sombra uniforme */
.card{border:0;border-left:3px solid var(--b);border-radius:0;padding:8px 0 8px 12px;margin-bottom:10px;cursor:pointer;background:transparent}
.card:hover,.card.active{border-left-color:var(--verde);background:var(--verde-claro)}
.card b{display:block;font-size:.98rem;font-weight:700}
.card small{color:var(--tinta-2)}
.ic{display:inline-flex;gap:4px;flex-wrap:wrap;margin-top:6px}
.ic span{font-size:.72rem;background:var(--papel-2);color:var(--tinta-2);padding:2px 6px;border-radius:var(--raio)}
/* mapa: fundo neutro. O gradiente pontilhado decorativo saiu — nao informava nada. */
#map{height:100%;background:var(--map-bg);position:relative;overflow:hidden}
/* Respeita a hierarquia de panes do Leaflet: marcadores acima das RAs,
   popups acima dos marcadores e controles acima do mapa. */
.leaflet-container{background:transparent}
.leaflet-interactive{filter:drop-shadow(0 1px 2px rgba(11,28,43,.16))}
.leaflet-tooltip.ra-label{background:#fff;color:var(--tinta);border:0;border-radius:var(--raio);box-shadow:0 2px 8px rgba(11,28,43,.2);font-weight:700;font-size:1.02rem;letter-spacing:0;padding:5px 9px}
.leaflet-tooltip.ra-label:before{display:none}
.leaflet-tooltip.ra-focus-label{background:rgba(255,255,255,.94);color:var(--tinta);border:1px solid var(--b);border-radius:var(--raio);box-shadow:0 2px 8px rgba(11,28,43,.14);font-weight:700;font-size:.84rem;letter-spacing:0;padding:4px 9px}
.leaflet-tooltip.ra-focus-label:before{display:none}
.mc-icon{background:var(--tinta);border:2.5px solid #fff;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;line-height:1;box-shadow:0 2px 9px rgba(11,28,43,.35);cursor:pointer}
.mc-icon span{font-size:.78rem;letter-spacing:-.02em}
.mc-icon:hover{background:var(--azul-dado)}
.pino svg{width:100%;height:100%;display:block;filter:drop-shadow(0 2px 3px rgba(11,28,43,.3));transform-origin:50% 100%;transition:transform .12s}
.pino-aprox svg path{stroke:var(--ambar);stroke-width:4}
.pino:hover svg{transform:scale(1.12)}
.leaflet-control-attribution{background:rgba(255,255,255,.92);color:var(--tinta);font-size:.7rem;padding:2px 6px;border-radius:var(--raio) 0 0 0}
.leaflet-control-attribution a{color:var(--tinta);text-decoration:underline}
#map.detalhe{background:#eef2f4}
#map.detalhe .leaflet-tile{transition:opacity .2s linear}
.leaflet-tooltip.pin-tip{background:var(--tinta);color:#fff;border:0;border-radius:var(--raio);padding:3px 8px;font-size:.78rem;font-weight:700;box-shadow:0 2px 8px rgba(11,28,43,.28);white-space:nowrap;pointer-events:none}
.leaflet-tooltip.pin-tip:before{border-top-color:var(--tinta)}
.count{font-size:.84rem;color:var(--tinta-2)}
.popup b{color:var(--tinta)}
.popup ul{margin:6px 0 0 16px;padding:0;font-size:.88rem}
.legend{background:rgba(255,255,255,.96);padding:8px 12px 10px;border-radius:var(--raio);font-size:.84rem;line-height:1.6;box-shadow:0 2px 10px rgba(11,28,43,.16);border:1px solid var(--b)}
.legend h4{margin:0 0 4px;font-size:.86rem;font-weight:700;color:var(--tinta);letter-spacing:0}
.legend-toggle{font:inherit;color:inherit;background:transparent;border:0;padding:0;cursor:pointer;width:100%;display:flex;align-items:center;gap:6px;justify-content:space-between;text-align:left}
.legend-toggle span{font-size:.72rem}
.legend.recolhida .lg-body{display:none}
.legend.recolhida h4{margin:0}
.legend i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;vertical-align:middle}
.ctrl-group{display:flex;gap:6px;align-items:center}
.reset-map{background:#fff;border:1px solid var(--b-forte);border-radius:var(--raio);height:36px;padding:0 12px;font-weight:700;color:var(--tinta);box-shadow:0 2px 10px rgba(11,28,43,.18);cursor:pointer;font-family:inherit}
.reset-map:hover{background:var(--papel-2)}
.clear-map{background:#fff;border:1px solid var(--b-forte);border-radius:var(--raio);width:36px;height:36px;display:flex;align-items:center;justify-content:center;color:var(--tinta);box-shadow:0 2px 10px rgba(11,28,43,.18);cursor:pointer}
.clear-map:hover{background:var(--papel-2)}
.clear-map.off{color:var(--b-forte);cursor:default;box-shadow:none}
.clear-map.off:hover{background:#fff}
/* KPIs: os quatro numeros sao a mesma medida — viram uma regua de leitura,
   nao quatro cartoes iguais */
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;border:1px solid var(--b);border-radius:var(--raio);overflow:hidden;background:#fff}
.kpis div{background:#fff;border-radius:0;padding:10px 8px;text-align:center;border-left:1px solid var(--b)}
.kpis div:first-child{border-left:0}
.kpis b{display:block;font-size:1.34rem;color:var(--tinta);font-weight:700;font-variant-numeric:tabular-nums}
.kpis span{font-size:.72rem;color:var(--tinta-2)}
/* selos: mesma forma, hierarquia clara (verde = tem; ambar = aproximado) */
.badge{font-size:.72rem;padding:2px 7px;border-radius:var(--raio);margin-right:4px;font-weight:700;display:inline-block}
.b-lib{background:var(--verde-claro);color:var(--verde)}
.b-nolib{background:var(--papel-2);color:var(--tinta-2)}
.b-aprox{background:var(--ambar-claro);color:var(--ambar)}
.b-valid{background:var(--azul-dado-claro);color:var(--azul-dado)}
.skip{position:absolute;left:-999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9999;border:2px solid var(--tinta)}
@media(max-width:800px){
header{padding:10px 12px;gap:8px;flex-wrap:wrap}
header h1{font-size:1rem}
header .tag{margin-left:0;font-size:.72rem}
.layout{grid-template-columns:1fr;grid-template-rows:auto minmax(56vh,1fr);height:auto;min-height:calc(100vh - 54px)}
aside{max-height:42vh;border-right:0;border-bottom:1px solid var(--b);padding:12px}
#map{height:58vh}
.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
.kpis div:nth-child(odd){border-left:0}
.kpis div:nth-child(n+3){border-top:1px solid var(--b)}
.leaflet-tooltip.ra-label{font-size:.86rem;padding:4px 6px}
}
@media(max-width:800px){
html,body{max-width:100%;overflow-x:hidden}
header{align-items:flex-start}
header h1{white-space:normal;line-height:1.15;flex:1 1 100%;min-width:0;font-size:.98rem}
.layout,aside,main,#map{min-width:0;width:100%;max-width:100vw}
.leaflet-container{max-width:100vw}
.kpis{width:100%;overflow:hidden}
.kpis b{font-size:1.18rem}
.kpis span{font-size:.66rem}
.chips{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}
.chip{white-space:nowrap}
.legend{max-width:74vw;font-size:.78rem;line-height:1.45;padding:6px 8px}
.legend .lg-note{display:none}
.reset-map{padding:7px 9px;font-size:.84rem}
}
/* movimento: o unico momento e o pino respondendo ao ponteiro; respeita quem pediu menos */
@media(prefers-reduced-motion:reduce){
*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}
.pino:hover svg{transform:none}
#map.detalhe .leaflet-tile{transition:none}
}
</style>
</head>
<body>
<a class="skip" href="#lista">Ir para a lista de ouvidorias</a>
<header>
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" aria-hidden="true"><circle cx="12" cy="9" r="3"/><path d="M12 2a7 7 0 0 1 7 7c0 5-7 13-7 13S5 14 5 9a7 7 0 0 1 7-7z"/></svg>
  <h1>Ouvidorias Acessíveis do Distrito Federal</h1>
  <span class="tag">Selo Acessibilidade 2024/2025 · __N__ ouvidorias</span>
</header>
<div class="layout">
<aside aria-label="Filtros e lista">
  <div class="kpis"><div><b>__N__</b><span>ouvidorias com selo</span></div><div><b>__NLIB__</b><span>com Libras presencial</span></div><div><b>__NCAP__</b><span>com equipe capacitada</span></div><div><b>__NVALID__</b><span>com coord. validada</span></div></div>
  <label for="q"><h2>Buscar</h2></label>
  <input id="q" type="search" placeholder="Nome, órgão ou região…" aria-label="Buscar ouvidoria">
  <label for="ra"><h2>Região Administrativa</h2></label>
  <select id="ra"><option value="">Todas as RAs</option></select>
  <h2>Recursos de acessibilidade</h2>
  <div class="chips" id="chips" role="group" aria-label="Filtrar por recurso"></div>
  <h2 id="lista">Ouvidorias <span class="count" id="count" role="status" aria-live="polite"></span></h2>
  <div id="cards"></div>
</aside>
<main><div id="map" role="region" aria-label="Mapa das ouvidorias do DF"></div></main>
</div>
<script>__LJS__</script>
<script>__MCJS__</script>
<script>
const RAS = __RAS__;
const PTS = __PTS__;
const REC = __REC__;const SHORT=__SHORT__;const sh=a=>SHORT[a]||a;
const INITIAL_CENTER=[-15.78,-47.85],INITIAL_ZOOM=10;
const map = L.map('map',{zoomControl:true,attributionControl:true,minZoom:9,maxZoom:18,zoomSnap:.25,zoomDelta:.5}).setView(INITIAL_CENTER,INITIAL_ZOOM);
const Z_DETALHE=13; // a partir daqui entra o fundo detalhado (ruas, prédios, POIs)
let selectedRA='';
function estiloRA(f,hover=false){const det=map.getZoom()>=Z_DETALHE;const selected=f.properties.RA===selectedRA;const base=det?.10:.82;return {color:selected?(det?'#17344f':'#ffffff'):(det?'#8aa0aa':'#c7d8df'),weight:selected?2.8:(hover?2.1:(det?1.3:1.45)),fillColor:selected?'#5f7882':'#789099',fillOpacity:selected?(det?.25:.96):(hover?base+.08:base),opacity:det?.85:.98};}
const raLayer = L.geoJSON(RAS,{style:(f)=>estiloRA(f),
  onEachFeature:(f,l)=>{l.bindTooltip(f.properties.RA,{sticky:true,opacity:.95});
    l.on('mouseover',()=>l.setStyle(estiloRA(f,true)));l.on('mouseout',()=>l.setStyle(estiloRA(f,false)));
    l.on('click',(e)=>{L.DomEvent.stopPropagation(e);sel.value=f.properties.RA;selectedRA=f.properties.RA;showRAName(selectedRA);render()})}}).addTo(map);
function fullPadding(){return map.getSize().x<600?[10,10]:[3,3]}
map.fitBounds(raLayer.getBounds(),{padding:fullPadding()});
const raNameLayer=L.layerGroup().addTo(map);
function getRALayer(ra){return raLayer.getLayers().find(l=>l.feature.properties.RA===ra)}
function updateRAStyles(){raLayer.eachLayer(l=>l.setStyle(estiloRA(l.feature)))}
// Fundo detalhado do OpenStreetMap (ruas, prédios, pontos de interesse) a partir do zoom de detalhe.
const osmFundo=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,className:'osm-tiles',attribution:'© OpenStreetMap contributors'});
function atualizarFundo(){const det=map.getZoom()>=Z_DETALHE;
 if(det&&!map.hasLayer(osmFundo)){osmFundo.setOpacity(0);osmFundo.addTo(map);setTimeout(()=>osmFundo.setOpacity(1),60)}
 else if(!det&&map.hasLayer(osmFundo)){map.removeLayer(osmFundo)}
 document.getElementById('map').classList.toggle('detalhe',det);
 updateRAStyles()}
map.on('zoomend',atualizarFundo);
function showRAName(ra){raNameLayer.clearLayers();if(!ra)return;const l=getRALayer(ra);if(!l)return;L.tooltip({permanent:true,direction:'center',className:'ra-focus-label',opacity:1,interactive:false}).setContent(ra).setLatLng(l.getBounds().getCenter()).addTo(raNameLayer)}
function destacarRA(ra){selectedRA=ra||'';updateRAStyles();showRAName(selectedRA)}
function focusRA(ra,animate=true){destacarRA(ra);const l=getRALayer(selectedRA);if(l)map.fitBounds(l.getBounds(),{padding:[70,70],animate})}
// Mostra a ouvidoria: sempre aproxima até o nível de detalhe (ruas/casas) e abre o popup.
function mostrarOuvidoria(m,y,x){const ALVO=16;
 const abrir=()=>{if(markers.getVisibleParent&&markers.getVisibleParent(m)!==m){markers.zoomToShowLayer(m,()=>m.openPopup())}else{m.openPopup()}};
 if(map.getZoom()>=ALVO&&map.getCenter().equals(L.latLng(y,x))){abrir();return}
 map.once('moveend',abrir);map.setView([y,x],Math.max(ALVO,map.getZoom()),{animate:true})}
function resetMapa(){selectedRA='';raNameLayer.clearLayers();sel.value='';document.getElementById('q').value='';active.clear();document.querySelectorAll('.chip').forEach(b=>b.setAttribute('aria-pressed','false'));render();updateRAStyles();map.fitBounds(raLayer.getBounds(),{padding:fullPadding(),animate:true});}
// Limpar apenas a busca e a Região Administrativa marcada (mantém os filtros de recurso).
function limparFiltros(){const tinhaRA=!!sel.value;document.getElementById('q').value='';if(tinhaRA){sel.value='';selectedRA='';raNameLayer.clearLayers()}render();updateRAStyles();
 if(tinhaRA){map.fitBounds(raLayer.getBounds(),{padding:fullPadding(),animate:true})}}
function atualizarBotaoLimpar(){const b=document.querySelector('.clear-map');if(!b)return;const ativo=!!document.getElementById('q').value||!!sel.value;b.disabled=!ativo;b.classList.toggle('off',!ativo)}
const botoesControl=L.control({position:'topright'});botoesControl.onAdd=()=>{const d=L.DomUtil.create('div','ctrl-group');
 const b1=L.DomUtil.create('button','reset-map',d);b1.type='button';b1.title='Voltar ao mapa completo';b1.textContent='Mapa completo';L.DomEvent.disableClickPropagation(b1);b1.onclick=resetMapa;
 const b2=L.DomUtil.create('button','clear-map',d);b2.type='button';b2.title='Limpar busca e região marcada';b2.setAttribute('aria-label','Limpar busca e região marcada');
 b2.innerHTML='<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 20h14"/><path d="M9.2 20 19.5 9.7a2.1 2.1 0 0 0 0-3L17.6 4.8a2.1 2.1 0 0 0-3 0L4.3 15.1a2.1 2.1 0 0 0 0 3l1.9 1.9z"/><path d="m10.6 6.6 6.8 6.8"/></svg>';
 L.DomEvent.disableClickPropagation(b2);b2.onclick=limparFiltros;
 return d};botoesControl.addTo(map);
const legend=L.control({position:'bottomleft'});legend.onAdd=()=>{const d=L.DomUtil.create('div','legend');
 d.innerHTML='<h4><button type="button" class="legend-toggle" aria-controls="legend-body" aria-expanded="true">Legenda <span aria-hidden="true">▾</span></button></h4><div class="lg-body" id="legend-body"><b>Marcadores</b><br><svg width="11" height="16" viewBox="0 0 24 36" style="vertical-align:-3px;margin-right:5px"><path d="M12 0C5.37 0 0 5.37 0 12c0 9.4 12 24 12 24s12-14.6 12-24C24 5.37 18.63 0 12 0Z" fill="#16a34a" stroke="#fff" stroke-width="3"/></svg>Libras presencial<br><svg width="11" height="16" viewBox="0 0 24 36" style="vertical-align:-3px;margin-right:5px"><path d="M12 0C5.37 0 0 5.37 0 12c0 9.4 12 24 12 24s12-14.6 12-24C24 5.37 18.63 0 12 0Z" fill="#3b82f6" stroke="#fff" stroke-width="3"/></svg>Sem Libras presencial<br><span class="marker-status">Contorno âmbar = localização aproximada</span><br><span class="lg-note"><small>Pino maior = mais itens de acessibilidade</small><br><small>Agrupamento (nº) = clique para aproximar</small><br><small>Aproxime (zoom 13+) para ver ruas e prédios</small><br></span><hr style="margin:7px 0;border:none;border-top:1px solid #d7e1e8"><b>Regiões Administrativas</b><br><span style="display:inline-block;width:12px;height:12px;border:1.5px solid #c7d8df;background:#789099;vertical-align:middle;margin-right:6px"></span>Mapa cinza-azulado<br><span class="lg-note"><small>Clique numa RA para filtrar · botão “Mapa completo” reseta</small></span></div>';
 d.classList.add('recolhida'); // evita cobrir pinos na visão geral; botão Legenda expande sob demanda
 const h=d.querySelector('.legend-toggle');L.DomEvent.disableClickPropagation(h);
 const caret=()=>{const s=h.querySelector('span');const open=!d.classList.contains('recolhida');h.setAttribute('aria-expanded',String(open));if(s)s.textContent=open?'▾':'▸'};
 caret();h.onclick=()=>{d.classList.toggle('recolhida');caret()};
 return d};legend.addTo(map);
const sel=document.getElementById('ra');
// A lista de RAs inclui as que existem só nos dados (ex.: Água Quente, RA criada após a base das 33).
[...new Set(RAS.features.map(f=>f.properties.RA).concat(PTS.features.map(f=>f.properties.RA)).filter(r=>r&&r!=='—'))].sort((a,b)=>a.localeCompare(b,'pt')).forEach(r=>sel.add(new Option(r,r)));
const chips=document.getElementById('chips');const active=new Set();
REC.forEach(r=>{const b=document.createElement('button');b.className='chip';b.textContent=sh(r);b.setAttribute('aria-pressed','false');
 b.onclick=()=>{active.has(r)?active.delete(r):active.add(r);b.setAttribute('aria-pressed',active.has(r));render()};chips.appendChild(b)});
const col=p=>p.libras==='Sim'?'#16a34a':'#3b82f6';
const semAcento=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
// Marcador em forma de pino (ponteiro) com "i" de informação; a ponta fica exatamente na coordenada.
function pinoHTML(cor){return '<svg viewBox="0 0 24 36" aria-hidden="true"><path d="M12 0C5.37 0 0 5.37 0 12c0 9.4 12 24 12 24s12-14.6 12-24C24 5.37 18.63 0 12 0Z" fill="'+cor+'" stroke="#ffffff" stroke-width="2"/><circle cx="12" cy="12" r="6.3" fill="#ffffff"/><text x="12" y="16" text-anchor="middle" font-size="11.5" font-weight="800" fill="'+cor+'" font-family="system-ui,Segoe UI,Roboto,sans-serif">i</text></svg>'}
function pinoIcon(p){const h=Math.round(30+p.n_itens*1.3),w=Math.round(h*2/3);return L.divIcon({className:p.fonte==='aprox'?'pino pino-aprox':'pino',html:pinoHTML(col(p)),iconSize:L.point(w,h),iconAnchor:L.point(w/2,h),popupAnchor:L.point(0,-h+6),tooltipAnchor:L.point(0,-h)})}
function clusterIcon(cluster){const n=cluster.getChildCount();const d=n<10?34:(n<30?42:50);return L.divIcon({html:'<div class="mc-icon" style="width:'+d+'px;height:'+d+'px"><span>'+n+'</span></div>',className:'',iconSize:L.point(d,d)})}
const markers=L.markerClusterGroup({maxClusterRadius:45,showCoverageOnHover:false,disableClusteringAtZoom:15,spiderfyOnMaxZoom:true,removeOutsideVisibleBounds:true,iconCreateFunction:clusterIcon}).addTo(map);let cur=null;
function popup(p,y,x){return `<div class="popup"><b>${p.nome}</b><br><small>${p.orgao}</small><br><small>${p.endereco} · RA ${p.RA}</small><br>
 <span class="badge ${p.libras==='Sim'?'b-lib':'b-nolib'}">${p.libras==='Sim'?'Libras presencial':'Sem Libras presencial'}</span>${p.fonte==='aprox'?'<span class="badge b-aprox">localização aproximada</span>':''}${p.fonte==='validado'?'<span class="badge b-valid">coordenada validada</span>':''}
 <ul>${p.itens.map(a=>'<li>'+a+'</li>').join('')}${p.capacitado==='Sim'?'<li>Equipe com capacitação em acessibilidade (2020–2024)</li>':''}</ul>
 <a href="https://www.google.com/maps/dir/?api=1&destination=${y},${x}" target="_blank" rel="noopener">Como chegar ↗</a> · <small>Autodeclaração em ${p.data}</small></div>`}
function render(){
 const q=semAcento(document.getElementById('q').value.trim()),ra=sel.value;
 const list=PTS.features.filter(f=>{const p=f.properties;
  return (!q||semAcento(p.nome+p.orgao+p.RA+p.sigla).includes(q))&&(!ra||p.RA===ra)&&[...active].every(a=>p.acess.includes(a))});
 markers.clearLayers();const cards=document.getElementById('cards');cards.innerHTML='';
 list.forEach((f,i)=>{const p=f.properties,[x,y]=f.geometry.coordinates;
  const m=L.marker([y,x],{icon:pinoIcon(p),riseOnHover:true,alt:p.nome+(p.fonte==='aprox'?' — localização aproximada':'')}).bindTooltip(p.nome+(p.fonte==='aprox'?' — localização aproximada':''),{direction:'top',offset:[0,-2],className:'pin-tip',opacity:1,sticky:false}).bindPopup(popup(p,y,x),{autoPan:true,maxWidth:330,autoPanPaddingTopLeft:L.point(10,60)});m.on('add',()=>{const el=m.getElement();if(el)el.setAttribute('aria-label',m.options.alt)});m.addTo(markers);m.on('click',(e)=>{L.DomEvent.stopPropagation(e);destacarRA(p.RA);if(map.getZoom()<16){mostrarOuvidoria(m,y,x)}});
  const c=document.createElement('div');c.className='card';c.tabIndex=0;c.setAttribute('role','button');c.setAttribute('aria-label','Abrir ouvidoria: '+p.nome);
  c.innerHTML=`<b>${p.nome}</b><small>${p.orgao}</small><br><small>RA ${p.RA}${p.fonte==='aprox'?' · <span class="badge b-aprox">local aprox.</span>':''}${p.fonte==='validado'?' · <span class="badge b-valid">coord. validada</span>':''}</small><div class="ic">${p.acess.map(a=>'<span>'+sh(a)+'</span>').join('')}</div>`;
  const go=()=>{destacarRA(p.RA);mostrarOuvidoria(m,y,x);document.querySelectorAll('.card').forEach(e=>e.classList.remove('active'));c.classList.add('active')};
  c.onclick=go;c.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}};cards.appendChild(c)});
 document.getElementById('count').textContent=`(${list.length})`;
 if(ra){focusRA(ra)}else if(selectedRA){updateRAStyles();showRAName(selectedRA)}
 atualizarBotaoLimpar()
}
document.getElementById('q').oninput=render;sel.onchange=render;render();
function ajustarTamanhoMapa(){map.invalidateSize();if(!sel.value)map.fitBounds(raLayer.getBounds(),{padding:fullPadding()});atualizarFundo();}
setTimeout(ajustarTamanhoMapa,150);window.addEventListener('resize',()=>setTimeout(ajustarTamanhoMapa,150));
atualizarFundo();
// Clicar fora das regiões/marcadores (área vazia do mapa) volta à visão inicial.
map.on('click',resetMapa);
</script>
</body></html>"""
out = (HTML.replace("__RAS__", json.dumps(ras, ensure_ascii=False))
           .replace("__PTS__", json.dumps(pts, ensure_ascii=False))
           .replace("__REC__", json.dumps(REC, ensure_ascii=False)).replace("__SHORT__", json.dumps(SHORT, ensure_ascii=False)).replace("__N__", str(n)).replace("__NLIB__", str(n_lib)).replace("__NCAP__", str(n_cap)).replace("__NVALID__", str(n_valid))
           .replace("__LCSS__", open("src/leaflet.css").read())
           .replace("__MCCSS__", open("src/markercluster.css").read())
           .replace("__LJS__", open("src/leaflet.js").read())
           .replace("__MCJS__", open("src/markercluster.js").read()))
open("docs/index.html", "w", encoding="utf-8").write(out)
print("ok", len(out)//1024, "KB")
