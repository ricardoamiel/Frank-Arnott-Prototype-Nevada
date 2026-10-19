# Carlin Gold Prospectivity, Nevada

Interactive viewer for a graph neural network prospectivity model of Carlin-type gold in northern Nevada.

**Live page:** https://ricardoamiel.github.io/Frank-Arnott-Prototype-Nevada/

The page is a single self-contained file (`index.html`): maps, model outputs, mines and charts are embedded, so it
works offline and needs no server. Basemap tiles come from Esri.

## What the page shows

The same model ranking is read in two ways:

| View | Question it answers | What the numbers mean |
|---|---|---|
| **Favorable zone** | Where should we look first? | The top k % of 1.5 km cells by model score (k = 5, 10, 15 or 20 %). Reported as the share of known mines and of contained gold that falls inside, and the lift over random. Relative figures: no claim about the chance of a discovery in a given cell. |
| **Block probability** | What is the chance that a block holds a mine? | Cells are grouped into blocks of 4.5, 10.5 or 15 km, and the block score is turned into a probability with isotonic regression. Absolute and checkable: among the blocks marked, the share that really holds a mine (hit rate) should match the mean calibrated probability. |

Two tabs:

- **Explore**: one map, one model, one level, with the success-rate curve (zone view) or the reliability chart
  (block view), and a comparison table of the three models.
- **Compare levels**: two synchronized maps side by side at two different levels (for example 5 % and 20 %). Panning
  or zooming one moves the other, and a ghost cursor marks the same point on the twin map. Below the maps and on the
  right, the ablation between the two levels: what the extra area buys in mines, gold, lift, km² per mine, hit rate
  and calibrated probability.

Models: **GAT** (graph attention network, configuration of the team notebook), **GAT bagging** (4 GATs with bootstrap)
and **LogReg** (logistic regression baseline), all calibrated with isotonic regression.

## How the figures were obtained

- **Input layers (6):** GEOFISICA, HIDRO GEOQ, ROCAS, SILICE, STREAM GEOQ and SUELOS GEOQ, on a 1.5 km grid
  (UTM 11N) inside the study area. Each cell is a node of an 8-connected graph.
- **Known mines:** the project inventory (136 points, 93 mine cells).
- **Validation:** every figure on the page comes from spatial cross-validation with 22.5 km blocks (5 folds,
  3 seeds). Each cell was scored by a model that never saw its block. The maps themselves are painted with the final
  models trained on all mines.
- **Gold:** contained gold of each deposit (past production plus reserves and resources) from USGS Open-File Report
  2014-1074. USGS gives one figure per deposit, not per mine: when a deposit groups several inventory mines, its gold
  is drawn once, at its main mine, and the other mines are shown as small points.

## Files

| File | Role |
|---|---|
| `index.html` | The published page (generated, do not edit by hand). |
| `plantilla.html` | Page template: layout, styles and d3 v7 code. Data are injected in place of `/*__DATA__*/null`. |
| `construir_web.py` | Builds `index.html`: reprojects the model rasters to Web Mercator and embeds rasters, mines, trends and ablation results into the template. |
| `preparar_minas.py` | Joins the mine inventory with the USGS deposit table (contained and produced gold per deposit). |
| `datos/` | Mines with their USGS gold figures (`minas_produccion.csv`, `minas.geojson`). |
| `fuentes/` | USGS OFR 2014-1074 deposit table. |

## Rebuilding the page

The build scripts read the model outputs of the parent project folder (grid, products and ablation tables), which
are not part of this repository. From that project:

```
python productos_v14.py --modelo base --oof resultados/oof      # also gat_bag and LogReg
python ablacion_ideas_v14.py --oof resultados/oof --modelos base,gat_bag,LogReg --semillas 3
python web/construir_web.py
```

Then commit `index.html`. After a change to `plantilla.html` only the last step is needed.

## Limits

- Probabilities refer to **known mines** in the inventory, at the stated cell or block size. They measure how often
  a cell or block like this one holds a known mine, not the geological probability of an undiscovered deposit.
- With 93 mine cells, small differences between models are within the fold-to-fold variation shown on the page
  (whiskers are ±1 standard deviation over folds and seeds).
- Negatives are "not known to hold a mine", not "barren".

## Credits

UNI and UTEC team. Mine gold figures: USGS Open-File Report 2014-1074. Basemaps: Esri World Imagery and Esri World
Light Gray Canvas.
