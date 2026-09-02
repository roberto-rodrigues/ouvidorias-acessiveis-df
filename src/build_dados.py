"""CSV do Selo Acessibilidade -> GeoJSON das ouvidorias (com RA via spatial join)."""
import pandas as pd, geopandas as gpd, json, warnings, re
from shapely.geometry import Point
from geo_sedes import SEDES
warnings.filterwarnings("ignore")

df = pd.read_csv("data/raw/selo_acessibilidade_2024.csv")
df.columns = ["ts", "orgao", "unidade", "cre", "libras", "selo", "itens", "capacitado", "servidor", "certs", "decl"]
df["orgao"] = df.orgao.str.strip()
df["itens_l"] = df.itens.fillna("").apply(lambda s: [i.strip() for i in re.split(r",\s*", s) if i.strip()])

hosp = gpd.read_file("data/raw/shapefiles/Hospitais.shp")
hrg = hosp[hosp.Hospitais.str.contains("GAMA")].iloc[0]

rows = []
for _, r in df.iterrows():
    if isinstance(r.unidade, str) and "HRG" in r.unidade:
        sigla, lat, lon, fonte, end = "SES-DF · HRG", hrg.geometry.y, hrg.geometry.x, "shp", f"{hrg.Endereco.title()}, {hrg.Numero} – Gama"
        nome = "Ouvidoria do Hospital Regional do Gama (HRG)"
    else:
        sigla, lat, lon, fonte, end = SEDES[r.orgao]
        nome = f"Ouvidoria – {sigla}"
    acess = list(r.itens_l)
    if r.libras == "Sim": acess.append("Atendimento presencial em Libras")
    if r.capacitado == "Sim": acess.append("Equipe capacitada em acessibilidade")
    rows.append(dict(nome=nome, sigla=sigla, orgao=r.orgao, endereco=end, lat=lat, lon=lon, fonte=fonte,
                     libras=r.libras, selo=r.selo, capacitado=r.capacitado, itens=r.itens_l, acess=acess,
                     n_itens=len(r.itens_l), data=r.ts.split(" ")[0]))

g = gpd.GeoDataFrame(rows, geometry=[Point(x["lon"], x["lat"]) for x in rows], crs=4326)
ras = gpd.read_file("data/raw/shapefiles/Regiões_Administrativas.shp")[["RA", "RS", "geometry"]]
g = gpd.sjoin(g, ras, how="left", predicate="within").drop(columns="index_right")
g["RA"] = g.RA.fillna("—")
g.drop(columns=["lat", "lon"]).to_file("data/processed/ouvidorias.geojson", driver="GeoJSON")
g.drop(columns="geometry").assign(lat=g.geometry.y, lon=g.geometry.x).to_csv("data/processed/ouvidorias_geo.csv", index=False)
print(g[["sigla", "RA", "fonte", "n_itens", "libras"]].to_string())
