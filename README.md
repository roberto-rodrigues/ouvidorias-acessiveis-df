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
`data/raw/ouvidorias_coords_validadas.csv` (colunas `SIGLA;Orgao;Latitude;Longitude;Tipo_acesso`,
delimitador `;`, decimal vírgula) e rodar `make dados site`.

### Pontos pendentes de validação

- `data/processed/pontos_aproximados_validacao.csv` — candidatos do OpenStreetMap para os pontos `aprox`
  (revisar antes de aplicar; campo `confianca` e `acao_recomendada`).
- `data/processed/pontos_aproximados_validacao_resumo.json` — contagem por confiança.
- `data/processed/coordenadas_validadas_import_report.json` — o que o CSV validado casou na base
  e a lista de registros que continuam sem coordenada validada.

## Marcadores

Os marcadores são **agrupados** (Leaflet.markercluster) com raio de 45 px: no mapa completo aparece um
círculo azul-escuro com a contagem de ouvidorias; clicar no agrupamento aproxima e separa os pontos.
A partir do zoom 15 o agrupamento é desativado e cada ouvidoria aparece individualmente.
Clicar num marcador ou num cartão da lista destaca a Região Administrativa e mostra o nome dela;
se o ponto ainda estiver dentro de um agrupamento, o mapa aproxima até exibi-lo.

## Atualizar com novas respostas

1. Substitua `data/raw/selo_acessibilidade_2024.csv` pela exportação nova do formulário.
2. Inclua o órgão em `geo_sedes.py` se for novo.
3. `make dados site` e commit.

## Créditos

Fundo cartográfico estilizado sem provedor externo · Limites territoriais: base oficial das RAs do DF (RA.json) + SES-DF (InfoSaúde) · Leaflet 1.9.4 (BSD-2) · Leaflet.markercluster 1.5.3 (MIT, vendorizado em `src/markercluster.*`).
