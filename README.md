# Ouvidorias Acessíveis do Distrito Federal

Mapa web das ouvidorias do GDF com recursos de acessibilidade para atendimento presencial ao cidadão,
a partir das respostas consolidadas dos formulários **Selo Acessibilidade 2024/2025** (autodeclaração das ouvidorias seccionais)
e das divisões territoriais do DF (shapefiles do InfoSaúde/SES-DF).

**Página publicada:** `docs/index.html` (arquivo único, sem servidor — pode ser servido via GitHub Pages).

## Estrutura

```
data/raw/        CSV do formulário + shapefiles (RS, Macro) + RA.json (base oficial das 33 RAs)
data/processed/  GeoJSON simplificado e ouvidorias geocodificadas (ouvidorias_geo.csv p/ validação)
src/             pipeline Python + Leaflet embutido
docs/            index.html gerado (saída publicável)
```

> As Regiões Administrativas usam a base **oficial** (GeoJSON EPSG:4326, 33 RAs atuais
> com numeração RA I–RA XXXIII) em `data/raw/RA.json`. Regiões de Saúde e Macrorregiões
> vêm dos shapefiles SES-DF/InfoSaúde em `data/raw/shapefiles`.

## Pipeline

```bash
pip install -r requirements.txt
make          # base -> dados -> site
```

| Etapa | Script | Faz |
|---|---|---|
| `base`  | `build_geo_base.py` | shapefiles → GeoJSON simplificado (RAs, RS, Macro) |
| `dados` | `build_dados.py`    | CSV do Selo → GeoJSON das ouvidorias; RA por spatial join |
| `site`  | `build_site.py`     | injeta dados + Leaflet num único `docs/index.html` |

## Coordenadas das sedes

Prioridade de resolução da coordenada de cada ouvidoria:

1. **`validado`** — `data/raw/ouvidorias_coords_validadas.csv` (lat/lon conferidos manualmente pela equipe).
   Tem precedência sobre tudo; é a fonte confiável.
2. **`shp`** — shapefile SES-DF/InfoSaúde (hospitais regionais).
3. **`osm`** — Nominatim/OpenStreetMap (conferir antes de publicar).
4. **`aprox`** — estimativa pela RA/sede — **validar**.

`src/geo_sedes.py` mantém o dicionário legado de sedes. Para corrigir um ponto,
o caminho recomendado é acrescentar a linha correspondente em
`data/raw/ouvidorias_coords_validadas.csv` (colunas `SIGLA,Orgao,Latitude,Longitude,Endereco`).
Quando a linha não traz `Endereco`, o endereço anterior (do `geo_sedes.py`) é mantido.

Regras aplicadas no pipeline:

- a coordenada **validada** sempre vence as demais fontes;
- para a SES, a coordenada do órgão só vale quando a unidade está em branco — os hospitais
  regionais (HRC/HRG/HRPL) continuam vindo do shapefile;
- a ouvidoria de uma **Administração Regional** fica sempre na RA do próprio nome, mesmo quando o
  ponto cai em outra RA na base oficial (ex.: RA SIA em trecho limítrofe do Guará, Sol Nascente
  dentro da poligonal de Ceilândia).

### Pontos pendentes de validação

- `data/processed/pontos_aproximados_validacao.csv` — candidatos do OpenStreetMap para os pontos `aprox`
  (revisar antes de aplicar; campo `confianca` e `acao_recomendada`).
- `data/processed/pontos_aproximados_validacao_resumo.json` — contagem por confiança.
- `data/processed/coordenadas_validadas_import_report.json` — o que o CSV validado casou na base
  e a lista de registros que continuam sem coordenada validada.

## Fundo do mapa

- **Zoom < 13 (visão geral):** fundo estilizado desenhado em CSS (teal + pontilhado) com as RAs em
  cinza-azulado — mantém o visual do painel e destaca os agrupamentos.
- **Zoom ≥ 13 (detalhe):** entra o **basemap do OpenStreetMap** (ruas, quadras, prédios e pontos de
  interesse como UBS, escolas, estádios) e a opacidade das RAs cai para ~10% para não esconder o mapa.
  Ao voltar para a visão geral, os tiles saem e o fundo estilizado retorna.
- O crédito `© OpenStreetMap contributors` é exibido no canto inferior direito (controle de atribuição
  do Leaflet) sempre que os tiles estão visíveis.
- A legenda é recolhível pelo título ("Legenda") e começa recolhida no mobile.
- Controles no canto superior direito: **Mapa completo** (volta à visão inicial, limpa RA, busca e
  filtros de recurso) e a **borracha** (limpa apenas a busca e a RA marcada; fica desabilitada quando
  não há nada para limpar). A busca é insensível a acento e maiúsculas ("saude" encontra "Saúde").
- A visão inicial usa `zoomSnap:0.25` para ampliar o enquadramento em passos fracionários sem cortar
  nenhuma RA nas bordas (`padding` de 3 px no desktop e 10 px no mobile).

## Marcadores

Os marcadores são **agrupados** (Leaflet.markercluster) com raio de 45 px: no mapa completo aparece um
círculo azul-escuro com a contagem de ouvidorias; clicar no agrupamento aproxima e separa os pontos.
A partir do zoom 15 o agrupamento é desativado e cada ouvidoria aparece individualmente.
- Clicar num marcador ou num cartão da lista destaca a Região Administrativa, **aproxima até o zoom 16
  (nível de rua/prédio, com o basemap detalhado)** e abre o popup da ouvidoria — inclusive para pontos
  isolados ou em dupla, que antes só abriam o popup sem aproximar.

## Atualizar com novas respostas

1. Substitua `data/raw/selo_acessibilidade_2024.csv` pela exportação nova do formulário.
2. Inclua o órgão em `geo_sedes.py` se for novo.
3. `make dados site` e commit.

## Créditos

Fundo cartográfico estilizado sem provedor externo · Limites territoriais: base oficial das RAs do DF (RA.json) + SES-DF (InfoSaúde) · Leaflet 1.9.4 (BSD-2) · Leaflet.markercluster 1.5.3 (MIT, vendorizado em `src/markercluster.*`).
