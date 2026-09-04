# Ouvidorias Acessíveis do Distrito Federal

Mapa web das ouvidorias do GDF com recursos de acessibilidade para atendimento presencial ao cidadão,
a partir das respostas do formulário **Selo Acessibilidade 2024** (autodeclaração das ouvidorias seccionais)
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

`src/geo_sedes.py` guarda lat/lon de cada órgão com a coluna `fonte`:
`osm` (Nominatim/OpenStreetMap), `aprox` (estimativa — **validar**), `shp` (shapefile SES-DF).
Para corrigir um ponto, edite ali e rode `make dados site`.

## Atualizar com novas respostas

1. Substitua `data/raw/selo_acessibilidade_2024.csv` pela exportação nova do formulário.
2. Inclua o órgão em `geo_sedes.py` se for novo.
3. `make dados site` e commit.

## Créditos

Basemap © CARTO / © OpenStreetMap contributors · Limites territoriais: SES-DF (InfoSaúde) · Leaflet 1.9.4 (BSD-2).
