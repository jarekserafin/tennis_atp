# Tennis Analytics — EDA & Insights

Exploratory data analysis of professional tennis results with a focus on player performance over time, surface effects, head‑to‑head dynamics, and simple rating models.

> This repository contains my own analysis and code.  
> **Data source:** Replace this with the dataset you use (e.g., Jeff Sackmann’s tennis database or another source) and link to the original repository/website + license.

## Goals
- Understand historical performance trends in ATP/WTA tennis.
- Quantify **surface effects** (clay/grass/hard/indoor).
- Analyze **head‑to‑head** records and streaks.
- Build simple **rating metrics** (win rates, rolling form, optional Elo).
- Produce clean, reproducible notebooks and charts.

## Repository Structure
```
.
├─ data/                 # raw or processed CSVs (ignored by git if large)
├─ notebooks/
│  ├─ 01_data_overview.ipynb        # schema, sanity checks
│  ├─ 02_player_performance.ipynb   # per-player trends, rolling stats
│  ├─ 03_surface_effects.ipynb      # clay/grass/hard comparisons
│  ├─ 04_head_to_head.ipynb         # H2H tables, streaks, serve/return splits*
│  └─ 05_ratings_elo.ipynb          # optional Elo implementation*
├─ src/
│  ├─ io.py              # load_data(), caching, dtype schemas
│  ├─ features.py        # feature engineering, rolling windows
│  ├─ viz.py             # plotting helpers (matplotlib)
│  └─ ratings.py         # simple Elo (optional)
├─ reports/
│  ├─ figures/           # exported charts (png)
│  └─ tables/            # CSV summaries
├─ requirements.txt
├─ Makefile
└─ README.md
```
\* optional modules — include if you implement them

## Data
- **Source:** _PUT LINK + NAME HERE_ (e.g., Jeff Sackmann’s `tennis_atp` dataset).
- **License:** _PUT LICENSE/TERMS HERE_.  
- **Files used (examples):**
  - `matches_YYYY.csv` — match-level results (date, tournament, players, surface, score, winner/loser, rankings).
  - `rankings_YYYY.csv` — weekly rankings.
- **Data hygiene:**
  - Deduplicate matches, standardize player names (ID mapping), normalize surfaces, parse dates/time zones.

## How to Run
```bash
# 1) Create environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) (Optional) Put CSVs into data/ or set DATA_DIR env variable
export DATA_DIR=./data

# 3) Make reproducible artifacts
make report   # executes notebooks, exports charts to reports/figures
```

### Makefile (excerpt)
```makefile
report:
	jupyter nbconvert --to notebook --execute notebooks/01_data_overview.ipynb --output notebooks/01_data_overview.out.ipynb
	jupyter nbconvert --to notebook --execute notebooks/02_player_performance.ipynb --output notebooks/02_player_performance.out.ipynb
	jupyter nbconvert --to notebook --execute notebooks/03_surface_effects.ipynb --output notebooks/03_surface_effects.out.ipynb
```

## Analyses & Figures (Examples)
- **Top players over time:** ranking trajectories and **rolling 52‑week win rates**.
- **Surface effects:** per‑player **win% by surface**, surface‑adjusted performance deltas.
- **Head‑to‑head:** summary tables, **serve/return** proxies (if available), longest streaks.
- **Form index:** rolling 10‑match performance index.
- **(Optional) Elo:** simple Elo by surface.

> Include a few example plots in `reports/figures/`:
> - `top_players_ranking_trends.png`
> - `surface_winrates.png`
> - `h2h_matrix_playerX_vs_playerY.png`
> - `elo_rating_over_time.png` (optional)

## Reproducibility & Quality
- Deterministic seeds where applicable.
- Clear data types and parsing (`src/io.py`).
- No hard‑coded local paths — use `DATA_DIR` or relative paths.
- Notebooks are **idempotent**: re‑run end‑to‑end without manual steps.

## Results (to be updated)
| Topic | Key Finding | Figure |
|------|-------------|--------|
| Surface Effects | _e.g., Player A +12pp win% on clay vs hard_ | `reports/figures/surface_winrates.png` |
| Ranking Trends | _e.g., Player B peak period 2014–2016_ | `reports/figures/top_players_ranking_trends.png` |
| H2H | _e.g., Player C leads 8–3 vs Player D (grass advantage)_ | `reports/figures/h2h_matrix_playerC_playerD.png` |

## Limitations
- Data quality varies across years/tours; potential name mismatches.
- Not all matches have complete serve/return stats.
- Elo here is a didactic implementation, not production‑grade.

## Acknowledgements
- Original dataset: _PUT LINK + AUTHOR HERE_  
- Inspiration: public tennis analytics community.
