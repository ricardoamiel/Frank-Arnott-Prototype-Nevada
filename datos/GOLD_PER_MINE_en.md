# Gold per mine: where it comes from and how it is split

This document explains the size of the mine circles in the viewer: which figure they show, which source it comes from, how a deposit's gold is split among its mines and how reliable each step is.

## 1. What the circle shows

Each circle is a mine of the project inventory (136 points). Its area is proportional to the contained gold assigned to that mine, in millions of troy ounces (Moz). Contained gold is past production plus reserves and resources at the date of the USGS compilation. It is the standard measure of a deposit's size, not only what was produced.

Hovering over a mine shows:

* the USGS deposit it belongs to and what it includes;
* the contained gold of the whole deposit;
* the share of that mine, in Moz and as a percentage of the deposit, and how many mines share the deposit;
* the past production of the deposit, when USGS reports it.

## 2. Sources

| Source | What it provides | File |
|---|---|---|
| Berger, Mosier, Bliss and Moring (2014). Sediment-hosted gold deposits of the world: database and grade and tonnage models. USGS Open-File Report 2014-1074, appendix 2 | One row per deposit: contained gold (ContainedAuTonne), tonnage and grade, past production (ProductionTonnage, AuPrGrade, ProductionYear), included sub-deposits (Includes) and coordinates | web/fuentes/usgs_ofr2014-1074_sediment_hosted_au.xlsx |
| Project inventory (MINAS_PUNTOS.shp), built from MRDS, the USGS Mineral Resources Data System | Name, status, production years and MRDS size class of each mine (field Tamaño__M: S small, M medium, L large; N, U, Y or empty with no useful class) and the link to its record | datos/MINAS_PUNTOS.shp |

## 3. Where the data are

* Result, one row per mine: web/datos/minas_produccion.csv. The same with geometry: web/datos/minas.geojson.
* Script that builds it: web/preparar_minas.py, run with: python web/preparar_minas.py
* Original USGS table: web/fuentes/usgs_ofr2014-1074_sediment_hosted_au.xlsx

Main columns of minas_produccion.csv (names in Spanish):

| Column | Meaning |
|---|---|
| deposito | Name of the mine in the inventory |
| usgs, usgs_incluye | Assigned USGS deposit and its sub-deposits |
| moz | Contained gold of the whole deposit (Moz) |
| prod_moz, anios_produccion | Past production of the deposit and its years |
| clase_mrds | MRDS size class of the mine (L, M, S or no class) |
| registro_duplicado | True for a second record of the same mine |
| pct_deposito | Share of the deposit assigned to the mine (%) |
| moz_mapa | Gold assigned to the mine (Moz): the size of the circle |
| minas_en_deposito | How many inventory mines share the deposit |
| metodo_reparto | Only mine of the deposit, split by MRDS size (estimate), repeated record, or no USGS figure |
| principal | Mine closest to the USGS coordinate (used for the gold-captured figures) |

## 4. Steps

1. Matching mines to deposits. Each inventory mine was assigned by hand to a USGS deposit, by name, by the Includes field and by distance. The nearest one does not work in the large complexes: Post and Goldstrike are closer to Deep Star than to Betze-Post. Four distant namesakes (14 to 87 km away) were discarded. Result: 103 of the 136 mines have a USGS deposit, in 55 deposits; the other 33 are not in the compilation.
2. Conversion. ContainedAuTonne is in tonnes of gold; it is converted to Moz with 1 t = 32,150.7 troy ounces.
3. Repeated records. Nine mines appear twice in the inventory with the same name within the same deposit (for example Dee Gold Mine and Gold Bar Mine). They count once: the record closest to the USGS coordinate gets the share and the other one stays as a repeated record, drawn as a small dot.
4. Weight of each MRDS class. For each class, the weight is the median contained gold of the deposits that have at least one mine of that class. The weight thus comes from the data themselves and is not set by hand: L = 16.4 Moz, M = 2.6 Moz, S = 0.28 Moz. Mines with no class weigh as small ones.
5. Split. Within each deposit, the share of a mine is its weight divided by the sum of the weights of the deposit's mines, and its gold is that share times the deposit's gold:

   mine gold = deposit gold × mine weight ÷ sum of the deposit's weights

6. Check. The shares of all mines add up to 228.2 Moz, the same as the sum of the 55 deposits. No gold is counted twice.

## 5. Example

