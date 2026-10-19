"""Une las 136 minas de MINAS_PUNTOS.shp con el oro contenido de cada depósito según USGS (OFR 2014-1074).

Fuente: Berger, Mosier, Bliss y Moring (2014), Sediment-hosted gold deposits of the world: database and grade and
tonnage models, USGS Open-File Report 2014-1074, apéndice 2. El campo ContainedAuTonne es el oro contenido del
depósito (producción histórica + reservas + recursos, a la fecha de la compilación): se convierte a millones de onzas
troy (1 t = 32.150,7 oz). No es solo la producción; es la medida estándar del tamaño de un depósito.

La correspondencia se hizo a mano (nombre, campo Includes y distancia), porque la más cercana falla en los complejos
grandes: Post y Goldstrike quedan más cerca de Deep Star que de Betze Post. USGS da una sola cifra por depósito, y un
depósito puede agrupar varias minas del inventario (Betze-Post incluye Screamer, Bazza, Deep Post, Long Lac y el tajo
Goldstrike).

Reparto entre las minas de un depósito (moz_mapa, el tamaño del círculo): no hay cifra pública de producción
acumulada por mina (ver datos/ORO_MINAS.md), así que el oro del depósito se reparte según la clase de tamaño de MRDS de
cada mina. El peso de cada clase es la mediana del oro contenido de los depósitos que tienen al menos una mina de esa
clase, de modo que sale de los mismos datos y no se fija a mano; las minas sin clase (N, U, Y o vacío) pesan como las
pequeñas. Los registros repetidos (mismo nombre dentro del depósito) se cuentan una vez: el más cercano a la
coordenada de USGS recibe la parte y el otro queda como registro duplicado. La suma de las partes es el oro del
depósito. Las cifras de los productos (oro capturado) siguen contando cada depósito una vez, en su mina principal
(la más cercana a la coordenada de USGS). Se agrega la producción histórica (ProductionTonnage por AuPrGrade, años en ProductionYear),
que es menor que el oro contenido: Betze-Post tiene 39,5 Moz contenidos y 30,0 Moz producidos entre 1974 y 2011.

Uso: python preparar_minas.py   (escribe datos/minas_produccion.csv y datos/minas.geojson)
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
OZ_POR_T = 32150.7466

# índice de la mina en MINAS_PUNTOS.shp -> NameDeposit de USGS (None = sin dato en la compilación)
# Se descartaron por homónimos lejanos (14 a 87 km): Pan Mine, Gold Canyon, West Pequip y Mac Ridge. Se
# mantienen Afgan (5,9 km) y Dark Star y Pinon Project, que USGS incluye en el proyecto Piñon (13,5 km).
USGS = {
    0: "Alligator Ridge", 1: None, 2: "Casino", 3: None, 4: None, 5: "Easy Junior", 6: "Galaxy", 7: "Golden Butte",
    8: "Green Springs", 9: "Green Springs", 10: "Griffon", 11: None, 12: "Illipah", 13: None, 14: None, 15: None,
    16: "Winrock", 17: "Yankee", 18: "Gold Quarry", 19: "Gold Quarry", 20: "Gold Pick/Gold Ridge", 21: "Goldstone",
    22: None, 23: "Tusc", 24: "Chert Cliff", 25: "Cortez", 26: "Cortez Hills", 27: None, 28: None, 29: "Gold Acres",
    30: "Gold Acres", 31: "Horse Canyon", 32: "Horse Canyon", 33: None, 34: "Cortez Hills", 35: "Pipeline",
    36: "Pipeline", 37: None, 38: None, 39: None, 40: "Archimedes", 41: None, 42: "Twin Creeks", 43: "Twin Creeks",
    44: "Twin Creeks", 45: "Pinson", 46: "Pinson", 47: "Getchell/Turquoise Ridge", 48: "Getchell/Turquoise Ridge",
    49: None, 50: "Pinson", 51: "Pinson", 52: "Pinson", 53: "Preble", 54: "Preble", 55: "Twin Creeks", 56: None,
    57: "Getchell/Turquoise Ridge", 58: "Getchell/Turquoise Ridge", 59: "Twin Creeks", 60: "Afgan", 61: "Gold Bar",
    62: "Gold Bar", 63: None, 64: "Gold Pick/Gold Ridge", 65: None, 66: "Burns Basin",
    67: "California Mountain", 68: None, 69: None, 70: None, 71: None, 72: "Generator Hill ", 73: None, 74: "Smith",
    75: "Long Canyon", 76: "Marlboro Canyon", 77: None, 78: "Mill Creek", 79: "Murray", 80: None,
    81: "Generator Hill ", 82: None, 83: "SSX/Steer/Saval", 84: "SSX/Steer/Saval", 85: "SSX/Steer/Saval",
    86: "SSX/Steer/Saval", 87: None, 88: "Piñon", 89: "Piñon", 90: None, 91: "SSX/Steer/Saval",
    92: "Starvation Canyon", 93: "SSX/Steer/Saval", 94: "Piñon", 95: "Generator Hill ", 96: None,
    97: "Winters Creek", 98: None, 99: "Betze-Post", 100: "Bluestar/Genesis", 101: "Bluestar/Genesis",
    102: "Bootstrap/Capstone/Tara", 103: "Bootstrap/Capstone/Tara", 104: "Bootstrap/Capstone/Tara", 105: "Carlin",
    106: "Carlin", 107: "Gold Quarry", 108: "Piñon", 109: "Piñon", 110: "Dee", 111: "Dee", 112: "Betze-Post",
    113: "Deep Star", 114: "Bluestar/Genesis", 115: "Bluestar/Genesis", 116: "Bluestar/Genesis", 117: "Gnom",
    118: "Betze-Post", 119: "Meikle", 120: "North Lantern", 121: "Leeville", 122: "Betze-Post", 123: None,
    124: "Meikle", 125: "Bluestar/Genesis", 126: None, 127: "Pete", 128: "Piñon", 129: "Betze-Post", 130: "REN",
    131: "Storm", 132: "Betze-Post", 133: "Wright Window", 134: "Emigrant Springs", 135: "Rain",
}
# producción conocida por mina (índice de la mina -> Moz). Si todas las minas de un depósito tienen cifra, el reparto usa
# estas cifras en lugar de la clase de MRDS. Hoy está vacío: no se encontró una fuente pública con la producción
# acumulada de cada mina de un mismo depósito (ver datos/ORO_MINAS.md).
PRODUCCION_MINA = {}
# clases de tamaño (Moz) para color y leyenda
CLASES = [(0, 0.1, "menos de 0,1 Moz"), (0.1, 1, "0,1 a 1 Moz"), (1, 5, "1 a 5 Moz"), (5, 15, "5 a 15 Moz"),
          (15, 1e9, "más de 15 Moz")]


def main():
    m = gpd.read_file(AQUI.parent / "datos" / "MINAS_PUNTOS.shp")
    u = pd.read_excel(AQUI / "fuentes" / "usgs_ofr2014-1074_sediment_hosted_au.xlsx")
    u = u[u.StateProvince.astype(str).str.contains("Nevada")].set_index("NameDeposit")
    ug = gpd.GeoDataFrame(u, geometry=gpd.points_from_xy(u.LongitudeDecimal, u.LatitudeDecimal), crs=4326)
    ug = ug.to_crs(m.crs)

    filas = []
    for i, r in m.iterrows():
        nombre = USGS[i]
        f = dict(id=i, deposito=r["Depósito"], trend=r["Trend___Di"], estado=r["Estado_de_"],
                 tamano_mrds=r["Tamaño__M"], lon=round(r["Longitud"], 5), lat=round(r["Latitud"], 5),
                 usgs=nombre, usgs_incluye=None, moz=np.nan, toneladas_mt=np.nan, ley_g_t=np.nan,
                 prod_moz=np.nan, anios_produccion=None, km_a_usgs=np.nan)
        if nombre:
            d = u.loc[nombre]
            f.update(moz=round(d.ContainedAuTonne * OZ_POR_T / 1e6, 3), toneladas_mt=d.TotalTonnage,
                     ley_g_t=d.AuToGrade, anios_produccion=d.ProductionYear,
                     prod_moz=round(d.ProductionTonnage * d.AuPrGrade * OZ_POR_T / 1e6, 3),
                     usgs_incluye=d.Includes if isinstance(d.Includes, str) else None,
                     km_a_usgs=round(r.geometry.distance(ug.loc[nombre].geometry) / 1000, 2))
        filas.append(f)
    t = pd.DataFrame(filas)
    # la mina más cercana a la coordenada de USGS representa al complejo; las demás son "parte de"
    t["principal"] = False
    for nombre, g in t[t.usgs.notna()].groupby("usgs"):
        t.loc[g.km_a_usgs.idxmin(), "principal"] = True
    princ = t[t.principal].set_index("usgs").deposito
    t["mina_principal"] = t.usgs.map(princ).where(t.usgs.notna() & ~t.principal)
    # registros repetidos dentro de un depósito: cuenta el más cercano a USGS
    t["registro_duplicado"] = False
    clave = t.deposito.str.lower().str.strip()
    for _, g in t[t.usgs.notna()].groupby([t.usgs, clave]):
        if len(g) > 1:
            t.loc[g.index.drop(g.km_a_usgs.idxmin()), "registro_duplicado"] = True
    # peso por clase de tamaño de MRDS: mediana del oro contenido de los depósitos que tienen al menos una mina de esa
    # clase (cada depósito cuenta una vez por clase)
    t["clase_mrds"] = t.tamano_mrds.where(t.tamano_mrds.isin(["L", "M", "S"]), "sin clase")
    vivos = t[t.usgs.notna() & ~t.registro_duplicado]
    n_por_dep = vivos.groupby("usgs").size()
    por_clase = vivos.drop_duplicates(["usgs", "clase_mrds"]).groupby("clase_mrds").moz
    pesos = por_clase.median().to_dict()
    pesos["sin clase"] = pesos["S"]
    assert pesos["L"] > pesos["M"] > pesos["S"], pesos
    print("Pesos por clase MRDS (mediana de Moz de los depósitos con una mina de la clase):",
          {k: round(v, 3) for k, v in pesos.items()}, "| depósitos:", por_clase.size().to_dict())
    t["peso_mrds"] = t.clase_mrds.map(pesos).where(t.usgs.notna() & ~t.registro_duplicado, 0.0)
    t["produccion_conocida"] = t.id.map(PRODUCCION_MINA)
    t["reparto_con_produccion"] = False
    for _, g in t[t.usgs.notna() & ~t.registro_duplicado].groupby("usgs"):
        if len(g) > 1 and g.produccion_conocida.notna().all():
            t.loc[g.index, "peso_mrds"] = g.produccion_conocida
            t.loc[g.index, "reparto_con_produccion"] = True
    suma = t.groupby("usgs").peso_mrds.transform("sum")
    t["pct_deposito"] = (100 * t.peso_mrds / suma).round(1).where(t.usgs.notna())
    t["moz_mapa"] = (t.moz * t.peso_mrds / suma).round(3).where(t.usgs.notna() & ~t.registro_duplicado)
    t["minas_en_deposito"] = t.usgs.map(n_por_dep)
    t["metodo_reparto"] = np.select(
        [t.usgs.isna(), t.registro_duplicado, t.minas_en_deposito == 1, t.reparto_con_produccion],
        ["sin dato de USGS", "registro duplicado", "única mina del depósito", "reparto por producción conocida"],
        "reparto por tamaño MRDS (estimado)")
    t["clase_moz"] = None
    for lo, hi, et in CLASES:
        t.loc[(t.moz_mapa >= lo) & (t.moz_mapa < hi), "clase_moz"] = et
    t["clase_moz"] = t.clase_moz.fillna("sin dato")
    t["productor"] = t.estado.isin(["Producer", "Past Producer"])
    lejos = t[t.km_a_usgs > 5]
    if len(lejos):
        print("Aviso, correspondencias por nombre a más de 5 km:")
        print(lejos[["deposito", "usgs", "km_a_usgs"]].to_string(index=False))

    (AQUI / "datos").mkdir(exist_ok=True)
    t.to_csv(AQUI / "datos" / "minas_produccion.csv", index=False)
    gpd.GeoDataFrame(t, geometry=gpd.points_from_xy(t.lon, t.lat), crs=4326).to_file(
        AQUI / "datos" / "minas.geojson", driver="GeoJSON")
    print(f"{t.usgs.notna().sum()} de {len(t)} minas con dato de USGS; {t[t.principal].moz.sum():.1f} Moz en "
          f"{t.principal.sum()} depósitos; suma de las partes {t.moz_mapa.sum():.1f} Moz")
    print(t.clase_moz.value_counts().to_string())


if __name__ == "__main__":
    main()
