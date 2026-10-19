"""Arma web/index.html: visor d3 v7 (en inglés) de las ideas 1 y 2 sobre un mapa base mundial.

Los productos están en la malla UTM 11N de 1500 m del cuaderno. Para dibujarlos sobre teselas Web Mercator
(EPSG:3857), cada ráster se reproyecta aquí con vecino más cercano a una malla Mercator de resolución equivalente
(1500 m en el terreno a la latitud del área). Así las celdas caen exactamente en su lugar sobre el mapa base.
Área, trends y minas van en longitud y latitud. Todo se incrusta en plantilla.html: un solo archivo, sin servidor.

Rásteres (uint8, 255 = sin dato):
    pct_<modelo>          percentil de la celda en el mapa final, de 0 a 250
    bloque_<modelo>_<L>   probabilidad calibrada del bloque de lado L celdas, x 500 (0,5 = 250)
    bloquepct_<modelo>_<L> percentil del bloque en el mapa final, de 0 a 250 (para marcar el k % de bloques)
    conmina_<L>           1 si el bloque contiene una mina del inventario (igual para todos los modelos)

La pestaña de comparación lee analisis/ablacion_ideas/web_ablacion.json (ablacion_ideas_v14.py).

Semáforo de accesibilidad y ambiente (datos/03_MapaSemaforo_COLOR.tif, RGBA de 30 m en NAD83 UTM 11N): sus tres
colores se leen como clases (1 verde, 2 amarillo, 3 rojo; 0 sin dato). Para el mapa se reproyecta por moda a una malla
Mercator de unos 300 m en el terreno y se incrusta como PNG de paleta. Para las cifras, cada celda de 1500 m del modelo
toma la clase más frecuente de sus píxeles, y se informa qué parte de cada zona del k % cae en cada clase.

Uso: python web/construir_web.py
     python web/construir_web.py --productos analisis/productos --ablacion analisis/ablacion_ideas --salida index_6capas.html

Por defecto usa la versión con LITO GEOQ v4 como séptima capa (adoptada el 19 de octubre de 2026: mejora el 5 % superior
y deja igual el 10 al 20 %); la versión de 6 capas del 13.º intento sigue disponible con los argumentos de arriba.
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


def leer_semaforo(ruta, paso=5):
    """Clases del semáforo a partir de sus colores, leído cada `paso` píxeles (150 m): verde 1, amarillo 2, rojo 3."""
    import rasterio
    from rasterio.enums import Resampling as Rs
    with rasterio.open(ruta) as s:
        a = s.read(out_shape=(s.count, s.height // paso, s.width // paso), resampling=Rs.nearest)
        tr, crs = s.transform * s.transform.scale(s.width / a.shape[2], s.height / a.shape[1]), s.crs
    r, v, al = a[0].astype(int), a[1].astype(int), a[3] > 0
    cls = np.zeros(r.shape, np.uint8)
    cls[al & (v > 150) & (r < 100)] = 1
    cls[al & (r > 240) & (v > 150)] = 2
    cls[al & (r > 200) & (v < 100)] = 3
    return cls, tr, crs


def b64(arr):
    return base64.b64encode(np.ascontiguousarray(arr, dtype=np.uint8).tobytes()).decode()


def main():
    import argparse
    import sys
    ap = argparse.ArgumentParser()
    ap.add_argument("--productos", default="analisis/productos_lito")
    ap.add_argument("--ablacion", default="analisis/ablacion_lito")
    ap.add_argument("--salida", default="index.html")
    a = ap.parse_args()
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
        f = RAIZ / a.productos / m / "web.json"
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
            pct_b = {(r, c): q for r, c, q in zip(b["r"], b["c"], b["pct"])}
            qb = np.array([pct_b.get(k, np.nan) for k in claves])
            rasters[f"bloquepct_{m}_{lado}"] = a_mercator(raster_celdas(
                np.where(np.isnan(qb), SIN_DATO, np.clip(np.round(qb * 250), 0, 250)).astype(np.uint8)))
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

    semaforo = None
    fs = RAIZ / "datos" / "03_MapaSemaforo_COLOR.tif"
    if fs.exists():
        import io
        from PIL import Image
        cls, tr_s, crs_s = leer_semaforo(fs)
        # celdas del modelo: clase más frecuente de sus píxeles
        celda = np.zeros((h, w), np.uint8)
        reproject(cls, celda, src_transform=tr_s, src_crs=crs_s, dst_transform=tr_utm, dst_crs=crs,
                  resampling=Resampling.mode, src_nodata=0, dst_nodata=0)
        c = celda[g["rows"], g["cols"]]
        reparto = lambda sel: [round(float(np.mean(c[sel] == k)) * 100, 1) for k in (1, 2, 3, 0)]
        for m, wj in modelos.items():
            pct = np.array(json.loads((RAIZ / a.productos / m / "web.json").read_text(encoding="utf8"))["pct_final"])
            wj["semaforo"] = {str(k): reparto(pct > 1 - k / 100) for k in (5, 10, 15, 20)}
        # mapa: malla Mercator de unos 300 m en el terreno, mismas esquinas que la del modelo
        f = 5
        Ws, Hs = W3 * f, H3 * f
        mapa = np.zeros((Hs, Ws), np.uint8)
        reproject(cls, mapa, src_transform=tr_s, src_crs=crs_s, dst_transform=from_origin(izq, arriba, res / f, res / f),
                  dst_crs="EPSG:3857", resampling=Resampling.mode, src_nodata=0, dst_nodata=0)
        im = Image.fromarray(mapa, "P")
        im.putpalette([0, 0, 0, 65, 171, 93, 255, 200, 0, 215, 48, 39] + [0] * 756)
        buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
        semaforo = dict(png=base64.b64encode(buf.getvalue()).decode(), w=Ws, h=Hs, area=reparto(slice(None)),
                        minas=[int(np.sum(c[g["y"] == 1] == k)) for k in (1, 2, 3, 0)])
        print(f"semáforo: {Ws} x {Hs} px, PNG {len(buf.getvalue()) / 1e3:.0f} kB | área verde/amarillo/rojo/sin dato % {semaforo['area']}")

    fa = RAIZ / a.ablacion / "web_ablacion.json"
    ablacion = json.loads(fa.read_text(encoding="utf8")) if fa.exists() else {}
    datos = dict(
        raster=dict(w=W3, h=H3, x0=izq, y0=arriba, res=res),
        capas={k: b64(v) for k, v in rasters.items()},
        area=simpl(area[["geometry"]]), trends=simpl(trends[["Name", "geometry"]]),
        minas=json.loads(minas.drop(columns=["x", "y"], errors="ignore").to_json(orient="records")),
        modelos=modelos, ablacion={k: v for k, v in ablacion.items() if k in modelos}, semaforo=semaforo,
    )
    html = (AQUI / "plantilla.html").read_text(encoding="utf8")
    html = html.replace("/*__DATA__*/null", json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
    (AQUI / a.salida).write_text(html, encoding="utf8")
    print(f"{a.salida}: {len(html) / 1e6:.2f} MB | Mercator {W3} x {H3} px de {res:.0f} m | modelos: {', '.join(modelos)}")


if __name__ == "__main__":
    main()
