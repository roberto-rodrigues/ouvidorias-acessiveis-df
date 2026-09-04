"""Fonte oficial RA (data/raw/RA.json — 33 RAs atuais) + shapefiles SES-DF (RS/Macro)
-> GeoJSON simplificado para web."""
import geopandas as gpd, warnings, os
warnings.filterwarnings("ignore")
SRC = "data/raw"; SHAPE = f"{SRC}/shapefiles"; DST = "data/processed"


def exp_ras(tol=0.0004):
    """Base oficial das Regiões Administrativas (RA.json, EPSG:4326)."""
    g = gpd.read_file(f"{SRC}/RA.json").rename(columns={"ra": "RA"})
    if g.crs is None or g.crs.to_epsg() != 4326:
        g = g.to_crs(4326)
    g["geometry"] = g.geometry.simplify(tol, preserve_topology=True)
    keep = [c for c in ["RA", "RA_leg", "num_ra"] if c in g.columns] + ["geometry"]
    g[keep].to_file(f"{DST}/ras.geojson", driver="GeoJSON")
    print("ras", len(g), f"{os.path.getsize(f'{DST}/ras.geojson')/1024:.0f} KB")


def exp(src, dst, tol=0.0004):
    g = gpd.read_file(f"{SHAPE}/{src}").to_crs(4326)
    g["geometry"] = g.geometry.simplify(tol, preserve_topology=True)
    g.to_file(f"{DST}/{dst}.geojson", driver="GeoJSON")
    print(dst, len(g), f"{os.path.getsize(f'{DST}/{dst}.geojson')/1024:.0f} KB")


exp_ras()
exp("Regiões_de_Saúde.shp", "regioes_saude")
exp("Macrorregiões_de_Saúde.shp", "macro")