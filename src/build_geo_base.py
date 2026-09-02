"""Shapefiles SES-DF -> GeoJSON simplificado para web (RAs, Regiões de Saúde, Macrorregiões)."""
import geopandas as gpd, warnings, os
warnings.filterwarnings("ignore")
SRC = "data/raw/shapefiles"; DST = "data/processed"
def exp(src, dst, tol=0.0004):
    g = gpd.read_file(f"{SRC}/{src}").to_crs(4326)
    g["geometry"] = g.geometry.simplify(tol, preserve_topology=True)
    g.to_file(f"{DST}/{dst}.geojson", driver="GeoJSON")
    print(dst, len(g), f"{os.path.getsize(f'{DST}/{dst}.geojson')/1024:.0f} KB")
exp("Regiões_Administrativas.shp", "ras")
exp("Regiões_de_Saúde.shp", "regioes_saude")
exp("Macrorregiões_de_Saúde.shp", "macro")
