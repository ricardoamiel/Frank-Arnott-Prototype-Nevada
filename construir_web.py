"""Arma web/index.html: visor d3 v7 (en inglés) de las ideas 1 y 2 sobre un mapa base mundial.

Los productos están en la malla UTM 11N de 1500 m del cuaderno. Para dibujarlos sobre teselas Web Mercator
(EPSG:3857), cada ráster se reproyecta aquí con vecino más cercano a una malla Mercator de resolución equivalente
(1500 m en el terreno a la latitud del área). Así las celdas caen exactamente en su lugar sobre el mapa base.
Área, trends y minas van en longitud y latitud. Todo se incrusta en plantilla.html: un solo archivo, sin servidor.

Rásteres (uint8, 255 = sin dato):
    pct_<modelo>          percentil de la celda en el mapa final, de 0 a 250
    bloque_<modelo>_<L>   probabilidad calibrada del bloque de lado L celdas, x 500 (0,5 = 250)
    conmina_<L>           1 si el bloque contiene una mina del inventario (igual para todos los modelos)

Uso: python web/construir_web.py
"""
import base64
import json
import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject, transform_bounds

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
ORDEN_MODELOS = ["LogReg", "GAT", "GAT_bag"]
SIN_DATO = 255


def b64(arr):
    return base64.b64encode(np.ascontiguousarray(arr, dtype=np.uint8).tobytes()).decode()


def main():
    import sys
    sys.path.insert(0, str(RAIZ))
    import optimizar_v13 as o
    g = o.cargar("cpu")
    h, w, tr_utm, crs = g["h"], g["w"], g["transform_g"], g["crs"]

    # malla Mercator: límites del área reproyectados y píxel equivalente a 1500 m en el centro del área
    izq, abajo, der, arriba = transform_bounds(crs, "EPSG:3857", tr_utm.c, tr_utm.f + h * tr_utm.e,
                                               tr_utm.c + w * tr_utm.a, tr_utm.f)
    lat_c = math.degrees(math.atan(math.sinh(((abajo + arriba) / 2) / 6378137)))
    res = 1500 / math.cos(math.radians(lat_c))
    W3, H3 = int(math.ceil((der - izq) / res)), int(math.ceil((arriba - abajo) / res))
    tr_3857 = from_origin(izq, arriba, res, res)

    def a_mercator(utm):
        dst = np.full((H3, W3), SIN_DATO, np.uint8)
        reproject(utm, dst, src_transform=tr_utm, src_crs=crs, dst_transform=tr_3857, dst_crs="EPSG:3857",
                  resampling=Resampling.nearest, src_nodata=SIN_DATO, dst_nodata=SIN_DATO)
        return dst

    def raster_celdas(valores):
        r = np.full((h, w), SIN_DATO, np.uint8)
        r[g["rows"], g["cols"]] = valores
        return r

    rasters, modelos = {}, {}
    minas = pd.read_csv(AQUI / "datos" / "minas_produccion.csv")
    for m in ORDEN_MODELOS:
        f = RAIZ / "analisis" / "productos" / m / "web.json"
        if not f.exists():
            continue
        wj = json.loads(f.read_text(encoding="utf8"))
        pct = np.array(wj.pop("pct_final"))
        rasters[f"pct_{m}"] = a_mercator(raster_celdas(np.clip(np.round(pct * 250), 0, 250).astype(np.uint8)))
        celda = np.array(wj.pop("celda_mina"))
        minas[f"pct_{m}"] = np.where(celda >= 0, np.round(pct[np.clip(celda, 0, None)] * 100, 2), np.nan)
        for lado, b in wj.pop("bloques").items():
            L = int(lado)
            prob = {(r, c): p for r, c, p in zip(b["r"], b["c"], b["prob"])}
            con = {(r, c): k for r, c, k in zip(b["r"], b["c"], b["con_mina"])}
            claves = list(zip(g["rows"] // L, g["cols"] // L))
            pb = np.array([prob.get(k, np.nan) for k in claves])
            vals = np.where(np.isnan(pb), SIN_DATO, np.clip(np.round(pb * 500), 0, 250)).astype(np.uint8)
            rasters[f"bloque_{m}_{lado}"] = a_mercator(raster_celdas(vals))
            if f"conmina_{lado}" not in rasters:
                rasters[f"conmina_{lado}"] = a_mercator(raster_celdas(
                    np.array([con.get(k, 0) for k in claves], np.uint8)))
        modelos[m] = wj
    if not modelos:
        raise SystemExit("No hay productos: corre antes productos_v14.py")

    area = gpd.read_file(RAIZ / "datos" / "AREA.shp").to_crs(4326)
    trends = gpd.read_file(RAIZ / "datos" / "TRENDS.shp").to_crs(4326)
    trends["Name"] = trends.Name.replace({"Gretchell Trend": "Getchell Trend"})   # errata en el shapefile
    simpl = lambda gdf: json.loads(gdf.assign(geometry=gdf.geometry.force_2d().simplify(0.004)).to_json())

    datos = dict(
        raster=dict(w=W3, h=H3, x0=izq, y0=arriba, res=res),
        capas={k: b64(v) for k, v in rasters.items()},
        area=simpl(area[["geometry"]]), trends=simpl(trends[["Name", "geometry"]]),
        minas=json.loads(minas.drop(columns=["x", "y"], errors="ignore").to_json(orient="records")),
        modelos=modelos,
    )
    html = (AQUI / "plantilla.html").read_text(encoding="utf8")
    html = html.replace("/*__DATA__*/null", json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
    (AQUI / "index.html").write_text(html, encoding="utf8")
    print(f"index.html: {len(html) / 1e6:.2f} MB | Mercator {W3} x {H3} px de {res:.0f} m | modelos: {', '.join(modelos)}")


if __name__ == "__main__":
    main()