Betze-Post holds 39.5 Moz and has six mines in the inventory. Three are large in MRDS (Deep Post, Goldstrike and Post) and three are small or have no class (Screamer, Bazza and Long Lac). The large ones weigh 16.4 each and the others 0.28, so the sum is 50.0. Each large mine gets 16.4 ÷ 50.0 = 32.8% (12.96 Moz) and each small one 0.6% (0.22 Moz). Before, the whole deposit was drawn as a single 39.5 Moz circle at Screamer, the mine closest to the USGS coordinate.

In Getchell and Turquoise Ridge (23.0 Moz), Turquoise Ridge is large and gets 67.9% (15.64 Moz); Getchell Gold Mine, Hansen Creek and Summer Camp are medium and get 10.7% each (2.46 Moz).

## 6. Search for real production per mine

Before using the MRDS classes, the cumulative production of each mine of the large complexes was searched. No cumulative, comparable per-mine figure was found for any of them:

| Complex | What was found | Why it is not enough |
|---|---|---|
| Betze-Post and Goldstrike | Annual production of the Betze-Post pit (642,493 oz in 2015) and of the Meikle and Rodeo underground mines (411,003 oz), and old reserves by orebody (Betze-Post 23.6 Moz and Meikle 6.1 Moz) | No cumulative production of Post, Deep Post, Screamer, Bazza or Long Lac separately |
| Twin Creeks | Combined production of Chimney Creek and Rabbit Creek of about 405,000 oz in one year, shortly before their 1993 merger | It is the sum of both mines, for a single year |
| Chimney Creek (MRDS record) | 300,000 oz in 1987 and 1988, 222,556 oz in 1989 and 220,000 oz in 1990 | It covers only four years of one mine of the complex |
| Getchell and Turquoise Ridge | Annual sales in SEC filings (179,676 oz in 1997 and 175,302 oz in 1998) and 1.25 Moz contained at Turquoise Ridge in a 1995 study | Company figures by year, not cumulative per mine |
| Carlin, Cortez and Gold Quarry | Totals of the Carlin trend (65.6 Moz produced to 2006) and the 10 Moz milestone of Cortez in 2004 | District or company totals, not per mine |

That is why every deposit with several mines uses the MRDS class. If the cumulative production of all mines of a deposit is found later, it goes into the PRODUCCION_MINA dictionary of web/preparar_minas.py, empty today, and that deposit is then split with those figures; the metodo_reparto column will then say split by known production.

Sources consulted:

* Wikipedia, Goldstrike mine: https://en.wikipedia.org/wiki/Goldstrike_mine
* The Northern Miner, Chimney, Rabbit Creek merger seems sure thing: https://northernminer.com/news/chimney-rabbit-creek-merger-seems-sure-thing/1000133073
* MRDS record of Chimney Creek Mine: https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10037801
* MRDS record of Goldstrike Mine: https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10047014
* Getchell Gold Corp, 10-K filings with the SEC, 1996 to 1998: https://www.sec.gov/Archives/edgar/data/0000824590/
* NBMG, annual presentations on Nevada mining: https://data.nbmg.unr.edu/Public/freedownloads/misc/presentations/

## 7. Split of each deposit with several mines

Fifteen deposits have more than one mine in the inventory (54 mines, not counting repeated records). All use the MRDS class:

| USGS deposit | Deposit gold (Moz) | Inventory mine | MRDS class | Share | Mine Moz |
|---|---|---|---|---|---|
| Betze-Post | 39.5 | Deep Post Mine | L | 32.8% | 12.96 |
|  |  | Goldstrike Mine | L | 32.8% | 12.96 |
|  |  | Post Deposit | L | 32.8% | 12.96 |
|  |  | Bazza Deposit | no class | 0.6% | 0.22 |
|  |  | Long Lac Deposit | no class | 0.6% | 0.22 |
|  |  | Screamer Deposit | S | 0.6% | 0.22 |
| Pipeline | 27.0 | Pipeline & South Pipeline Mines | L | 98.3% | 26.55 |
|  |  | Pipeline | no class | 1.7% | 0.46 |
| Getchell/Turquoise Ridge | 23.0 | Turquoise Ridge Mine | L | 67.9% | 15.64 |
|  |  | Getchell Gold Mine | M | 10.7% | 2.46 |
|  |  | Hansen Creek Deposit | M | 10.7% | 2.46 |
|  |  | Summer Camp Deposit | M | 10.7% | 2.46 |
| Gold Quarry | 22.6 | Gold Quarry Mine | L | 33.3% | 7.54 |
|  |  | Gold Quarry Mine Area | L | 33.3% | 7.54 |
|  |  | Chukar Footwall Mine | L | 33.3% | 7.54 |
| Meikle | 16.4 | Greater Goldstrike, North Mines | L | 50.0% | 8.19 |
|  |  | Meikle Mine | L | 50.0% | 8.19 |
| Twin Creeks | 15.6 | Chimney Creek Mine | L | 33.1% | 5.16 |
|  |  | Rabbit Creek Mine | L | 33.1% | 5.16 |
|  |  | Twin Creeks Mine | L | 33.1% | 5.16 |
|  |  | Chimney Creek Deposit | S | 0.6% | 0.09 |
| Bluestar/Genesis | 15.5 | Blue Star Mine | M | 43.0% | 6.65 |
|  |  | Genesis Mine | M | 43.0% | 6.65 |
|  |  | Bobcat Deposit | S | 4.7% | 0.72 |
|  |  | Genesis-Blue Star Mines Area | S | 4.7% | 0.72 |
|  |  | North Star Deposit | S | 4.7% | 0.72 |
| Carlin | 13.7 | Carlin Gold Mine | M | 50.0% | 6.85 |
|  |  | Carlin-Hardie-Pete Mine Area | M | 50.0% | 6.85 |
| Cortez Hills | 9.8 | Cortez Hills Gold Property | no class | 50.0% | 4.90 |
|  |  | Pediment Gold Property | no class | 50.0% | 4.90 |
| Pinson | 3.7 | Cx Deposit | no class | 20.0% | 0.74 |
|  |  | Felix Canyon | S | 20.0% | 0.74 |
|  |  | Mag Deposit | S | 20.0% | 0.74 |
|  |  | Pinson Gold Mine | S | 20.0% | 0.74 |
|  |  | Pinson Mine | S | 20.0% | 0.74 |
| Generator Hill | 2.3 | Generator Hill Deposit | M | 33.3% | 0.75 |
|  |  | North Generator Hill Deposit | M | 33.3% | 0.75 |
|  |  | West Generator Hill Deposit | M | 33.3% | 0.75 |
| SSX/Steer/Saval | 1.8 | Pattani Springs Deposit | S | 20.0% | 0.37 |
|  |  | Saval Canyon Deposit | no class | 20.0% | 0.37 |
|  |  | Saval-Steer Deposit | no class | 20.0% | 0.37 |
|  |  | South Saval Extension (SSX) Mine | no class | 20.0% | 0.37 |
|  |  | Steer Canyon Deposit | no class | 20.0% | 0.37 |
| Gold Pick/Gold Ridge | 1.1 | Gold Pick Deposit | M | 90.2% | 0.97 |
|  |  | Gold Ridge Deposit | S | 9.8% | 0.10 |
| Piñon | 1.0 | South Bullion / Trout Creek Deposit | no class | 16.7% | 0.17 |
|  |  | South Bullion Deposit | no class | 16.7% | 0.17 |
|  |  | Trout Creek Deposit | no class | 16.7% | 0.17 |
|  |  | Dark Star | no class | 16.7% | 0.17 |
|  |  | Dark Star Gold Deposit | no class | 16.7% | 0.17 |
|  |  | Pinon Project | no class | 16.7% | 0.17 |
| Bootstrap/Capstone/Tara | 1.0 | Bootstrap Mine | M | 47.4% | 0.49 |
|  |  | Bootstrap-Capstone-Tara Gold Mine | M | 47.4% | 0.49 |
|  |  | Capstone Deposit | S | 5.2% | 0.05 |

## 8. Limits

* The MRDS class is qualitative: it says whether a mine is large, medium or small, not how much it produced. The split is a reasonable estimate of relative weight, not a measured figure.
* Some inventory records group several mines, for example Gold Quarry Mine Area or Genesis-Blue Star Mines Area. They get their share like any other mine of their class.
* The gold-captured figures of the panel (share of the gold in the marked zone) do not use this split. They still count each whole deposit once, at its main mine, so as not to mix an estimate with the validation metrics.
* The USGS figure is from the date of the compilation (2014). Deposits that kept growing, such as Goldstrike, would hold more contained gold today.
