# Tennis ATP — Exploratory Data Analysis

A study project exploring ATP men's tennis rankings, player characteristics, and match statistics with Python. The analyses use local CSV data, pandas, NumPy, Matplotlib, Seaborn, and SciPy.

## Repository structure

```text
.
├── data/                       # Local ATP datasets
│   ├── atp_players.csv
│   ├── atp_rankings_70s.csv     # Rankings split by decade (70s–20s)
│   ├── atp_rankings_current.csv
│   ├── atp_matches_1968.csv     # Annual singles results (1968–2026)
│   ├── ...                    # Additional doubles, Futures, and qualifying/Challenger files
│   ├── matches_data_dictionary.txt
│   ├── LICENSE                # Dataset license
│   ├── UPSTREAM_README.md     # Original dataset documentation
│   └── .sackmann-source.json  # Download source, revision, and file hashes
├── rankings.ipynb              # Main exploratory analysis and charts
├── tennis.ipynb                # Initial data exploration and manual cleaning
├── rankings.py                # Average player age over ranking dates
├── stats.py                   # Annual match statistics from 1991 onward
├── update_data.py             # Download and update Sackmann's ATP data
├── player_corrections.json    # Local player-data corrections kept during updates
├── tests/                     # Data updater tests
├── requirements.txt
└── README.md
```

## Available analyses

### `rankings.ipynb`

The main notebook discovers the ranking files and annual singles files available in `data/`, currently covering seasons 1968–2026. It also loads player biographies and removes duplicate ranking records by date and player. Its ranking analyses retain records with at least 68 ranking points, a calculated player age of at least 16 years, and a height of at least 160 cm. Records with missing age or height are also excluded from this sample. These filters apply to the ranking analysis table (`merged_df`); the source CSV files and match analysis table are retained.

It includes:

- Player height distribution and average age over time.
- The share of left-handed players over time and average ranking points by playing hand.
- Correlations between age, height, and ranking points.
- Ranking-point trajectories for five selected players.
- Trends in aces, first serves made, double faults, and match duration, with linear regression and Pearson correlation coefficients.
- Seasonal win counts by surface for two selected players and average match duration by surface.

The notebook filters match data to 1990 onward before analysing match duration; subsequent match analyses use that filtered dataset. Aces, first serves made, and double faults are calculated as the mean of the two players' counts, rather than the combined match total. Surface comparisons show win counts, rather than win percentages.

### `rankings.py`

Discovers all `atp_rankings_*.csv` files, including `atp_rankings_current.csv`, removes duplicate records by date and player, joins player biographies, and plots average age by ranking date. It selects the first 100 rows per date in the input order with `groupby(...).head(100)`; it does not explicitly sort by rank.

### `stats.py`

Discovers annual singles files from 1991 onward and builds a table of yearly averages: first serves made by winners, winners' double faults, winners' height, winners' and losers' age, age difference, and match duration. It also calculates the share of matches won by players whose playing hand is recorded as `R` or `U` (unknown). The script prints the first rows and displays a chart of average match duration.

### `tennis.ipynb`

An initial exploration of player data, the top 150 ranking positions on 27 May 2024, missing playing-hand values, and match data from 2003 and 2023. It contains manual corrections tied to specific row indices and currently needs corrections before it can be run from start to finish; see the limitations below.

## Data

The data was collected and compiled by Jeff Sackmann / Tennis Abstract for the original [ATP tennis dataset](https://github.com/JeffSackmann/tennis_atp). Downloads use the [Sackmann data archive](https://github.com/Aneeshers/tennis-sackmann-archive), which preserves an ATP snapshot from June 2026. The dataset is distributed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/); the updater also downloads the license and original dataset README into `data/`.

The files used by the analyses are included in `data/`:

| Files | Contents |
| --- | --- |
| `atp_players.csv` | Player IDs, names, playing hand, date of birth, country, height, and Wikidata ID |
| `atp_rankings_70s.csv` through `atp_rankings_20s.csv` | Historical ranking dates, positions, player IDs, and points |
| `atp_rankings_current.csv` | A local 2026 ranking snapshot, with the latest ranking date of 8 June 2026 |
| `atp_matches_1968.csv` through `atp_matches_2026.csv` | Singles results, tournament information, player details, and available match statistics |
| `matches_data_dictionary.txt` | Descriptions of match columns and codes |

The 2024 file has been refreshed and the 2025 and 2026 files added. The 2026 match file has tournament dates through 25 May 2026 and represents a partial season. Tournament dates usually identify the tournament week, rather than the day of an individual match. The name `current` refers to the stored ranking snapshot, rather than a live feed. Additional doubles, Futures, amateur, and qualifying/Challenger files are present, but the current analyses do not load them.

## Downloading and updating data

From the repository root, run:

```bash
python3 update_data.py
```

Use the same command for the first download and every subsequent update. It requires Python and an internet connection; no extra Python packages, Git installation, or GitHub login are needed. On Windows, use `python` instead of `python3`.

By default, the updater synchronizes all annual singles results, historical and current rankings, player biographies, and dataset documentation. It compares local files with GitHub's file hashes and downloads only missing or changed files, including corrections to older seasons. Changed files in this selection are replaced with the source versions; unrelated local files are retained.

All downloads use one source commit. The updater stages the changed files, checks their hashes and required CSV columns, and only then replaces local data. A failed download or validation leaves existing data intact. Source details are recorded in `data/.sackmann-source.json`, and the latest match and ranking dates are printed after an update.

Player corrections are stored in `player_corrections.json`, keyed by Sackmann's player ID, and applied after source validation. Source and corrected local hashes are recorded separately, so subsequent updates retain these corrections and skip unchanged data. The current correction sets Jorge Brian Panta Herreros (ID `106410`) to 178 cm, as supplied by the project owner; the source file incorrectly records 3 cm.

```bash
# List available changes without downloading or changing local files
python3 update_data.py --check

# Also synchronize doubles, Futures, qualifying/Challenger, and amateur match files
python3 update_data.py --all

# Download into a separate directory
python3 update_data.py --data-dir /path/to/another/data
```

The selected source is an archive of Sackmann's data from June 2026. Re-running the updater checks that archive for changes; it cannot provide newer results unless the archive itself is updated. The latest recorded source commit is available in the local metadata file.

After updating, rerun the scripts or restart the notebook kernel and run the cells in order. `rankings.ipynb`, `rankings.py`, and `stats.py` discover available files automatically, so adding a new season does not require editing year ranges. The analyses use the project's `data/` directory; `--data-dir` only changes where the updater writes files.

## Setup and usage

Run these commands from the repository root. The main notebook uses relative paths such as `data/atp_players.csv`; the scripts locate `data/` beside their source files.

### Create an environment and install dependencies

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Run the main notebook

```bash
jupyter notebook rankings.ipynb
```

Select the Python kernel from the environment with the installed dependencies, then run the cells in order. Charts and calculated values appear in the notebook. `tennis.ipynb` can also be opened in Jupyter, but requires the corrections described below.

### Run the scripts

```bash
python rankings.py
python stats.py
```

Each script displays a Matplotlib chart with `plt.show()`; a graphical environment is needed to view the plot window. `rankings.py` also prints its data-processing time, and `stats.py` prints a preview of the yearly statistics table. Charts and tables are not automatically exported to files.

### Verify the data updater

```bash
python3 -m unittest discover -s tests -v
```

These tests run offline and cover file selection, repeated updates, integrity and schema validation, and preserving existing data after a download failure.

