# Oro de las minas: de dónde sale y cómo se reparte

Este documento explica el tamaño de los círculos de las minas en el visor: qué cifra muestran, de qué fuente sale, cómo se reparte el oro de un depósito entre sus minas y qué tan confiable es cada paso.

## 1. Qué muestra el círculo

Cada círculo es una mina del inventario del proyecto (136 puntos). Su área es proporcional al oro contenido que le toca a esa mina, en millones de onzas troy (Moz). El oro contenido es la producción histórica más las reservas y los recursos, a la fecha de la compilación de USGS. Es la medida estándar del tamaño de un depósito; no es solo lo que se produjo.

Al pasar el cursor sobre una mina se ve:

* el depósito de USGS al que pertenece y lo que incluye;
* el oro contenido de todo el depósito;
* la parte de esa mina, en Moz y en porcentaje del depósito, y cuántas minas comparten el depósito;
* la producción histórica del depósito, cuando USGS la informa.

## 2. Fuentes

| Fuente | Qué aporta | Archivo |
|---|---|---|
| Berger, Mosier, Bliss y Moring (2014). Sediment-hosted gold deposits of the world: database and grade and tonnage models. USGS Open-File Report 2014-1074, apéndice 2 | Una fila por depósito: oro contenido (ContainedAuTonne), tonelaje y ley, producción histórica (ProductionTonnage, AuPrGrade, ProductionYear), sub depósitos incluidos (Includes) y coordenadas | web/fuentes/usgs_ofr2014-1074_sediment_hosted_au.xlsx |
| Inventario del proyecto (MINAS_PUNTOS.shp), que toma sus datos de MRDS, la base de recursos minerales de USGS | Nombre, estado, años de producción y clase de tamaño de MRDS de cada mina (campo Tamaño__M: S pequeña, M mediana, L grande; N, U, Y o vacío sin clase útil) y el enlace a su ficha | datos/MINAS_PUNTOS.shp |

## 3. Dónde está la data

* Resultado, una fila por mina: web/datos/minas_produccion.csv. Lo mismo con geometría: web/datos/minas.geojson.
* Script que lo genera: web/preparar_minas.py. Se corre con: python web/preparar_minas.py
* Tabla original de USGS: web/fuentes/usgs_ofr2014-1074_sediment_hosted_au.xlsx

Columnas principales de minas_produccion.csv:

| Columna | Significado |
|---|---|
| deposito | Nombre de la mina en el inventario |
| usgs, usgs_incluye | Depósito de USGS asignado y sus sub depósitos |
| moz | Oro contenido de todo el depósito (Moz) |
| prod_moz, anios_produccion | Producción histórica del depósito y sus años |
| clase_mrds | Clase de tamaño de MRDS de la mina (L, M, S o sin clase) |
| registro_duplicado | Verdadero si es un segundo registro de la misma mina |
| pct_deposito | Parte del depósito que se asigna a la mina (%) |
| moz_mapa | Oro asignado a la mina (Moz): es el tamaño del círculo |
| minas_en_deposito | Cuántas minas del inventario comparten el depósito |
| metodo_reparto | Única mina del depósito, reparto por tamaño MRDS (estimado), registro duplicado o sin dato de USGS |
| principal | Mina más cercana a la coordenada de USGS (se usa para las cifras de oro capturado) |

## 4. Proceso

1. Correspondencia mina y depósito. Cada mina del inventario se asignó a mano a un depósito de USGS, por nombre, por el campo Includes y por distancia. La más cercana no sirve en los complejos grandes: Post y Goldstrike quedan más cerca de Deep Star que de Betze-Post. Se descartaron cuatro homónimos lejanos (de 14 a 87 km). Resultado: 103 de las 136 minas tienen depósito de USGS, en 55 depósitos; las otras 33 no aparecen en la compilación.
2. Conversión. ContainedAuTonne está en toneladas de oro; se pasa a Moz con 1 t = 32.150,7 onzas troy.
3. Registros repetidos. Nueve minas aparecen dos veces en el inventario con el mismo nombre dentro del mismo depósito (por ejemplo, Dee Gold Mine y Gold Bar Mine). Se cuentan una sola vez: el registro más cercano a la coordenada de USGS recibe la parte y el otro queda como registro duplicado, con un punto chico.
4. Peso de cada clase de MRDS. Para cada clase se toma la mediana del oro contenido de los depósitos que tienen al menos una mina de esa clase. Así el peso sale de los mismos datos y no se fija a mano: L = 16,4 Moz, M = 2,6 Moz, S = 0,28 Moz. Las minas sin clase pesan como las pequeñas.
5. Reparto. Dentro de cada depósito, la parte de una mina es su peso dividido por la suma de los pesos de las minas del depósito, y su oro es esa parte por el oro del depósito:

   oro de la mina = oro del depósito × peso de la mina ÷ suma de los pesos del depósito

