"""CSV do Selo Acessibilidade -> GeoJSON das ouvidorias (com RA via spatial join)."""
import pandas as pd, geopandas as gpd, warnings, re, unicodedata
from shapely.geometry import Point
from geo_sedes import SEDES
warnings.filterwarnings("ignore")

CSV = "data/raw/selo_acessibilidade_2024.csv"  # arquivo histórico; hoje consolida respostas 2024/2025

def norm(s):
    s = "" if pd.isna(s) else str(s).strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()

def loose(s):
    s=norm(s)
    s=s.replace(" do distrito federal", "").replace(" df", "")
    return re.sub(r"[^a-z0-9]+", "", s)

def load_validated_coords():
    path = "data/raw/ouvidorias_coords_validadas.csv"
    try:
        d = pd.read_csv(path)
    except FileNotFoundError:
        return {}
    coords = {}
    for _, r in d.iterrows():
        org = str(r.get("Orgao", "")).strip()
        if not org:
            continue
        raw_end = r.get("Endereco", "") if "Endereco" in d.columns else ""
        end = "" if pd.isna(raw_end) else str(raw_end).strip()
        coords[loose(org)] = dict(
            sigla=str(r.get("SIGLA", "")).strip(),
            lat=float(r["Latitude"]), lon=float(r["Longitude"]),
            end=end
        )
    return coords

VALIDATED_COORDS = load_validated_coords()

def sigla_de(org):
    m = re.search(r"\(([^)]+)\)", str(org))
    if m:
        return m.group(1).strip()
    stop = {"de", "da", "do", "das", "dos", "e", "a", "o", "as", "os", "no", "na"}
    parts = [p for p in re.split(r"\W+", str(org)) if p and p.lower() not in stop]
    sig = "".join(p[0].upper() for p in parts[:5])
    return sig or "Órgão"

# Base oficial das RAs para spatial join e fallback de localização das Administrações Regionais.
ras = gpd.read_file("data/raw/RA.json").rename(columns={"ra": "RA"})[["RA", "geometry"]]
ra_lookup = {norm(v): v for v in ras["RA"]}
ra_lookup_loose = {loose(v): v for v in ras["RA"]}
rep_points = ras.copy()
rep_points["geometry"] = rep_points.geometry.representative_point()
ra_centroid = {r.RA: (r.geometry.y, r.geometry.x) for _, r in rep_points.iterrows()}
RA_ALIASES = {
    "scia": ra_lookup_loose.get("scia", "SCIA"),
    "estrutural": ra_lookup_loose.get("scia", "SCIA"),
    "sia": ra_lookup_loose.get("sia", "SIA"),
    "arniqueiras": ra_lookup_loose.get("arniqueira", "Arniqueira"),
    "sudoeste/octogonal": ra_lookup_loose.get("sudoesteoctogonal", "Sudoeste/ Octogonal"),
    "sol nascente/por do sol": ra_lookup_loose.get("solnascentepordosol", "Sol Nascente/  Pôr do Sol"),
    # RAs criadas depois da base oficial das 33 (Água Quente, lei 7.191/2022): entram apenas como RA declarada.
    "agua quente": "Água Quente",
}

def ra_from_admin(org):
    n = norm(org)
    if not n.startswith("administracao regional"):
        return None
    n = re.sub(r"^administracao regional (de |da |do |das |dos )?", "", n).strip()
    if n in RA_ALIASES:
        return RA_ALIASES[n]
    return ra_lookup.get(n) or ra_lookup_loose.get(loose(n))

def fallback_sede(org, cre=""):
    v = VALIDATED_COORDS.get(loose(org))
    if v:
        return (v.get("sigla") or sigla_de(org)), v["lat"], v["lon"], "validado", (v["end"] or "Coordenada validada (endereço a confirmar)")
    ra = ra_from_admin(org) or ra_lookup.get(norm(cre))
    sigla = f"RA {ra}" if ra else sigla_de(org)
    if ra and ra in ra_centroid:
        lat, lon = ra_centroid[ra]
        return sigla, lat, lon, "aprox", f"Localização aproximada na RA {ra} (validar sede)"
    return sigla, -15.78377, -47.90832, "aprox", "Localização aproximada a validar"

hosp = gpd.read_file("data/raw/shapefiles/Hospitais.shp")