6. Verificación. La suma de las partes de todas las minas da 228,2 Moz, igual que la suma de los 55 depósitos. Ningún oro se cuenta dos veces.

## 5. Ejemplo

Betze-Post tiene 39,5 Moz contenidos y seis minas en el inventario. Tres son grandes en MRDS (Deep Post, Goldstrike y Post) y tres son pequeñas o sin clase (Screamer, Bazza y Long Lac). Las grandes pesan 16,4 cada una y las otras 0,28, así que la suma es 50,0. Cada grande recibe 16,4 ÷ 50,0 = 32,8 % (12,96 Moz) y cada chica 0,6 % (0,22 Moz). Antes, todo el depósito se dibujaba como un solo círculo de 39,5 Moz en Screamer, que era la mina más cercana a la coordenada de USGS.

En Getchell y Turquoise Ridge (23,0 Moz), Turquoise Ridge es grande y recibe el 67,9 % (15,64 Moz); Getchell Gold Mine, Hansen Creek y Summer Camp son medianas y reciben 10,7 % cada una (2,46 Moz).

## 6. Búsqueda de producción real por mina

Antes de usar las clases de MRDS se buscó la producción acumulada de cada mina en los complejos grandes. No se encontró una cifra acumulada y comparable por mina en ninguno de ellos:

| Complejo | Qué se encontró | Por qué no alcanza |
|---|---|---|
| Betze-Post y Goldstrike | Producción anual del tajo Betze-Post (642.493 oz en 2015) y de las minas subterráneas Meikle y Rodeo (411.003 oz), y reservas antiguas por cuerpo (Betze-Post 23,6 Moz y Meikle 6,1 Moz) | No hay producción acumulada de Post, Deep Post, Screamer, Bazza ni Long Lac por separado |
| Twin Creeks | Producción conjunta de Chimney Creek y Rabbit Creek de unas 405.000 oz en un año, poco antes de su fusión en 1993 | Es la suma de las dos minas y de un solo año |
| Chimney Creek (ficha MRDS) | 300.000 oz en 1987 y 1988, 222.556 oz en 1989 y 220.000 oz en 1990 | Solo cubre cuatro años de una de las minas del complejo |
| Getchell y Turquoise Ridge | Ventas anuales en los informes a la SEC (179.676 oz en 1997 y 175.302 oz en 1998) y 1,25 Moz contenidas en Turquoise Ridge según un estudio de 1995 | Cifras de la empresa por año, no acumuladas por mina |
| Carlin, Cortez y Gold Quarry | Totales de la franja de Carlin (65,6 Moz producidas hasta 2006) y el hito de 10 Moz de Cortez en 2004 | Totales de distrito o de empresa, no de cada mina |

Por eso todos los depósitos con varias minas usan la clase de MRDS. Si más adelante se consigue la producción acumulada de todas las minas de un depósito, se carga en el diccionario PRODUCCION_MINA de web/preparar_minas.py, que hoy está vacío, y ese depósito pasa a repartirse con esas cifras; la columna metodo_reparto dirá entonces reparto por producción conocida.

Fuentes consultadas en la búsqueda:

* Wikipedia, Goldstrike mine: https://en.wikipedia.org/wiki/Goldstrike_mine
* The Northern Miner, Chimney, Rabbit Creek merger seems sure thing: https://northernminer.com/news/chimney-rabbit-creek-merger-seems-sure-thing/1000133073
* Ficha MRDS de Chimney Creek Mine: https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10037801
* Ficha MRDS de Goldstrike Mine: https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10047014
* Getchell Gold Corp, informes 10-K a la SEC de 1996 a 1998: https://www.sec.gov/Archives/edgar/data/0000824590/
* NBMG, presentaciones anuales de la minería de Nevada: https://data.nbmg.unr.edu/Public/freedownloads/misc/presentations/

## 7. Reparto de cada depósito con varias minas

Quince depósitos tienen más de una mina en el inventario (54 minas, sin contar los registros repetidos). Todos usan la clase de MRDS:

| Depósito USGS | Oro del depósito (Moz) | Mina del inventario | Clase MRDS | Parte | Moz de la mina |
|---|---|---|---|---|---|
| Betze-Post | 39,5 | Deep Post Mine | L | 32,8 % | 12,96 |
|  |  | Goldstrike Mine | L | 32,8 % | 12,96 |
|  |  | Post Deposit | L | 32,8 % | 12,96 |
|  |  | Bazza Deposit | sin clase | 0,6 % | 0,22 |
|  |  | Long Lac Deposit | sin clase | 0,6 % | 0,22 |
|  |  | Screamer Deposit | S | 0,6 % | 0,22 |
| Pipeline | 27,0 | Pipeline & South Pipeline Mines | L | 98,3 % | 26,55 |
|  |  | Pipeline | sin clase | 1,7 % | 0,46 |
| Getchell/Turquoise Ridge | 23,0 | Turquoise Ridge Mine | L | 67,9 % | 15,64 |
|  |  | Getchell Gold Mine | M | 10,7 % | 2,46 |
|  |  | Hansen Creek Deposit | M | 10,7 % | 2,46 |
|  |  | Summer Camp Deposit | M | 10,7 % | 2,46 |
| Gold Quarry | 22,6 | Gold Quarry Mine | L | 33,3 % | 7,54 |
|  |  | Gold Quarry Mine Area | L | 33,3 % | 7,54 |
|  |  | Chukar Footwall Mine | L | 33,3 % | 7,54 |
| Meikle | 16,4 | Greater Goldstrike, North Mines | L | 50,0 % | 8,19 |
|  |  | Meikle Mine | L | 50,0 % | 8,19 |
| Twin Creeks | 15,6 | Chimney Creek Mine | L | 33,1 % | 5,16 |
|  |  | Rabbit Creek Mine | L | 33,1 % | 5,16 |
|  |  | Twin Creeks Mine | L | 33,1 % | 5,16 |
|  |  | Chimney Creek Deposit | S | 0,6 % | 0,09 |
| Bluestar/Genesis | 15,5 | Blue Star Mine | M | 43,0 % | 6,65 |
|  |  | Genesis Mine | M | 43,0 % | 6,65 |
|  |  | Bobcat Deposit | S | 4,7 % | 0,72 |
|  |  | Genesis-Blue Star Mines Area | S | 4,7 % | 0,72 |
|  |  | North Star Deposit | S | 4,7 % | 0,72 |
| Carlin | 13,7 | Carlin Gold Mine | M | 50,0 % | 6,85 |
|  |  | Carlin-Hardie-Pete Mine Area | M | 50,0 % | 6,85 |
| Cortez Hills | 9,8 | Cortez Hills Gold Property | sin clase | 50,0 % | 4,90 |
|  |  | Pediment Gold Property | sin clase | 50,0 % | 4,90 |
| Pinson | 3,7 | Cx Deposit | sin clase | 20,0 % | 0,74 |
|  |  | Felix Canyon | S | 20,0 % | 0,74 |
|  |  | Mag Deposit | S | 20,0 % | 0,74 |
|  |  | Pinson Gold Mine | S | 20,0 % | 0,74 |
|  |  | Pinson Mine | S | 20,0 % | 0,74 |
| Generator Hill | 2,3 | Generator Hill Deposit | M | 33,3 % | 0,75 |
|  |  | North Generator Hill Deposit | M | 33,3 % | 0,75 |
|  |  | West Generator Hill Deposit | M | 33,3 % | 0,75 |
| SSX/Steer/Saval | 1,8 | Pattani Springs Deposit | S | 20,0 % | 0,37 |
|  |  | Saval Canyon Deposit | sin clase | 20,0 % | 0,37 |
|  |  | Saval-Steer Deposit | sin clase | 20,0 % | 0,37 |
|  |  | South Saval Extension (SSX) Mine | sin clase | 20,0 % | 0,37 |
|  |  | Steer Canyon Deposit | sin clase | 20,0 % | 0,37 |
| Gold Pick/Gold Ridge | 1,1 | Gold Pick Deposit | M | 90,2 % | 0,97 |
|  |  | Gold Ridge Deposit | S | 9,8 % | 0,10 |
| Piñon | 1,0 | South Bullion / Trout Creek Deposit | sin clase | 16,7 % | 0,17 |
|  |  | South Bullion Deposit | sin clase | 16,7 % | 0,17 |
|  |  | Trout Creek Deposit | sin clase | 16,7 % | 0,17 |
|  |  | Dark Star | sin clase | 16,7 % | 0,17 |
|  |  | Dark Star Gold Deposit | sin clase | 16,7 % | 0,17 |
|  |  | Pinon Project | sin clase | 16,7 % | 0,17 |
| Bootstrap/Capstone/Tara | 1,0 | Bootstrap Mine | M | 47,4 % | 0,49 |
|  |  | Bootstrap-Capstone-Tara Gold Mine | M | 47,4 % | 0,49 |
|  |  | Capstone Deposit | S | 5,2 % | 0,05 |

## 8. Límites

* La clase de MRDS es cualitativa: dice si una mina es grande, mediana o pequeña, pero no cuánto produjo. El reparto es una estimación razonable del peso relativo, no una cifra medida.
* Algunos registros del inventario agrupan varias minas, por ejemplo Gold Quarry Mine Area o Genesis-Blue Star Mines Area. Reciben su parte como cualquier otra mina de su clase.
* Las cifras de oro capturado del panel (porcentaje del oro en la zona marcada) no usan este reparto. Siguen contando cada depósito completo una vez, en su mina principal, para no mezclar una estimación con las métricas de validación.
* La cifra de USGS es de la fecha de la compilación (2014). Los depósitos que siguieron creciendo, como Goldstrike, hoy tendrían más oro contenido.