def hospital_sede(unidade):
    u = norm(unidade)
    if not ("hospital regional" in u or re.search(r"\bhr[a-z]*\b", u)):
        return None
    targets = []
    if "gama" in u or "hrg" in u: targets = ["GAMA"]
    elif "planaltina" in u or "hrpl" in u: targets = ["PLANALTINA"]
    elif "ceilandia" in u or "hrc" in u: targets = ["CEILANDIA", "CEILÂNDIA"]
    if not targets:
        return None
    mask = hosp.Hospitais.apply(lambda x: any(t in norm(x).upper() for t in targets))
    if not mask.any():
        return None
    h = hosp[mask].iloc[0]
    sig = "SES-DF · " + ("HRG" if "GAMA" in targets else "HRPL" if "PLANALTINA" in targets else "HRC")
    nome = str(h.Hospitais).title()
    end = f"{str(h.Endereco).title()}, {h.Numero} – {h.RA}"
    return sig, h.geometry.y, h.geometry.x, "shp", end, f"Ouvidoria do {nome}"

df = pd.read_csv(CSV)
df.columns = ["ts", "orgao", "unidade", "cre", "libras", "selo", "itens", "capacitado", "decl"]
df["orgao"] = df.orgao.str.strip()
df["itens_l"] = df.itens.fillna("").apply(lambda s: [i.strip() for i in re.split(r",\s*", s) if i.strip()])

rows = []
for _, r in df.iterrows():
    hs = hospital_sede(r.unidade)
    if hs:
        sigla, lat, lon, fonte, end, nome = hs
    elif r.orgao in SEDES:
        sigla, lat, lon, fonte, end = SEDES[r.orgao]
        v = VALIDATED_COORDS.get(loose(r.orgao)) if (pd.isna(r.unidade) or not str(r.unidade).strip()) else None
        if v:
            lat, lon, fonte = v["lat"], v["lon"], "validado"
            if v["end"]:
                end = v["end"]
        nome = f"Ouvidoria – {sigla}"
    else:
        sigla, lat, lon, fonte, end = fallback_sede(r.orgao, r.cre)
        nome = f"Ouvidoria – {sigla}"
    acess = list(r.itens_l)
    if r.libras == "Sim": acess.append("Atendimento presencial em Libras")
    if r.capacitado == "Sim": acess.append("Equipe capacitada em acessibilidade")
    rows.append(dict(nome=nome, sigla=sigla, orgao=r.orgao, endereco=end, lat=lat, lon=lon, fonte=fonte,
                     libras=r.libras, selo=r.selo, capacitado=r.capacitado, itens=r.itens_l, acess=acess,
                     n_itens=len(r.itens_l), data=str(r.ts).split(" ")[0],
                     ra_declarada=(ra_from_admin(r.orgao) or "")))

g = gpd.GeoDataFrame(rows, geometry=[Point(x["lon"], x["lat"]) for x in rows], crs=4326)
# Spatial join usa a base oficial de RAs (RA.json) para atribuir cada ouvidoria
# à Região Administrativa correta.
g = gpd.sjoin(g, ras, how="left", predicate="within").drop(columns="index_right")
g["RA_derivada"] = g["RA"]
# A ouvidoria de uma Administração Regional pertence à RA do próprio nome, mesmo quando o
# ponto cai em outra RA na base oficial (ex.: RA SIA em trecho limítrofe do Guará).
mask = g["ra_declarada"].fillna("").ne("")
g.loc[mask, "RA"] = g.loc[mask, "ra_declarada"]
ajustadas = g[mask & (g["RA_derivada"].fillna("") != g["RA"])]
if len(ajustadas):
    print("RA ajustada para administração regional:")
    print(ajustadas[["sigla", "RA_derivada", "RA"]].to_string(index=False))
g["RA"] = g.RA.fillna("—")
g = g.drop(columns=["ra_declarada", "RA_derivada"])
g.drop(columns=["lat", "lon"]).to_file("data/processed/ouvidorias.geojson", driver="GeoJSON")
g.drop(columns="geometry").assign(lat=g.geometry.y, lon=g.geometry.x).to_csv("data/processed/ouvidorias_geo.csv", index=False)
print(g[["sigla", "RA", "fonte", "n_itens", "libras"]].to_string())
print("ouvidorias", len(g), "aprox", (g.fonte == "aprox").sum())
